import json
import uuid

from shapely.ops import transform
from haversine import haversine
import shapely.geometry as geometry
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.geometry import mapping
from shapely.ops import cascaded_union, polygonize, unary_union
from scipy.spatial import Delaunay
import numpy as np
import math
import pyproj as pp

def calculate_projected_polygon_area(polygon):
    '''
    Project the polygon onto an equal area projection
    and return its area.
    
    @param polygon: A shapely polygon.
    @return: The polygon's area.
    '''
    point = polygon.representative_point()
    m = pp.Proj(proj='laea +lat_0={} +lon_0={}'.format(point.x, point.y))
    #m = Basemap(width=1,height=1, resolution='l',projection='laea',lat_ts=point.x,lat_0=point.x,lon_0=point.y)
    coords = polygon.exterior.coords
    new_coords = []
    for (x1,y1) in coords:
        new_coords += [ m(x1,y1)]

    new_polygon = Polygon(new_coords)
    return new_polygon.area

 
def alpha_shape(points, distance_function=haversine, distance=1):
    """
    Compute the alpha shape (concave hull) of a set
    of points.
 
    @param points: Iterable container of points.
    @param alpha: alpha value to influence the
        gooeyness of the border. Smaller numbers
        don't fall inward as much as larger numbers.
        Too large, and you lose everything!
    """
    if len(points) < 4:
        # When you have a triangle, there is no sense
        # in computing an alpha shape.
        return geometry.MultiPoint(list(points)).convex_hull
 
    def add_edge(edges, edge_points, coords, i, j):
        """
        Add a line between the i-th and j-th points,
        if not in the list already
        """
        if (i, j) in edges or (j, i) in edges:
            # already added
            return
        edges.add( (i, j) )
        edge_points.append(coords[ [i, j] ])
 
    coords = np.array([point.coords[0]
                       for point in points])
 
    tri = Delaunay(coords)
    edges = set()
    edge_points = []
    # loop over triangles:
    # ia, ib, ic = indices of corner points of the
    # triangle
    polygons = []

    for ia, ib, ic in tri.vertices:
        pa = coords[ia]
        pb = coords[ib]
        pc = coords[ic]
 
        # Lengths of sides of triangle
        '''
        a = math.sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2)
        b = math.sqrt((pb[0]-pc[0])**2 + (pb[1]-pc[1])**2)
        c = math.sqrt((pc[0]-pa[0])**2 + (pc[1]-pa[1])**2)
        '''

        a = distance_function(pa[::-1], pb[::-1])
        b = distance_function(pb[::-1], pc[::-1])
        c = distance_function(pa[::-1], pc[::-1])

        if a > distance or b > distance or c > distance:
            continue
 
        """
        # Semiperimeter of triangle
        s = (a + b + c)/2.0
 
        # Area of triangle by Heron's formula
        area = math.sqrt(s*(s-a)*(s-b)*(s-c))
        circum_r = a*b*c/(4.0*area)
 
        # Here's the radius filter.
        #print circum_r
        if circum_r < 1.0/alpha:
        """

        add_edge(edges, edge_points, coords, ia, ib)
        add_edge(edges, edge_points, coords, ib, ic)
        add_edge(edges, edge_points, coords, ic, ia)

        #print >>sys.stderr, "ia:", ia
        rounded = 7
        poly = Polygon([coords[ia], coords[ib], coords[ic]])
        if not poly.is_valid:
            print >>sys.stderr, "not valid:", poly
        else:
            polygons += [poly]

        '''
        epsilon = 0.0000001
        if np.allclose(coords[ia], coords[ib], epsilon):
            print >>sys.stderr, "close:", ia, ib, coords[ia], coords[ib]
        if np.allclose(coords[ia], coords[ic], epsilon):
            print >>sys.stderr, "close:", ia, ic, coords[ib], coords[ic]
        if np.allclose(coords[ib], coords[ic], epsilon):
            print >>sys.stderr, "close:", ib, ic, coords[ia], coords[ic]
        '''
 
    #print "sum", sum([p.is_valid for p in polygons])
    #print >>sys.stderr, "polygons:", polygons
    #m = geometry.MultiLineString(edge_points)
    #triangles = list(polygonize(m))
    #print >>sys.stderr, "len:", len(polygons), polygons[54405], polygons[54406]
    return cascaded_union(polygons), edge_points

import sys
from optparse import OptionParser

def main():
    usage = """
    python concave_hull sampled_osm.ssv
    """
    num_args= 1
    parser = OptionParser(usage=usage)

    parser.add_option('-d', '--distance', dest='distance', default=1, help="The distance between which to keep triangles", type='float')
    #parser.add_option('-u', '--useless', dest='uselesss', default=False, action='store_true', help='Another useless option')

    (options, args) = parser.parse_args()

    if len(args) < num_args:
        parser.print_help()
        sys.exit(1)

    points = []
    points = np.genfromtxt(args[0], delimiter=' ')

    #print >>sys.stderr, "point:", points
    points = [geometry.shape(Point(point[1], point[0]))     #Add points as longitude latitude pairs
                      for point in points]
    concave_hull, edge_points = alpha_shape( points, distance=options.distance)
    features = []

    if type(concave_hull) is Polygon:
        concave_hull = [concave_hull]

    for polygon in concave_hull:
        area = calculate_projected_polygon_area(polygon)
        features += [ { "type": "Feature",
                        "geometry": mapping(polygon),
                        "properties": {
                            "name": "",
                            "area": area / 1000000.,
                            "uid": str(uuid.uuid4())
                            }
                        } ]
        #print >>sys.stderr, "polygon:", polygon
        print >>sys.stderr, "projected_polygon:", area / 1000000
    features.sort(key=lambda x: -x['properties']['area']);

    output_json = {"type":"FeatureCollection",
                    "features": features
                    }
    #print >>sys.stderr, "polygon:", polygon
    #print >>sys.stderr, "concave_hull:", concave_hull

    #print json.dumps(mapping(concave_hull))
    print json.dumps(output_json,indent=2)

if __name__ == '__main__':
    main()

