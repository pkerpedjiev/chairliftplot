d3.xml("with_elevation/stuhleck.osm", "application/xml", function(xml) {
    var ways = $(xml).find("way");
    //var ways = xml.documentElement.getElementsByTagName("way");
    //
    ways.each(function() {
        var way = $(this);
        var nds = $(way).find('nd');

        var firstNode = $(xml).find("#" + $(nds[0]).attr('ref'));
        var start = {latitude: +firstNode.attr('lat'),
            longitude: +firstNode.attr('lon'),
            elevation: +firstNode.attr('elev')};

        var xs = [];
        var zs = [];

        for (var i = 0; i < nds.length; i++) {
            var nd = $(nds[i]);
            var node = $(xml).find("#" + nd.attr('ref'));
            var here =  {"latitude": +node.attr('lat'),
                "longitude": +node.attr('lon'),
                "elevation": +node.attr('elev')};

            var dist = haversine(start, here);

            xs.push(dist);
            zs.push(here.elevation);
        }

        console.log('xs', xs);
        console.log('zs', zs);

    });
});
