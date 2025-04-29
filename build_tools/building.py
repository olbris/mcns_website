"""
Functions for building the various bits and pieces of the website
"""

import pandas as pd
import navis.interfaces.neuprint as neu

from typing import List, Dict
from urllib.parse import quote_plus
from d3graph import d3graph, vec2adjmat

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
)


def make_dimorphism_pages(
    mcns_meta: pd.DataFrame,
    fw_meta: pd.DataFrame,
    fw_edges: pd.DataFrame,
    skip_graphs: bool = False,
):
    """Generate the overview page and individual summaries for each dimorphic cell type.

    Parameters
    ----------
    mcns_meta : pd.DataFrame
                The meta data for the neurons as returned from neuPrint.
    fw_meta :   pd.DataFrame
                The meta data for the neurons as returned from FlyTable.
    fw_edges :  pd.DataFrame
                Edge list for FlyWire neurons.

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
    by_hemilineage = group_by_hemilineage(dimorphic_meta, male_meta, female_meta)

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
            f"  Generating summary page for {record['type']} (dimorphic)...", flush=True
        )

        # Generate the graph
        if not skip_graphs:
            try:
                generate_graphs(
                    record["type"],
                    mcns_meta[mcns_meta["mapping"] == record["mapping"]],
                    fw_meta[fw_meta["mapping"] == record["mapping"]],
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
            record["graph_file_mcns_rel"] = f"../graphs/{record['type']}_mcns.html"

            record["graph_file_fw"] = (
                BUILD_DIR / "graphs" / (record["type"] + "_fw.html")
            )
            record["graph_file_fw_rel"] = f"../graphs/{record['type']}_fw.html"

        # Render the template with the meta data
        rendered = individual_template.render(meta=record)

        # Write the rendered HTML to a file
        with open(SUMMARY_TYPES_DIR / f"{record['type_file']}.md", "w") as f:
            f.write(rendered)

    # Loop through each male-specific cell type and generate a page for it
    individual_template = JINJA_ENV.get_template("male_spec_individual.md")
    for record in male_meta:
        print(
            f"  Generating summary page for {record['type']} (male-specific)...",
            flush=True,
        )

        # Generate the graph
        if not skip_graphs:
            try:
                generate_graphs(
                    record["type"],
                    mcns_meta[mcns_meta["mapping"] == record["mapping"]],
                    pd.DataFrame(),
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
            record["graph_file_mcns_rel"] = f"../graphs/{record['type']}_mcns.html"

        # Render the template with the meta data
        rendered = individual_template.render(meta=record)

        # Write the rendered HTML to a file
        with open(BUILD_DIR / f"{record['type_file']}.md", "w") as f:
            f.write(rendered)

    # Loop through each male-specific cell type and generate a page for it
    individual_template = JINJA_ENV.get_template("female_spec_individual.md")
    for record in female_meta:
        print(
            f"  Generating summary page for {record['type']} (female-specific)...",
            flush=True,
        )

        # Generate the graph
        if not skip_graphs:
            try:
                generate_graphs(
                    record["type"],
                    pd.DataFrame(),
                    fw_meta[fw_meta["mapping"] == record["mapping"]],
                    fw_meta,
                    fw_edges,
                )
            except Exception as e:
                print(
                    f"  Failed to generate graph for {record['type']}: {e}", flush=True
                )

            record["graph_file_fw"] = (
                BUILD_DIR / "graphs" / (record["type"] + "_fw.html")
            )
            record["graph_file_fw_rel"] = f"../graphs/{record['type']}_fw.html"

        # Render the template with the meta data
        rendered = individual_template.render(meta=record)

        # Write the rendered HTML to a file
        with open(BUILD_DIR / f"{record['type_file']}.md", "w") as f:
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
                dimorphic_meta[-1][col] = "None"
            else:
                dimorphic_meta[-1][col] = ", ".join(vals.astype(str))

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
                male_meta[-1][col] = "None"
            else:
                male_meta[-1][col] = ", ".join(vals.astype(str))

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
        .fillna("unknown")
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
                female_meta[-1][col] = "None"
            else:
                female_meta[-1][col] = ", ".join(vals.astype(str))

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


def group_by_hemilineage(
    dimorphic_meta: List[Dict], male_meta: List[Dict], female_meta: List[Dict]
) -> List[List[Dict]]:
    """Group the dimorphic cell types by hemilineage.

    Parameters
    ----------
    dimorphic_meta :    list of dicts
                        The meta data for the dimorphic cell types.
    male_meta :         list of dicts
                        The meta data for the male-specific cell types.
    female_meta :       list of dicts
                        The meta data for the female-specific cell types.

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
        by_hemilineage[hl]["types"][-1]["type_type"] = "dimorphic"

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
        by_hemilineage[hl]["types"][-1]["type_type"] = "male-specific"

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
        by_hemilineage[hl]["types"][-1]["type_type"] = "female-specific"

    # Convert the dictionary to a list and sort alphabetically by name
    by_hemilineage = list(by_hemilineage.values())
    by_hemilineage = sorted(by_hemilineage, key=lambda x: x["name"])
    for hl in by_hemilineage:
        hl["types"] = sorted(hl["types"], key=lambda x: x["type"])

    return by_hemilineage


def make_supertype_pages(mcns_meta: pd.DataFrame, fw_meta: pd.DataFrame) -> None:
    """Generate the individual summaries for each (dimorphic) supertype.

    mcns_meta : pd.DataFrame
                The meta data for the neurons as returned from neuPrint.
    fw_meta :   pd.DataFrame
                The meta data for the neurons as returned from FlyTable.

    """
    print("Generating supertype pages...", flush=True)
    # Load the template for the summary pages
    template = JINJA_ENV.get_template("supertype_individual.md")

    # Filter to dimorphic super types (we may remove this in the future)
    mcns_meta = (
        mcns_meta[mcns_meta.dimorphism.str.contains("dimorphic", na=False)]
        .drop(columns=["roiInfo", "inputRois", "outputRois"])
        .copy()
    )

    # For each type compile a dictionary with relevant data
    supertypes_meta = []
    for t, table in mcns_meta.groupby("supertype"):
        supertypes_meta.append({})

        # Agglomerate into a single value for each column (if possible)
        for col in table.columns:
            vals = table[col].fillna("None").unique()
            if len(vals) == 1:
                supertypes_meta[-1][col] = vals[0]
            else:
                supertypes_meta[-1][col] = ", ".join(vals.astype(str))

        # Add neuron counts
        counts = table.somaSide.value_counts()
        if counts.empty:
            counts = table.rootSide.value_counts()

        supertypes_meta[-1]["n_mcnsr"] = counts.get("R", 0)
        supertypes_meta[-1]["n_mcnsl"] = counts.get("L", 0)

        # Add type counts
        type_counts = table.groupby("somaSide").type.nunique()
        supertypes_meta[-1]["n_types_mcnsr"] = type_counts.get("R", 0)
        supertypes_meta[-1]["n_types_mcnsl"] = type_counts.get("L", 0)

        # Get a neuroglancer scene to populate
        scene = prep_scene(table)
        scene.layers[1]["segments"] = table["bodyId"].values

        # Grab the corresponding supertype in FlyWire
        table_fw = fw_meta[fw_meta.supertype == t]

        if table_fw.empty:
            print(f"  No matching FlyWire supertype for {t}.", flush=True)
        else:
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
                    hemilineages_meta[-1][col] = "None"
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


def generate_thumbnail(type, mcns_meta, fw_meta):
    """Generate a thumbnail image for the given neuron type.

    Parameters
    ----------
    type :      str
                The type of neuron to generate the thumbnail for.
    mcns_meta : pd.DataFrame
                The meta data for the MCNS neurons.
    fw_meta :   pd.DataFrame
                The  meta data for the FlyWire neurons.

    """
    pass


def generate_graphs(
    type_name, type_meta_mcns, type_meta_fw, fw_meta_full, fw_edges, N=5
):
    """Generate D3 graphs for the given neurons.

    Parameters
    ----------
    type :      str
                The type of neuron to generate the graph for.
                This is primarily used for the filename as
                the graphs are generated from the meta data
                (see below).
    type_meta_mcns : pd.DataFrame
                The meta data for the MCNS neurons to generate graphs for.
    type_meta_fw : pd.DataFrame
                The meta data for the FlyWire neurons to generate graphs for.
    fw_meta_full : pd.DataFrame
                The full meta data for FlyWire.
    fw_edges :  pd.DataFrame
                The edges for the FlyWire neurons. See
                loading.py for the function that loads this data.
    N :         int
                The number of top N in- and out-edges to keep.

    """
    print(f"Generating graphs for {type_name}...", flush=True)

    # We may need to drop duplicates here
    fw_meta_full = fw_meta_full.drop_duplicates("root_id")

    # Make our lives a bit easier and align column names
    fw_edges = fw_edges.rename(columns={"syn_count": "weight"})

    # First up: graph for the MCNS neurons
    if not type_meta_mcns.empty:
        # Fetch downstream partners
        ann, down = neu.fetch_adjacencies(
            sources=neu.NeuronCriteria(bodyId=type_meta_mcns["bodyId"].values),
        )

        # Add type information
        down["pre_type"] = down.bodyId_pre.map(ann.set_index("bodyId").type)
        down["post_type"] = down.bodyId_post.map(ann.set_index("bodyId").type)

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
        ann, up = neu.fetch_adjacencies(
            targets=neu.NeuronCriteria(bodyId=type_meta_mcns["bodyId"].values),
        )
        up["pre_type"] = up.bodyId_pre.map(ann.set_index("bodyId").type)
        up["post_type"] = up.bodyId_post.map(ann.set_index("bodyId").type)
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
        down["pre_type"] = down.pre_pt_root_id.map(
            fw_meta_full.set_index("root_id").type
        )
        down["post_type"] = down.post_pt_root_id.map(
            fw_meta_full.set_index("root_id").type
        )
        up["pre_type"] = up.pre_pt_root_id.map(fw_meta_full.set_index("root_id").type)
        up["post_type"] = up.post_pt_root_id.map(fw_meta_full.set_index("root_id").type)

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
