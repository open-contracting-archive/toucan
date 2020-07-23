(function(){
    app.setParams(function(params){
        if ($('#pretty-json').is(":checked"))
            params['pretty-json'] = true;
        else
            params['pretty-json'] = false;
        params['encoding'] = $('#encoding').val();
        return params;
    });
})();
