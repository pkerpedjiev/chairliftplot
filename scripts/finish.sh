#!/bin/bash

name=$1;
echo $name
./node_modules/topojson/bin/topojson --bbox -p -q 100000 -o jsons/${name}.topo boundaries=jsons/${name}.json;
cp jsons/${name}.topo ~/projects/emptypipes/minisites/2015-10-26-ski-areas/jsons/ski-areas.topo
