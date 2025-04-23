"""
Some global variables and constants for the build tools.
"""

import nglscenes as ngl
import navis.interfaces.neuprint as neu

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

#####
# A basic Neuroglancer scene to use as a base for the visualisation
#####
NGL_BASE_URL = "https://clio-ng.janelia.org/#!gs://flyem-user-links/short/2025-04-14.184028.199909.json"
NGL_BASE_SCENE = ngl.Scene.from_url(NGL_BASE_URL)

#####
# URLs for the MCNS and FlyWire meta data
#####
FLYWIRE_SOURCE = NGL_BASE_SCENE.layers["female (FlyWire)"]["source"]
MCNS_SOURCE = NGL_BASE_SCENE.layers["maleCNS"]["source"]["url"]
DVID_SERVER = "https://" + MCNS_SOURCE.replace("dvid://https://", "").split("/")[0]
DVID_NODE = MCNS_SOURCE.replace("dvid://https://", "").split("/")[1]

print(f"Using DVID server: {DVID_SERVER}")
print(f"Using DVID node: {DVID_NODE}")

#####
# Mappings between MCNS -> FlyWire/MANC
# These mappings are re-generated on a 30-minute CRON job on the server
#####
MCNS_FW_MAPPING_URL = (
    "https://flyem.mrc-lmb.cam.ac.uk/flyconnectome/mappings/mcns_fw_mapping.json"
)
MCNS_MANC_MAPPING_URL = (
    "https://flyem.mrc-lmb.cam.ac.uk/flyconnectome/mappings/mcns_manc_mapping.json"
)

#####
# URL for downloading edges for the FlyWire connectome
# This file is the grouped edge list from https://zenodo.org/records/10676866
#####
FW_EDGES_URL = "https://flyem.mrc-lmb.cam.ac.uk/flyconnectome/flywire_connectivity/proofread_connections_783_grouped.feather"

#####
# Various directories for the build / cache
#####

# Basepath for the repository
REPO_BASE_PATH = Path(__file__).parent.parent

# Directory for the JINJA templates
TEMPLATE_DIR = REPO_BASE_PATH / "templates"

# Directory for the generated HTML files
BUILD_DIR = REPO_BASE_PATH / "docs/build"
THUMBNAILS_DIR = BUILD_DIR / "thumbnails"
GRAPH_DIR = BUILD_DIR / "graphs"

# Directory for the some cached data (use the --update-metadata flag to trigger a refresh)
CACHE_DIR = REPO_BASE_PATH / ".cache"
MCNS_META_DATA_CACHE = CACHE_DIR / "mcns_meta_data.feather"
FW_META_DATA_CACHE = CACHE_DIR / "fw_meta_data.feather"
MAPPING_CACHE = CACHE_DIR / "mapping.json"

# Make sure the directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
GRAPH_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
BUILD_DIR.mkdir(parents=True, exist_ok=True)

#####
# Set up the Jinja2 environment
#####
JINJA_ENV = Environment(
    loader=FileSystemLoader(searchpath=TEMPLATE_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)

#####
# A global neuprint client
#####
NEUPRINT_CLIENT = neu.Client(server="https://neuprint-cns.janelia.org", dataset="cns")

#####
# Some BASE URLs for neuPrint
#####

# Basic neuPrint search
NEUPRINT_SEARCH_URL = "https://neuprint-cns.janelia.org/results?dataset=cns&qt=findneurons&q=1&qr%5B0%5D%5Bcode%5D=fn&qr%5B0%5D%5Bds%5D=cns&qr%5B0%5D%5Bpm%5D%5Bdataset%5D=cns&qr%5B0%5D%5Bpm%5D%5BinputMatchAny%5D=false&qr%5B0%5D%5Bpm%5D%5BoutputMatchAny%5D=false&qr%5B0%5D%5Bpm%5D%5Ball_segments%5D=false&qr%5B0%5D%5Bpm%5D%5Benable_contains%5D=true&qr%5B0%5D%5Bpm%5D%5Bneuron_name%5D={neuron_name}&qr%5B0%5D%5BvisProps%5D%5BrowsPerPage%5D=25&tab=0"

# Connectivity search
NEUPRINT_CONNECTIVITY_URL = "https://neuprint-cns.janelia.org/results?dataset=cns&qt=simpleconnection&q=1&qr%5B0%5D%5Bcode%5D=sc&qr%5B0%5D%5Bds%5D=cns&qr%5B0%5D%5Bpm%5D%5Bdataset%5D=cns&qr%5B0%5D%5Bpm%5D%5Benable_contains%5D=true&qr%5B0%5D%5Bpm%5D%5Bneuron_name%5D={neuron_name}&qr%5B0%5D%5Bpm%5D%5Bfind_inputs%5D=false&qr%5B0%5D%5BvisProps%5D%5BpaginateExpansion%5D=true&tab=0"
