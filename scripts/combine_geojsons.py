#!/usr/bin/python

import json
import sys
from optparse import OptionParser

def main():
    usage = """
    python scripts/combine_geojsons.py geo1.json [geo2.json]
    """
    num_args= 0
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    new_features = []
    for arg in args:
        with open(arg, 'r') as f:
            geo_json = json.load(f)

            for feature in geo_json['features']:
                new_features += [feature]

    print json.dumps({"type": "FeatureCollection",
                      "features": new_features})

if __name__ == '__main__':
    main()

