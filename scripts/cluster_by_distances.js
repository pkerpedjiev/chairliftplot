var d3 = require('d3');
var topojson = require("topojson");

function proximityCluster(points, distance,dist) {
    //cluster points such that whenever two points are
    //within distance of each other, they are placed in
    //the same cluster

    //take m n-d points as input and
    //return an array of length m containing integers
    //where each integers encodes the cluster that the ith
    //point is in
    //
    // dist is a function that computes the distance between
    // any two points

    var clusters = [], links = [];
    var linksDict = {};
    
    // all points are in their own cluster
    for (var i = 0; i < points.length; i++) {
        clusters.push(i);
        linksDict[i] = [];
    }

    // sort the points by x values
    points = points.sort(function(a,b) { return a[0] - b[0]; });

    for (i = 0; i < points.length; i++) {
        //check for points to the right
        for (j = i+1; j < points.length; j++) {
            if (Math.abs(points[j][0] - points[i][0]) > distance)
                break;  // gone too far

            if (dist(points[i], points[j]) < distance) {
                // the two points are close enough to be linked
                links.push([i,j]);
                linksDict[i].push(j);
                linksDict[j].push(i);
            }
        }
    }

    var visited = d3.set();

    // traverse the list of links and assign clusters
    function dfs(currNode, prevNode) {
        visited.add(currNode);
        clusters[currNode] = Math.min(clusters[currNode], clusters[prevNode]);

        for (var i = 0; i < linksDict[currNode].length; i++) {
            if (visited.has(linksDict[currNode][i]))
                continue;

            dfs(linksDict[currNode][i], currNode);
        }
    }

    // go through every point and traverse its list of links
    // assigning clusters
    for (i = 0; i < points.length; i++) {
        if (visited.has(i))
            continue;

        dfs(i, i);
    }

    return {"clusters": clusters, "links": links};
}

function haversine(lat1, lon1, lat2, lon2) {
    /*
    Calculate the haversine distance between two points on the
    globe. Code taken from:

    http://stackoverflow.com/a/14561433
   */
    Number.prototype.toRad = function() {
        return this * Math.PI / 180;
    };

    var R = 6371; // km 
    //has a problem with the .toRad() method below.
    var x1 = lat2-lat1;
    var dLat = x1.toRad();  
    var x2 = lon2-lon1;
    var dLon = x2.toRad();  

    var a = Math.sin(dLat/2) * Math.sin(dLat/2) + 
                    Math.cos(lat1.toRad()) * Math.cos(lat2.toRad()) * 
                    Math.sin(dLon/2) * Math.sin(dLon/2);  
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
    var d = R * c;

    return d;
}

function distanceBetweenNodes(node1, node2) { 
    return haversine(+node1['$'].lat, +node1['$'].lon, +node2['$'].lat, +node2['$'].lon);
}

function clusterOsmPoints(osmData, distance) {
    /* Take the input XML data structure and cluster
     * the points according to how far from each other they
     * are.
     *
     * Return a dictionary where the cluster names are the keys
     * and the values are lists of (lat, lon) pairs
     */
    var clusters = proximityCluster(osmData.osm.node, distance, distanceBetweenNodes);
    var clusterPoints = {};

    for (var i = 0; i < clusters.clusters.length; i++) {
        // iterate over every cluster assignment for each point
        var currCluster;

        // check if we've already seen this cluster of points before
        if (clusters.clusters[i] in clusterPoints) 
            currCluster = clusterPoints[clusters.clusters[i]]; 
        else
            currCluster = [];  // we haven't create a new one

        currCluster.push([+osmData.osm.node[i].$.lat, +osmData.osm.node[i].$.lon]);
        clusterPoints[clusters.clusters[i]] = currCluster;
    }

    return clusterPoints;
}

function clustersToTriangles(clusterPoints, distance) {
    /* Create alpha shapes for all of the clusters in clusterPoints
     *
     * Return a dictionary of the cells.
     */
    var newCellsDict = {};
    for (var clusterId in clusterPoints) {
        if (clusterPoints[clusterId].length < 2)
            continue;

        if (clusterPoints[clusterId].length == 2) {
            newCellsDict[clusterId] = [clusterPoints[clusterId]];
            continue;
        }

        var mesh = d3.geom.delaunay(clusterPoints[clusterId]).filter(function(t) {
            return  (haversine(t[0][0], t[0][1], t[1][0], t[1][1]) < distance &&
                     haversine(t[0][0], t[0][1], t[2][0], t[2][1]) < distance &&
                     haversine(t[2][0], t[2][1], t[1][0], t[1][1]) < distance);
        });
        
        newCellsDict[clusterId] = mesh;
    }

    return newCellsDict;
}

function clustersToAlphaShapes1(clusterPoints, distance) {
    /* Create alpha shapes for all of the clusters in clusterPoints
     *
     * Return a dictionary of the cells.
     */
    if (arguments.length == 1)
        distance = 1;

    var cellsDict = {};
    var newCellsDict = {};
    for (var clusterId in clusterPoints) {
        if (clusterPoints[clusterId].length < 2)
            continue;

        if (clusterPoints[clusterId].length == 2) {
            newCellsDict[clusterId] = clusterPoints[clusterId];
            continue;
        }


        var mesh = d3.geom.delaunay(clusterPoints[clusterId]).filter(function(t) {
            return  (haversine(t[0][0], t[0][1], t[1][0], t[1][1]) < distance &&
                     haversine(t[0][0], t[0][1], t[2][0], t[2][1]) < distance &&
                     haversine(t[2][0], t[2][1], t[1][0], t[1][1]) < distance);
        });

        var collection = {type: "FeatureCollection", features: mesh.map(function(d) {
            return { "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [d]
                    }
                };
            })
        };

        var topology = topojson.topology({collection: collection}, {"verbose": "truthy"});
        console.log('topology', topology);

        /*
        for (var i = 0; i < topology.arcs.length; i++)
            console.log('arc:', topology.arcs[i]);

        for (var i = 0; i < topology.objects.collection.geometries.length; i++)
            console.log('geom:', topology.objects.collection.geometries[i]);
            */

        var merged =  topojson.merge(topology, topology.objects.collection.geometries);
        mergedCoords = merged.coordinates.filter(function(d) { return d.length > 0; })
        .map(function(d) { return d[0]; });
        console.log('mergedCoords:', mergedCoords);

        newCellsDict[clusterId] = mergedCoords;
    }

    return cellsDict;
}

var main = function() {
    var argv = require('minimist')(process.argv.slice(2));

    if (argv._.length < 1) {
        console.log('Not enough arguments:', argv._);
    }

    if ('d' in argv)
        distance = argv['d'];
    else
        distance = 1;

    var fs = require('fs');
    var xml2js = require('xml2js');

    var parser = new xml2js.Parser();
    fs.readFile(argv._[0], function(err, data) {
        parser.parseString(data, function (err, result) {
            var clusterPoints = clusterOsmPoints(result, distance);
            var alphaShapes = clustersToAlphaShapes(clusterPoints, distance);

            var outputStruct = {"bounds": alphaShapes,
                                "distance": distance };

            //console.log(JSON.stringify(outputStruct));
        });
    });
};

if (require.main === module) {
    main();
}
