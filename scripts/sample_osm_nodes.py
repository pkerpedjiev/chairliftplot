#!/usr/bin/python

import itertools as it
import numpy as np
import shapely.geometry as sg
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
                points = []
                for nd in elem.findall('nd'):
                    #print >>sys.stderr, "nd.attrib", nd.attrib
                    if 'ref' in nd.attrib:
                        points += [lat_lons[nd.attrib['ref']]]
                    nd.clear()
                #print >>sys.stderr, "points:", points


                if len(points) < 3:
                    continue

                polygon = sg.Polygon(points)
                bounds = polygon.bounds

                xs = np.arange(bounds[0], bounds[2], 0.003)
                ys = np.arange(bounds[1], bounds[3], 0.003)

                for x,y in it.product(xs, ys):
                    point = sg.Point(x,y)
                    if point.within(polygon):
                        print point.x, point.y

            if elem.tag != 'nd':
                elem.clear()
                root.clear()

if __name__ == '__main__':
    main()

