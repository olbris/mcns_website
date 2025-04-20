"""
Functions for loading and caching data from neuPrint and FlyWire.
"""

import json
import requests

import cocoa as cc
import pandas as pd
import navis.interfaces.neuprint as neu

from .env import (
    MCNS_FW_MAPPING_URL,
    # MCNS_MANC_MAPPING_URL,
    FW_EDGES_URL,
    MCNS_META_DATA_CACHE,
    FW_META_DATA_CACHE,
    MAPPING_CACHE,
    CACHE_DIR,
    NEUPRINT_CLIENT,
)


def load_cache_meta_data(force_update=False):
    """Load the (possibly cached) meta data."""
    if MCNS_META_DATA_CACHE.exists() and not force_update:
        mcns_data = pd.read_feather(MCNS_META_DATA_CACHE)
        print(
            "Loaded meta data from cache. Use the --update-metadata flag to force reloading.",
            flush=True,
        )
    else:
        print("Loading MCNS meta data from neuPrint...", flush=True, end="")
        mcns_data, _ = neu.fetch_neurons(
            neu.NeuronCriteria(status="Traced"), client=NEUPRINT_CLIENT
        )

        # Try to convert object columns to strings - otherwise loading the data becomes obscenely slow
        for col in mcns_data.select_dtypes(include=["object"]).columns:
            try:
                mcns_data[col] = mcns_data[col].astype("string")
            except Exception as e:
                print(f"Failed to convert column {col}: {e}", flush=True)

        mcns_data.to_feather(MCNS_META_DATA_CACHE)
        print(f"Done. Found {len(mcns_data):,} MCNS neurons.", flush=True)

    if FW_META_DATA_CACHE.exists() and not force_update:
        fw_data = pd.read_feather(FW_META_DATA_CACHE)
        print(
            "Loaded FlyWire meta data from cache. Use the --update-metadata flag to force reloading.",
            flush=True,
        )
    else:
        print("Loading meta data from FlyTable...", flush=True, end="")
        fw_data = cc.FlyWire(live_annot=True).get_annotations()

        # Try to convert object columns to strings - otherwise loading the data becomes obscenely slow
        for col in fw_data.select_dtypes(include=["object"]).columns:
            try:
                fw_data[col] = fw_data[col].astype("string")
            except Exception as e:
                print(f"Failed to convert column {col}: {e}", flush=True)

        fw_data.to_feather(FW_META_DATA_CACHE)
        print(f"Done. Found {len(fw_data):,} FlyWire neurons.", flush=True)

    fw_data['type'] = fw_data.cell_type.fillna(fw_data.hemibrain_type).fillna(fw_data.malecns_type)

    return mcns_data, fw_data


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
