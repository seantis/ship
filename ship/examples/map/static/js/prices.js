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
  data.cantons.features.forEach(function(feature) {
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
.json('cantons', 'data/switzerland.json')
.onload(function(data) {
  var outerg = vis.append('g').attr('id', 'bboxg');
  var mapProj = d3.geo.mercator();

  setNewProjectionSize = function(width, height) {
    fitProjection(mapProj, data.cantons, [[0,0],[width, height]], true);
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
      update_premiums();
    }
  });

  $('g#bboxg').data('bbox', bbox(data));

  var mapProjPath = d3.geo.path().projection(mapProj);

  outerg.selectAll("path")
    .data(data.cantons.features)
    .enter().append("path")
    .attr("id", function(d) {
          return "canton-" + d.id.toLowerCase();
      })
    .attr("class", "cantons")
    .attr("d", mapProjPath);
//    .append("svg:title")
//      .text(function(d) {
//          return d.properties.Name;
//      });

  $(document).trigger('stf-ready');

  function getSelectedDeductible() {
    return +$("#deductibleLabel").text();
  }

  function updateProjection() {
    outerg.selectAll('path')
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

  releaseMap();

});
function releaseMap() {
  update_premiums(function() {
    $('#overlay').hide();  
  });
}
