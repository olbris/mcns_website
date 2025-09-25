"""
Some global variables and constants for the build tools.
"""

import os

import nglscenes as ngl
import navis.interfaces.neuprint as neu

from pathlib import Path
from requests_futures.sessions import FuturesSession
from jinja2 import Environment, FileSystemLoader, select_autoescape

# FutureSession for async requests
FUTURE_SESSION = FuturesSession(max_workers=10)

#####
# A basic Neuroglancer scene to use as a base for the visualisation
#####
NGL_BASE_URL = "https://neuroglancer-demo.appspot.com/#!gs://flyem-user-links/short/MaleCNS-v0.9-brain.json"
NGL_BASE_SCENE = ngl.Scene.from_url(NGL_BASE_URL)
NGL_BASE_URL_VNC = "https://neuroglancer-demo.appspot.com/#!gs://flyem-user-links/short/MaleCNS-v0.9-vnc.json"
NGL_BASE_SCENE_VNC = ngl.Scene.from_url(NGL_BASE_URL_VNC)
NGL_BASE_URL_TOP = "https://neuroglancer-demo.appspot.com/#!gs://flyem-user-links/short/MaleCNS-v0.9-brain+vnc.json"
NGL_BASE_SCENE_TOP = ngl.Scene.from_url(NGL_BASE_URL_TOP)

# Make sure the segmentation layers are empty
for scene in (NGL_BASE_SCENE, NGL_BASE_SCENE_VNC, NGL_BASE_SCENE_TOP):
    for i in range(2):
        scene.layers[i]['segments'] = []

# Make backgrounds white
# for scene in (NGL_BASE_SCENE, NGL_BASE_SCENE_VNC, NGL_BASE_SCENE_TOP):
#     scene["projectionBackgroundColor"] = "#ffffff"

#####
# URLs for the MCNS and FlyWire meta data
#####
# FLYWIRE_SOURCE = NGL_BASE_SCENE.layers["female (FlyWire)"][
#     "source"
# ]  # precomputed layer
# print(f"Philipp's flywire source: {FLYWIRE_SOURCE}")
# switched to hardcoded; the ng scene we use now has this info in an archived
#   layer, and ngl.Scene.from_url() doesn't load them
FLYWIRE_SOURCE = "precomputed://https://flyem.mrc-lmb.cam.ac.uk/flyconnectome/flywire2mcns/783_v2"

# used to get DVID info from the NG scene, but that info is no longer there;
#     now it's passed in via env var
# MCNS_SOURCE = NGL_BASE_SCENE.layers["maleCNS"]["source"]["url"]  # DVID layer
# DVID_SERVER = "https://" + MCNS_SOURCE.replace("dvid://https://", "").split("/")[0]
# DVID_NODE = MCNS_SOURCE.replace("dvid://https://", "").split("/")[1]
DVID_SERVER = os.environ["DVID_SERVER"]
DVID_NODE = os.environ["DVID_NODE"]

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
SUMMARY_TYPES_DIR = BUILD_DIR / "summary_types"
THUMBNAILS_DIR = BUILD_DIR / "thumbnails"
GRAPH_DIR = BUILD_DIR / "graphs"
TABLES_DIR = BUILD_DIR / "tables"
SUPERTYPE_DIR = BUILD_DIR / "supertypes"
HEMILINEAGE_DIR = BUILD_DIR / "hemilineages"
SYNONYMS_DIR = BUILD_DIR / "synonyms"

# Directory for the final HTML files
SITE_DIR = REPO_BASE_PATH / "site"

# Directory for the some cached data (use the --update-metadata flag to trigger a refresh)
CACHE_DIR = REPO_BASE_PATH / ".cache"
MCNS_META_DATA_CACHE = CACHE_DIR / "mcns_meta_data.feather"
MCNS_ROI_INFO_CACHE = CACHE_DIR / "mcns_roi_info.feather"
FW_META_DATA_CACHE = CACHE_DIR / "fw_meta_data.feather"
FW_ROI_INFO_CACHE = CACHE_DIR / "fw_roi_info.feather"
MAPPING_CACHE = CACHE_DIR / "mapping.json"

# Make sure the directories exist
for dir in (
    CACHE_DIR,
    BUILD_DIR,
    SUMMARY_TYPES_DIR,
    THUMBNAILS_DIR,
    GRAPH_DIR,
    TABLES_DIR,
    SUPERTYPE_DIR,
    HEMILINEAGE_DIR,
    SYNONYMS_DIR,
):
    dir.mkdir(parents=True, exist_ok=True)

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
