"""
Functions for loading and caching data from neuPrint and FlyWire.
"""

import json
import requests

import cocoa as cc
import pandas as pd
import navis.interfaces.neuprint as neu

from io import BytesIO

from .env import (
    MCNS_FW_MAPPING_URL,
    # MCNS_MANC_MAPPING_URL,
    FW_EDGES_URL,
    MCNS_META_DATA_CACHE,
    MCNS_ROI_INFO_CACHE,
    FW_META_DATA_CACHE,
    FW_ROI_INFO_CACHE,
    MAPPING_CACHE,
    CACHE_DIR,
    NEUPRINT_CLIENT,
)


def load_cache_meta_data(force_update=False):
    """Load the (possibly cached) meta data."""
    if (
        MCNS_META_DATA_CACHE.exists()
        and MCNS_ROI_INFO_CACHE.exists()
        and not force_update
    ):
        mcns_data = pd.read_feather(MCNS_META_DATA_CACHE)
        mcns_roi_info = pd.read_feather(MCNS_ROI_INFO_CACHE)
        print(
            "Loaded MCNS meta data from cache. Use the --update-metadata flag to force reloading.",
            flush=True,
        )
    else:
        print("Loading MCNS meta data from neuPrint...", flush=True, end="")
        mcns_data, mcns_roi_info = neu.fetch_neurons(
            neu.NeuronCriteria(), client=NEUPRINT_CLIENT
        )

        # Try to convert object columns to strings - otherwise loading the data becomes obscenely slow
        for col in mcns_data.select_dtypes(include=["object"]).columns:
            try:
                mcns_data[col] = mcns_data[col].astype("string")
            except Exception as e:
                print(f"Failed to convert column {col}: {e}", flush=True)

        mcns_data.to_feather(MCNS_META_DATA_CACHE)
        mcns_roi_info.to_feather(MCNS_ROI_INFO_CACHE)
        print(f"Done. Found {len(mcns_data):,} MCNS neurons.", flush=True)

    if FW_META_DATA_CACHE.exists() and not force_update:
        fw_data = pd.read_feather(FW_META_DATA_CACHE)
        print(
            "Loaded FlyWire meta data from cache. Use the --update-metadata flag to force reloading.",
            flush=True,
        )
    else:
        print("Loading FlyWire meta data from FlyTable...", flush=True, end="")
        fw_data = cc.FlyWire(live_annot=True).get_annotations()

        # Try to convert object columns to strings - otherwise loading the data becomes obscenely slow
        for col in fw_data.select_dtypes(include=["object"]).columns:
            try:
                fw_data[col] = fw_data[col].astype("string")
            except Exception as e:
                print(f"Failed to convert column {col}: {e}", flush=True)

        fw_data.to_feather(FW_META_DATA_CACHE)
        print(f"Done. Found {len(fw_data):,} FlyWire neurons.", flush=True)

    fw_data["type"] = fw_data.cell_type.fillna(fw_data.hemibrain_type).fillna(
        fw_data.malecns_type
    )

    if FW_ROI_INFO_CACHE.exists():
        fw_roi_info = pd.read_feather(FW_ROI_INFO_CACHE)
        print(
            "Loaded FlyWire ROI info from cache. Use the --update-metadata flag to force reloading.",
            flush=True,
        )
    else:
        print("Loading and compiling FlyWire ROI info from Zenodo...", flush=True, end="")
        # Load presynapses (17Mb)
        r = requests.get(
            "https://zenodo.org/records/10676866/files/per_neuron_neuropil_count_pre_783.feather?download=1"
        )
        r.raise_for_status()
        pre = pd.read_feather(BytesIO(r.content)).rename(
            columns={"pre_pt_root_id": "root_id"}
        )
        # Load postsynapses (233Mb)
        r = requests.get(
            "https://zenodo.org/records/10676866/files/per_neuron_neuropil_count_post_783.feather?download=1"
        )
        r.raise_for_status()
        post = pd.read_feather(BytesIO(r.content)).rename(
            columns={"post_pt_root_id": "root_id"}
        )
        # Combine
        fw_roi_info = pd.merge(
            pre.set_index(["root_id", "neuropil"])["count"],
            post.set_index(["root_id", "neuropil"])["count"],
            left_index=True,
            right_index=True,
        ).reset_index(drop=False)
        fw_roi_info.columns = ["root_id", "roi", "pre", "post"]

        # Rename neuropils to align to MaleCNS
        fw_roi_info.loc[fw_roi_info.roi.str.endswith("_L", na=False), "roi"] = fw_roi_info.loc[fw_roi_info.roi.str.endswith("_L", na=False), "roi"].str.replace("_L", "(L)")
        fw_roi_info.loc[fw_roi_info.roi.str.endswith("_R", na=False), "roi"] = fw_roi_info.loc[fw_roi_info.roi.str.endswith("_R", na=False), "roi"].str.replace("_R", "(R)")

        # Save to cache
        fw_roi_info.to_feather(FW_ROI_INFO_CACHE)
        print("Done.", flush=True)

    return mcns_data, fw_data, mcns_roi_info, fw_roi_info


def load_cache_mapping(force_update=False):
    """Load the (possibly cached) male-female mapping."""
    if MAPPING_CACHE.exists() and not force_update:
        with open(MAPPING_CACHE, "r") as f:
            mappings = json.load(f)
            mappings = {int(k): v for k, v in mappings.items()}  # Convert keys to int
        print(
            "Loaded cross-dataset mapping from cache. Use the --update-metadata flag to force reloading.",
            flush=True,
        )
    else:
        print("Loading cross-dataset from flyem1...", flush=True, end="")
        r = requests.get(MCNS_FW_MAPPING_URL)
        mappings = r.json()

        # Remove the dataset prefix from the "{dataset}:{id}" keys
        mappings = {int(k.split(":")[1]): v for k, v in mappings.items()}

        with open(MAPPING_CACHE, "w") as f:
            json.dump(mappings, f)
        print("Done.", flush=True)

    return mappings


def load_cache_fw_edges(force_update=False):
    """Load the (possibly cached) FlyWire edges."""
    filename = FW_EDGES_URL.split("/")[-1]
    filepath = CACHE_DIR / filename

    if filepath.exists() and not force_update:
        fw_edges = pd.read_feather(filepath)
        print(
            "Loaded FlyWire edges from cache. Use the --update-metadata flag to force reloading.",
            flush=True,
        )
    else:
        print("Loading FlyWire edges from flyem1...", flush=True, end="")
        fw_edges = pd.read_feather(FW_EDGES_URL)
        fw_edges.to_feather(filepath)
        print("Done.", flush=True)

    return fw_edges
