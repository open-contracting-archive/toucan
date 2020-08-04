var app = {};
(function () {

    var _fileItems = [];
    var _paramSetters = [];
    var _done = false;

    this.setParams = function (func) {
        _paramSetters.push(func);
    };

    /** functions **/

    function isUploadButtonEnabled() {
        return !$('#upload-button').is(':disabled');
    }

    function enableUploadButton() {
        $('#upload-button').removeAttr('disabled');
    }

    function disableUploadButton() {
        $('#upload-button').attr('disabled', true);
    }

    function disableAddFiles() {
        $('.fileinput-button').attr('disabled', true);
        $('.fileinput-button input:file').attr('disabled', true);
        $('.fileinput-button label').removeAttr("for");
    }

    function enableAddFiles() {
        $('.fileinput-button').removeAttr('disabled');
        $('.fileinput-button input:file').removeAttr('disabled');
    }

    function hideMessages() {
        $('.response-warning')
            .addClass('hidden');
    }

    function addFile(data) {
        data.myID = $.now();
        _fileItems.push(data);
    }

    function getNumOfFiles() {
        if (!_fileItems) {
            return 0;
        }
        return _fileItems.length;
    }

    function removeFile(id) {
        var toDelete = -1;
        $.each(_fileItems, function (i, el) {
            if (el.myId === id) {
                toDelete = -1
            }
        });
        _fileItems.splice(toDelete, 1);
        if (_fileItems.length === 0) {
            disableUploadButton();
        }
    }

    function clearFiles(){
        _fileItems = [];
    }

    function showProcessingModal() {
        $('#processing-modal').modal('show');
    }

    function hideProcessingModal() {
        $('#processing-modal').modal('hide');
    }

    /** listeners **/

    function whenUploadAdded(e, data) {
        addFile(data);
        if (!isUploadButtonEnabled()) {
            enableUploadButton();
        }
        if (getNumOfFiles() === 1) {
            $('.file-selector-empty').addClass('hidden');
            $('.actions').removeClass('hidden');
            $('.files').removeClass('hidden');
            $('.drop-area')
                .removeClass('empty')
                .addClass('row');
        }
    }

    function whenUploadFailed(e, data) {
        if (data.errorThrown === 'abort') {
            // not really an error, but file has been removed by user before attempting to upload
            removeFile(data.myId);
        } else if (data.textStatus === 'error') {
            // error from the server
            data.files.forEach(function (o, i) {
                o.errorMessage = data.jqXHR.responseText;
            });
            removeFile(data.myId);
        }
    }

    function whenUploadFinishes() {
        // if there is at least one valid upload, enable the button
        if (!isUploadButtonEnabled() && $('.template-download .text-success').length) {
            enableUploadButton()
        }
    }

    function whenAjaxReqFails(jqXHR) {
        if (jqXHR.status === 401)
            $('.response-warning.file-process-failed').removeClass('hidden');
        else
            $('.response-fail').removeClass('hidden');
        hideProcessingModal();
    }

    function performAction(url) {
        showProcessingModal();
        var actionParams = {};
        _paramSetters.forEach(function (f) {
            f(actionParams);
        });
        $.ajax(url, {data: actionParams})
            .done(function (data) {
                $('.response-success .file-size').html(utils.readableFileSize(data.size));
                $('.response-success .download').attr('href', data.url);
                $('.response-success').removeClass('hidden');
                if (data.hasOwnProperty('warnings') && data.warnings.length > 0) {
                    $('.response-warning.action-failed').removeClass('hidden');
                    $('.response-warning.action-failed ul').html($.map(data.warnings, function (o) {
                        return '<li>' + o + '</li>'
                    }).join('\n'))
                }
                hideProcessingModal();
                $('.actions').hide();
                $('#fileupload').fileupload('destroy');
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                whenAjaxReqFails(jqXHR);
            })
            .always(function () {
                _done = true
            });
    }

    function upload() {
        disableUploadButton();
        disableAddFiles();
        hideMessages();

        /* check if results were sent and performAction directly, otherwise files are uploaded first */
        if ($('#upload-button').hasClass('sendResult') == true) {
            params = '?sendResult=true&type=' + JSON.parse($('#fileupload').attr('data-form-data')).type
            performAction($('#fileupload').attr('data-perform-action') + params);
        } else {
            var promises = $.map(_fileItems, function (val) {
                return val.submit();
            });
            $.when.apply($, promises)
                .done(function () {
                    performAction($('#fileupload').attr('data-perform-action'));
                })
                .fail(function () {
                    enableAddFiles();
                    $('.response-warning.file-process-failed').removeClass('hidden');
                })
                .always(function () {
                    clearFiles(); // so they will not be uploaded again
                    var failures = $.grep(promises, function (promise) {
                        return promise.state() === 'rejected';
                    });
                    if (failures.length){
                        // validations failed for some files, show message
                        $('.response-warning.file-process-failed').removeClass('hidden');
                    }
                })
            ;
        }
    }

    function upload_url() {
        hideMessages();
        $('#processing-modal .total-files')
            .html($('.input-url-container .form-group .input-group .form-control').length);
        $('#processing-modal .downloading-status').removeClass('hidden');
        showProcessingModal();
        $('.response-fail').addClass('hidden');
        $('.form-group').removeClass('has-error');
        $('.help-block').remove();

        $.ajax('/upload-url/', {'dataType': 'json', type: 'POST',
        'data': $('.input-url-container .form-group .input-group .form-control').serialize() +
        '&type=' + JSON.parse($('#fileupload').attr('data-form-data')).type,
        headers: {'X-CSRFToken': JSON.parse($('#fileupload').attr('data-form-data')).csrfmiddlewaretoken}})
            .done(function () {
                performAction($('#url-button').attr('data-perform-action'));
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                $.each(JSON.parse(jqXHR.responseText), function(i, item) {
                    slt = "#" + item.id;
                    msg = item.message;
                    $(slt).addClass('has-error');
                    $(slt).append('<div class="help-block">' + msg + '</div>');
                });
                whenAjaxReqFails(jqXHR);
                $('#processing-modal .downloading-status').addClass('hidden');
            })
            .always(function () {
                clearInterval(pollInterval);
            })
            pollInterval = setInterval(function () {
                $.ajax('/upload-url/status/', {'dataType': 'json', type: 'GET'})
                    .done(function (data) {
                        $('#processing-modal .current-files').html(data);
                    })
                ;
            }, 500);
        ;
    }

    function send_to() {
        window.location.href = $('.to-function').val() + '?sendResult=true';
    }

    /** plugin initialization & listeners**/

    var fileupload = $('#fileupload')
        .fileupload()
        .bind('fileuploadadded', whenUploadAdded)
        .bind('fileuploadfail', whenUploadFailed)
        .bind('fileuploadfinished', whenUploadFinishes)
    ;

    /** upload call binding **/
    $("#upload-button").click(upload);

    /* click upload url button behaviour */
    $("#url-button").click(upload_url);

    /* click send button behaviour */
    $('.send-button').click(send_to);

    /* add warning before closing/navigating away from page */
    window.onload = function () {
        /* clear URL input text */
        $('#input_url_0 input').val('');

        /* check if results were sent to this page */
        if (window.location.search == '?sendResult=true') {
            showProcessingModal();
            disableAddFiles();
            enableUploadButton();
            $('.drop-area').removeClass('empty');
            $('.drop-area').addClass('single');
            $('.drop-area .file-selector-empty').addClass('hidden');
            $('.drop-area .drop-area-received-msg').removeClass('hidden');
            $('.drop-area .drop-area-received-msg .file-result').html('result.zip');
            $('.actions').removeClass('hidden');
            $('#upload-button').addClass('sendResult');
            hideProcessingModal();
        }

        /* add warning before closing/navigating away from page */
        window.addEventListener("beforeunload", function (e) {
            if (_fileItems.length === 0 || _done) {
                return undefined;
            }
            var confirmationMessage = 'It looks like you have been editing something. '
                + 'If you leave before saving, your changes will be lost.';

            (e || window.event).returnValue = confirmationMessage; //Gecko + IE
            return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
        });
    };

}).apply(app);

