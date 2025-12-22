#!/bin/bash
set -x

# Disable Numba caching to fix datashader
export NUMBA_CACHE_DIR=/tmp

# Install packages
sudo pip3 install --ignore-installed pandas numpy seaborn matplotlib dask[complete] datashader

echo "Bootstrap completed successfully!"