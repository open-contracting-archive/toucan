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
        $('.response-fail').removeClass('hidden');
        hideProcessingModal();
    }

    function performAction(values) {
        showProcessingModal();
        var actionParams = {};
        _paramSetters.forEach(function (f) {
            f(actionParams);
        });
        $.ajax($('#fileupload').attr('data-perform-action'), {data: actionParams})
            .done(function (data) {
                $('.response-success .f-file-size').html(utils.readableFileSize(data.size));
                $('.response-success .f-file').attr('href', data.url);
                $('.response-success .d-drive').attr('href', data.url + '?out=drive');
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
            .fail(whenAjaxReqFails)
            .always(function () {
                _done = true
            });
    }

    function upload() {
        disableUploadButton();
        disableAddFiles();
        hideMessages();

        var promises = $.map(_fileItems, function (val) {
            return val.submit();
        });
        $.when.apply($, promises)
            .done(performAction)
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

    function saveDrive() {
        showProcessingModal();
        $.ajax($('.response-success .d-drive').attr('href'), { 'dataType': 'json' })
            .done(function(data) {
                $('.google-drive-success .file-google-name').html(data.name);
                $('.google-drive-success .file-google-id').html(data.id);
                $('.google-drive-success').removeClass('hidden');
                $('.response-access-drive').addClass('hidden');
                $('.response-fail-drive').addClass('hidden');
            })
            .fail(function(jqXHR, textStatus, errorThrown){
                if (jqXHR.responseText == 'AccessDeniedError'){
                    $('.response-access-drive').removeClass('hidden');
                } else {
                    $('.response-fail-drive').removeClass('hidden');
                }
            })
            .always(function() {
                hideProcessingModal()
            });
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

    /* click save to Drive button behaviour */
    $('.d-drive').click(saveDrive);

    /* add warning before closing/navigating away from page */
    window.onload = function () {
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

