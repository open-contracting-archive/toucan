var toucan = toucan || {};
(function (namespace)
{
    var outputFormatBox = $('input[name="output_format"]').parents('.form-group'),
        filterField = $('input[name="filter_field"]'),
        filterValue = $('input[name="filter_value"]'),
        filterBox = filterField.parents('.form-group')
    ;

    function addError(selector, withHelpBlock) {
        selector.addClass('has-error');
        if (withHelpBlock)
            selector.find('.help-block').removeClass('hidden');
    }

    function removeError(selector, withHelpBlock) {
        selector.removeClass('has-error');
        if (withHelpBlock)
            selector.find('.help-block').addClass('hidden');
    }

    function validateOutputFormat() {
        /* if no options are checked, show error */
        if (outputFormatBox.find('input:checked').length < 1) {
            if (!outputFormatBox.hasClass('has-error')) {
                addError(outputFormatBox, true);
            }
        } else if (outputFormatBox.hasClass('has-error')) {
            removeError(outputFormatBox, true);
        }
    }

    function validateFilters() {
        if (filterField.val() && !filterValue.val()) {
            addError(filterBox);
        } else if (filterBox.hasClass('has-error')) {
            removeError(filterBox);
        }
    }

    namespace.showErrorsFromServer = function () {

    };

    outputFormatBox.change(validateOutputFormat);
    filterValue.blur(validateFilters);
    filterValue.keypress(validateFilters);

})(toucan.unflattenOptions = toucan.unflattenOptions || {});