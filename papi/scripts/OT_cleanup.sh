#!/bin/bash

# Due to some issues with the JAVA cache that may cause the OT main window not to open.
# In that case, we need to delete the cache directory $HOME/.PANICObservationTool

OT_CACHE=${HOME}/.PANICObservationTool
echo "Deleting $OT_CACHE"

rm -rf $OT_CACHE

