(function(){

  var _fileItems=[];
  
  /** functions **/

  var isUploadButtonEnabled = function()
  {
    return !$('#upload-button').is(':disabled');
  }

  var enableUploadButton = function()
  {
    $('#upload-button').removeAttr('disabled');
  }

  var disableUploadButton = function()
  {
    $('#upload-button').attr('disabled', true);
  }

  var disableAddFiles = function()
  {
    $('.fileinput-button').attr('disabled', true);
    $('.fileinput-button input:file').attr('disabled', true);
  }

  var whenUploadAdded = function(e, data)
  {
    data.myID = $.now();
    _fileItems.push(data);
    if ( !isUploadButtonEnabled() )
    {
      enableUploadButton();
    }
  }

  var whenUploadFailed = function(e, data)
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

  // https://stackoverflow.com/questions/20459630/javascript-human-readable-filesize
  function readableFileSize(size) {
	var units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
	var i = 0;
	while(size >= 1024) {
		size /= 1024;
		++i;
	}
	return size.toFixed(1) + ' ' + units[i];
  }

  var upload = function()
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
        $('.response').addClass('alert-danger');
        $('.response').html('<b>An error has ocurred!</b>'
            +' Please verify that all your files are valid OCDS JSON, and try again in a few minutes.');
        $('.response').removeClass('hidden');
    };
    $.when.apply($, promises)
        .done(function(){
            $('#processing-modal').modal('show');
    		$.ajax($('#fileupload').attr('data-perform-action'))
				.done(function(data){
                    $('.response').addClass('alert-info');
					$('.response').html('<b>Success!</b>'
							+ ' result.zip (' 
							+  readableFileSize(data.size)
							+ ') <a href="'
							+ data.url
							+ '">Download</a>');
					$('.response').removeClass('hidden');
				})
                .fail(failFunc);
            })
        .fail(failFunc)
        .always(function(){
            $('#processing-modal').modal('hide');
            $('.drop-area').hide();
            $('.buttons').hide();
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
})();
