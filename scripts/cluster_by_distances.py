#!/usr/bin/python

import numpy as np
import sys
from haversine import haversine
from optparse import OptionParser

import xml.etree.ElementTree as ET

def proximity_cluster(points, distance,dist):
    #cluster points such that whenever two points are
    #within distance of each other, they are placed in
    #the same cluster

    #take m n-d points as input and
    #return an array of length m containing integers
    #where each integers encodes the cluster that the ith
    #point is in
   # 
    # dist is a function that computes the distance between
    # any two points

    print >>sys.stderr, "distance:", distance

    clusters = []
    links = []
    linksDict = {}
    
    # all points are in their own cluster
    for i in range(len(points)):
        clusters.append(i);
        linksDict[i] = [];

    # sort the points by x values
    points.sort(key=lambda x: x[0])

    for i in range(len(points)):
        if i % 100 == 0:
            print "\r{} of {}".format(i, len(points))

        for j in range(i+1, len(points)):
            d1 = dist([points[j][0], points[j][1]],[points[i][0],points[j][1]])
            if d1 > distance:
                break;  # gone too far

            d = dist(points[i], points[j])
            if (dist(points[i], points[j]) < distance):
                # the two points are close enough to be linked
                links.append([i,j])
                linksDict[i].append(j)
                linksDict[j].append(i)

    visited = set()

    queue = []
    # traverse the list of links and assign clusters
    def bfs():
        to_visit = set()
        while len(queue) > 0:
            currNode, prevNode = queue.pop(0)
            if currNode in visited:
                continue
            
            visited.add(currNode);
            clusters[currNode] = min(clusters[currNode], clusters[prevNode]);

            for i in range(len(linksDict[currNode])):
                if linksDict[currNode][i] in visited or linksDict[currNode][i] in to_visit:
                    continue;

                to_visit.add(linksDict[currNode][i])
                queue.append((linksDict[currNode][i], currNode))

    # go through every point and traverse its list of links
    # assigning clusters
    for i in range(len(points)):
        if i in visited:
            continue;

        queue = [(i,i)]
        bfs()

    return {"clusters": clusters, "links": links};

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

def distanceBetweenNodes(node1, node2):
    dist = haversine(node1, node2)
    return dist

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
    ret = proximity_cluster(points, options.distance, distanceBetweenNodes)
    print "ret[clusters]", ret["clusters"]

if __name__ == '__main__':
    
    main()

