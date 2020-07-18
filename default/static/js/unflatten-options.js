var toucanApp = toucanApp || {};
(function (namespace)
{
    var _optionsCache = {};

    var outputFormatBox = $('input[name="output_format"]').parents('.form-group'),
        filterField = $('input[name="filter_field"]'),
        filterValue = $('input[name="filter_value"]'),
        filterBox = filterField.parents('.form-group'),
        alertBox = $('#unflatten-options-modal .alert.alert-danger'),
        schemaSelector = $('select[name="schema"]'),
        schemaTreeContainer = $('#tree-container'),
        progressBar = $('#unflatten-options .progress'),
        closeButton = $('.close-modal'),
        preserveFieldsContainer = $('#preserve-fields-container'),
        preserveFieldsSearchInput = $('#preserve_fields_search')
    ;

    function showSchemaTree() {
        schemaTreeContainer.removeClass('hidden');
        progressBar.addClass('hidden');
    }

    function hideSchemaTree() {
        schemaTreeContainer.addClass('hidden');
        progressBar.removeClass('hidden');
    }

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

    function createSchemaOptionsTree(data, key) {
        var ref = $.jstree.reference(schemaTreeContainer);

        if (ref) {
            ref.destroy();
        }
        if (key) {
            _optionsCache[key] = data;
        }
        schemaTreeContainer.html(data);
        schemaTreeContainer.jstree({
            plugins: ['checkbox', 'search'],
            core: {
                expand_selected_onload : false,
                themes: {
                    dots: false
                }
            },
            checkbox: {
                keep_selected_style: false
            }
        });

        setPreserveFields();
        showSchemaTree();
    }

    function loadSchemaOptions(){
        var schemaSelected = schemaSelector.val();

        hideSchemaTree();
        if (!_optionsCache[schemaSelected] ) {
            $.ajax('/to-spreadsheet/get-schema-options', {
                data: {
                    url: schemaSelected
                }
            }).done(function(data){
                createSchemaOptionsTree(data, schemaSelected)
            });
        } else {
            createSchemaOptionsTree(_optionsCache[schemaSelected]);
        }
    }

    function setPreserveFields() {
        /* this function copies the checked values from the tree to hidden inputs in the Unflatten Form */
        var selected = $.jstree.reference(schemaTreeContainer).get_top_selected(true);
        preserveFieldsContainer.empty();

        $.each(selected, function (index, el) {
            var val = el.data.path;
            preserveFieldsContainer.append('<input type="hidden" name="preserve_fields" value="' + val + '"/>')
        });
    }

    function searchInTree(value){
        $.jstree.reference(schemaTreeContainer).search(value);
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
    schemaSelector.change(loadSchemaOptions);
    closeButton.click(setPreserveFields);
    preserveFieldsSearchInput.typeWatch({ callback: searchInTree });

    $(document).ready(loadSchemaOptions);

})(toucanApp.unflattenOptions = toucanApp.unflattenOptions || {});