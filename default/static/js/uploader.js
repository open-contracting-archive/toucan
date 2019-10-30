var app = {};
(function(){

  var _fileItems = [];
  var _paramSetters = []; 
  var _done = false;

  this.setParams = function(func)
  {
      _paramSetters.push(func);
  }
  
  /** functions **/

  function isUploadButtonEnabled()
  {
    return !$('#upload-button').is(':disabled');
  }

  function enableUploadButton()
  {
    $('#upload-button').removeAttr('disabled');
  }

  function disableUploadButton()
  {
    $('#upload-button').attr('disabled', true);
  }

  function disableAddFiles()
  {
    $('.fileinput-button').attr('disabled', true);
    $('.fileinput-button input:file').attr('disabled', true);
  }

  function whenUploadAdded(e, data)
  {
    data.myID = $.now();
    _fileItems.push(data);
    if ( !isUploadButtonEnabled() )
    {
      enableUploadButton();
    }
    if (_fileItems.length == 1)
    {
       $('.file-selector-empty').addClass('hidden');     
       $('.actions').removeClass('hidden');
       $('.files').removeClass('hidden');
       $('.drop-area').removeClass('empty');
       $('.drop-area').addClass('row');
    }
  }

  function whenUploadFailed(e, data)
  {
    if (data.errorThrown == 'abort'){
      // not really an error, but file has been removed by user
      var toDelete = -1;
      $.each(_fileItems, function(i, el){
        if (el.myId === data.myId) {
          toDelete = -1
        }
      });
      _fileItems.splice(toDelete, 1);
      if (_fileItems.length == 0){
        disableUploadButton();
      }
    }
  }

  function upload()
  {
    disableUploadButton();
    disableAddFiles();
	myfiles = $.map(_fileItems, function(obj){
	    return obj.files[0];
	});
    
	var promises = $.map(_fileItems, function(val)
    {
  		return val.submit();
	});
    var failFunc = function(){
        $('.response-fail').removeClass('hidden');
        $('#processing-modal').modal('hide');
    };
    $.when.apply($, promises)
        .done(function(){
            $('#processing-modal').modal('show');
            actionParams = {}
            _paramSetters.forEach(function(f){
                f(actionParams);
                });
    		$.ajax($('#fileupload').attr('data-perform-action'), { data: actionParams })
				.done(function(data){
                    $('.response-success .file-size').html(utils.readableFileSize(data.size));
                    $('.response-success .download').attr('href', data.url);
					$('.response-success').removeClass('hidden');
					if (data.hasOwnProperty('warnings') && data.warnings.length > 0) {
					    $('.response-warning').removeClass('hidden');
					    $('.response-warning ul').html($.map(data.warnings, function(o){
					        return '<li>' + o + '</li>'
                        }).join('\n'))
                    }
                    $('#processing-modal').modal('hide');
				})
                .fail(failFunc)
                .always(function(){_done=true});
            })
        .fail(failFunc)
        .always(function(){
            $('.actions').hide();
            $('#fileupload').fileupload('destroy');
            });
  }

  /** plugin initialization **/
  
  $('#fileupload').fileupload();

  $('#fileupload')
    .bind('fileuploadadded', whenUploadAdded)
    .bind('fileuploadfail', whenUploadFailed)
    ;

  /** upload call binding **/
  $("#upload-button").click(upload);

  /* add warning before closing/navigating away from page */
  window.onload = function() {
    window.addEventListener("beforeunload", function (e) {
      if (_fileItems.length == 0 || _done) {
        return undefined;
      }
      var confirmationMessage = 'It looks like you have been editing something. '
        + 'If you leave before saving, your changes will be lost.';

      (e || window.event).returnValue = confirmationMessage; //Gecko + IE
      return confirmationMessage; //Gecko + Webkit, Safari, Chrome etc.
    });
  };

}).apply(app);

