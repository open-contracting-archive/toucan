var toucanApp = {};
(function(){
    function infoControl() {
        $('.info #collapse-panel').collapse('toggle');
    }

    function whenPanelShows(e) {
        $('#collapse-control .control.more').addClass('hidden');
        $('#collapse-control .control.less').removeClass('hidden');
    }

    function whenPanelHides(e) {
        $('#collapse-control .control.less').addClass('hidden');
        $('#collapse-control .control.more').removeClass('hidden');
    }

    this.showProcessingModal = function(customSelector) {
        if (customSelector) {
            $('#processing-modal ' + customSelector).removeClass('hidden');
            $('#processing-modal .default-message').addClass('hidden');
        }
        $('#processing-modal').modal('show');
    };

    this.hideProcessingModal = function(customSelector) {
        if (customSelector) {
            $('#processing-modal ' + customSelector).addClass('hidden');
            $('#processing-modal .default-message').removeClass('hidden');
        }
        $('#processing-modal').modal('hide');
    };

    // add handler
    $('#collapse-control').click(infoControl);
    $('.info #collapse-panel')
        .on('show.bs.collapse', whenPanelShows)
        .on('hide.bs.collapse', whenPanelHides)
}).apply(toucanApp);