"""
This script generates the following pages for the website:

1. The overview page for all sexually dimorphic cell types
2. The summaries for individual sexually dimorphic cell types
"""

import argparse
import random

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
    "--skip-graphs",
    action="store_true",
    # we're not using graphs anymore; use --no-skip-graphs if you want them
    default=True,
    help="Skip the generation of networks graphs.",
)
parser.add_argument(
    "--skip-tables",
    action="store_true",
    help="Skip the generation of connectivity tables.",
)
parser.add_argument(
    "--skip-supertypes",
    action="store_true",
    help="Skip the generation of summary pages for supertypes.",
)
parser.add_argument(
    "--skip-hemilineages",
    action="store_true",
    help="Skip the generation of summary pages for hemilineages.",
)
parser.add_argument(
    "--skip-synonyms",
    action="store_true",
    help="Skip the generation of summary pages for synonyms.",
)
parser.add_argument(
    "--clear-build",
    action="store_true",
    help="Clear the build directory before generating pages.",
)
parser.add_argument(
    "--clear-site",
    action="store_true",
    help="Clear the site directory before generating pages.",
)

# allow user to specify how many random pages to build for testing
parser.add_argument(
    "--random-pages",
    type=int,
    default=None,
    help="Specify a number of random pages to build (for testing).",
)

parser.add_argument(
    "--random-seed",
    type=int,
    default=283761,   # chosen by poking the keyboard
    help="Specify a random seed for reproducibility.",
)


if __name__ == "__main__":
    # Load the template
    args = parser.parse_args()

    # Load meta data
    mcns_meta, fw_meta, mcns_roi_info, fw_roi_info = loading.load_cache_meta_data(
        force_update=args.update_metadata
    )
    # mcns_meta["type"] = mcns_meta.type.fillna(mcns_meta.flywireType).fillna("unknown")
    mappings = loading.load_cache_mapping(force_update=args.update_metadata)
    fw_edges = loading.load_cache_fw_edges(force_update=args.update_metadata)

    # Add MCNS <-> FlyWire mapping to the meta data
    mcns_meta["mapping"] = mcns_meta["bodyId"].map(mappings)
    fw_meta["mapping"] = fw_meta["root_id"].map(mappings)

    if args.clear_build:
        # Clear the build directory
        building.clear_build_directory()

    if args.clear_site:
        # Clear the site directory
        building.clear_site_directory()

    if args.random_pages is not None:
        if args.random_pages <= 0:
            raise ValueError("The --random-pages argument must be a positive integer.")
        random.seed(args.random_seed)

    # Generate the supertype pages
    if not args.skip_supertypes:
        building.make_supertype_pages(
            mcns_meta, fw_meta, skip_thumbnails=args.skip_thumbnails, random_pages=args.random_pages,
        )

    # Generate the individual synonyms pages + thumbnails
    if not args.skip_synonyms:
        building.make_synonyms_pages(
            mcns_meta, fw_meta, skip_thumbnails=args.skip_thumbnails, random_pages=args.random_pages,
        )

    # Generate the hemilineage pages
    if not args.skip_hemilineages:
        building.make_hemilineage_pages(mcns_meta, fw_meta, random_pages=args.random_pages)

    # Generate the dimorphism pages (overview and individual pages)
    building.make_dimorphism_pages(
        mcns_meta,
        fw_meta,
        fw_edges,
        mcns_roi_info,
        fw_roi_info,
        skip_graphs=args.skip_graphs,
        skip_thumbnails=args.skip_thumbnails,
        skip_tables=args.skip_tables,
        random_pages=args.random_pages,
    )
