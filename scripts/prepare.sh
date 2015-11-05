#!/bin/bash

name=$1;
echo $name

#cp filtered_osm/${name}.osm bak/${name}.osm
python scripts/concave_hull.py sampled_osm/${name}.ssv -d 3 > jsons/${name}.json
./scripts/finish.sh $1
