#!/usr/bin/env bash

# This script uploads the thumbnails flyem1
tar -czf thumbnails.tar.gz docs/build/thumbnails
rsync -aLP thumbnails.tar.gz jefferis@flyem1.lmb:/var/www/html/flyconnectome/misc/