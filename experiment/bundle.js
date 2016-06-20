d3.json("force.json", function(error, json) {
		if (error) throw error;
		var names = [];
		var tags = [];
		var nodes = json.nodes,links = json.links;
		var n = nodes.length;
		var cosmat = new Array(n);
		for (i=0;i<n;i++)
		{
			cosmat[i] = new Array(n);
			for (j=0;j<n;j++)
			{
				cosmat[i][j] = 0;
			}
		}
		nodes.forEach(function(node, i) {
			names[i] = node.name;
			tags[i] = node.group;
		});
		
		links.forEach(function(link,i){
			cosmat[link.source][link.target] = link.value;
		});
		console.log(cosmat);
		render_bundle(names,cosmat,tags)
	});
	function render_bundle(names,cosmat,tags){
		//1.定义数据
		var nodecolors =["#FF2D2D","#79FF79","#9393FF"];
		var linkcolors =["#FFFF6F","#80FFFF","#FF77FF"];
		//var linkcolors =["#A6A600","#00AEAE","#AE00AE"];
		// var nodecolors =["#EA0000","#28FF28","#6A6AFF"];
		// var linkcolors =["#F9F900","#00FFFF","#FF00FF"];

		//2.转换数据，并输出转换后的数据					
		var chord_layout = d3.layout.chord()
			                 .padding(0.03)		//节点之间的间隔
			                 .sortSubgroups(d3.descending)	//排序
			                 .matrix(cosmat);	//输入矩阵

		var groups = chord_layout.groups();
		var chords = chord_layout.chords();
		
		//3.SVG，弦图，颜色函数的定义
		var width  = 400;
		var height = 400;
		var innerRadius = width/2 * 0.7;
		var outerRadius = innerRadius * 1.1;

		var color20 = d3.scale.category20();

		var svg = d3.select("#bundle").append("svg")
			.attr("width", width)
			.attr("height", height)
		    .append("g")
			.attr("transform", "translate(" + width/2 + "," + height/2 + ")");

		//4.绘制节点（即分组，有多少个城市画多少个弧形），及绘制城市名称
		var outer_arc =  d3.svg.arc()
					 .innerRadius(innerRadius)
					 .outerRadius(outerRadius);
		
		var g_outer = svg.append("g").attr("class","g_arc");
		
		g_outer.selectAll("path")
				.data(groups)
				.enter()
				.append("path")
				.style("fill", function(d,i) { return nodecolors[Math.round(tags[i])-2]; })
				.style("stroke", function(d,i) { return nodecolors[Math.round(tags[i])-2]; })
				.attr("d", outer_arc );
						
		g_outer.selectAll("text")
				.data(groups)
				.enter()
				.append("text")
				.each( function(d,i) { 
					d.angle = (d.startAngle + d.endAngle) / 2; 
					d.name = names[i];
				})
				.attr("dy",".35em")
				.attr("transform", function(d){
					return "rotate(" + ( d.angle * 180 / Math.PI ) + ")" +
						   "translate(0,"+ -1.0*(outerRadius+10) +")" +
						    ( ( d.angle > Math.PI*3/4 && d.angle < Math.PI*5/4 ) ? "rotate(180)" : "");
				})
				.text(function(d){
					return d.name;
				});					

		//5.绘制内部弦（即所有城市人口的来源，即有5*5=25条弧）
		var inner_chord =  d3.svg.chord()
						.radius(innerRadius);
		
		var g_iner = svg.append("g").attr("class", "g_bundle");

		g_iner.selectAll("path")
			.data(chords)
		    .enter()
			.append("path")
			.attr("d", inner_chord )
		    .style("fill", function(d) {
		    	 pair = [tags[d.source.index],tags[d.target.index]].toString()
		    	 if ( (pair == [2.0,3.0].toString()) || (pair == [3.0,2.0].toString()) )
		    	 	{return linkcolors[0];}
		    	 else if ( (pair == [3.0,4.0].toString()) || (pair == [4.0,3.0].toString()) )
		    	 	{return linkcolors[1];}
		    	 else {return linkcolors[2]; }
		    	})
			.style("opacity", 0.8)
			.style("stroke","#000")
			.style("stroke-width","0.5px");

		//6. 设置mouseover及mouseout事件的响应
		g_iner.selectAll("path")
			.on("mouseover",function(d,i){
				g_iner.selectAll("path")
					  .style("opacity",function(p,j){
						if(j==i)
							{ return 0.8;}
						else
							{ return 0.2;}
					});
				d3.select("#data-info")
					.select("#content")
					.text(names[d.source.index]+','+names[d.target.index]+': \n'+
						cosmat[d.source.index][d.target.index].toFixed(2) );
				//mouseover on matrix
				d3.selectAll(".row text").classed("active", function(p,j) {
			        return j == d.target.index;
			      });
			    d3.selectAll(".column text").classed("active", function(p,j) {
			        return j == d.source.index;
			      });

			})
			.on("mouseout",function(d,i){
				g_iner.selectAll("path")
					  .style("opacity",0.8);
				d3.selectAll(".row text").classed("active", false);
				d3.selectAll(".column text").classed("active", false);
			});
		g_outer.selectAll("path")
				.on("mouseover",function(d,i){
					str = names[i] + ":";
					flag = false
					g_iner.selectAll("path")
						  .style("opacity",function(p){
						  	if((p.source.index != i) && (p.target.index != i)) 
						  		{  return 0.2; }
						  	else
						  		{  
						  			if (p.source.index == i){
						  				j = p.target.index;
						  			}
						  			else { j = p.source.index;}
						  			if (flag) { str = str + "," }
						  			flag = true
						  			str = str  + names[j] + "(" + cosmat[i][j].toFixed(2) + ")";
						  			return 0.8;
						  		} 
						  });
					d3.select("#data-info")
									.select("#content")
									.text(str);
					//mouseover on matrix
					d3.selectAll(".row text").classed("active", function(p,j) {
				        return j == i;
				      });
				    d3.selectAll(".column text").classed("active", function(p,j) {
				        return j == i;
				      });
				})
				.on("mouseout",function(d,i){
					g_iner.selectAll("path")
						.style("opacity",0.8);
					d3.selectAll(".row text").classed("active", false);
					d3.selectAll(".column text").classed("active", false);
			});
		}