---
title: Download
hide:
  - navigation

---

# :fontawesome-solid-download: Download the dataset

## Programmatic access

You can explore the dataset interactively using the [neuPrint platform](https://neuprint.janelia.org/).
To access the data programmatically, we recommend using the dedicated Python and R packages:

=== "Python"

    The [`neuprint-python`](https://github.com/connectome-neuprint/neuprint-python) package provides a Python
    interface to the neuPrint API.

    ```bash
    pip install neuprint-python
    ```

    Next, go to [neuPrint](https://neuprint.janelia.org/) and create an account. Follow
    [these instructions](https://connectome-neuprint.github.io/neuprint-python/docs/quickstart.html#client-and-authorization-token)
    for getting your API token.

    ```python
    import neuprint as neu
    client = Client("https://neuprint.janelia.org", api_token="<your_token>")

    # Get neuron annotations
    criteria = neu.NeuronCriteria(type="DA1_ORN")
    meta, roi_info = client.fetch_neurons(criteria)

    # Get connectivity
    edges, neuron_info = client.fetch_adjacencies(criteria)
    ```

    For more examples, please see the maleCNS Github repository.

    <div style="text-align: center;">
      <a href="https://github.com/connectome-neuprint/neuprint-python" class="md-button">neuprint-python</a>
    </div>

=== "R"

    The [`neuprintr`](https://github.com/natverse/neuprintr) package provides a programmatic
    interface to the neuPrint API for R.

    ```r
    # install
    if (!require("devtools")) install.packages("devtools")
    devtools::install_github("natverse/neuprintr")

    # use
    library(neuprintr)
    ```

    Next, go to [neuPrint](https://neuprint.janelia.org/) and create an account. Follow
    [these instructions](https://connectome-neuprint.github.io/neuprint-python/docs/quickstart.html#client-and-authorization-token)
    for getting your API token.

    ```r
    # Manually initialize the connection - alternatively you can set variables in your .Renviron file
    conn = neuprint_login(server= "https://neuprint.janelia.org/", token= "<your_token>")
    ```

    For more examples, please see the maleCNS Github repository.

    <div style="text-align: center;">
      <a href="https://github.com/natverse/neuprintr" class="md-button">neuprintr</a>
    </div>

## Bulk download

Alternatively, you can also bulk download the individual data products. Data tables are provided in [Apache Arrow Feather](https://arrow.apache.org/docs/python/feather.html) file format, which can be read using `pyarrow` or `pandas`.

### Image data

### Segmentation

### Neuron annotations
- table of neuron properties (20 MB): [body-annotations-male-cns-v0.9-minconf-0.5.feather](https://storage.googleapis.com/flyem-male-cns/v0.9/connectome-data/flat-connectome/body-annotations-male-cns-v0.9-minconf-0.5.feather)
- table of neurotransmitter information for each neuron (44 MB): [body-neurotransmitters-male-cns-v0.9.feather](https://storage.googleapis.com/flyem-male-cns/v0.9/connectome-data/flat-connectome/body-neurotransmitters-male-cns-v0.9.feather)

### Skeletons












### Connectivity
- table of neuron-to-neuron connections and their strengths; this is the full connection graph (1.1 GB): [connectome-weights-male-cns-v0.9-minconf-0.5.feather](https://storage.googleapis.com/flyem-male-cns/v0.9/connectome-data/flat-connectome/connectome-weights-male-cns-v0.9-minconf-0.5.feather)
- table of neurons with overall connection strengths (780 MB): [body-stats-male-cns-v0.9-minconf-0.5.feather](https://storage.googleapis.com/flyem-male-cns/v0.9/connectome-data/flat-connectome/body-stats-male-cns-v0.9-minconf-0.5.feather)


### Synapse data
- table of each synapse, with neurons and confidences (6.8 GB): [syn-partners-male-cns-v0.9-minconf-0.5.feather](https://storage.googleapis.com/flyem-male-cns/v0.9/connectome-data/flat-connectome/syn-partners-male-cns-v0.9-minconf-0.5.feather)
- table of each synapse location, neuron, and compartment (12.7 GB): [syn-points-male-cns-v0.9-minconf-0.5.feather](https://storage.googleapis.com/flyem-male-cns/v0.9/connectome-data/flat-connectome/syn-points-male-cns-v0.9-minconf-0.5.feather)
- table of each synapse with all neurotransmitter confidences (2.7 GB): [tbar-neurotransmitters-male-cns-v0.9.feather](https://storage.googleapis.com/flyem-male-cns/v0.9/connectome-data/flat-connectome/tbar-neurotransmitters-male-cns-v0.9.feather)




<div style="text-align: center;">
    <p>The Male CNS is <a href="https://creativecommons.org/licenses/by/4.0/">licensed under CC-BY</a>.</p>
</div>
