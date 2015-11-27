#!/usr/bin/python

import json
import sys
from optparse import OptionParser

def main():
    usage = """
    python filter_geojson.py geojson.json
    """
    num_args= 0
    parser = OptionParser(usage=usage)

    parser.add_option('-t', '--top', dest='top', default=None, help="Return only the top n entries", type='int')
    parser.add_option('-n', '--keep-only-with-names', dest='keep_only_with_names', default=False, 
                      help="Keep only those entries with names", action='store_true')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    with open(args[0], 'r') as f:
        js = json.load(f)
        features = filter(lambda x: 'name' in x['properties'] and len(x['properties']['name']) > 0, js['features'])
        entries = sorted(features, key=lambda x: -x['properties']['area'])
        
        if options.top is not None:
            js['features'] = entries[:options.top]

        print json.dumps(js, indent=2)

if __name__ == '__main__':
    main()

