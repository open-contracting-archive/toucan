(function(){
    var fileUploadObj = $('#fileupload'), dropArea = $('.drop-area'), uploadButton = $('#upload-button'),
        processingModal = $('#processing-modal');
    var selectedFile;

    function transformInServer() {
        // mask the page
        processingModal.modal('show');
         $.ajax('/to-spreadsheet/go/', {
             'dataType': 'json',
             'data': $('#unflatten-options').serialize(),
             'method': 'POST'
            })
             .done(showLinksToResults)
             .fail(showErrors)
        ;
    }

    function showLinksToResults(data) {
        if (data.xlsx) {
            $('.response-success .download-xlsx').attr('href', data.xlsx.url);
            $('.response-success .file-size-xlsx').html(utils.readableFileSize(data.xlsx.size));
        }
        if (data.xlsx) {
            $('.response-success .download-csv').attr('href', data.csv.url);
            $('.response-success .file-size-csv').html(utils.readableFileSize(data.csv.size));
        }
        $('.response-success').removeClass('hidden');
    }

    function showErrors() {

    }

    /* listen when a file is selected or dropped in the designated area */
    fileUploadObj.bind('fileuploadadd', function (e, data) {
        dropArea.removeClass('empty');
        // hide default message
        dropArea.children('.msg-empty').addClass('hidden');
        // fill area with file's name and size
        dropArea.children('file-selected')
            .prepend(data.files[0].name)
            .children('small')
            .html(utils.readableFileSize(data.files[0].size))
        ;
        // show "Start" button
        uploadButton.removeClass('hidden');
        selectedFile = data;
    });

    /* "Start" button click listener */
    uploadButton.click(function () {
        // we don't want to add any more files
        fileUploadObj.fileupload('disable');

        selectedFile.submit() // send the file
            .done()
        ;
    });

})();