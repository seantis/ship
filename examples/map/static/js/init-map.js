var width = window.innerWidth, height = window.innerHeight;
var vis = d3.select("#map").append("svg:svg").attr('width', width).attr('height', height);

var po = org.polymaps;
//var poMapType;

$(document).bind('stf-ready', function(){
    var curZoomLevel;
    
    // Create the map object, add it to #map…
    var map = po.map().container(vis.node())
      .zoom(8.5)
      .center({
          lat: 46.7,
          lon: 9
      }).add(po.interact());
    
    // Add the CloudMade image tiles as a base layer…
	var mapTiles;
	
    /*map.add(mapTiles /*po.image()    
	.url(po.url("http://{S}tile.cloudmade.com"
     + "/1a1b06b230af4efdbb989ea99e9841af" // http://cloudmade.com/register
     + "/45763/256/{Z}/{X}/{Y}.png")
     .hosts(["a.", "b.", "c.", ""]))*/
    //.url("http://s3.amazonaws.com/com.modestmaps.bluemarble/{Z}-r{Y}-c{X}.jpg")
	//);
    
	
    // Add the compass control on top.
    map.add(po.compass().pan("none"));
	
	//$('g#bboxg').data('bbox');
    
    var $bboxg = $('g#bboxg'), bboxg = $bboxg.get(0);
    var $compass = $('g.compass'), compass = $compass.get(0);
    var bounds = $bboxg.data('bbox');
	//console.log(bounds);
	
	$('input[name="mapType"]').change(function() {
		var newMapTiles;
    //var val = $('input[name="mapType"]:checked').val();
    var showCities = $('#showCitiesChk:checked').val();
		//if (val == 'osm'  ||  val == 'osmlabels') {
      var style;
      if (showCities)
        style = 61319;
      else
        style = 61326;

			newMapTiles = po.image()    
			.url(po.url("http://{S}tile.cloudmade.com"
		     + "/1a1b06b230af4efdbb989ea99e9841af" // http://cloudmade.com/register
         + "/"+style+"/256/{Z}/{X}/{Y}.png"   

           // alternative styles: 26171, 44094, 58465 (no labels), 19321 (greens and lakes), 
           //   61316 (white, water, no roads)   http://maps.cloudmade.com/editor/style/61326
           // + "/8ee2a50541944fb9bcedded5165f09d9"     // registered by Ilya 
         )
		     .hosts(["a.", "b.", "c.", ""]));
			 map.zoomRange([1, 18]);
    /*
    }
		else if(val == 'bluemarble') {
			newMapTiles = po.image()    
			.url("http://s3.amazonaws.com/com.modestmaps.bluemarble/{Z}-r{Y}-c{X}.jpg");
			map.zoomRange([0, 9]);
		}
		else {
			 map.zoomRange([1, 18]);
		}
    */
		if (newMapTiles) {
			map.add(newMapTiles);
		}
		if(mapTiles) {
			map.remove(mapTiles);
		}
		
        bboxg.parentNode.appendChild(bboxg);
		compass.parentNode.appendChild(compass);
		
		//poMapType = val;
		mapTiles = newMapTiles;
	}).change();
	
    
    var zoomChange = function(){
        var topLeft = map.locationPoint({
            lon: bounds[0][0],
            lat: bounds[1][1]
        });
        var bottomRight = map.locationPoint({
            lon: bounds[1][0],
            lat: bounds[0][1]
        });
        //console.log(bottomRight.x - topLeft.x, bottomRight.y - topLeft.y);
        setNewProjectionSize(bottomRight.x - topLeft.x, bottomRight.y - topLeft.y);
        bboxg.parentNode.appendChild(bboxg);
		compass.parentNode.appendChild(compass);
    };
    
	var move = function() {
		vis.select("g#bboxg").attr("transform", transform);
        
        var newZoomLevel = map.zoom();
        if (newZoomLevel != curZoomLevel) {
            zoomChange();
            curZoomLevel = newZoomLevel;
        }
	}
	
    map.on("move", move);
	
  $(window).resize(function() {
    move();
    vis.attr('width', window.innerWidth).attr('height', window.innerHeight);
  });

	move();
    
    function transform(d){
        d = map.locationPoint({
            lon: bounds[0][0],
            lat: bounds[1][1]
        });
        return "translate(" + d.x + "," + d.y + ")";
    }
	
    $('input[name="ageRadio"], input[name="yearRadio"], input[name="accidentRadio"], input[name="typeRadio"], select[name="insurerSelect"]').change(function() {
        update_premiums();
    });

    var hideTimeout = null;

    $('.cantons').each(function(i) {
        $(this).mouseenter(function(e) {
        	var toolTipHtml = ""+this.__data__.properties.Name;
        	
        	if ($(this).data("price")!=undefined) {
        		toolTipHtml += "<div class=\"tt_price\">"+$(this).data("price")+" CHF</div>";
        	}

          toolTipHtml = '<div class="head">' + toolTipHtml + "</div>"
                function render_legend(value, average, image_base_path, icon_size) {
                        under_average = 0;
                        if(value < average) {
                            under_average = average - value;
                        }
                        over_average = 0;
                        if(value > average) {
                            over_average = value - average;
                            value = average;
                        }
                        while(value >= 1) {
                            toolTipHtml += '<img width="'+ icon_size + 'px" class="doc" src="' + image_base_path  + '.svg" />';
                            value--;
                        }
                        while(under_average >= 1) {
                            toolTipHtml += '<img width="'+ icon_size +'px" class="doc-std" src="' + image_base_path + '-gray.svg" />';
                            under_average--;
                        }
                        while(over_average >= 1) {
                            toolTipHtml += '<img width="'+ icon_size +'px" class="doc-ovr" src="' + image_base_path + '-red.svg" />';
                            over_average--;
                        }
//        		toolTipHtml += "<div class=\"tt_docs100k\">"+docs+"</div>";
                }
        	if ($(this).data("docs100k")!=undefined) {
                       toolTipHtml += '<div style="float: left; width: 200px; padding-right: 20px">';
                        docs = $(this).data("docs100k");
                        render_legend(docs/10, 18, 'static/img/doctor', 20);
                        toolTipHtml += '<div class="legend"><img width="20px" class="doc" src="static/img/doctor.svg" /> Doctors per 10\'000</div>';
                        toolTipHtml += '<div class="legend"><img width="20px" class="doc" src="static/img/doctor-gray.svg" /> Swiss average</div>';
                        toolTipHtml += '<div class="legend"><img width="20px" class="doc" src="static/img/doctor-red.svg" /> Over Swiss average</div>';
                        toolTipHtml += '</div>';
        	}
        	if ($(this).data("hospitalbeds")!=undefined) {
                        //toolTipHtml += '<div style="float: left; width: 200px;">';
                        beds = $(this).data("hospitalbeds");
                        render_legend(beds/10, 46, 'static/img/bed', 20);
        		toolTipHtml += "<div class=\"tt_hospitalbeds\">"+beds+"</div>";
                        toolTipHtml += '<div class="legend"><img width="20px" class="doc" src="static/img/bed.svg" /> Beds per 10\'000</div>';
                        toolTipHtml += '<div class="legend"><img width="20px" class="doc" src="static/img/bed-gray.svg" /> Swiss average</div>';
                        toolTipHtml += '<div class="legend"><img width="20px" class="doc" src="static/img/bed-red.svg" /> Over Swiss average</div>';
                        toolTipHtml += '</div>';
        	}
        		
            $('#tooltip').css({
                       left:  e.pageX + 20,
                       top:   e.pageY - 10
            }).html(toolTipHtml).fadeIn();
            $('.canton.selected').each(function(i) { $(this).removeClass('selected') });
            $(this).addClass('selected');

            // move element "on top of" all others within the same grouping
            this.parentNode.appendChild(this);
            clearTimeout(hideTimeout);
        });
        $(this).mouseleave(function(e) {
            if(hideTimeout) {
                clearTimeout(hideTimeout);
            }
            var that = this;
            hideTimeout = setTimeout(function() {
                // move element to the back
                that.parentNode.insertBefore(that, that.parentNode.firstChild);
                $('#tooltip').fadeOut(); 
                $(that).removeClass('selected');
            }, 100);
        });

    });

    $('#panel').mouseenter(function() {
        $("#tooltip").fadeOut();
    });

    // catch mouseenter to avoid hiding the tooltip
    $('#tooltip').mouseenter(function(e) {
        clearTimeout(hideTimeout);
    });

});

