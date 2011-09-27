function doSubmit(e) {
        e = e || window.event;
        
        if (e.stopPropagation) {
            e.stopPropagation();
        }
        e.cancelBubble = true;
        
        try {
            swfupload.startUpload();
        } catch (ex) {
            alert("Can't upload file.");
        }
        
        return false;
    }
    
    function uploadDone() {
        
        var uploads = swfupload.getStats().successful_uploads,
            i = 0;
        
        console.log(uploads);
        console.log("Upload done.");
        
        for (i; i++; i < uploads) {
            console.log(swfupload.getFiles(i));
        }
    }
    
    /* 
    Parameters: num_select - number of files selected in the dialog
                num_queued - number of files successfully added to the queue
                total_queued - total number of files in the queue
    */
    function dialogDone(num_selected, num_queued, total_queued) {
        var file_list = [],
            list_str = "",
            i;
        
        // Note that we're basically overwriting the entire list if the user
        // accesses the dialog more than once, so accessing via the total_queued
        // nunmber won't result in dupes.
        for (i=0; i < total_queued; i++) {
            var f = swfupload.getFile(i);
            console.log(i);
            file_list.push(f);
            list_str += '<li class="file_list_entry" id="file_' + i + '">' + f.name + '</li>';
        }
        
        console.log(file_list);
        
        $("#file_list").html(list_str);
    }