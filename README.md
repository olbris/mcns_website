# Website to accompany the male CNS connectome

> [!CAUTION]
> This repository currently builds neuroglancer links using the MCNS DVID server as source. The URL is also visible in the workflow outputs. Making the repo or the website public as is risks leaking the server address.

## TODOs

### Dimorphism overview
- [ ] Add explanation / example of dimorphism

### Individual dimorphism summaries
- [x] 3d plots
- [x] neuroglancer links
- [ ] network graphs and partner summaries
- [ ] dendrogram/umap of the N closest types
- [ ] for sex-specific neurons: closest type in the other sex

## Setup

1. Install [uv](https://docs.astral.sh/uv/)
2. Clone this repository

## Build

### Local

The website is build using `mkdocs` and `jinja2` templates. Dependencies are managed using `uv`.

To build the website locally, run:

```bash
uv run build_pages.py
uv run mkdocs build
```

To serve the website locally, run:

```bash
uv run mkdocs serve
```

### Github

On Github the website is built and deployed using a Github actions
workflow that is triggered on every push to the `main` branch. It
can also be triggered manually using the workflow dispatch feature.

