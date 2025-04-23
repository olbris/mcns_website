"""
Functions for building the various bits and pieces of the website
"""

import pandas as pd
import navis.interfaces.neuprint as neu

from urllib.parse import quote_plus
from d3graph import d3graph, vec2adjmat

from .env import (
    BUILD_DIR,
    GRAPH_DIR,
    THUMBNAILS_DIR,
    NGL_BASE_SCENE,
    JINJA_ENV,
    NEUPRINT_SEARCH_URL,
    NEUPRINT_CONNECTIVITY_URL,
)


def make_dimorphism_pages(mcns_meta, fw_meta, fw_edges):
    """Generate the overview page and individual summaries for each dimorphic cell type.

    Parameters
    ----------
    meta : pd.DataFrame
        The meta data for the neurons as returned from neuPrint.

    """
    print("Generating overview page...", flush=True)
    # Load the template for the overview page
    overview_template = JINJA_ENV.get_template("dimorphism_overview.md")

    # Filter to dimorphic types
    dimorphic_types = mcns_meta[
        mcns_meta.dimorphism.str.contains("dimorphic", na=False)
    ]

    # For each type compile a dictionary with relevant data
    dimorphic_meta = []
    for t, table in dimorphic_types.groupby("mapping"):
        dimorphic_meta.append({})

        # Agglomerate into a single value for each column (if possible)
        for col in table.columns:
            vals = table[col].fillna("None").unique()
            if len(vals) == 1:
                dimorphic_meta[-1][col] = vals[0]
            else:
                dimorphic_meta[-1][col] = ", ".join(vals.astype(str))

        # Add counts
        counts = table.somaSide.value_counts()
        dimorphic_meta[-1]["n_mcnsr"] = counts.get("R", 0)
        dimorphic_meta[-1]["n_mcnsl"] = counts.get("L", 0)

        # Generate links to neuPrint
        dimorphic_meta[-1]["neuprint_url"] = NEUPRINT_SEARCH_URL.format(
            neuron_name=quote_plus(dimorphic_meta[-1]["type"])
        )
        dimorphic_meta[-1]["neuprint_conn_url"] = NEUPRINT_CONNECTIVITY_URL.format(
            neuron_name=quote_plus(dimorphic_meta[-1]["type"])
        )

        scene = NGL_BASE_SCENE.copy()
        scene.layers[1]["segments"] = table["bodyId"].values
        scene.layers[1]["segmentDefaultColor"] = "#00e9e7"

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
            scene.layers[2]["segmentDefaultColor"] = "#e511d0"

        dimorphic_meta[-1]["url"] = scene.url

    print(f"Found {len(dimorphic_meta):,} dimorphic cell types.", flush=True)

    # Filter to male-specific types
    male_types = mcns_meta[mcns_meta.dimorphism.str.contains("male-specific", na=False)]

    # !!!! Currently there are still a few supposedly male-specific neurons that
    # do not have a type. We will drop them for now.
    male_types = male_types[male_types.type.notnull()]

    # For each type compile a dictionary with relevant data
    male_meta = []
    for t, table in male_types.groupby("type"):
        male_meta.append({})

        for col in table.columns:
            vals = table[col].fillna("None").unique()
            if len(vals) == 1:
                male_meta[-1][col] = vals[0]
            else:
                male_meta[-1][col] = ", ".join(vals.astype(str))

        scene = NGL_BASE_SCENE.copy()
        scene.layers[1]["segments"] = table["bodyId"].values
        scene.layers[1]["segmentDefaultColor"] = "#00e9e7"

        male_meta[-1]["url"] = scene.url

    print(f"Found {len(male_meta):,} male-specific cell types.", flush=True)

    # Filter to female-specific types
    female_types = fw_meta[
        fw_meta.dimorphism.str.contains("female-specific", na=False)
    ].copy()

    female_types["type"] = (
        female_types.cell_type.fillna(female_types.malecns_type)
        .fillna(female_types.hemibrain_type)
        .fillna("unknown")
    )

    # For each type compile a dictionary with relevant data
    female_meta = []
    for t, table in female_types.groupby("type"):
        female_meta.append({})

        # Agglomerate into a single value for each column (if possible)
        for col in table.columns:
            vals = table[col].unique()
            if len(vals) == 1:
                female_meta[-1][col] = vals[0]
            else:
                female_meta[-1][col] = ", ".join(vals.astype(str))

        scene = NGL_BASE_SCENE.copy()
        scene.layers[2]["segments"] = table["root_id"].values
        scene.layers[2]["segmentDefaultColor"] = "#e511d0"

        female_meta[-1]["url"] = scene.url

    print(f"Found {len(female_meta):,} female-specific cell types.", flush=True)

    # Sort the meta data by type
    dimorphic_meta = sorted(dimorphic_meta, key=lambda x: x["type"])
    male_meta = sorted(male_meta, key=lambda x: x["type"])
    female_meta = sorted(female_meta, key=lambda x: x["type"])

    # Render the template with the meta data
    rendered = overview_template.render(
        dimorphic_types=dimorphic_meta,
        male_types=male_meta,
        female_types=female_meta,
    )

    #  Write the rendered HTML to a file
    with open(BUILD_DIR / "dimorphism_overview.md", "w") as f:
        f.write(rendered)

    print("Done.", flush=True)

    # Generate individual pages for each dimorphic cell type
    print("Generating individual pages...", flush=True, end="")

    # Load the template for the individual pages
    individual_template = JINJA_ENV.get_template("dimorphism_individual.md")

    # Loop through each dimorphic cell type and generate a page for it
    for record in dimorphic_meta:
        print(
            f"  Generating summary page for {record['type']} (dimorphic)...", flush=True
        )

        # Generate the graph
        try:
            generate_graphs(
                record["type"],
                mcns_meta[mcns_meta["mapping"] == record["mapping"]],
                fw_meta[fw_meta["mapping"] == record["mapping"]],
                fw_meta,
                fw_edges,
            )
        except Exception as e:
            print(f"  Failed to generate graph for {record['type']}: {e}", flush=True)

        record["graph_file_mcns"] = (
            BUILD_DIR / "graphs" / (record["type"] + "_mcns.html")
        )
        record["graph_file_mcns_rel"] = f"../graphs/{record['type']}_mcns.html"

        record["graph_file_fw"] = BUILD_DIR / "graphs" / (record["type"] + "_fw.html")
        record["graph_file_fw_rel"] = f"../graphs/{record['type']}_fw.html"

        # Render the template with the meta data
        rendered = individual_template.render(meta=record)

        # Write the rendered HTML to a file
        with open(BUILD_DIR / f"{record['type']}.md", "w") as f:
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
    # Remove all files in the build directory
    for file in BUILD_DIR.glob("*"):
        if file.is_file():
            file.unlink()

    # Remove all files in the graph directory
    for file in GRAPH_DIR.glob("*"):
        if file.is_file():
            file.unlink()

    # Remove all files in the thumbnails directory
    for file in THUMBNAILS_DIR.glob("*"):
        if file.is_file():
            file.unlink()

    print("Cleared the build directory.", flush=True)
