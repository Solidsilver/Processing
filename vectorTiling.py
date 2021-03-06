#!/usr/bin/env python3
import json
import logging
import os
import subprocess
import sys

import click

import utils


@click.command()
@click.argument("output", required=True, type=click.Path(exists=False))
@click.argument("sources", type=click.Path(exists=True), nargs=-1)
@click.option(
    "--catalog",
    type=click.Path(exists=True),
    help="read a catalog file instead of a list of geojson files",
)
@click.option("--min_zoom", default=5, help="min zoom level to generate")
@click.option("--max_zoom", default=14, help="max zoom level to generate")
@click.option("--layer", default="lands", help="layer name")
def vectorTiling(output, sources, catalog, min_zoom, max_zoom, layer):
    """ Generate an MBTiles file of vector tiles from the output of an OpenBounds project.

    \b
    PARAMS: 
        - sources : A directory containing geojson files, or a list of geojson files"
        - output : file.mbtiles for the generated data 
    """

    if os.path.exists(output):
        logging.error("Error, output path already exists")
        sys.exit(-1)

    if catalog:
        with open(catalog, "rb") as f:
            geojson = json.load(f)
        source_paths = [item["properties"]["path"] for item in geojson["features"]]
    else:
        source_paths = []
        for arg in sources:
            for item in utils.get_files(arg):
                if (
                    os.path.splitext(item)[1] == ".geojson"
                    and os.path.basename(item) != "catalog.geojson"
                ):
                    source_paths.append(item)

    logging.info("{} geojson files found".format(len(source_paths)))

    command = (
        "tippecanoe -o "
        + output
        + " "
        + " ".join(source_paths)
        + " --no-progress-indicator "
        + " --no-polygon-splitting "
        + "--coalesce --reverse --reorder "
        + "--detect-shared-borders "  # try really hard to coalesce polygons with the same properties
        + " -l "  # Avoid small gaps between polygons when simplifying
        + layer
        + " -z {} -Z {}".format(max_zoom, min_zoom)  # force to use a single layer
    )
    logging.info(command)
    subprocess.call(command, shell=True)


if __name__ == "__main__":
    vectorTiling()
