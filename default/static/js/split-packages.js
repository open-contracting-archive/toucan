(function(){
    toucanApp.setParams(function(params){
        if ($('.packageType').val() == 'release')
            params['packageType'] = 'release';
        else if ($('.packageType').val() == 'record')
            params['packageType'] = 'record';

        if ($('#change-published-date').is(":checked"))
            params['changePublishedDate'] = 'true';
        else
            params['changePublishedDate'] = 'false';

        params['splitSize'] = $('#splitSize').val();
        return params;
    });

    toucanApp.addValidator(function(){
        if (splitSize.checkValidity() && $('#splitSize').val() != '') {
            $('.response-warning.action-failed').addClass('hidden');
            return true;
        }
        $('.response-warning.action-failed').html(splitPackages.msj_warning());
        $('.response-warning.action-failed').removeClass('hidden');
        return false;
    });
})();
