var setNewProjectionSize, updateArrivals, arrivalsAnimPlaying;
var blue = "#0571B0";
var red = "#CA0020";

function domainForColors(colors, min, max) {
  var d, domain, i, _ref;
  domain = [min];
  d = (max - min) / (colors.length - 1);
  for (i = 1, _ref = colors.length - 1; 1 <= _ref ? i <= _ref : i >= _ref; 1 <= _ref ? i++ : i--) {
    domain.push(min + d * i);
  }
  return domain;
}

function bbox(data) {
  var left = Infinity,
  bottom = -Infinity,
  right = -Infinity,
  top = Infinity;
  data.boundary.features.forEach(function(feature) {
    d3.geo.bounds(feature).forEach(function(coords) {
      var x = coords[0],
      y = coords[1];
      if (x < left) left = x;
      if (x > right) right = x;
      if (y > bottom) bottom = y;
      if (y < top) top = y;
    });
  });
  //console.log(left, right, bottom, top);
  return [[left,top], [right,bottom]];
}

d3.loadData()
.json('boundary', 'data/switzerland_boundaries.json')
.onload(function(data) {


  var outerg = vis.append('g').attr('id', 'bboxg');
  var cantons = vis.append('svg:g').attr('id', 'cantons');
  var mapProj = d3.geo.mercator();

  setNewProjectionSize = function(width, height) {
    fitProjection(mapProj, data.boundary, [[0,0],[width, height]], true);
    if(updateProjection) updateProjection();
  }
  setNewProjectionSize(width, height);

  var speedColorScale = d3.scale.linear()
  .domain([0, d3.max(d3.values(data.speeds))])
  .range([blue, red]);

  var deductibleOptions = [300, 500, 1000, 1500, 2000, 2500];
  $("#deductible_slider")
  .slider({
    orientation: 'horizontal',
    min: 0,
    max: 5,
    value: 1,
    step: 1,
    slide: function(event, ui) {
      $('#deductibleLabel').text(deductibleOptions[ui.value]);
    },
    change: function(event, ui) {
      update_premiums();
    },
  });

  $('g#bboxg').data('bbox', bbox(data));
  $(document).trigger('stf-ready');

  var mapProjPath = d3.geo.path().projection(mapProj);

  outerg.selectAll("path")
  .data(data.boundary.features)
  .enter().append("path")
  .attr("class", "boundary")
  .attr("d", mapProjPath)
  .attr("fill", "rgb(230,230,230)")
  .attr("stroke", "rgb(200,200,200)")
  .attr("stroke-width", "0.5");

var path = d3.geo.path()
    .projection(d3.geo.albersUsa()
    .scale(1400)
    .translate([680, 360]));

d3.json("query?age=26&year=2013&franchise=300", function(data) {
    var quantize = d3.scale.quantile().domain([100, 500]).range(d3.range(9));

    d3.json("data/switzerland.json", function(json) {
        cantons.selectAll("path")
            .data(json.features)
            .enter().append("svg:path")
            .attr("class", function(d) {
                for (i = 0;i < data.length; i++) {
                    if (data[i].canton.toLowerCase() == d.id.toLowerCase()) {
                        return "boundary q" + quantize(data[i].premium) + "-9";
                    }
                }
            })
            .attr("d", path);
    });
});


  function getTrainCount(edgeid, hour) {
    var hours = data.trains[edgeid];
    if (hours !== undefined  &&  hours[hour] !== undefined) {
      return hours[hour];
    }
    return 0;
  }

  function trainCountToText(count) {
    if (count === 0) return 'No trains';
    if (count === 1) return 'One train';
    return count + ' trains';
  }

  function getStationTrainCount(stationid, hour) {
    var hours = data.stationTrainsByHour[stationid];
    if (hours !== undefined  &&  hours[hour] !== undefined) {
      return hours[hour];
    }
    return 0;
  }

  function getSelectedDeductible() {
    return +$("#deductibleLabel").text();
  }

  $('#showStationsChk').click(function() { updatePrices(true); });
  $('#showRailwaysChk').click(function() { updatePrices(true); });
  $('#startArrivalsAnim').click(startArrivalsAnim);
  $('#stopArrivalsAnim').click(stopArrivalsAnim);

  function startArrivalsAnim() {
    arrivalsAnimPlaying = true;
    updateArrivals(60 * 10);
  }

  function stopArrivalsAnim() {
    arrivalsAnimPlaying = false;
    updatePrices();
  }

  function updateProjection() {
    outerg.selectAll('path.segments')
    .attr('d', mapProjPath);

    outerg.selectAll('circle.stations')
    .attr('cx', function(d) { return mapProj(d.geometry.coordinates)[0]; })
    .attr('cy', function(d) { return mapProj(d.geometry.coordinates)[1]; })
    ;
    outerg.selectAll("path.boundary")
    .attr("d", mapProjPath);
  }

  function updatePrices(force, noAnim) {

    if (force) noAnim = true;
    var animDuration = 1000;

    var deductible = getSelectedDeductible();
    $('#deductibleLabel').html(getSelectedDeductible());

    var showRailways = $('#showRailwaysChk').is(':checked');
    var showStations = $('#showStationsChk').is(':checked');

    var segmentsGroup = outerg.selectAll('g.segments');
    if (force || showRailways) {

      outerg.selectAll('path.segments')
      .transition()
      .duration(noAnim ? 0 : animDuration)
      .attr('stroke-width', function(d, i) {
        if (showRailways) {
          var edgeid = +d.properties.edge_id;
          return 0.1 +
          (getTrainCount(edgeid, hour) + getTrainCount(-edgeid, hour))/3;
        } else {
          return 1.2;
        } 
      })
      .attr('stroke', function(d, i) {
        var edgeid = +d.properties.edge_id;
        var speed = data.speeds[edgeid];

        return speedColorScale(speed > 0 ? speed : 0);
      });
    }
    
    var stationsGroup = outerg.selectAll('g.stations');
    if (!showStations) {
      outerg.selectAll('circle.stations')
      .attr('visibility','hidden')
      /*
      .attr('fill','white')
      .attr('stroke','black')
      .attr('r', 2)
      */
      ;
    }

    if (force || showStations) {
      if (!showRailways) {
        outerg.selectAll('circle.stations')
        .attr('visibility','visible')
        .attr('stroke','#ccc')
        .attr('fill',red)
        .transition()
        .duration(noAnim ? 0 : animDuration)
        .attr('r', function(d, i) {
          var station_id = +d.properties.station_id;
          return 0.1 + Math.sqrt(getStationTrainCount(station_id, getSelectedDeductible()));
        });
      }
    }
  }

  updateProjection();
  updatePrices(true);

  $('svg circle.stations').tipsy({
    gravity: 's',
    html: true,
    delayIn: 300,
    delayOut: 100,
    title: function() {
      var d = this.__data__.properties;
      return  '<b>'+d.name + '</b><br>' + 
      trainCountToText(getStationTrainCount(d.station_id, getSelectedDeductible())) +
      ' stop here<br> between ' + getSelectedDeductible();
    }
  });

  $('svg path.segments').tipsy({
    gravity: 's',
    html: true,
    delayIn: 300,
    delayOut: 100,
    title: function() {
      var d = this.__data__.properties;
      var edgeid = +d.edge_id;
      return  '<b>'+trainCountToText(getTrainCount(edgeid, getSelectedDeductible())) + '</b> pass here<br> ' +
      ' between ' +getSelectedDeductible()
      +'<br>'+
      ' at avg speed of <b>' + data.speeds[edgeid] + ' km/h</b>' 
      ;
    }
  });

  releaseMap();

  /*
  d3.json('data/station_arrivals.json', function(arrivalsData) {

    updateArrivals = function (minutes) {
      if (!arrivalsAnimPlaying) return;

      $('#hourLabel').html( 
        Math.floor((minutes  / 60) % 24) + ':' +  (minutes % 60)
      );
      var minutesInDay = 24 * 60;

      outerg.selectAll('circle.stations')
      .transition()
      .duration(1500)
      .attr('fill', 'green')
      .attr('r', function(d, i) {
        var station_id = d.properties.station_id;
        var data = arrivalsData[minutes * 60];
        if (data !== undefined) {
          if (data[station_id] !== undefined) {
            return Math.sqrt(data[station_id] * 50);
          }
        }
        return 0;
      });
      if (minutes < minutesInDay) {
        setTimeout("updateArrivals("+(minutes+1)+")", 1000);
      }

    }

  });
  */

});
function releaseMap() {
  $('#overlay').hide();
}