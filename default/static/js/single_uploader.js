var toucanApp = toucanApp || {};
(function(){
    var fileUploadObj = $('#fileupload').fileupload(),
        dropArea = $('.drop-area'),
        uploadButton = $('#upload-button'),
        sendButton = $('.send-button'),
        processingModal = $('#processing-modal'),
        successBox = $('.response-success'),
        restartButton = $('.response-restart'),
        errorBox = $('.response-fail'),
        defaultErrorBox = $('.response-fail.default-error'),
        fileWarning = $('.text-danger'),
        fileErrorBox = $('.response-warning.file-process-failed'),
        formGroup = $('.form-group'),
        dropAreaFileLink = $('.drop-area-msg label'),
        urlInput = $('#input_url_0 input'),
        actions = $('.actions'),
        actionsParams = $('.action-extra-params'),
        urlHelpBlock = $('.input-url-container .help-block'),
        tabPanels = $('.nav.nav-tabs'),
        tabContent = $('.tab-content')
    ;

    var selectedFile;
    var _paramSetters = [];

    this.setParams = function (func) {
        _paramSetters.push(func);
    };

    /** functions **/

    function enableUploadButton() {
        uploadButton.removeAttr('disabled');
    }

    function disableUploadButton() {
        uploadButton.attr('disabled', 'disabled');
    }

    function enableFileInput() {
        fileUploadObj.fileupload('enable');
        if (dropAreaFileLink.hasClass('hidden')){
            dropAreaFileLink.removeClass('hidden')
        }
    }

    function disableFileInput() {
        fileUploadObj.fileupload('disable');
        dropAreaFileLink.addClass('hidden');
    }

    function enableProcessRestart(status) {
        tabPanels.addClass('hidden');
        tabContent.addClass('hidden');
        actionsParams.addClass('hidden');
        restartButton.removeClass('hidden');
    }

    function showLinksToResults(data) {
        /* show links to results (and file sizes) */
        if (data.xlsx) {
            successBox.find('li.xlsx').removeClass('hidden');
            successBox.find('.download-xlsx').attr('href', data.xlsx.url);
            successBox.find('.file-size-xlsx').html(utils.readableFileSize(data.xlsx.size));
            successBox.find('.save-drive-link.xlsx').attr('data-url', data.xlsx.driveUrl);
        }
        if (data.csv) {
            successBox.find('li.csv').removeClass('hidden');
            successBox.find('.download-csv').attr('href', data.csv.url);
            successBox.find('.file-size-csv').html(utils.readableFileSize(data.csv.size));
            successBox.find('.save-drive-link.csv').attr('data-url', data.csv.driveUrl);
        }
        // to-json returns only one json file
        if (data.url) {
            successBox.find('.file.download-link').attr('href', data.url);
            successBox.find('.file.size').html(utils.readableFileSize(data.size));
            successBox.find('.file.save-drive-link').attr('data-url', data.driveUrl);
        }
        successBox.removeClass('hidden');
    }

    function showActionErrorMessage(jqXHR, textStatus, errorThrown) {
        // show error messages received from the server, after calling the unflatten function
        if ('responseJSON' in jqXHR && 'form_errors' in jqXHR.responseJSON) {
            toucanApp.unflattenOptions.showErrorsFromServer(jqXHR.responseJSON.form_errors);
            defaultErrorBox.removeClass('hidden')
                .children('.unflatten-invalid-options')
                .removeClass('hidden');
            $('#unflatten-options-modal').modal('show');
        } else {
            // shows a default error message written in the template
            errorBox.removeClass('hidden')
                .children('.default-message')
                .removeClass('hidden');
        }
        enableFileInput();
    }

    function showFileErrorMsg(jqXHR, textStatus, errorThrown) {
        // shows the 401 error for invalid type
        if (jqXHR.status === 401) {
            fileErrorBox.removeClass('hidden');
            fileWarning.html(jqXHR.responseText || textStatus);
        } else {
            if (jqXHR || textStatus) {
                // shows an error message received from the server
                errorBox.removeClass('hidden')
                    .children('.unflatten-invalid-options')
                    .removeClass('hidden')
                    .children('.msg')
                    .html(jqXHR.responseText || textStatus)
                ;
            } else {
                defaultErrorBox.removeClass('hidden');
            }
        }
    }

    function showUrlErrors(jqXHR) {
        $.each(JSON.parse(jqXHR.responseText), function(i, item) {
            slt = "#" + item.id;
            msg = item.message;
            $(slt).addClass('has-error');
            urlHelpBlock.html(msg);
        });
        fileErrorBox.removeClass('hidden');
        processingModal.modal('hide');
    }

    function clear() {
        /* removes all messages in screen */
        errorBox
            .addClass('hidden')
            .children()
            .addClass('hidden')
        ;
        fileErrorBox.addClass('hidden')
            .children()
            .addClass('hidden')
        ;
        successBox.find('li.xlsx').addClass('hidden');
        successBox.find('.xlsx .save-drive-link').removeClass('hidden');
        successBox.find('.xlsx .open-drive-link').addClass('hidden');
        successBox.find('li.csv').addClass('hidden');
        successBox.find('.csv .save-drive-link').removeClass('hidden');
        successBox.find('.csv .open-drive-link').addClass('hidden');
        successBox.addClass('hidden');
        formGroup.removeClass('has-error');
        urlHelpBlock.empty();

        if (toucanApp.unflattenOptions) {
            toucanApp.unflattenOptions.clear();
        }
    }

    function checkSendResult() {
        return uploadButton.hasClass('sendResult');
    }

    function getActiveTab() {
        var selection = $('.nav.nav-tabs .active a');
        if (selection.attr('href') === '#urls'){
            return 'url';
        }
        else{
            return 'file';
        }
    }

    function uploadButtonStatus(event) {
        if ($(event.target).attr('href') === '#urls'){
            enableUploadButton();
        }
        else {
            if (!selectedFile) {
                disableUploadButton();
            } else {
                enableUploadButton();
            }
        }
    }

    /** listeners **/

    function transformInServer(send) {
        /* call the server to transform the files */
        // mask the page
        processingModal.modal('show');
        url = $('#upload-button').attr('data-perform-action');
        // set parameters
        if (url === '/to-spreadsheet/go/') {
             data = $('#unflatten-options').serialize();
             method = 'POST';
        } else if (url === '/to-json/go/') {
            var data = {};
            _paramSetters.forEach(function (f) {
                f(data);
            });
            method = 'GET';
        }
        // check if results were sent
        if (send === 'sendResult') {
            data = data + '&sendResult=true&type=' + JSON.parse($('#fileupload').attr('data-form-data')).type;
        }

        $.ajax(url, {
            'dataType': 'json',
            'data': data,
            'method': method
        })
            .done(showLinksToResults)
            .done(enableProcessRestart)
            .fail(function(jqXHR, textStatus, errorThrown) {
                showActionErrorMessage(jqXHR, textStatus, errorThrown);
                // if result were sent and there was an error, show restart button and file error message
                if (send === 'sendResult'){
                    showFileErrorMsg(jqXHR, textStatus, errorThrown);
                    enableProcessRestart();
                }
            })
            .always(function () {
                // hide the modal after the ajax call
                processingModal.modal('hide');
            })
        ;
    }

    function uploadAndSubmitFile() {
        // we don't want to add any more files
        disableFileInput();
        // clear error messages
        clear();

        selectedFile.submit() // send the file
            .done(transformInServer)
            .fail(showFileErrorMsg)
            // enable the file input again if there is an error!
            .fail(enableFileInput)
        ;
    }

    function sendUrlAndSubmit() {
        var data = Object.assign( {},
            { 'input_url_0': $('#input_url_0 input').val() },
            fileUploadObj.fileupload('option', 'formData')
        );
        clear();

        $.ajax('/upload-url/', {
            type: 'POST',
            data: data
        })
            .done(transformInServer)
            .fail(showUrlErrors)
        ;
    }

    function send_to() {
        window.location.href = $('.to-function').val() + '?sendResult=true';
    }

    function send() {
        if (checkSendResult()) {
            transformInServer('sendResult');
        }
        else {
            if (getActiveTab() === 'url') {
                sendUrlAndSubmit();
            }
            else {
                uploadAndSubmitFile();
            }
        }
    }

    /** plugin initialization & listeners**/

    fileUploadObj.bind('fileuploadadd', function (e, data) {
        /* listen when a file is selected or dropped in the designated area */
        dropArea.removeClass('empty');
        // hide default message
        dropArea.children('.drop-area-msg-empty').addClass('hidden');
        // fill area with file's name and size
        $('.drop-area .file-selected')
            .html(data.files[0].name
                + '<small>('
                + utils.readableFileSize(data.files[0].size)
                + ')</small>'
            )
        ;
        dropArea.children('.drop-area-msg').removeClass('hidden');
        // enable "Start" button
        enableUploadButton();
        // select only one file to upload
        selectedFile = data;
    });

    /* upload call binding */
    uploadButton.click(send);

    /* click send button behaviour */
    sendButton.click(send_to);

    /* change tab */
    tabPanels.click(uploadButtonStatus);

    /* prevent browser's default action when dragging and dropping files */
    $(document).bind('drop dragover', function (e) {
        e.preventDefault();
    });

    $(document).ready(function(){
        // clear the input's value
        urlInput.val('');
        disableUploadButton();

        // check if results were sent to this page
        if (window.location.search == '?sendResult=true') {
            processingModal.modal('show');
            $.ajax('/send-result/validate/', {'dataType': 'json', type: 'GET'})
                .done(function (data) {
                    dropArea.removeClass('empty');
                    dropArea.children('.drop-area-msg-empty').addClass('hidden');
                    dropArea.children('.drop-area-received-msg').removeClass('hidden');
                    $('.drop-area-received-msg .file-result').html(data);
                    actions.removeClass('hidden');
                    uploadButton.addClass('sendResult');
                    enableUploadButton();
                })
                .fail(function () {
                    defaultErrorBox.removeClass('hidden');
                })
                .always(function () {
                    processingModal.modal('hide');
                });
        }
    });

}).apply(toucanApp);