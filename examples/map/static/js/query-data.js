var query_cache = {};

var transforms = ['-webkit-transform', '-moz-transform', '-ms-transform', '-o-transform']

var logo = $('#title img');
var rotation_interval, rotation = 0;
var stop_rotation = false;

var rotate_stop = function() {
    stop_rotation = true;
}

var rotate_logo = function() {

    if (rotation_interval) {
        return;
    }

    var rotate = function() {
        rotation += 10;
        for (var i=0; i < transforms.length; i++) {
            logo.css(transforms[i], "rotate(" + rotation + "deg)");
        }

        if (rotation == 350) {
            rotation = -10;
            if (stop_rotation) {
                clearInterval(rotation_interval);
                rotation_interval = 0;

                for (i=0; i < transforms.length; i++) {
                    logo.css(transforms[i], "");
                }
            }
        }
    }
    
    rotation_interval = setInterval(rotate, 10);
}

rotate_logo();

var update_premiums = function(callback) {
    rotate_logo();

    var year = $('input[name="yearRadio"]:checked').val();
    var age = $('input[name="ageRadio"]:checked').val();
    var franchise = $('#deductibleLabel').text();
    var accident = $('input[name="accidentRadio"]:checked').val();
    var insurer = $('select[name="insurerSelect"] option:selected').val();
    var type = $('input[name="typeRadio"]:checked').val();
    
    query_premiums(year, age, franchise, accident, type, insurer, function(data) {
        handle_update(data);
        if (callback) callback();
        rotate_stop();
    });
};

var query_premiums = function(year, age, franchise, accident, type, insurer, callback) {
    var url = '/query?age=' + age;
    url += '&year=' + year;
    url += '&franchise=' + franchise;
    url += '&accident=' + accident;
    url += '&type=' + type;
    url += '&insurer=' + insurer;

    if (url in query_cache) {
        callback(query_cache[url]);
        return;
    };

    var update_cache = function(data) {
        query_cache[url] = data;
        callback(data);
    };

    jQuery.getJSON(url, update_cache);
};

var handle_update = function(prices) {
    var min = 140, max = 460, mean = 300;
    var sum=0;
    for (var i = 0; i < prices.length; i++) {
      if (prices[i].premium < min) {
// fix in scale          min = prices[i].premium;
      }

      if (prices[i].premium > max) {
// fix in scale          max = prices[i].premium;
      }
      sum += prices[i].premium;
    }
    
//    mean = sum / prices.length;

    var quantizeUpper = d3.scale.quantile().domain([mean, max]).range(d3.range(9));
    var quantizeLower = d3.scale.quantile().domain([mean, min]).range(d3.range(9));
    
    for (i = 0; i < prices.length; i++) {
        var id = '#canton-' + prices[i].canton.toLowerCase();
        if (prices[i].premium <= mean) {
        	var invertRange = 9- quantizeLower(prices[i].premium);
	        $(id).attr('class', 'canton Blues q' + invertRange + '-9');
        } else {
	        $(id).attr('class', 'canton Reds q' + quantizeUpper(prices[i].premium) + '-9');
        }
        $(id).data("price",prices[i].premium);
    }
};
