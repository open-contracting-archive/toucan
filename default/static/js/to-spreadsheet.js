(function(){
    var fileUploadObj = $('#fileupload').fileupload(),
        dropArea = $('.drop-area'),
        uploadButton = $('#upload-button'),
        processingModal = $('#processing-modal'),
        successBox = $('.response-success'),
        errorBox = $('.response-fail'),
        dropAreaFileLink = $('.drop-area-msg label'),
        urlInput = $('#input_url_0 input'),
        urlHelpBlock = $('.input-url-container .help-block'),
        tabPanels = $('.schema-nav .btn')
    ;

    var selectedFile;

    function enableUploadButton() {
        uploadButton.removeAttr('disabled');
    }

    function disableUploadButton() {
        uploadButton.attr('disabled', 'disabled');
    }

    function transformInServer() {
        /* call the server to transform the files */
        // mask the page
        processingModal.modal('show');
        $.ajax('/to-spreadsheet/go/', {
             'dataType': 'json',
             'data': $('#unflatten-options').serialize(),
             'method': 'POST'
            })
             .done(showLinksToResults)
             .fail(showActionErrorMessage)
             .always(function () {
                 // hide the modal after the ajax call
                processingModal.modal('hide');
             })
        ;
    }

    function showLinksToResults(data) {
        /* show links to results (and file sizes) */
        if (data.xlsx) {
            successBox.find('.xlsx').removeClass('hidden');
            successBox.find('.download-xlsx').attr('href', data.xlsx.url);
            successBox.find('.file-size-xlsx').html(utils.readableFileSize(data.xlsx.size));
        }
        if (data.csv) {
            successBox.find('.csv').removeClass('hidden');
            successBox.find('.download-csv').attr('href', data.csv.url);
            successBox.find('.file-size-csv').html(utils.readableFileSize(data.csv.size));
        }
        successBox.removeClass('hidden');
    }

    function showActionErrorMessage(jqXHR, textStatus, errorThrown) {
        /* show error messages received from the server, after calling the unflatten function */
        if ('responseJSON' in jqXHR && 'form_errors' in jqXHR.responseJSON) {
            toucanApp.unflattenOptions.showErrorsFromServer(jqXHR.responseJSON.form_errors);
            errorBox.removeClass('hidden')
                .children('.unflatten-invalid-options')
                .removeClass('hidden');
            $('#unflatten-options-modal').modal('show');

        }
        else {
            // shows a default error message written in the template
            errorBox.removeClass('hidden')
                .children('.default-message')
                .removeClass('hidden');
        }
        enableFileInput();
    }

    function showFileErrorMsg(jqXHR, textStatus, errorThrown) {
        // shows an error message received from the server
        errorBox.removeClass('hidden')
            .children('.unflatten-invalid-options')
            .removeClass('hidden')
            .children('.msg')
            .html(jqXHR.responseText || textStatus)
        ;
    }

    function clear() {
        /* removes all messages in screen */
        errorBox
            .addClass('hidden')
            .children()
            .addClass('hidden')
        ;
        successBox.find('.xlsx').addClass('hidden');
        successBox.find('.csv').addClass('hidden');
        successBox.addClass('hidden');
        urlHelpBlock.empty();

        toucanApp.unflattenOptions.clear();
    }

    function enableFileInput(){
        fileUploadObj.fileupload('enable');
        if (dropAreaFileLink.hasClass('hidden')){
            dropAreaFileLink.removeClass('hidden')
        }
    }

    function disableFileInput(){
        fileUploadObj.fileupload('disable');
        dropAreaFileLink.addClass('hidden');
    }

    function getActiveTab() {
        var selection = $('.panel-collapse.collapse.in');
        if (selection.hasClass('toucan-nav-input')){
            return 'url';
        }
        else{
            return 'file';
        }
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

    function showUrlErrors(jqXHR) {
        $.each(JSON.parse(jqXHR.responseText), function(i, item) {
            slt = "#" + item.id;
            msg = item.message;
            $(slt).addClass('has-error');
            urlHelpBlock.html(msg);
        });
        $('.response-fail').removeClass('hidden');
        $('#processing-modal').modal('hide');
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
        }).done(transformInServer)
        .fail(showUrlErrors)
    }

    function send() {
        if (getActiveTab() === 'url') {
            sendUrlAndSubmit();
        }
        else {
            uploadAndSubmitFile();
        }
    }

    function uploadButtonStatus(event) {
        if ($(event.target).children('input').hasClass('toucan-nav-input')){
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
        selectedFile = data;
    });

    /* "Start" button click listener */
    uploadButton.click(send);

    tabPanels.click(uploadButtonStatus);

    /* prevent browser's default action when dragging and dropping files */
    $(document).bind('drop dragover', function (e) {
        e.preventDefault();
    });

    $(document).ready(function(){
        // clear the input's value
        urlInput.val('');
        disableUploadButton();
    });
})();