var width = 590,
    height = 400,
    color = "#0099FF";

var palette = ["#FFFFFF","#F8E6CC","#F1CE99","#EBB566","#E49D33","#DE8500"];

var thresholds = [0, 249, 499, 999, 1999];

var get_color = function(v) {
	for (var c = 0; c < thresholds.length; c += 1) {
		if (v <= thresholds[c]) {
			//console.log(v, c);
			return palette[c];
		}
	}
	return palette[5];
}

var distribution = [];
	
var svg = d3.select("#canvas").append("svg")
    .attr("width", width)
    .attr("height", height);

var path = d3.geo.path();

var tooltip = d3.select("body")
    .append("div")
    .attr("class", "tooltip")
    .text("")
    .attr("visibility", "hidden");
    
d3.json("data/boston_marathon.json", function(error, info) {

  loadData(info);
});

var myturn = 0,
	running = false,
	timer;
 
function loadData(info) {
	var INTERVAL = 5;
	var ticks = 60 / INTERVAL;
	var segments = 6 * ticks;

		function makeTime() {
			var hours,
				minutes,
				meridian = "AM";
		
			hours = 10 + Math.floor(myturn / ticks);
			if (hours >= 12) {
				meridian = "PM";
			}
			if (hours > 12) {
				hours = hours % 12;
			}
			minutes = INTERVAL * (myturn % ticks);
			if (minutes < 10) {
				minutes = "0" + minutes;
			}			
			$("#clock").html(hours + ":" + minutes + " " + meridian);				
		}
		
  var mass = info.geojson,
  	counties = topojson.object(mass, mass.objects.counties).geometries,
  	points = topojson.object(mass, mass.objects.marathon).geometries,
  	route = "",
  	flags = [];

  //add start and end points to markers
  info.markers = info.markers[0]  
  info.markers.unshift([points[0].coordinates[1], points[0].coordinates[0]]);
  //info.markers.push([points[2].coordinates[1], points[2].coordinates[0]]);
  
  //convert to xy
  info.markers.forEach(function(d) {
  	var obj = {
  		"type": "Point",
  		"coordinates": [d[1], d[0]]
  	};
  	points = path(obj).slice(1).split(/[A-z,]/);
  	flags.push([parseFloat(points[0]), parseFloat(points[1])]);
  	route += "L" + parseFloat(points[0]) + "," + parseFloat(points[1]);  	
  });
  route = "M" + route.slice(1);

  var maps = svg.append("g").attr("id", "maps");
  var marks = svg.append("g").attr("id", "marks");

  //background political boundaries
  maps.selectAll(".district")
    .data(counties)
    .enter().append("path")
    .attr("d", path)
    .attr("id", function(d, i) {
    	return "fips-" + d.id;
    })
    .attr("class", "district")
    .on("mouseover", function(d, i) {
        d3.select(this).style("fill", "#FF9"); 
        tooltip.html(d.id); 
        return tooltip.style("visibility", "visible");
       })
    .on("mousemove", function(d){return tooltip.style("top", (d3.event.pageY-10)+"px").style("left", d3.event.pageX < 600 ? (d3.event.pageX+10)+"px" : (d3.event.pageX-220)+"px");})
    .on("mouseout", function(d, i) {
        d3.select(this).style("fill", "#99E6FF"); 
        return tooltip.style("visibility", "hidden");
    });

  svg.selectAll(".legend")
	.data(palette)
	.enter()
	.append("rect")
	.attr("class", "legend")
	.attr("x", 15)
	.attr("width", 15)
	.attr("height", 15)
	.attr("y", function(d, i) { return 15 + 20 * i; })
	.style("fill", function(d, i) { return d; });

  svg.selectAll(".legend_text")
	.data(palette)
	.enter()
	.append("text")
	.attr("class", "legend_text")
	.style("text-anchor", "start")
	.attr("y", function(d, i) { return 27 + 20 * i; })
	.attr("x", 34)
	.text(function(d, i) { 
		if (i === 5) {
			return 125 * Math.pow(2, i - 1) + "+"; 		
		} else if (i === 0) {
			return "0"; 
		} else if (i === 1) {
			return "1 - " + (125 * Math.pow(2, i) - 1); 
		}
		return 125 * Math.pow(2, i - 1) + " - " + (125 * Math.pow(2, i) - 1); 		
	});


  svg.append("text")
  	.attr("id", "legend_title")
	.attr("y", 10)
	.attr("x", 15)
	.style("text-anchor", "start")
	.attr("class", "legend_title")
	.text("Runners");  	

    
  maps.append("path")
    .attr("d", route)
    .attr("class", "route");

  marks.selectAll(".marker") 
  	.data(flags)
  	.enter()
  	.append("circle")
  	.attr("class", "flag")
  	.attr("id", function(d, i) { return "flag-" + i; })
  	.attr("cx", function(d) { return d[0] * 88 - 71750; })
  	.attr("cy", function(d) { return d[1] * 88 - 10950; })
  	.attr("r", function(d) { return 5; })
    .on("mouseover", function(d, i) {
        tooltip.html("Runners at kilometer " + i + " at " + $("#clock").html() + ":<br /><div class='bignum'>" + (distribution[i] ? add_commas(distribution[i]) : 0) + "</div>"); 
        return tooltip.style("visibility", "visible");
       })
    .on("mousemove", function(d) {
    	console.log(d3.event.pageX);
		return tooltip.style("top", (d3.event.pageY-10)+"px").style("left", d3.event.pageX < 400 ? (d3.event.pageX+10)+"px" : (d3.event.pageX-220)+"px");
	})
    .on("mouseout", function(d, i) {
        return tooltip.style("visibility", "hidden");
    });
      
  maps.attr("transform", "translate(-71750, -10950)scale(88,88)");
  
	d3.json("data/condensed_time.json", function(error, root) {
		var data = root,
			c, t, i;
		
		//data.sort(function(a, b) { return parseInt(a.key, 10) > b.finished ? 1 : -1; });			
		//shift squares to the t_th timeblock
		
		function move(t) {
			$("#clock").css({
				color: t >= 58 ? "#C00" : "#000",
				'font-weight': t >= 58 ? "bold" : "normal"
			});
		
			distribution = data[t];			
			d3.selectAll(".flag").style("fill", "#FFF");			
			$.each(distribution, function(i, v) {
				d3.selectAll("#flag-" + i).style("fill", get_color(v));
			});
			
		}

		move(0);
			
		$("#next").bind("click", function() {
			if (running) {
				stop();
			}
		
			if (myturn < segments) {
				myturn += 1;
				makeTime();
				move(myturn);
			}
		});	
		
		$("#prev").bind("click", function() {
			if (running) {
				stop();
			}
			
			if (myturn > 0) {
				myturn -= 1;
				makeTime();
				move(myturn);
			}
		});	
		
		function advance() {
			if (myturn < segments) {
				myturn += 1;
				makeTime();
				move(myturn);
				
			} else {
				stop();
			}		
		}
		
		$("#redo").bind("click", function() {
			if (running) {
				stop();
			}
			myturn = 0;
			makeTime();
			move(myturn);
		});			

		$("#skip").bind("click", function() {
			if (running) {
				stop();
			}
			myturn = segments;
			makeTime();
			move(myturn);
		});			

		$("#play").bind("click", function() {
			if (!running) {
				start();
			} else {
				stop();
			}
		});		
		
		function start() {
			running = true;
			timer = setInterval(function() { advance(); }, 500);
			$("#play").html("Pause");
			$("#play").css("background-color", "#C00");
		}

		function stop() {
			running = false;
			clearInterval(timer);
			$("#play").html("Play");
			$("#play").css("background-color", "#0C0");
		}
			
	});
}