var toucan = toucan || {};
(function (namespace)
{
    var outputFormatBox = $('input[name="output_format"]').parents('.form-group'),
        filterField = $('input[name="filter_field"]'),
        filterValue = $('input[name="filter_value"]'),
        filterBox = filterField.parents('.form-group'),
        alertBox = $('#unflatten-options-modal .alert.alert-danger')
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

    function validateFilters(e) {
        /* validate the filter options (filter-field, filter-value) */
        if (e.type === 'keyup') {
            removeError(filterBox);
            return;
        }
        if (filterField.val()
            && !filterValue.val()
        ) {
            addError(filterBox);
        } else if (filterBox.hasClass('has-error')) {
            removeError(filterBox);
        }
    }

    namespace.showErrorsFromServer = function (errors) {
        var messages = $('<ul></ul>');
        $.each(errors, function(key, value) {
            $('input[name="'+key+'"]').parents('.form-group').addClass('has-error');
            $.each(value, function(i, e){
                messages.append($('<li></li>').html(e));
            });
        });
        alertBox
            .append(messages)
            .removeClass('hidden')
        ;
    };

    namespace.clear = function() {
        alertBox
            .empty()
            .addClass('hidden')
        ;
        $('.form-group').removeClass('has-error');
    };

    outputFormatBox.change(validateOutputFormat);
    filterValue.blur(validateFilters);
    filterValue.keyup(validateFilters);

})(toucan.unflattenOptions = toucan.unflattenOptions || {});