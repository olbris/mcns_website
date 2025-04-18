"""
This script generates the following pages for the website:

1. The overview page for all sexually dimorphic cell types
2. The summaries for individual sexually dimorphic cell types
"""

import json
import navis
import requests
import argparse

import cocoa as cc
import pandas as pd
import nglscenes as ngl
import navis.interfaces.neuprint as neu

from pathlib import Path
from d3blocks import D3Blocks
from jinja2 import Environment, FileSystemLoader, select_autoescape

NGL_BASE_URL = "https://clio-ng.janelia.org/#!gs://flyem-user-links/short/2025-04-14.184028.199909.json"
NGL_BASE_SCENE = ngl.Scene.from_url(NGL_BASE_URL)

MCNS_FW_MAPPING_URL = (
    "https://flyem.mrc-lmb.cam.ac.uk/flyconnectome/mappings/mcns_fw_mapping.json"
)
MCNS_MANC_MAPPING_URL = (
    "https://flyem.mrc-lmb.cam.ac.uk/flyconnectome/mappings/mcns_manc_mapping.json"
)

TEMPLATE_DIR = Path(__file__).parent / "templates"
BUILD_DIR = Path(__file__).parent / "docs/build"

CACHE_DIR = Path(__file__).parent / ".cache"
GRAPH_CACHE_DIR = BUILD_DIR / "graphs"
MCNS_META_DATA_CACHE = CACHE_DIR / "mcns_meta_data.feather"
FW_META_DATA_CACHE = CACHE_DIR / "fw_meta_data.feather"
MAPPING_CACHE = CACHE_DIR / "mapping.json"

# Make sure the directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
GRAPH_CACHE_DIR.mkdir(parents=True, exist_ok=True)
BUILD_DIR.mkdir(parents=True, exist_ok=True)

# Set up the Jinja2 environment
ENV = Environment(
    loader=FileSystemLoader(searchpath=TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)

# Set up the argument parser
parser = argparse.ArgumentParser(
    description="Generate HTML pages for sexually dimorphic cell types."
)
# Add option to force meta data update
parser.add_argument(
    "--force-update",
    help="Force update of the meta data cache.",
)
# Add options to skip certain steps
parser.add_argument(
    "--skip-thumbnails",
    action="store_true",
    help="Skip the generation of thumbnail images.",
)
parser.add_argument(
    "--skip-overview",
    action="store_true",
    help="Skip the generation of the overview page.",
)
parser.add_argument(
    "--skip-profiles",
    action="store_true",
    help="Skip the generation of individual cell type pages.",
)

client = neu.Client(server="https://neuprint-cns.janelia.org", dataset="cns")


def load_cache_meta_data(force_update=False):
    """Load the (possibly cached) meta data."""
    if MCNS_META_DATA_CACHE.exists() and not force_update:
        mcns_data = pd.read_feather(MCNS_META_DATA_CACHE)
        print(
            "Loaded meta data from cache. Use the --force-update flag to force reloading.",
            flush=True,
        )
    else:
        print("Loading MCNS meta data from neuPrint...", flush=True, end="")
        mcns_data, _ = neu.fetch_neurons(
            neu.NeuronCriteria(status="Traced"), client=client
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
            "Loaded FlyWire meta data from cache. Use the --force-update flag to force reloading.",
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

    return mcns_data, fw_data


def load_cache_mapping(force_update=False):
    """Load the (possibly cached) male-female mapping."""
    if MAPPING_CACHE.exists() and not force_update:
        with open(MAPPING_CACHE, "r") as f:
            data = json.load(f)
            data = {int(k): v for k, v in data.items()}  # Convert keys to int
        print(
            "Loaded cross-dataset mapping from cache. Use the --force-update flag to force reloading.",
            flush=True,
        )
    else:
        print("Loading cross-dataset from flyem1...", flush=True, end="")
        r = requests.get(MCNS_FW_MAPPING_URL)
        data = r.json()

        # Remove the dataset prefix from the "{dataset}:{id}" keys
        data = {int(k.split(":")[1]): v for k, v in data.items()}

        with open(MAPPING_CACHE, "w") as f:
            json.dump(data, f)
        print("Done.", flush=True)

    return data


def make_dimorphism_pages(mcns_meta, fw_meta):
    """Generate the overview page.

    Parameters
    ----------
    meta : pd.DataFrame
        The meta data for the neurons as returned from neuPrint.

    """
    print("Generating overview page...", flush=True)
    # Load the template for the overview page
    overview_template = ENV.get_template("dimorphism_overview.md")

    # Filter to dimorphic types
    dimorphic_types = mcns_meta[
        mcns_meta.dimorphism.str.contains("dimorphic", na=False)
    ]

    # For each type compile a dictionary with relevant data
    dimorphic_meta = []
    for t, table in dimorphic_types.groupby("mapping"):
        dimorphic_meta.append({})

        for col in table.columns:
            vals = table[col].fillna("None").unique()
            if len(vals) == 1:
                dimorphic_meta[-1][col] = vals[0]
            else:
                dimorphic_meta[-1][col] = ", ".join(vals.astype(str))

        scene = NGL_BASE_SCENE.copy()
        scene.layers[1]["segments"] = table["bodyId"].values
        scene.layers[1]["segmentDefaultColor"] = "#00e9e7"

        # Grab the corresponding type in FlyWire
        table_fw = fw_meta[fw_meta["mapping"] == t]

        if table_fw.empty:
            print(f"  No matching FlyWire type for {t}.", flush=True)
        else:
            scene.layers[2]["segments"] = table_fw["root_id"].values
            scene.layers[2]["segmentDefaultColor"] = "#e511d0"

        dimorphic_meta[-1]["url"] = scene.url

    print(f"Found {len(dimorphic_meta):,} dimorphic cell types.", flush=True)
    # Render the template with the meta data
    rendered = overview_template.render(dimorphic_types=dimorphic_meta)

    #  Write the rendered HTML to a file
    with open(BUILD_DIR / "dimorphism_overview.md", "w") as f:
        f.write(rendered)

    print("Done.", flush=True)

    # Generate individual pages for each dimorphic cell type
    print("Generating individual pages...", flush=True, end="")
    # Loop through each dimorphic cell type and generate a page
    for record in dimorphic_meta:
        print(f"  Generating summary page for {record['type']}...", flush=True)

        # Generate the graph
        generate_graphs(
            record['type'],
            mcns_meta[mcns_meta["mapping"] == record["mapping"]],
            fw_meta[fw_meta["mapping"] == record["mapping"]],
        )

        record['graph_file'] = BUILD_DIR / "graphs" / (record['type'] + ".html")

        with open(record['graph_file'], "r") as f:
            record['graph_html'] = f.read()

        build_summary_page(record)
        break

    print("Done.", flush=True)


def generate_graphs(type, mcns, fw):
    """Generate D3 graphs for the given neurons.

    Parameters
    ----------
    mcns : pd.DataFrame
        The meta data for the MCNS neurons.
    fw : pd.DataFrame
        The meta data for the FlyWire neurons.

    """
    # Fetch MCNS connectivity
    ann, cn = neu.fetch_adjacencies(
        neu.NeuronCriteria(bodyId=mcns["bodyId"].values),
    )
    cn["pre_type"] = cn.bodyId_pre.map(ann.set_index("bodyId").type)
    cn["post_type"] = cn.bodyId_post.map(ann.set_index("bodyId").type)
    df = (
        cn.groupby(["pre_type", "post_type"], as_index=False)
        .weight.sum()
        .rename(columns={"pre_type": "source", "post_type": "target"})
        .sort_values("weight", ascending=False)
    ).reset_index(drop=True)

    print(df.iloc[:10])

    d3 = D3Blocks()
    d3.elasticgraph(df.iloc[:10], filepath=GRAPH_CACHE_DIR / f"{type}.html")

    return GRAPH_CACHE_DIR / f"{type}.html"


def build_summary_page(record):
    # Load the template for the individual pages
    individual_template = ENV.get_template("dimorphism_individual.md")

    rendered = individual_template.render(meta=record)

    # Write the rendered HTML to a file
    with open(BUILD_DIR / f"{record['type']}.md", "w") as f:
        f.write(rendered)


if __name__ == "__main__":
    # Load the template
    args = parser.parse_args()

    # Load data
    mcns_meta, fw_meta = load_cache_meta_data(force_update=args.force_update)
    mcns_meta["type"] = mcns_meta.type.fillna(mcns_meta.flywireType).fillna("unknown")
    mappings = load_cache_mapping(force_update=args.force_update)

    # Add mapping to the meta data
    mcns_meta["mapping"] = mcns_meta["bodyId"].map(mappings)
    fw_meta["mapping"] = fw_meta["root_id"].map(mappings)

    make_dimorphism_pages(mcns_meta, fw_meta)
