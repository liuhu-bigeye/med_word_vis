render_force();
	function render_force(){
		var width = 800,
		height = 500
			
		function color(grp){
			console.log(grp);
			col = ["#EA0000","#28FF28","#6A6AFF"];
			return col[grp-2];
		}

		var svg = d3.select("#force").append("svg")
			.attr("width", width)
			.attr("height", height);

		var force = d3.layout.force()
			.gravity(0.05)
			.distance(100)
			.charge(-100)
			.size([width, height]);

		d3.json("force.json", function(error, json) {
		  if (error) throw error;

		  force
			  .nodes(json.nodes)
			  .links(json.links)
			  .start();

		  var link = svg.selectAll(".link")
			  .data(json.links)
			.enter().append("line")
			  .attr("class", "link")
			  .style("stroke-width", function(d) { return Math.sqrt(d.value); });

		  var place = svg.selectAll("g")
			  .data(json.nodes)
			  .enter().append("g")
			
		  var node = place.append("circle")
			  .attr("class", "node")
			  .attr("r", 5)
			  .style("fill", function(d) { return color(d.group); })
			  .call(force.drag);

		  var name = place.append("text")
				.attr("class", "name")
				.attr("dx", 12)
				.attr("dy", ".35em")
				.text(function(d) { return d.name })
				.style("font-family","sans-serif");

		  var brush = svg.append("g")
				.attr("class", "brush")
				.call(d3.svg.brush()
				.x(d3.scale.identity().domain([0, width]))
				.y(d3.scale.identity().domain([0, height]))
				.on("brush", function() {
				  var extent = d3.event.target.extent();
				  node.classed("selected", function(d) {
					return extent[0][0] <= d.x && d.x < extent[1][0]
						&& extent[0][1] <= d.y && d.y < extent[1][1];
				  });
				  name.classed("selected",function(d) {
					return extent[0][1] <= d.x && d.x < extent[1][0]
						&& extent[0][1] <= d.y && d.y < extent[1][1];
				  });
				}));
			

		  force.on("tick", function() {
			link.attr("x1", function(d) { return d.source.x; })
				.attr("y1", function(d) { return d.source.y; })
				.attr("x2", function(d) { return d.target.x; })
				.attr("y2", function(d) { return d.target.y; });

			place.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
			
		  });
});
	}