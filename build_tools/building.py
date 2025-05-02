"""
Functions for building the various bits and pieces of the website.
"""

import navis
import logging
import warnings

import dvid as dv
import numpy as np
import pandas as pd
import octarine as oc
import cloudvolume as cv
import navis.interfaces.neuprint as neu

from pathlib import Path
from typing import List, Dict
from urllib.parse import quote_plus
from d3graph import d3graph, vec2adjmat
from concurrent.futures import as_completed

from .env import (
    BUILD_DIR,
    GRAPH_DIR,
    SUMMARY_TYPES_DIR,
    THUMBNAILS_DIR,
    SUPERTYPE_DIR,
    HEMILINEAGE_DIR,
    NGL_BASE_SCENE,
    NGL_BASE_SCENE_VNC,
    NGL_BASE_SCENE_TOP,
    JINJA_ENV,
    NEUPRINT_SEARCH_URL,
    NEUPRINT_CONNECTIVITY_URL,
    FLYWIRE_SOURCE,
    DVID_SERVER,
    DVID_NODE,
    NEUPRINT_CLIENT,
    FUTURE_SESSION,
)

# Silence the d3graph logger
logging.getLogger("d3graph").setLevel(logging.WARNING)

MESH_BRAIN = None
MESH_VNC = None
OC_VIEWER = None

dv.setup(DVID_SERVER, DVID_NODE)

navis.patch_cloudvolume()


def make_dimorphism_pages(
    mcns_meta: pd.DataFrame,
    fw_meta: pd.DataFrame,
    fw_edges: pd.DataFrame,
    mcns_roi_info: pd.DataFrame,
    fw_roi_info: pd.DataFrame,
    skip_graphs: bool = False,
    skip_thumbnails: bool = False,
) -> None:
    """Generate the overview page and individual summaries for each dimorphic cell type.

    Parameters
    ----------
    mcns_meta : pd.DataFrame
                The meta data for MaleCNS neurons as returned from neuPrint.
    fw_meta :   pd.DataFrame
                The meta data for FlyWire neurons as returned from FlyTable.
    fw_edges :  pd.DataFrame
                Edge list for FlyWire neurons.
    mcns_roi_info : pd.DataFrame
                The ROI info for MaleCNS neurons as returned from neuPrint.
    fw_roi_info : pd.DataFrame
                The ROI info for FlyWire neurons. Compiled from Zenodo data dump
                - see loading.py for details.
    skip_graphs : bool
                If True, skip generating the graphs for the neurons.
    skip_thumbnails : bool
                If True, skip generating the thumbnails for the neurons.

    Returns
    -------
    None

    """
    # Collect data for the various types
    dimorphic_meta, male_meta, female_meta = extract_type_data(mcns_meta, fw_meta)

    # Sort the meta data alphabetically by type
    dimorphic_meta = sorted(dimorphic_meta, key=lambda x: x["type"])
    male_meta = sorted(male_meta, key=lambda x: x["type"])
    female_meta = sorted(female_meta, key=lambda x: x["type"])

    # Group types by hemilineages
    by_hemilineage = group_by_hemilineage(
        dimorphic_meta, male_meta, female_meta, mcns_meta, fw_meta
    )

    # Group types by supertypes
    by_supertype = group_by_supertype(
        dimorphic_meta, male_meta, female_meta, mcns_meta, fw_meta
    )

    # Group types by brain region
    by_region = group_by_region(
        dimorphic_meta, male_meta, female_meta, mcns_roi_info, fw_roi_info
    )

    print("Generating overview page...", flush=True)

    # Load the template for the overview page
    overview_template = JINJA_ENV.get_template("dimorphism_overview.md")

    # Render the template with the meta data
    rendered = overview_template.render(
        dimorphic_types=dimorphic_meta,
        male_types=male_meta,
        female_types=female_meta,
        summary_types_dir=SUMMARY_TYPES_DIR.name,
        hemilineages=by_hemilineage,
        supertypes=by_supertype,
        regions=by_region,
    )

    #  Write the rendered HTML to a file
    with open(BUILD_DIR / "dimorphism_overview.md", "w") as f:
        f.write(rendered)

    print("Done.", flush=True)

    # Generate individual pages for each dimorphic cell type
    print("Generating individual dimorphism pages...", flush=True, end="")

    # Loop through each dimorphic cell type and generate a page for it
    individual_template = JINJA_ENV.get_template("dimorphism_individual.md")
    for record in dimorphic_meta:
        print(
            f"  Generating summary page for type {record['type']} (dimorphic)...",
            flush=True,
        )

        # Generate the graph
        if not skip_graphs:
            try:
                generate_graphs(
                    record["type"],
                    mcns_meta[mcns_meta["mapping"] == record["mapping"]],
                    fw_meta[fw_meta["mapping"] == record["mapping"]],
                    mcns_meta,
                    fw_meta,
                    fw_edges,
                )
            except Exception as e:
                print(
                    f"  Failed to generate graph for {record['type']}: {e}", flush=True
                )
        record["graph_file_mcns"] = (
            BUILD_DIR / "graphs" / (record["type"] + "_mcns.html")
        )
        record["graph_file_mcns_rel"] = f"../../graphs/{record['type']}_mcns.html"
        record["graph_file_fw"] = BUILD_DIR / "graphs" / (record["type"] + "_fw.html")
        record["graph_file_fw_rel"] = f"../../graphs/{record['type']}_fw.html"

        if not skip_thumbnails:
            # Generate the thumbnail
            try:
                generate_thumbnail(
                    mcns_meta[mcns_meta["mapping"] == record["mapping"]],
                    fw_meta[fw_meta["mapping"] == record["mapping"]],
                    THUMBNAILS_DIR / f"{record['type_file']}.png",
                )
            except Exception as e:
                print(
                    f"  Failed to generate thumbnail for {record['type']}: {e}",
                    flush=True,
                )

        # Render the template with the meta data
        rendered = individual_template.render(meta=record)

        # Write the rendered HTML to a file
        with open(SUMMARY_TYPES_DIR / f"{record['type_file']}.md", "w") as f:
            f.write(rendered)

    # Loop through each male-specific cell type and generate a page for it
    individual_template = JINJA_ENV.get_template("male_spec_individual.md")
    for record in male_meta:
        print(
            f"  Generating summary page for type {record['type']} (male-specific)...",
            flush=True,
        )

        # Generate the graph
        if not skip_graphs:
            try:
                generate_graphs(
                    record["type"],
                    mcns_meta[mcns_meta["mapping"] == record["mapping"]],
                    pd.DataFrame(),
                    mcns_meta,
                    fw_meta,
                    fw_edges,
                )
            except Exception as e:
                print(
                    f"  Failed to generate graph for {record['type']}: {e}", flush=True
                )

        record["graph_file_mcns"] = (
            BUILD_DIR / "graphs" / (record["type"] + "_mcns.html")
        )
        record["graph_file_mcns_rel"] = f"../../graphs/{record['type']}_mcns.html"

        if not skip_thumbnails:
            # Generate the thumbnail
            try:
                generate_thumbnail(
                    mcns_meta[mcns_meta["mapping"] == record["mapping"]],
                    fw_meta[fw_meta["mapping"] == record["mapping"]],
                    THUMBNAILS_DIR / f"{record['type_file']}.png",
                )
            except Exception as e:
                print(
                    f"  Failed to generate thumbnail for {record['type']}: {e}",
                    flush=True,
                )

        # Render the template with the meta data
        rendered = individual_template.render(meta=record)

        # Write the rendered HTML to a file
        with open(SUMMARY_TYPES_DIR / f"{record['type_file']}.md", "w") as f:
            f.write(rendered)

    # Loop through each male-specific cell type and generate a page for it
    individual_template = JINJA_ENV.get_template("female_spec_individual.md")
    for record in female_meta:
        print(
            f"  Generating summary page for type {record['type']} (female-specific)...",
            flush=True,
        )

        # Generate the graph
        if not skip_graphs:
            try:
                generate_graphs(
                    record["type"],
                    pd.DataFrame(),
                    fw_meta[fw_meta["mapping"] == record["mapping"]],
                    mcns_meta,
                    fw_meta,
                    fw_edges,
                )
            except Exception as e:
                print(
                    f"  Failed to generate graph for {record['type']}: {e}", flush=True
                )

        record["graph_file_fw"] = BUILD_DIR / "graphs" / (record["type"] + "_fw.html")
        record["graph_file_fw_rel"] = f"../../graphs/{record['type']}_fw.html"

        if not skip_thumbnails:
            # Generate the thumbnail
            try:
                generate_thumbnail(
                    mcns_meta[mcns_meta["mapping"] == record["mapping"]],
                    fw_meta[fw_meta["mapping"] == record["mapping"]],
                    THUMBNAILS_DIR / f"{record['type_file']}.png",
                )
            except Exception as e:
                print(
                    f"  Failed to generate thumbnail for {record['type']}: {e}",
                    flush=True,
                )

        # Render the template with the meta data
        rendered = individual_template.render(meta=record)

        # Write the rendered HTML to a file
        with open(SUMMARY_TYPES_DIR / f"{record['type_file']}.md", "w") as f:
            f.write(rendered)

    print("Done.", flush=True)


def extract_type_data(mcns_meta, fw_meta):
    """Extract the data for the dimorphic cell types.

    Parameters
    ----------
    mcns_meta : pd.DataFrame
                The meta data for the neurons as returned from neuPrint.
    fw_meta :   pd.DataFrame
                The meta data for the neurons as returned from FlyTable.

    Returns
    -------
    dimorphic_meta : list of dicts
                    The meta data for the dimorphic cell types.
    male_meta :     list of dicts
                    The meta data for the male-specific cell types.
    female_meta :   list of dicts
                    The meta data for the female-specific cell types.

    """
    ####
    # Dimorphic types
    ###

    # Filter to dimorphic types
    # (i.e. "sexually dimorphic" and "potentially sexually dimorphic")
    dimorphic_types = mcns_meta[
        mcns_meta.dimorphism.str.contains("dimorphic", na=False)
    ].drop(columns=["roiInfo", "inputRois", "outputRois"])

    # For each type compile a dictionary with relevant data
    dimorphic_meta = []
    for t, table in dimorphic_types.groupby("mapping"):
        dimorphic_meta.append({})

        dimorphic_meta[-1]["type_file"] = t.replace(" ", "_").replace("/", "_")

        # Agglomerate into a single value for each column (if possible)
        for col in table.columns:
            vals = table[col].dropna().unique()
            if len(vals) == 1:
                dimorphic_meta[-1][col] = vals[0]
            elif len(vals) == 0:
                dimorphic_meta[-1][col] = "N/A"
            else:
                dimorphic_meta[-1][col] = ", ".join(vals.astype(str))

        # What type of dimorphism is this?
        dimorphic_meta[-1]["dimorphism_type"] = "dimorphic"

        # Add counts
        counts = table.somaSide.value_counts()
        if counts.empty:
            counts = table.rootSide.value_counts()

        dimorphic_meta[-1]["n_mcnsr"] = counts.get("R", 0)
        dimorphic_meta[-1]["n_mcnsl"] = counts.get("L", 0)

        # Generate links to neuPrint
        dimorphic_meta[-1]["neuprint_url"] = NEUPRINT_SEARCH_URL.format(
            neuron_name=quote_plus(dimorphic_meta[-1]["type"])
        )
        dimorphic_meta[-1]["neuprint_conn_url"] = NEUPRINT_CONNECTIVITY_URL.format(
            neuron_name=quote_plus(dimorphic_meta[-1]["type"])
        )

        # Get a neuroglancer scene to populate
        scene = prep_scene(table)
        scene.layers[1]["segments"] = table["bodyId"].values

        # Grab the corresponding type in FlyWire
        table_fw = fw_meta[fw_meta["mapping"] == t]
        if table_fw.empty:
            print(f"  No matching FlyWire type for {t}.", flush=True)
        else:
            # Agglomerate into a single value for each column (if possible)
            for col in table_fw.columns:
                # Skip columns that are already in the MCNS meta data
                if col in mcns_meta.columns:
                    continue
                vals = table_fw[col].dropna().unique()
                if len(vals) == 1:
                    dimorphic_meta[-1][col] = vals[0]
                elif len(vals) == 0:
                    dimorphic_meta[-1][col] = "N/A"
                else:
                    dimorphic_meta[-1][col] = ", ".join(vals.astype(str))

            # Add counts
            counts = table_fw.side.value_counts()
            dimorphic_meta[-1]["n_fwr"] = counts.get("right", 0)
            dimorphic_meta[-1]["n_fwl"] = counts.get("left", 0)

            scene.layers[2]["segments"] = table_fw["root_id"].values

        dimorphic_meta[-1]["url"] = scene.url

    print(f"Found {len(dimorphic_meta):,} dimorphic cell types.", flush=True)

    ####
    # Male-specific types
    ###

    # Filter to male-specific types
    male_types = mcns_meta[mcns_meta.dimorphism.str.contains("male-specific", na=False)]

    # !!!! Currently there are still a few supposedly male-specific neurons that
    # !!!! do not have a type. We will drop them for now.
    male_types = male_types[male_types.type.notnull()]

    male_meta = []
    for t, table in male_types.groupby("type"):
        male_meta.append({})

        male_meta[-1]["type_file"] = t.replace(" ", "_").replace("/", "_")

        for col in table.columns:
            vals = table[col].dropna().unique()
            if len(vals) == 1:
                male_meta[-1][col] = vals[0]
            elif len(vals) == 0:
                male_meta[-1][col] = "N/A"
            else:
                male_meta[-1][col] = ", ".join(vals.astype(str))

        # What type of dimorphism is this?
        male_meta[-1]["dimorphism_type"] = "male-specific"

        # Add counts
        counts = table.somaSide.value_counts()
        if counts.empty:
            counts = table.rootSide.value_counts()

        male_meta[-1]["n_mcnsr"] = counts.get("R", 0)
        male_meta[-1]["n_mcnsl"] = counts.get("L", 0)

        # Generate links to neuPrint
        male_meta[-1]["neuprint_url"] = NEUPRINT_SEARCH_URL.format(
            neuron_name=quote_plus(male_meta[-1]["type"])
        )
        male_meta[-1]["neuprint_conn_url"] = NEUPRINT_CONNECTIVITY_URL.format(
            neuron_name=quote_plus(male_meta[-1]["type"])
        )

        # Get a neuroglancer scene to populate
        scene = prep_scene(table)
        scene.layers[1]["segments"] = table["bodyId"].values
        male_meta[-1]["url"] = scene.url

    print(f"Found {len(male_meta):,} male-specific cell types.", flush=True)

    ####
    # Female-specific types
    ###
    # Filter to female-specific types
    female_types = fw_meta[
        fw_meta.dimorphism.str.contains("female-specific", na=False)
    ].copy()

    female_types["type"] = (
        female_types.cell_type.fillna(female_types.malecns_type)
        .fillna(female_types.hemibrain_type)
        # .fillna("unknown")
    )
    female_meta = []
    for t, table_fw in female_types.groupby("type"):
        female_meta.append({})

        female_meta[-1]["type_file"] = t.replace(" ", "_").replace("/", "_")

        # Agglomerate into a single value for each column (if possible)
        for col in table_fw.columns:
            vals = table_fw[col].dropna().unique()
            if len(vals) == 1:
                female_meta[-1][col] = vals[0]
            elif len(vals) == 0:
                female_meta[-1][col] = "N/A"
            else:
                female_meta[-1][col] = ", ".join(vals.astype(str))

        # What type of dimorphism is this?
        female_meta[-1]["dimorphism_type"] = "female-specific"

        # Add counts
        counts = table_fw.side.value_counts()
        female_meta[-1]["n_fwr"] = counts.get("right", 0)
        female_meta[-1]["n_fwl"] = counts.get("left", 0)

        # Get a neuroglancer scene to populate
        scene = prep_scene(table_fw)
        scene.layers[2]["segments"] = table_fw["root_id"].values

        female_meta[-1]["url"] = scene.url

    print(f"Found {len(female_meta):,} female-specific cell types.", flush=True)

    return dimorphic_meta, male_meta, female_meta


def group_by_region(
    dimorphic_meta: List[Dict],
    male_meta: List[Dict],
    female_meta: List[Dict],
    mcns_roi_info: pd.DataFrame,
    fw_roi_info: pd.DataFrame,
    threshold=0.1,
) -> List[List[Dict]]:
    """Sort the dimorphic/sex-specific cell types into brain regions.

    Parameters
    ----------
    dimorphic_meta :    list of dicts
                        The meta data for the dimorphic cell types.
    male_meta :         list of dicts
                        The meta data for the male-specific cell types.
    female_meta :       list of dicts
                        The meta data for the female-specific cell types.
    mcns_roi_info :     pd.DataFrame
                        The ROI info for MaleCNS neurons as returned from neuPrint.
    fw_roi_info :       pd.DataFrame
                        The ROI info for FlyWire neurons. Compiled from Zenodo
                        data dump - see loading.py for details.
    threshold :         float [0-1]
                        Fraction of the total in- OR outputs to a given ROI to be
                        considered a main input/output. Default is 0.1.

    Returns
    -------
    by_region :         dict with list of dicts
                        A dictionary with list of dictionaries for each brain region:
                        {"CentralBrain": [{"name": "region1", "types": []}, ...], ...}

    """
    # First assign each primary ROI to either Optic, VNC or brain
    roi_hierarchy = NEUPRINT_CLIENT.meta["roiHierarchy"]
    roi2compartment = {}
    for comp in roi_hierarchy["children"]:
        roi2compartment.update({c["name"]: comp["name"] for c in comp["children"]})

    # Collapse left and right compartments
    roi2compartment = {
        r.replace("(L)", "").replace("(R)", ""): c.replace("(L)", "").replace("(R)", "")
        for r, c in roi2compartment.items()
    }

    # Collapse left and right ROIs in the ROI info
    mcns_roi_info["roi"] = (
        mcns_roi_info["roi"].str.replace("(L)", "").str.replace("(R)", "")
    )
    fw_roi_info["roi"] = (
        fw_roi_info["roi"].str.replace("(L)", "").str.replace("(R)", "")
    )

    # Fix up Mushroom body compartments to align with FlyWire
    mb_vl = ("aL", "a'L")
    mb_ml = ("gL", "bL", "b'L")
    mcns_roi_info.loc[mcns_roi_info.roi.isin((mb_vl)), "roi"] = "MB_VL"
    mcns_roi_info.loc[mcns_roi_info.roi.isin((mb_ml)), "roi"] = "MB_ML"
    mcns_roi_info.loc[mcns_roi_info.roi == "PED", "roi"] = "MB_PED"
    roi2compartment.update(
        {"MB_VL": "CentralBrain", "MB_ML": "CentralBrain", "MB_PED": "CentralBrain"}
    )

    # Aggregate the ROI info again
    mcns_roi_info = (
        mcns_roi_info.groupby(["bodyId", "roi"])[["pre", "post"]].sum().reset_index()
    )
    fw_roi_info = (
        fw_roi_info.groupby(["root_id", "roi"])[["pre", "post"]].sum().reset_index()
    )

    # Normalise the ROI counts
    mcns_roi_info["post_norm"] = (
        mcns_roi_info["post"]
        / mcns_roi_info.bodyId.map(mcns_roi_info.groupby("bodyId")["post"].sum())
    ).fillna(0)
    mcns_roi_info["pre_norm"] = (
        mcns_roi_info["pre"]
        / mcns_roi_info.bodyId.map(mcns_roi_info.groupby("bodyId")["pre"].sum())
    ).fillna(0)
    fw_roi_info["post_norm"] = (
        fw_roi_info["post"]
        / fw_roi_info.root_id.map(fw_roi_info.groupby("root_id")["post"].sum())
    ).fillna(0)
    fw_roi_info["pre_norm"] = (
        fw_roi_info["pre"]
        / fw_roi_info.root_id.map(fw_roi_info.groupby("root_id")["pre"].sum())
    ).fillna(0)

    # Drop non-primary ROIs from mcns_roi_info
    mcns_roi_info = mcns_roi_info[mcns_roi_info.roi.isin(list(roi2compartment))]

    # Loop through each dimorphic cell type and get its main input/output ROIs
    by_region = {}
    for record in dimorphic_meta + male_meta:
        # Parse the body IDs
        if isinstance(record["bodyId"], str):
            bids = np.array(record["bodyId"].split(",")).astype(int)
        else:
            bids = np.array([record["bodyId"]]).astype(int)

        # Get aggregate ROIs for these IDs
        rois = (
            mcns_roi_info[mcns_roi_info.bodyId.isin(bids)]
            .groupby("roi")[["pre_norm", "post_norm"]]
            .mean()
        )
        record["roi_counts"] = rois.to_dict()

        for roi in rois.index.values[
            (rois.pre_norm >= threshold) | (rois.post_norm >= threshold)
        ]:
            comp = roi2compartment.get(roi, "unknown")
            if comp not in by_region:
                by_region[comp] = {}
            if roi not in by_region[comp]:
                by_region[comp][roi] = {"types": []}
            by_region[comp][roi]["name"] = roi
            by_region[comp][roi]["types"].append(record)

    for record in female_meta:
        # Parse the root IDs
        if isinstance(record["root_id"], str):
            roots = np.array(record["root_id"].split(",")).astype(int)
        else:
            roots = np.array([record["root_id"]]).astype(int)

        # Get aggregate ROIs for these IDs
        rois = (
            fw_roi_info[fw_roi_info.root_id.isin(roots)]
            .groupby("roi")[["pre_norm", "post_norm"]]
            .mean()
        )
        record["roi_counts"] = rois.to_dict()

        for roi in rois.index.values[
            (rois.pre_norm >= threshold) | (rois.post_norm >= threshold)
        ]:
            comp = roi2compartment.get(roi, "unknown")
            if comp not in by_region:
                by_region[comp] = {}
            if roi not in by_region[comp]:
                by_region[comp][roi] = {"types": []}
            by_region[comp][roi]["name"] = roi
            by_region[comp][roi]["types"].append(record)

    # Drop some ROIs that we don't want
    for comp in by_region:
        by_region[comp] = {
            k: v
            for k, v in by_region[comp].items()
            if k
            not in ["Optic-unspecified", "VNC-unspecified", "CentralBrain-unspecified"]
        }

    # Sort ROIs alphabetically
    for comp in by_region:
        by_region[comp] = {k: by_region[comp][k] for k in sorted(by_region[comp])}

    # Sort types by how much they are in each compartment
    for comp in by_region:
        for roi in by_region[comp]:
            by_region[comp][roi]["types"] = sorted(
                by_region[comp][roi]["types"],
                key=lambda x: max(
                    x["roi_counts"]["pre_norm"][roi], x["roi_counts"]["post_norm"][roi]
                ),
                reverse=True,
            )

    return by_region


def group_by_supertype(
    dimorphic_meta: List[Dict],
    male_meta: List[Dict],
    female_meta: List[Dict],
    mcns_meta: pd.DataFrame,
    fw_meta: pd.DataFrame,
) -> List[List[Dict]]:
    """Sort the dimorphic/sex-specific cell types into supertypes.

    Parameters
    ----------
    dimorphic_meta :    list of dicts
                        The meta data for the dimorphic cell types.
    male_meta :         list of dicts
                        The meta data for the male-specific cell types.
    female_meta :       list of dicts
                        The meta data for the female-specific cell types.
    mcns_meta :         pd.DataFrame
                        The meta data for the neurons as returned from neuPrint.
    fw_meta :           pd.DataFrame
                        The meta data for the neurons as returned from FlyTable.

    Returns
    -------
    by_supertype :      list of dicts
                        A list with a dictionary for each supertype.

    """
    by_supertype = {}

    def get_ids_from_record(record):
        body_ids = np.array([], dtype=int)
        if record.get("bodyId", None):
            if isinstance(record["bodyId"], str):
                body_ids = np.array(record["bodyId"].split(",")).astype(int)
            else:
                body_ids = np.array([record["bodyId"]], dtype=int)
        root_ids = np.array([], dtype=int)
        if record.get("root_id", None):
            if isinstance(record["root_id"], str):
                root_ids = np.array(record["root_id"].split(",")).astype(int)
            else:
                root_ids = np.array([record["root_id"]], dtype=int)

        return body_ids, root_ids

    # Loop through each dimorphic cell type and add it to its supertype
    for record in dimorphic_meta + male_meta + female_meta:
        body_ids, root_ids = get_ids_from_record(record)

        # We're assuming that types with no supertype are their own supertypes
        # N.B. that currently types can be split across multiple supertypes
        supertypes = record.get("supertype", None)
        if not supertypes:
            supertypes = str(np.append(body_ids, root_ids).min())

        for st in supertypes.split(","):
            st = st.strip()
            if st not in by_supertype:
                by_supertype[st] = {
                    "types": [],
                    "body_ids": [],
                    "root_ids": [],
                    "dimorphism_types": set(),
                }
            by_supertype[st]["name"] = st
            by_supertype[st]["types"].append(record)
            by_supertype[st]["body_ids"].extend(body_ids)
            by_supertype[st]["root_ids"].extend(root_ids)
            by_supertype[st]["dimorphism_types"].add(record["dimorphism_type"])

    # For each supertype collect some meta data
    for name, st in by_supertype.items():
        # MCNS counts
        st["n_mcns"] = len(st["body_ids"])
        # FlyWire counts
        st["n_fw"] = len(st["root_ids"])
        # What kind of dimorphism is in this supertype?
        st["dimorphism_types"] = ", ".join(list(st["dimorphism_types"]))

    # Convert the dictionary to a list and sort alphabetically by name
    by_supertype = list(by_supertype.values())
    by_supertype = sorted(by_supertype, key=lambda x: x["name"])

    return by_supertype


def group_by_hemilineage(
    dimorphic_meta: List[Dict],
    male_meta: List[Dict],
    female_meta: List[Dict],
    mcns_meta: pd.DataFrame,
    fw_meta: pd.DataFrame,
) -> List[List[Dict]]:
    """Sort the dimorphic/sex-specific cell types into hemilineages.

    Parameters
    ----------
    dimorphic_meta :    list of dicts
                        The meta data for the dimorphic cell types.
    male_meta :         list of dicts
                        The meta data for the male-specific cell types.
    female_meta :       list of dicts
                        The meta data for the female-specific cell types.
    mcns_meta :         pd.DataFrame
                        The meta data for the neurons as returned from neuPrint.
    fw_meta :           pd.DataFrame
                        The meta data for the neurons as returned from FlyTable.

    Returns
    -------
    by_hemilineage :    list of dicts
                        A list with a dictionary for each hemilineages.

    """
    by_hemilineage = {}

    # Loop through each dimorphic cell type and add it to the hemilineage
    for record in dimorphic_meta:
        if record.get("itoleeHl"):
            hl = record["itoleeHl"]
        elif record.get("trumanHl"):
            hl = record["trumanHl"]
        else:
            hl = "unknown"

        if hl not in by_hemilineage:
            by_hemilineage[hl] = {"types": []}

        by_hemilineage[hl]["name"] = hl

        # Add the type's whole record to the hemilineage
        by_hemilineage[hl]["types"].append(record)

    # Loop through each male-specific cell type and add it to the hemilineage
    for record in male_meta:
        if record.get("itoleeHl"):
            hl = record["itoleeHl"]
        elif record.get("trumanHl"):
            hl = record["trumanHl"]
        else:
            hl = "unknown"
        if hl not in by_hemilineage:
            by_hemilineage[hl] = {"types": []}

        by_hemilineage[hl]["name"] = hl

        # Add the type's whole record to the hemilineage
        by_hemilineage[hl]["types"].append(record)

    # Loop through each female-specific cell type and add it to the hemilineage
    for record in female_meta:
        if record.get("ito_lee_hemilineage"):
            hl = record["ito_lee_hemilineage"]
        else:
            hl = "unknown"
        if hl not in by_hemilineage:
            by_hemilineage[hl] = {"types": []}

        by_hemilineage[hl]["name"] = hl

        # Add the type's whole record to the hemilineage
        by_hemilineage[hl]["types"].append(record)

    # For each hemilineage collect some meta data
    for hl in by_hemilineage:
        hl_mcns = mcns_meta[(mcns_meta.itoleeHl == hl) | (mcns_meta.trumanHl == hl)]
        hl_fw = fw_meta[(fw_meta.ito_lee_hemilineage == hl)]

        if hl_mcns.fruDsx.str.contains("coexpress", na=False).any():
            by_hemilineage[hl]["fru_dsx"] = "fru+/dsx+"
        elif (
            hl_mcns.fruDsx.str.contains("fru", na=False).any()
            & hl_mcns.fruDsx.str.contains("dsx", na=False).any()
        ):
            by_hemilineage[hl]["fru_dsx"] = "fru+/dsx+"
        elif hl_mcns.fruDsx.str.contains("fru", na=False).any():
            by_hemilineage[hl]["fru_dsx"] = "fru+/dsx-"
        elif hl_mcns.fruDsx.str.contains("fru", na=False).any():
            by_hemilineage[hl]["fru_dsx"] = "fru-/dsx+"
        else:
            by_hemilineage[hl]["fru_dsx"] = "fru-/dsx-"

        # Add MCNS counts
        counts = hl_mcns.somaSide.value_counts()
        by_hemilineage[hl]["n_mcnsr"] = counts.get("R", 0)
        by_hemilineage[hl]["n_mcnsl"] = counts.get("L", 0)

        # Add FlyWire counts
        counts = hl_fw.side.value_counts()
        by_hemilineage[hl]["n_fwr"] = counts.get("right", 0)
        by_hemilineage[hl]["n_fwl"] = counts.get("left", 0)

        # Generate a neuroglancer URL
        scene = prep_scene(hl_mcns)
        scene.layers[1]["segments"] = hl_mcns["bodyId"].values
        scene.layers[2]["segments"] = hl_fw["root_id"].values

        # Add the URL to the hemilineage
        by_hemilineage[hl]["url"] = scene.url

    # Convert the dictionary to a list and sort alphabetically by name
    by_hemilineage = list(by_hemilineage.values())
    by_hemilineage = sorted(by_hemilineage, key=lambda x: x["name"])
    for hl in by_hemilineage:
        hl["types"] = sorted(hl["types"], key=lambda x: x["type"])

    return by_hemilineage


def make_supertype_pages(
    mcns_meta: pd.DataFrame, fw_meta: pd.DataFrame, skip_thumbnails: bool
) -> None:
    """Generate the individual summaries for each (dimorphic) supertype.

    Parameters
    ----------
    mcns_meta : pd.DataFrame
                The meta data for the neurons as returned from neuPrint.
    fw_meta :   pd.DataFrame
                The meta data for the neurons as returned from FlyTable.
    skip_thumbnails : bool
                Whether to skip generating thumbnails for the supertype pages.

    """
    print("Generating supertype pages...", flush=True)

    # Collect all supertypes
    supertypes = np.append(
        mcns_meta.supertype.dropna().unique(), fw_meta.supertype.dropna().unique()
    )
    supertypes = np.unique(supertypes)

    # For each type compile a dictionary with relevant data
    supertypes_meta = []
    for t in supertypes:
        supertypes_meta.append({})

        table_mcns = mcns_meta[mcns_meta.supertype == t]

        if table_mcns.empty:
            print(f"  No matching MCNS supertype for {t}.", flush=True)
        else:
            # Agglomerate into a single value for each column (if possible)
            for col in table_mcns.columns:
                vals = table_mcns[col].fillna("None").unique()
                if len(vals) == 1:
                    supertypes_meta[-1][col] = vals[0]
                else:
                    supertypes_meta[-1][col] = ", ".join(vals.astype(str))

        # Add neuron counts
        counts = table_mcns.somaSide.value_counts()
        if counts.empty:
            counts = table_mcns.rootSide.value_counts()

        supertypes_meta[-1]["n_mcnsr"] = counts.get("R", 0)
        supertypes_meta[-1]["n_mcnsl"] = counts.get("L", 0)

        # Add type counts
        type_counts = table_mcns.groupby("somaSide").type.nunique()
        supertypes_meta[-1]["n_types_mcnsr"] = type_counts.get("R", 0)
        supertypes_meta[-1]["n_types_mcnsl"] = type_counts.get("L", 0)

        # Get a neuroglancer scene to populate
        scene = prep_scene(table_mcns)
        scene.layers[1]["segments"] = table_mcns["bodyId"].values

        # Grab the corresponding supertype in FlyWire
        table_fw = fw_meta[fw_meta.supertype == t]

        if table_fw.empty:
            print(f"  No matching FlyWire supertype for {t}.", flush=True)
        # Add info from FlyWire if we didn't have male-specific data
        elif table_mcns.empty:
            for col in table_fw.columns:
                vals = table_fw[col].dropna().unique()
                if len(vals) == 1:
                    supertypes_meta[-1][col] = vals[0]
                else:
                    supertypes_meta[-1][col] = ", ".join(vals.astype(str))

        # Add counts
        counts = table_fw.side.value_counts()
        supertypes_meta[-1]["n_fwr"] = counts.get("right", 0)
        supertypes_meta[-1]["n_fwl"] = counts.get("left", 0)

        # Add type counts
        type_counts = table_fw.groupby("side").type.nunique()
        supertypes_meta[-1]["n_types_fwr"] = type_counts.get("right", 0)
        supertypes_meta[-1]["n_types_fwl"] = type_counts.get("left", 0)

        scene.layers[2]["segments"] = table_fw["root_id"].values
        scene.layers[2]["segmentDefaultColor"] = "#e511d0"

        supertypes_meta[-1]["url"] = scene.url

    print(f"Found {len(supertypes_meta):,} (dimorphic) supertypes.", flush=True)

    # Load the template for the summary pages
    template = JINJA_ENV.get_template("supertype_individual.md")

    # Loop through each super type and generate a page for it
    for record in supertypes_meta:
        print(
            f"  Generating summary page for supertype '{record['supertype']}'...",
            flush=True,
        )

        # Render the template with the meta data
        rendered = template.render(meta=record)

        # Write the rendered HTML to a file
        with open(SUPERTYPE_DIR / f"{record['supertype']}.md", "w") as f:
            f.write(rendered)

    if not skip_thumbnails:
        print("Generating thumbnails for supertypes...", flush=True)
        for record in supertypes_meta:
            this_mcns_meta = mcns_meta[mcns_meta.supertype == record["supertype"]]
            this_fw_meta = fw_meta[fw_meta.supertype == record["supertype"]]

            if (
                not this_mcns_meta.dimorphism.notnull().any()
                and not this_fw_meta.dimorphism.notnull().any()
            ):
                print(
                    f"  Skipping {record['supertype']}: no dimorphic neurons found.",
                    flush=True,
                )
                continue

            try:
                generate_thumbnail(
                    this_mcns_meta,
                    this_fw_meta,
                    THUMBNAILS_DIR / f"{record['supertype']}.png",
                )
            except Exception as e:
                print(
                    f"  Failed to generate thumbnail for supertype {record['supertype']}: {e}",
                    flush=True,
                )

    print("Done.", flush=True)


def make_hemilineage_pages(mcns_meta, fw_meta):
    """Generate the individual summaries for each (dimorphic) hemilineage.

    Parameters
    ----------
    mcns_meta : pd.DataFrame
                The meta data for the neurons as returned from neuPrint.
    fw_meta :   pd.DataFrame
                The meta data for the neurons as returned from FlyTable.

    """
    print("Generating supertype pages...", flush=True)
    # Load the template for the summary pages
    template = JINJA_ENV.get_template("hemilineage_individual.md")

    # Filter to dimorphic super types (we may remove this in the future)
    mcns_meta = mcns_meta.copy()
    mcns_meta = mcns_meta.drop(columns=["roiInfo", "inputRois", "outputRois"]).copy()

    # For each type compile a dictionary with relevant data
    hemilineages_meta = []
    for col in ("itoleeHl", "trumanHl"):
        for t, table in mcns_meta.groupby(col):
            hemilineages_meta.append({})

            hemilineages_meta[-1]["hemilineage"] = t
            hemilineages_meta[-1]["hemilineage_file"] = t.replace(" ", "_").replace(
                "/", "_"
            )

            # Agglomerate into a single value for each column (if possible)
            for col in table.columns:
                vals = table[col].dropna().unique()
                if len(vals) == 1:
                    hemilineages_meta[-1][col] = vals[0]
                elif len(vals) == 0:
                    hemilineages_meta[-1][col] = "N/A"
                else:
                    hemilineages_meta[-1][col] = ", ".join(vals.astype(str))

            # Add neuron counts
            counts = table.somaSide.value_counts()
            if counts.empty:
                counts = table.rootSide.value_counts()

            hemilineages_meta[-1]["n_mcnsr"] = counts.get("R", 0)
            hemilineages_meta[-1]["n_mcnsl"] = counts.get("L", 0)

            # Add type counts
            type_counts = table.groupby("somaSide").type.nunique()
            hemilineages_meta[-1]["n_types_mcnsr"] = type_counts.get("R", 0)
            hemilineages_meta[-1]["n_types_mcnsl"] = type_counts.get("L", 0)

            # Get a neuroglancer scene to populate
            scene = prep_scene(table)
            scene.layers[1]["segments"] = table["bodyId"].values

            # Grab the corresponding hemilineage in FlyWire
            table_fw = fw_meta[fw_meta.ito_lee_hemilineage == t]

            if table_fw.empty:
                print(f"  No matching FlyWire hemilineage for {t}.", flush=True)
            else:
                # Add counts
                counts = table_fw.side.value_counts()
                hemilineages_meta[-1]["n_fwr"] = counts.get("right", 0)
                hemilineages_meta[-1]["n_fwl"] = counts.get("left", 0)

                # Add type counts
                type_counts = table_fw.groupby("side").type.nunique()
                hemilineages_meta[-1]["n_types_fwr"] = type_counts.get("right", 0)
                hemilineages_meta[-1]["n_types_fwl"] = type_counts.get("left", 0)

                scene.layers[2]["segments"] = table_fw["root_id"].values
                scene.layers[2]["segmentDefaultColor"] = "#e511d0"

            hemilineages_meta[-1]["url"] = scene.url

    print(f"Found {len(hemilineages_meta):,} (dimorphic) supertypes.", flush=True)

    # Loop through each super type and generate a page for it
    for record in hemilineages_meta:
        print(
            f"  Generating summary page for hemilineage '{record['hemilineage']}'...",
            flush=True,
        )

        # Render the template with the meta data
        rendered = template.render(meta=record)

        # Write the rendered HTML to a file
        with open(HEMILINEAGE_DIR / f"{record['hemilineage_file']}.md", "w") as f:
            f.write(rendered)

    print("Done.", flush=True)


def generate_thumbnail(mcns_meta: pd.DataFrame, fw_meta: pd.DataFrame, outfile: Path, skip_existing: bool = True):
    """Generate a thumbnail image for the given neuron type.

    Parameters
    ----------
    mcns_meta : pd.DataFrame
                Meta data of male CNS neurons to include in the thumbnail.
    fw_meta :   iterable | None
                Meta data of FlyWire neurons to include in the thumbnail.
    outfile :   Path
                Path to write the file to.

    """
    # Check if the output file already exists
    if skip_existing and outfile.exists():
        print(f"  Thumbnail {outfile.name} already exists, skipping...", flush=True)
        return

    print(f"  Generating thumbnail {outfile.name}...", flush=True)
    global MESH_BRAIN, MESH_VNC, FLYWIRE_CLOUDVOL, OC_VIEWER
    # Load the mesh if it is not already loaded
    if MESH_BRAIN is None:
        vol = cv.CloudVolume(
            "gs://flyem-cns-roi-7c971aa681da83f9a074a1f0e8ef60f4/fullbrain-major-shells/",
            use_https=True,
            progress=False,
        )
        MESH_BRAIN = navis.Volume(
            vol.mesh.get([1, 2, 3]), name="BRAIN"
        )  # CB + optic lobes

    if MESH_VNC is None:
        vol = cv.CloudVolume(
            "precomputed://gs://flyem-cns-roi-7c971aa681da83f9a074a1f0e8ef60f4/vnc-neuropil-shell",
            use_https=True,
            progress=False,
        )
        MESH_VNC = navis.Volume(vol.mesh.get([1]), name="VNC")

    if not OC_VIEWER:
        OC_VIEWER = oc.Viewer(offscreen=True)

    # Hide progress bars while loading meshes
    # (there is currently no way to do that with navis.read_precomputed)
    navis.config.pbar_hide = True

    # Get FlyWire meshes
    fw_meshes = navis.NeuronList([])
    if not fw_meta.empty:
        # Read precomputed meshes from FlyWire
        # Note: we could use navis.read_precomputed directly but that's slower
        # (presumably because it uses processes rather than threads)
        base_url = FLYWIRE_SOURCE.replace("precomputed://", "")
        futures = {
            FUTURE_SESSION.get(f"{base_url}/{id}"): id
            for id in fw_meta["root_id"]
        }

        for future in as_completed(futures):
            id = futures[future]
            r = future.result()
            r.raise_for_status()
            fw_meshes.append(
                navis.read_precomputed(r.content, datatype="mesh", info=False, id=id)
            )

    # Get MCNS meshes
    mcns_meshes = navis.NeuronList([])
    if not mcns_meta.empty:
        # Read precomputed meshes from DVID
        base_url = f"{DVID_SERVER}/api/node/{DVID_NODE}/segmentation_meshes/key"
        futures = {
            FUTURE_SESSION.get(f"{base_url}/{id}.ngmesh"): id
            for id in mcns_meta["bodyId"]
        }

        for future in as_completed(futures):
            id = futures[future]
            r = future.result()
            r.raise_for_status()
            mcns_meshes.append(
                navis.read_precomputed(r.content, datatype="mesh", info=False, id=id)
            )

    # Show progress bars again
    navis.config.pbar_hide = False

    # Add neurons to viewer
    if len(fw_meshes):
        OC_VIEWER.add_neurons(fw_meshes, color="#e511d0")
    if len(mcns_meshes):
        OC_VIEWER.add_neurons(mcns_meshes, color="#00e9e7")

    # What kind of neurons do we have?
    if not mcns_meta.empty:
        table = mcns_meta
    else:
        table = fw_meta
    sc_col = "superclass" if "superclass" in table.columns else "super_class"
    has_ascending = (
        ("ascending_neuron" in table[sc_col].values)
        or ("ascending" in table[sc_col].values)
        or ("sensory_ascending" in table[sc_col].values)
    )
    has_descending = (
        ("descending_neuron" in table[sc_col].values)
        or ("descending" in table[sc_col].values)
        or ("sensory_descending" in table[sc_col].values)
    )
    has_central = ("cb_intrinsic" in table[sc_col].values) or (
        "central" in table[sc_col].values
    )
    has_vnc = "vnc_intrinsic" in table[sc_col].values

    # Pick a scene based on the neuron type
    if has_ascending or has_descending or (has_central and has_vnc):
        # Brain and VNC neurons
        OC_VIEWER.add_mesh(MESH_BRAIN, color=(0.8, 0.8, 0.8), alpha=0.1)
        OC_VIEWER.add_mesh(MESH_VNC, color=(0.8, 0.8, 0.8), alpha=0.1)
        OC_VIEWER.set_view(
            {
                "position": np.array(
                    [-380324.37368731, 274816.33737857, 570152.25830276]
                ),
                "rotation": np.array([-0.7110673, -0.03489443, 0.70219136, 0.00964166]),
                "scale": np.array([1.0, 1.0, 1.0]),
                "reference_up": np.array([0.0, -1.0, 0.0]),
                "fov": 0.0,
                "width": 766557.316514536,
                "height": 766557.316514536,
                "zoom": 1.0,
                "maintain_aspect": True,
                "depth_range": None,
            }
        )
    elif has_vnc:
        # Just VNC neurons
        OC_VIEWER.add_mesh(MESH_VNC, color=(0.8, 0.8, 0.8), alpha=0.1)
        OC_VIEWER.set_view(
            {
                "position": np.array(
                    [389551.99130054, -255612.95457865, 608158.34951343]
                ),
                "rotation": np.array([0.54627717, 0.54208679, -0.45810277, 0.4448202]),
                "scale": np.array([1.0, 1.0, 1.0]),
                "reference_up": np.array([0.0, 0.0, 1.0]),
                "fov": 0.0,
                "width": 525756.094337834,
                "height": 525756.094337834,
                "zoom": 1.0,
                "maintain_aspect": True,
                "depth_range": None,
            }
        )
    else:
        # Just brain neurons
        OC_VIEWER.add_mesh(MESH_BRAIN, color=(0.8, 0.8, 0.8), alpha=0.1)
        OC_VIEWER.set_view(
            {
                "position": np.array([387225.3840714, 229749.96777565, 95873.17475057]),
                "rotation": np.array([1.0, 0.0, 0.0, 0.0]),
                "scale": np.array([1.0, 1.0, 1.0]),
                "reference_up": np.array([0.0, -1.0, 0.0]),
                "fov": 0.0,
                "width": 480452.4541556888,
                "height": 480452.4541556888,
                "zoom": 1.0,
                "maintain_aspect": True,
                "depth_range": None,
            }
        )

    OC_VIEWER.screenshot(str(outfile.resolve()), size=(600, 400))
    OC_VIEWER.clear()


def generate_graphs(
    type_name: str,
    type_meta_mcns: pd.DataFrame,
    type_meta_fw: pd.DataFrame,
    mcns_meta_full: pd.DataFrame,
    fw_meta_full: pd.DataFrame,
    fw_edges: pd.DataFrame,
    N: int = 5,
) -> None:
    """Generate D3 graphs for the given neurons.

    Parameters
    ----------
    type_name : str
                The type of neuron to generate the graph for.
                This is primarily used for the filename as
                the graphs are generated from the meta data
                (see below).
    type_meta_mcns : pd.DataFrame
                The meta data for the MCNS neurons to generate graphs for.
    type_meta_fw : pd.DataFrame
                The meta data for the FlyWire neurons to generate graphs for.
    mcns_meta_full : pd.DataFrame
                The full meta data for MaleCNS. We need this to assign types
                to synaptic partners.
    fw_meta_full : pd.DataFrame
                The full meta data for FlyWire. We need this to assign types
                to synaptic partners.
    fw_edges :  pd.DataFrame
                The edges for the FlyWire neurons. See
                loading.py for the function that loads this data.
    N :         int
                The number of top N in- and out-edges to keep.

    Returns
    -------
    None
                But will write the graphs to `GRAPH_DIR / f"{type_name}{_mcns/_fw}.html"`.

    """
    print(f"  Generating graphs for {type_name}...", flush=True)

    mcns_mapping = mcns_meta_full.set_index("bodyId").mapping.to_dict()
    fw_mapping = fw_meta_full.set_index("root_id").mapping.to_dict()

    # We may need to drop duplicates here
    fw_meta_full = fw_meta_full.drop_duplicates("root_id")

    # Make our lives a bit easier and align column names
    fw_edges = fw_edges.rename(columns={"syn_count": "weight"})

    # First up: graph for the MCNS neurons
    if not type_meta_mcns.empty:
        # Fetch downstream partners (ignore userwarnings)
        with warnings.catch_warnings(action="ignore"):
            ann, down = neu.fetch_adjacencies(
                sources=neu.NeuronCriteria(bodyId=type_meta_mcns["bodyId"].values),
            )

        # Add type information
        down["pre_type"] = down.bodyId_pre.map(mcns_mapping)
        down["post_type"] = down.bodyId_post.map(mcns_mapping)

        # Group by pre- and post-synaptic types
        down = (
            down.groupby(["pre_type", "post_type"], as_index=False)
            .weight.sum()
            .sort_values("weight", ascending=False)
        )
        # Remove self-loops
        down = down[down.pre_type != down.post_type]
        # Remove unknown types
        down = down[down.pre_type.notnull() & down.post_type.notnull()]

        # Same for upstream partners
        with warnings.catch_warnings(action="ignore"):
            ann, up = neu.fetch_adjacencies(
                targets=neu.NeuronCriteria(bodyId=type_meta_mcns["bodyId"].values),
            )
        up["pre_type"] = up.bodyId_pre.map(mcns_mapping)
        up["post_type"] = up.bodyId_post.map(mcns_mapping)
        up = (
            up.groupby(["pre_type", "post_type"], as_index=False)
            .weight.sum()
            .sort_values("weight", ascending=False)
        )
        up = up[up.pre_type != up.post_type]
        up = up[up.pre_type.notnull() & up.post_type.notnull()]

        # Combine but keep only the top N in- and out-edges
        df = (
            pd.concat([down.iloc[:N], up.iloc[:N]], axis=0)
            .drop_duplicates()
            .reset_index(drop=True)
        )

        # Generate the D3 graph
        edges2d3(df, GRAPH_DIR / f"{type_name}_mcns.html", color="#00ffff")

    # Now do the same for FlyWire
    if not type_meta_fw.empty:
        # Subset the edges to the ones that are in the meta data
        down = fw_edges[
            fw_edges.pre_pt_root_id.isin(type_meta_fw["root_id"].values)
        ].copy()
        up = fw_edges[
            fw_edges.post_pt_root_id.isin(type_meta_fw["root_id"].values)
        ].copy()

        # Add type information
        down["pre_type"] = down.pre_pt_root_id.map(fw_mapping)
        down["post_type"] = down.post_pt_root_id.map(fw_mapping)
        up["pre_type"] = up.pre_pt_root_id.map(fw_mapping)
        up["post_type"] = up.post_pt_root_id.map(fw_mapping)

        # Group by pre- and post-synaptic types
        down = (
            down.groupby(["pre_type", "post_type"], as_index=False)
            .weight.sum()
            .sort_values("weight", ascending=False)
        )
        up = (
            up.groupby(["pre_type", "post_type"], as_index=False)
            .weight.sum()
            .sort_values("weight", ascending=False)
        )
        # Remove self-loops
        up = up[(up.pre_type != up.post_type)]
        down = down[(down.pre_type != down.post_type)]
        # Remove unknown types
        up = up[up.pre_type.notnull() & up.post_type.notnull()]
        down = down[down.pre_type.notnull() & down.post_type.notnull()]

        # Combine but keep only the top N in- and out-edges
        df = (
            pd.concat([down.iloc[:N], up.iloc[:N]], axis=0)
            .drop_duplicates()
            .reset_index(drop=True)
        )

        # Generate the D3 graph
        edges2d3(df, GRAPH_DIR / f"{type_name}_fw.html", color="#ff00ff")


def edges2d3(edges, filepath, color=None):
    # Convert to adjacency matrix
    adjmat = vec2adjmat(edges.pre_type, edges.post_type, weight=edges.weight)

    # Initialise the graph
    d3 = d3graph()

    # Process adjacency matrix
    d3.graph(adjmat, color=None)

    d3.set_edge_properties(directed=True, label="weight")
    d3.set_node_properties(color=color, fontcolor="#000000")

    # For some reason the library is not passing through the save_button parameter
    # and we have to render the graph manually again
    d3.show(
        figsize=(400, 400),
        title="Graph",
        filepath=filepath,
        showfig=False,
        overwrite=True,
        show_slider=False,
        set_slider=0,
        save_button=False,
    )

    return filepath


def clear_build_directory():
    """Clear the build directory. This will only remove files but not the directories themselves."""
    for dir in (
        BUILD_DIR,
        GRAPH_DIR,
        SUMMARY_TYPES_DIR,
        THUMBNAILS_DIR,
        SUPERTYPE_DIR,
        HEMILINEAGE_DIR,
    ):
        # Remove all files in the directory
        for file in dir.glob("*"):
            if file.is_file():
                file.unlink()

    print("Cleared the build directory.", flush=True)


def prep_scene(table):
    """Pick and prep a neuroglancer scene based on the neurons in it.

    Parameters
    ----------
    table : pd.DataFrame
            The table to generate the scene for.

    Returns
    -------
    scene : nglscenes.Scene
            The scene to use for the neuroglancer view.

    """
    sc_col = "superclass" if "superclass" in table.columns else "super_class"
    has_ascending = ("ascending_neuron" in table[sc_col].values) or (
        "ascending" in table[sc_col].values
    )
    has_descending = ("descending_neuron" in table[sc_col].values) or (
        "descending" in table[sc_col].values
    )
    has_central = ("cb_intrinsic" in table[sc_col].values) or (
        "central" in table[sc_col].values
    )
    has_vnc = "vnc_intrinsic" in table[sc_col].values

    # Pick a scene based on the neuron type
    if has_ascending or has_descending:
        scene = NGL_BASE_SCENE_TOP.copy()
    elif has_central and has_vnc:
        scene = NGL_BASE_SCENE_TOP.copy()
    elif has_central:
        scene = NGL_BASE_SCENE.copy()
    else:
        scene = NGL_BASE_SCENE_VNC.copy()

    # Hide the VNC neuropil mesh if we don't have any neurons in the VNC
    if not has_descending and not has_ascending and not has_vnc:
        scene.layers["vnc-neuropil-shell"]["visible"] = False

    scene.layers[1]["segmentDefaultColor"] = "#00e9e7"
    scene.layers[2]["segmentDefaultColor"] = "#e511d0"

    return scene
