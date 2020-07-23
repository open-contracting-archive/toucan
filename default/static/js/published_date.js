(function(){
    app.setParams(function(params){
        params['publishedDate'] = $('#publishedDate').val()
        return params;
    });
    $('#publishedDate').val((new Date()).toISOString());
    var options =  {
        translation: {
            P: {pattern: '[Z+-]'},
            S: {pattern: '[+-]'}
        },
        onKeyPress: function(cep, e, field, options) {
          var masks = ['0000-00-00T00:00:00P', '0000-00-00T00:00:00S00:00'];
          var mask = (cep.length>19) && (cep.charAt(19) == '+' || cep.charAt(19) == '-') ? masks[1] : masks[0];
          $('#publishedDate').mask(mask, options);
        }
    };
    $('#publishedDate').mask('0000-00-00T00:00:00P', options);
})();
