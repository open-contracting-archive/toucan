(function(){

  var _fileItems=[];

 // plugin initialization 
 $('#fileupload').fileupload({
    url: 'http://localhost:8000/upload/',
    acceptFileTypes: /\.json$/i,
    filesContainer: '.files',
    sequencialUploads: true,
    disableVideoPreview: true,
    disableAudioPreview: true,
    disableImagePreview: true
  });

  $('#fileupload')
    .bind('fileuploadadded', function(e, data){
	  data.myID = $.now();
      _fileItems.push(data);
	  $('#upload-button').removeAttr('disabled');
    })
  ;
  $('#fileupload')
    .bind('fileuploadfail', function(e, data){
      var toDelete = -1;
      $.each(_fileItems, function(i, el){
        if (el.myId === data.myId) {
          toDelete = -1
        }
      });
      _fileItems.splice(toDelete, 1);
      console.log(_fileItems)
    })
  ;

  // upload function
  $("#upload-button").click(function(){
    $.each(_fileItems, function(i, val){
		val.submit();
	});
  });
})();
