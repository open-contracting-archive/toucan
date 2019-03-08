(function(){
    function setLanguage(){
        $.ajax('/i18n/setlang/', {
            method: 'POST',
            data: {
                language: $(this).attr('data-language-code'),
                csrfmiddlewaretoken: $(this).attr('data-token')
            }
        })
        .done(function(){
            location.reload()
        });
    }

    $('.language-option').click(setLanguage)
})();
