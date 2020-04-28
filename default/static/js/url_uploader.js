var app = {};

function inputDelete(button) {
    $(button).parents('.form-group').remove();
    if ($('.extension-url-container .btn.input-delete').length < 2) {
        $('.extension-url-container .btn.input-delete').attr('disabled', true);
    }
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

(function () {

    var _paramSetters = [];
    var _done = false;

    this.setParams = function (func) {
        _paramSetters.push(func);
    };

    /** functions **/

    function hideMessages() {
        $('.response-warning')
            .addClass('hidden');
    }

    function showProcessingModal() {
        $('#processing-modal').modal('show');
    }

    function hideProcessingModal() {
        $('#processing-modal').modal('hide');
    }

    function whenAjaxReqFails(jqXHR) {
        $('.response-fail').removeClass('hidden');
        hideProcessingModal();
    }

    function performUrlAction() {
        var actionParams = {};
        _paramSetters.forEach(function (f) {
            f(actionParams);
        });
        $.ajax($('#url-button').attr('data-perform-action'), {data: actionParams})
            .done(function (data) {
                $('.response-success .file-size').html(utils.readableFileSize(data.size));
                $('.response-success .download').attr('href', data.url);
                $('.response-success').removeClass('hidden');
                hideProcessingModal();
            })
            .fail(whenAjaxReqFails)
            .always(function () {
                _done = true
            });
    }

    function upload_url() {
        hideMessages();
        showProcessingModal();
        $.ajax('/upload-url/',
        {'dataType': 'json', type: 'POST',
        'data': $('.input-url-container .form-group .input-group .form-control').serialize(),
         headers: { "X-CSRFToken": getCookie('csrftoken') }
        } )
            .done(function (data) {
                performUrlAction();
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                $('.response-warning.url-process-failed .message-url').html(
                    ( jqXHR.responseText || textStatus )
                );
                $('.response-warning.url-process-failed').removeClass('hidden');
                hideProcessingModal();
            })
        ;
    }

    /** upload url **/
    $("#url-button").click(upload_url);

    $('.choice-header').on('change', function() {
        if ($(this).is(':checked')) {
            var allClasses = $(this).attr('class');
            var operationIndex = allClasses.search(/toucan-nav-[^\s]+/);
            var operationClass = allClasses.substring(operationIndex);
            $('.panel-collapse.collapse ').not(this).collapse('hide');
            $('.panel-collapse.collapse.' + operationClass).collapse('show');
        }
    });

    $('#add-url').click(function () {
        var numInputs = $('.input-url-container').children().length;
        $('.input-url-container .btn.btn-danger').attr('disabled', false);
        $('.input-url-container').append('<div class="form-group">' +
            '<div class="input-group">' +
            '<input type="text" class="form-control" name="input_url_' + numInputs + '" id="id_' + numInputs + '"/>' +
            '<span class="input-group-btn">' +
            '<button class="btn btn-danger input-delete" onclick="inputDelete(this)" type="button">x</button>' +
            '</span>' +
            '</div>' +
            '</div>')
    });

    $('#url-input').click(function () {
        if ($('.extension-url-container .btn.input-delete').length < 2) {
            $('.extension-url-container .btn.input-delete').attr('disabled', true);
        }
    });

}).apply(app);
