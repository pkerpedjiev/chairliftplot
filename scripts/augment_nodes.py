#!/usr/bin/python

import xml.etree.ElementTree as ET

import json
import sys
import urllib2

from optparse import OptionParser

def add_elevation_to_node(node, override = False):
    '''
    Take the latitude and longitude of a particular node,
    get the elevation using Google's API and output the
    result.

    :param node: An XML node
    :param override: Override the elevation data if it already has it.
    '''
    if 'elev' in node.attrib and not override:
        return

    if 'lat' not in node.attrib or 'lon' not in node.attrib:
        raise ValueError ("Missing latitude or longitude in node: " + str(node.attrib))

    wait_time = 2
    found = False

    while not found and wait_time < 120:
        try:
            query_url = "https://maps.googleapis.com/maps/api/elevation/json?locations={},{}".format(node.attrib['lat'], node.attrib['lon'])
            u = urllib2.urlopen(query_url)
            js = json.loads(u.read())
            if js['status'] == 'OK':
                node.attrib['elev'] = "{:.4f}".format(js['results'][0]['elevation'])
                found = True
            else:
                print >>sys.stderr, "Error getting elevation for node:", node.attrib
        except Exception as ex:
            # wait if we overload the google maps api
            time.sleep(wait_time)
            wait_time *= 2

def add_elevation_to_nodes(filename):
    '''
    Add an elevation to each node from the osm file specified in filename.

    Print the output to stdout.

    :param filename: The name of the OSM file
    '''
    tree = ET.parse(filename)
    root = tree.getroot()

    for node in root.iter('node'):
        add_elevation_to_node(node)

    tree.write(sys.stdout)

def main():
    usage = """
    python augment_nodes.py map.osm

    Add elevation data to the nodes in an osm map.
    """
    num_args= 1
    parser = OptionParser(usage=usage)

    #parser.add_option('-o', '--options', dest='some_option', default='yo', help="Place holder for a real option", type='str')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    add_elevation_to_nodes(args[0])

if __name__ == '__main__':
    main()

