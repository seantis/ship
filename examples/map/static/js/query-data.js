var update_premiums = function() {
    var year = $('input[name="yearRadio"]:checked').val();
    var age = $('input[name="ageRadio"]:checked').val();
    var franchise = $('#deductibleLabel').text();
    
    query_premiums(year, age, franchise, function(data) {
        console.log(data);
    });
};

var query_premiums = function(year, age, franchise, callback) {
    var url = '/query?age=' + age + '&year=' + year + '&franchise=' + franchise;
    jQuery.getJSON(url, callback);
};