function radial(input_json_data, canvas_size) {
  var diameter = canvas_size;
  
  var tree = d3.layout.tree()
      .size([360, diameter / 2 - 120])
      .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });
  
  var diagonal = d3.svg.diagonal.radial()
      .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });
  
  var svg = d3.select("body").append("svg")
      .attr("width", diameter)
      .attr("height", diameter - 50)
      .append("g")
      .attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");
  
  d3.json(input_json_data, function(error, root) {
    if (error) throw error;
  
    var nodes = tree.nodes(root),
        links = tree.links(nodes);
  
    var link = svg.selectAll(".link")
        .data(links)
      .enter().append("path")
        .attr("class", "link")
        .attr("d", diagonal);
  
    var node = svg.selectAll(".node")
        .data(nodes)
      .enter().append("g")
        .attr("class", "node")
        .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; })
  
    node.append("circle")
        .attr("r", 4.5)
        .attr("class", function(d) {return ((d.is_dist) ? "with_dist" : ((d.is_extent) ? "with_extent" : "default"));});
  
    node.append("text")
        .attr("dy", ".31em")
        .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
        .attr("transform", function(d) { return d.x < 180 ? "translate(8)" : "rotate(180)translate(-8)"; })
        .attr("title", function(d) { return taxonToolTip(d); })
        .text(function(d) { return d.name; })
        .on("click", function(d) { window.open("http://qa1.seaaroundus.org/data/#/taxon/" + d.key); });
        
    function taxonToolTip(d) { 
      return ("<h2>" + d.name + "</h2><table><tr><td>Key</td><td>" + d.key + "</td></tr>" +
              ((d.hasOwnProperty('level')) ? ("<tr><td>Level</td><td>" + d.level + "</td></tr>") : "") + 
              ((d.hasOwnProperty('lineage')) ? ("<tr><td>Lineage</td><td>" + d.lineage + "</td></tr>") : "") +
              ((d.hasOwnProperty('is_dist')) ? ("<tr><td>Distribution </td><td>" + d.is_dist + "</td></tr>") : "") +
              ((d.hasOwnProperty('is_extent')) ? ("<tr><td>Extent</td><td>" + d.is_extent + "</td></tr>") : "") +
              ((d.hasOwnProperty('total_catch')) ? ("<tr><td>Catch</td><td>" + d.total_catch + "</td></tr>") : "") +
              ((d.hasOwnProperty('total_value')) ? ("<tr><td>Value</td><td>" + d.total_value + "</td></tr>") : "") +
              "</table>"
             );
    }
  
    $(document).ready(function() {
      $("text").tooltipster({
        followMouse: true,
        contentAsHTML: true
      });
    });
  });
  
  d3.select(self.frameElement).style("height", diameter - 100 + "px");
};