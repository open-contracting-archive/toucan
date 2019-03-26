var app = {};
(function(){

  var _fileItems=[];
  var _beforeSend = null;

  this.beforeSend = function(func)
  {
      _beforeSend = func;
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
       $('.buttons').removeClass('hidden');
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
    };
    $.when.apply($, promises)
        .done(function(){
            $('#processing-modal').modal('show');
            var params = {};
            if (_beforeSend && typeof _beforeSend === "function")
            {
                var res = _beforeSend();
                if(res)
                {
                    params = res
                }
            } 
    		$.ajax($('#fileupload').attr('data-perform-action'), { data: params })
				.done(function(data){
                    $('.response-success .file-size').html(readableFileSize(data.size));
                    $('.response-success .download').attr('href', data.url);
					$('.response-success').removeClass('hidden');
				})
                .fail(failFunc);
            })
        .fail(failFunc)
        .always(function(){
            $('#processing-modal').modal('hide');
            // $('.drop-area').hide();
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

}).apply(app);
