---
title: Download
hide:
  - navigation

---

# :fontawesome-solid-download: Download the dataset

## Programmatic access

You can explore the dataset interactively using the [neuPrint platform](https://neuprint.janelia.org/).
To access the data programmatically, we recommend using the dedicated Python and an R packages:

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

Alternatively, you can also bulk download the individual data products:

### Graph

Download the graph as edge list + associated meta data files from:

### Annotations

### Skeletons

### Image data

### Segmentation

### Synapse locations

