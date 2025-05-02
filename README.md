# Website to accompany the male CNS connectome

> [!CAUTION]
> This repository currently builds neuroglancer links using the MCNS DVID server as source. The URL is also visible in the workflow outputs. Making the repo or the website public as is risks leaking the server address.

## TODOs

### General
- [ ] switch from unstructured dictionaries to DataClasses for more transparent data handling

### Dimorphism overview
- [ ] add explanation / example of dimorphism

### Individual summaries
- [x] 3d plots
- [x] neuroglancer links
- [x] network graphs
- [ ] partner summaries
- [ ] dendrogram/umap of the N closest types
- [ ] for sex-specific neurons: closest type in the other sex

## Setup

1. Install [uv](https://docs.astral.sh/uv/)
2. Clone this repository

## Build

### Local

The website is build using `mkdocs` and `jinja2` templates. Dependencies are managed using `uv`.

In addition, you need to set the following environment variables to set up for fetching meta data:
- `NEUPRINT_APPLICATION_CREDENTIALS`: A neuPrint API token
- `CAVE_SECRET`: API token for CAVE (FlyWire); this should not be needed, and I will remove it in the future
- `SEATABLE_SERVER`: URL for our FlyTable instance
- `SEATABLE_TOKEN`: API token for FlyTable

To build the website locally, run:

```bash
uv run build_pages.py
uv run mkdocs build
```

You can set various flags to control the build process:

- `--skip-thumbnails`: Skip generation of the thumbnails (by far the most expensive part)
- `--skip-graphs`: Skip generation of the network graphs (second most expensive part)
- `--update-metadata`: Force updating the metadata (neuPrint/FlyTable)
- `--clear-build`: Clear the build directory before building

To serve the website locally, run:

```bash
uv run mkdocs serve
```

### Github

On Github the website is built and deployed using a Github actions
workflow that is triggered on every push to the `main` branch. It
can also be triggered manually using the workflow dispatch feature.

