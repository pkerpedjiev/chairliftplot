#!/usr/bin/python

import xml.etree.ElementTree as ET
import sys
from optparse import OptionParser

def main():
    usage = """
    python sample_osm_nodes.py file.osm
    """
    num_args= 0
    parser = OptionParser(usage=usage)

    parser.add_option('-n', '--n', dest='n', default=1, help="Sample one out of every n nodes", type='int')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    # get an iterable
    context = ET.iterparse(args[0], events=("start", "end"))

    # turn it into an iterator
    context = iter(context)

    # get the root element
    event, root = context.next()

    counter = 0
    for event, elem in context:
        if event == 'end' and elem.tag == 'node':
            counter += 1

            if counter % options.n == 0:
                if 'lat' in elem.attrib and 'lon' in elem.attrib:
                    print elem.attrib['lat'], elem.attrib['lon']
            elem.clear()
            root.clear()

if __name__ == '__main__':
    main()

