#!/usr/bin/python

import itertools as it
import haversine as hv
import numpy as np
import shapely.geometry as sg
import xml.etree.ElementTree as ET
import sys
from optparse import OptionParser

def add_waypoints(way, nodes, distance):
    '''
    Add points along the way to help in building 
    the alpha shape.

    @param way: The way XML node
    @param lat_lons: The latitudes and longitudes of all the nodes indexed by id
    @return: Nothin, print a bunch of latitudes and longitudes
    '''
    nds = list(way.iter('nd'))
    for i in range(len(nds)-1):
        node_start = nodes[nds[i].attrib['ref']]
        node_end = nodes[nds[i+1].attrib['ref']]

        vec_length = hv.haversine(node_start, node_end)
        #print >>sys.stderr, "vec_length:", vec_length
        vec_length_parts = int(2 + (1+ vec_length / distance))

        lats = np.linspace(node_start[0], node_end[0], vec_length_parts)
        lons = np.linspace(node_start[1], node_end[1], vec_length_parts)

        #print >>sys.stderr, "len(lats)", len(lats), len(lons)
        #print >>sys.stderr, "zip", zip(lats, lons)

        for j in range(1, len(zip(lats, lons))):
            dir_vec = np.array([lats[j], lons[j]]) - np.array([lats[j-1], lons[j-1]])
            ortho_vec1 = np.array([-dir_vec[1], dir_vec[0]])
            ortho_vec2 = np.array([dir_vec[1], -dir_vec[0]])

            norm1 = np.linalg.norm(ortho_vec1)
            norm2 = np.linalg.norm(ortho_vec2)

            print lats[j-1], lons[j-1]

            epsilon = 0.00000001
            if norm1 < epsilon or norm2 < epsilon:
                print >>sys.stderr, "TOO SHORT:", norm1, norm2
                continue

            ortho_vec1 = 0.0003 * ortho_vec1 / norm1
            ortho_vec2 = 0.0003 * ortho_vec2 / norm2

            side1 = np.array([lats[j-1], lons[j-1]]) + ortho_vec1
            side2 = np.array([lats[j-1], lons[j-1]]) + ortho_vec2

            print side1[0], side1[1]
            print side2[0], side2[1]

        side1 = np.array([lats[j], lons[j]]) + ortho_vec1
        side2 = np.array([lats[j], lons[j]]) + ortho_vec2
        print lats[j], lons[j]
        #print side1[0], side1[1]
        #print side2[0], side2[1]
            
        #print >>sys.stderr, "points:", zip(lats, lons)
        #for lat,lon in  zip(lats, lons):
        #    print lat, lon

def fill_land_area(elem, lat_lons):
    '''
    Add artificial grid points within a land area
    so as to be able to fit it within an alpha shape.

    @param elem: The element containing the way.
    @param lat_lons: The latitudes and longitudes of the ways.
    @return: Nothing, just print a bunch of stuff
    '''
    points = []
    for nd in elem.findall('nd'):
        #print >>sys.stderr, "nd.attrib", nd.attrib
        if 'ref' in nd.attrib:
            points += [lat_lons[nd.attrib['ref']]]
        nd.clear()
    #print >>sys.stderr, "points:", points

    if len(points) < 3:
        return

    polygon = sg.Polygon(points)
    bounds = polygon.bounds

    xs = np.arange(bounds[0], bounds[2], 0.003)
    ys = np.arange(bounds[1], bounds[3], 0.003)

    for x,y in it.product(xs, ys):
        point = sg.Point(x,y)
        if point.within(polygon):
            print point.x, point.y
    

def main():
    usage = """
    python sample_osm_nodes.py file.osm
    """
    num_args= 0
    parser = OptionParser(usage=usage)

    parser.add_option('-n', '--n', dest='n', default=1, help="Sample one out of every n nodes", type='int')
    parser.add_option('-d', '--distance', dest='distance', default=1, help="The distance for the alpha shapes", type='float')
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

    lat_lons = {}

    counter = 0
    for event, elem in context:
        if event == 'end':
            if elem.tag == 'node':
                counter += 1

                if counter % options.n == 0:
                    if 'lat' in elem.attrib and 'lon' in elem.attrib and 'id' in elem.attrib:
                        lat_lons[elem.attrib['id']] = (float(elem.attrib['lat']), float(elem.attrib['lon']))
                        print elem.attrib['lat'], elem.attrib['lon']
            if elem.tag == 'way':
                landuse = False
                for tag in elem.iter('tag'):
                    if 'k' not in tag.attrib or 'v' not in tag.attrib:
                        continue
                    if tag.attrib['k'] == 'landuse' and tag.attrib['v'] == 'residential':
                        landuse = True
                        fill_land_area(elem, lat_lons)
                if not landuse:
                    add_waypoints(elem, lat_lons, options.distance)
                pass

            if elem.tag != 'nd':
                elem.clear()
                root.clear()

if __name__ == '__main__':
    main()
