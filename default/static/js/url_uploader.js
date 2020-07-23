(function(){
    this.inputDelete = function (button) {
        $(button).parents('.form-group').remove();
        if ($('.input-url-container .btn.input-delete').length < 2) {
            $('.input-url-container .btn.input-delete').attr('disabled', true);
        }
    };
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
        $('.input-url-container').append('<div class="form-group" id="input_url_' + numInputs + '">' +
            '<div class="input-group">' +
            '<input type="text" class="form-control" name="input_url_' + numInputs + '"/>' +
            '<span class="input-group-btn">' +
            '<button class="btn btn-danger input-delete" onclick="inputDelete(this)" type="button">x</button>' +
            '</span>' +
            '</div>' +
            '</div>')
    });
})();