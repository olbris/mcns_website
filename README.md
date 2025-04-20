# Website to accompany the male CNS connectome

> [!CAUTION]
> This repository currently builds neuroglancer links using the MCNS DVID server as source. Making the repo or the website public as is risks leaking the server address.

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

Currently, the website has to be built locally using `mkdocs` and `jinja2` templates. The results are then pushed to the Github repository
where they are deployed to GitHub pages. In the future, we should consider setting up a CI/CD pipeline to automate this process and to
avoid pushing large files to the repository.

To build the website, run:

```bash
uv run build_pages.py
uv run mkdocs build
```

## Development

```bash
uv run mkdocs serve
```


