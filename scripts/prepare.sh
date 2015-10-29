#!/bin/bash

name=$1;
echo $name

python scripts/concave_hull.py filtered_osm/${name}.osm -d 1 > jsons/${name}.json
topojson --bbox -p -q 100000 -o jsons/${name}.topo boundaries=jsons/${name}.json;
cp jsons/${name}.topo /Users/pkerp/minisites/2015-10-26-ski-areas/jsons/ski-areas.topo
