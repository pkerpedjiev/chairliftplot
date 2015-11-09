#!/usr/bin/python

import json
import sys
from optparse import OptionParser

def main():
    usage = """
    python flip_coords.py geojson

    Switch the x and y coordinates of a geojson file. Works only if there
    is a polygon in the geometry.
    """
    num_args= 0
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    if args[0] == '-':
        f = sys.stdin
    else:
        f = open(args[0], 'r')

    js = json.load(f)
    for feature in js['features']:
        if feature['geometry']['type'] != 'Polygon':
            print >>sys.stderr, "Invalid geometry:", feature['geometry']['type']
        else:
            for edges in feature['geometry']['coordinates']:
                for point in edges:
                    p0,p1 = point[0], point[1]
                    point[0],point[1] = p1,p0

    print json.dumps(js,indent=2)

if __name__ == '__main__':
    main()

