(function(){
    var app = this;
    var _googleApiURL = 'https://accounts.google.com/o/oauth2/v2/auth';
    var _myBaseUrl = window.location.href.match('(https?:\/\/[^/]*\/)')[0];
    var _googleApiParams = {
        redirect_uri: _myBaseUrl + 'googleapi-auth-response',
        access_type: 'offline',
        response_type: 'code',
        scope: 'https://www.googleapis.com/auth/drive.file'
    };

    this.setGoogleApiClientID = function(id) {
      _googleApiParams['client_id'] = id;
    };

    function doPoll(successCallback, errorCallback){
        $.get(_myBaseUrl + 'google-drive-save-status')
            .done(function (data) {
                if (data.status === 'waiting'){
                    doPoll(successCallback, errorCallback);
                }
                else if (data.status === 'success') {
                    successCallback(data);
                }
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                errorCallback(jqXHR, textStatus, errorThrown);
            });
    }

    function saveToDrive(event) {

        var successCallback = function(data, classSelector){
            var linkSelector = '.response-success .open-drive-link';
            var saveSelector = '.response-success .file.save-drive-link';
            if (classSelector){
                linkSelector = linkSelector + '.' + classSelector;
                saveSelector = saveSelector + '.' + classSelector;
            }

            $(linkSelector + ' a').attr('href', data.url);
            $(linkSelector).removeClass('hidden');
            $(saveSelector).addClass('hidden');
            $('.response-fail-empty').addClass('hidden');
            app.hideProcessingModal('.auth-message');
        };

        var failedCallback = function(jqXHR, textStatus){
            var jsonResponse = $.parseJSON(jqXHR.responseText);
            $('.response-fail-empty .message-content').html(
                ( jsonResponse.message || jqXHR.responseText || textStatus )
            );
            $('.response-fail-empty').removeClass('hidden');
            app.hideProcessingModal('.auth-message');
        };

        var url = $(event.target).attr('data-url');
        var classSelector = $(event.target).attr('data-class');

        app.showProcessingModal('.auth-message');
        $.ajax(url)
            .done(function(response)
            {
                // there are credentials already saved for this user, so the response contains the details of the uploaded file
                if (response.authenticated && response.authenticated === true)
                {
                    successCallback(response, classSelector);
                }
                else
                {
                    // open the authentication page in a new window
                    window.open(_googleApiURL + '?' + $.param(_googleApiParams), '_blank');
                    // poll and wait for a response
                    doPoll(successCallback, failedCallback)
                }
            })
            .fail(failedCallback);
    }
    /* click save to Drive button behaviour */
    $('.file.save-drive-link').click(saveToDrive);
}).apply(toucanApp);