(function(){
    var fileUploadObj = $('#fileupload').fileupload(),
        dropArea = $('.drop-area'),
        uploadButton = $('#upload-button'),
        processingModal = $('#processing-modal'),
        successBox = $('.response-success'),
        errorBox = $('.response-fail');

    var selectedFile;

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
        }
        else {
            // shows a default error message written in the template
            errorBox.removeClass('hidden')
                .children('.default-message')
                .removeClass('hidden');
        }
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

        toucanApp.unflattenOptions.clear();
    }

    fileUploadObj.bind('fileuploadadd', function (e, data) {
        /* listen when a file is selected or dropped in the designated area */
        dropArea.removeClass('empty');
        // hide default message
        dropArea.children('.msg-empty').addClass('hidden');
        // fill area with file's name and size
        dropArea.children('.file-selected')
            .html(data.files[0].name
                + '<small>('
                + utils.readableFileSize(data.files[0].size)
                + ')</small>'
            )
        ;
        dropArea.children('.file-selector-empty').addClass('hidden');
        // show "Start" button
        uploadButton.removeClass('hidden');
        selectedFile = data;
    });

    /* "Start" button click listener */
    uploadButton.click(function () {
        // we don't want to add any more files
        fileUploadObj.fileupload('disable');
        // clear error messages
        clear();

        selectedFile.submit() // send the file
            .done(transformInServer)
            .fail(showFileErrorMsg)
            // enable the input again if there is an error!
            .fail(function () { fileUploadObj.fileupload('enable')})
        ;
    });

    /* prevent browser's default action when dragging and dropping files */
    $(document).bind('drop dragover', function (e) {
        e.preventDefault();
    });
})();