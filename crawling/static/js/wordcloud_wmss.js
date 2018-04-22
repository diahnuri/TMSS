function worklot(){
					var teks = document.getElementById('konten_berita').value;
					var kata = teks.match(/\b(\w+)\b/g);
					var frequency_list = [];
					var word_list = [];
					var maxSize = 0;

					for (i=0; i<kata.length; i++){
					    if(word_list.indexOf(kata[i]) < 0){
					        word_list.push(kata[i]);
					    } else {
					        break;
					    }
					    var size = 0;
					    for(j=0; j<kata.length; j++){
					        if(kata[i]==kata[j]){
					            size +=1;
					        }
					        else {
					            size +=0;
					        }
					    }

					    if(size>maxSize){
					        maxSize=size;
					    }
					    frequency_list.push({"text":kata[i], "size":size});
					}

				var dump = JSON.stringify(frequency_list);
	    		$('#example').dataTable({
	    				"aaData":dump,
	    				"aoColumns":[
	    				{"mDataProp":"text"},
	    				{"mDataProp":"size"}
	    				],
	    				"order":[[1,"desc"]],
	    				"lengthMenu":[[5,10,15,-1],[5,10,15,"All"]]
	    				});

					var fill = d3.scale.category20();

					var fontSize = d3.scale.linear()
					        .domain([1, maxSize])
					        .range([10, 100]);

					d3.layout.cloud().size([800, 300])
					        .words(frequency_list)
					        .padding(1)
					        .rotate(function(){ return ~~(Math.random() * 2) * 90;})
					        .font("Impact")
					        .text(function(d){ return d.text; })			
					        .fontSize(function(d) { return fontSize(d.size); })
					        .on("end", draw)
					        .start();

					function draw(words) {
						$('#word-cloud').html("");
					    d3.select("#word-cloud").append("svg")
					            .attr("width", 850)
					            .attr("height", 350)
					            .attr("class", "wordcloud")
					            .append("g")
					            // without the transform, words words would get cutoff to the left and top, they would
					            // appear outside of the SVG area
					            .attr("transform", "translate(320,200)")
					            .selectAll("text")
					            .data(words)
					            .enter().append("text")
					            .style("font-size", function(d) { return d.size + "px"; })
					            .style("fill", function(d, i) { return fill(i); })
					            .attr("text-anchor", "middle")
					            .attr("transform", function(d) {
					                return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
					            })
					            .text(function(d) { return d.text; });
					}
			}		
