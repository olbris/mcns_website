"""
This script generates the following pages for the website:

1. The overview page for all sexually dimorphic cell types
2. The summaries for individual sexually dimorphic cell types
"""

import argparse

from build_tools import loading, building

# Set up the argument parser
parser = argparse.ArgumentParser(
    description="Generate HTML pages for sexually dimorphic cell types."
)
# Add option to force meta data update
parser.add_argument(
    "--update-metadata",
    action="store_true",
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
parser.add_argument(
    "--clear-build",
    action="store_true",
    help="Clear the build directory before generating pages.",
)


if __name__ == "__main__":
    # Load the template
    args = parser.parse_args()

    # Load meta data
    mcns_meta, fw_meta = loading.load_cache_meta_data(force_update=args.update_metadata)
    mcns_meta["type"] = mcns_meta.type.fillna(mcns_meta.flywireType).fillna("unknown")
    mappings = loading.load_cache_mapping(force_update=args.update_metadata)
    fw_edges = loading.load_cache_fw_edges(force_update=args.update_metadata)

    # Add MCNS <-> FlyWire mapping to the meta data
    mcns_meta["mapping"] = mcns_meta["bodyId"].map(mappings)
    fw_meta["mapping"] = fw_meta["root_id"].map(mappings)

    # Generate the dimorphism pages (overview and individual pages)
    building.make_dimorphism_pages(mcns_meta, fw_meta, fw_edges)
