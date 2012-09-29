var query_cache = {};

var update_premiums = function() {
    var year = $('input[name="yearRadio"]:checked').val();
    var age = $('input[name="ageRadio"]:checked').val();
    var franchise = $('#deductibleLabel').text();
    
    query_premiums(year, age, franchise, handle_update);
};

var query_premiums = function(year, age, franchise, callback) {
    var url = '/query?age=' + age + '&year=' + year + '&franchise=' + franchise;

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
//    var min = 100, max = 500;
    var min = 140, max = 460, mean = 0;
    var sum=0;
    for (var i = 0; i < prices.length; i++) {
      if (prices[i].premium < min) {
          min = prices[i].premium;
      }

      if (prices[i].premium > max) {
          max = prices[i].premium;
      }
      sum += prices[i].premium;
    }
    mean = sum / prices.length;
    console.log("min "+min+" max " +max+" mean "+mean);

    var quantizeUpper = d3.scale.quantile().domain([mean, max]).range(d3.range(9));
    var quantizeLower = d3.scale.quantile().domain([mean, min]).range(d3.range(9));
    
    for (i = 0; i < prices.length; i++) {
        var id = '#canton-' + prices[i].canton.toLowerCase();
        if (prices[i].premium <= mean) {
        	var invertRange = 9- quantizeLower(prices[i].premium);
	        $(id).attr('class', 'Greens q' + invertRange + '-9');
        } else {
	        $(id).attr('class', 'Reds q' + quantizeUpper(prices[i].premium) + '-9');
        }
    }
};