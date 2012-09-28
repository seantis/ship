var query_cache = {};

var update_premiums = function() {
    var year = $('input[name="yearRadio"]:checked').val();
    var age = $('input[name="ageRadio"]:checked').val();
    var franchise = $('#deductibleLabel').text();
    var accident = $('input[name="accidentRadio"]:checked').val();
    
    query_premiums(year, age, franchise, accident, handle_update);
};

var query_premiums = function(year, age, franchise, accident, callback) {
    var url = '/query?age=' + age;
    url += '&year=' + year;
    url += '&franchise=' + franchise;
    url += '&accident=' + accident;

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
    var min = 10000000, max = 0;
    for (var i = 0; i < prices.length; i++) {
        if (prices[i].premium < min) {
            min = prices[i].premium;
        }

        if (prices[i].premium > max) {
            max = prices[i].premium;
        }
    }

    var quantize = d3.scale.quantile().domain([min, max]).range(d3.range(9));
    for (i = 0; i < prices.length; i++) {
        var id = '#canton-' + prices[i].canton.toLowerCase();
        $(id).attr('class', 'canton q' + quantize(prices[i].premium) + '-9');
    }
};