var utils={};
(function(){
  // https://stackoverflow.com/questions/20459630/javascript-human-readable-filesize
  this.readableFileSize = function(size) {
	var units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
	var i = 0;
	while(size >= 1024) {
		size /= 1024;
		++i;
	}
	return size.toFixed(1) + ' ' + units[i];
  }

}).apply(utils);
