#!/usr/bin/python

import numpy as np
import sys
from haversine import haversine
from optparse import OptionParser

import xml.etree.ElementTree as ET

def extract_points(tree, distance=1):
    '''
    Get a list of points to use for clustering from the osm
    file. The points will consist of all nodes, as well as
    extra points that are placed along long ways to make sure
    that they are included.

    @param tree: An XML tree structure.
    @return: A list of points.
    '''
    root = tree.getroot()
    points = []

    nodes = {}
    for node in tree.iter('node'):
        points += [[float(node.attrib['lat']), float(node.attrib['lon'])]]
        nodes[node.attrib['id']] = points[-1]
    for way in tree.iter('way'):
        nds = list(way.iter('nd'))
        for i in range(len(nds)-1):
            node_start = nodes[nds[i].attrib['ref']]
            node_end = nodes[nds[i+1].attrib['ref']]

            vec_length = haversine(node_start, node_end)
            #print >>sys.stderr, "vec_length:", vec_length
            vec_length_parts = int(2 + (1+ vec_length / distance))

            lats = np.linspace(node_start[0], node_end[0], vec_length_parts)
            lons = np.linspace(node_start[1], node_end[1], vec_length_parts) 

            #print >>sys.stderr, "len(lats)", len(lats), len(lons)
            #print >>sys.stderr, "zip", zip(lats, lons)

            #print >>sys.stderr, "points:", zip(lats, lons)
            points += zip(lats, lons)

    return points

def main():
    usage = """
    python cluster_by_distances.py file.osm
    """
    num_args= 0
    parser = OptionParser(usage=usage)

    parser.add_option('-d', '--distance', dest='distance', default=1, help="The distance within which to cluster items", type='int')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    tree = ET.parse(args[0])
    points = extract_points(tree, options.distance)

if __name__ == '__main__':
    
    main()

