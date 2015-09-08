#!/usr/bin/python

import scipy.spatial as ss
import sys

import xml.etree.ElementTree as ET

from optparse import OptionParser

def node_to_coord_id(node):
    '''
    Extract the coordinates and id of the node.

    :param node: An OSM node
    :return: (coords, ref)
    '''
    if 'lat' not in node.attrib or 'lon' not in node.attrib:
        raise ValueError('Missing latitude or longitude in node: ' + str(node.attrib))
    if 'id' not in node.attrib:
        raise ValueError('Missing id in node: ' + str(node.attrib))

    return ([float(node.attrib['lat']), float(node.attrib['lon'])], node.attrib['id'])

def main():
    usage = """
    python cluster_by_adjacent_distance map.osm

    Cluster all nodes into clusters where each node is at most
    a distance (d) from at least one other node in the cluster.

    Output lists of nodes according to their clusters
    """
    num_args= 0
    parser = OptionParser(usage=usage)

    parser.add_option('-d', '--distance', dest='distance', default=1000, help="The distance between nodes to connect them", type=float)
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    tree = ET.parse(args[0])
    root = tree.getroot()

    coord_refs = map(node_to_coord_id, root.iter('node'))
    print "\n".join(["{} {}".format(" ".join(map(str,cr[0])), cr[1]) for cr in coord_refs])

if __name__ == '__main__':
    main()

