populateLayoutSelect = function(selectId, url) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            var select = document.getElementById(selectId);

            while(select.hasChildNodes()) {
                select.removeChild(select.firstChild);
            }

            var ele = document.createElement('option');
            ele.value = '-1';
            ele.text = 'select Layout...';
            ele.selected = true;
            ele.disabled = true;
            ele.hidden = true;

            select.appendChild(ele);

            for (var i = 0; i < res_obj['data']['layouts'].length; i++) {
                var ele = document.createElement('option');
                ele.value = res_obj['data']['layouts'][i]['url']['project_list'];
                ele.text = res_obj['data']['layouts'][i]['name'];

                select.appendChild(ele);
            }
        } else {
            console.log('failed', res_obj);
        }
    }
    xhr.send("");
}

populateProjectSelect = function(selectProjectId, url) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            var select = document.getElementById(selectId);

            while(select.hasChildNodes()) {
                select.removeChild(select.firstChild);
            }

            var ele = document.createElement('option');
            ele.value = '-1';
            ele.text = 'select Project...';
            ele.selected = true;
            ele.disabled = true;
            ele.hidden = true;

            select.appendChild(ele);

            for (var i = 0; i < res_obj['data']['layouts'].length; i++) {
                var ele = document.createElement('option');
                ele.value = res_obj['data']['layouts'][i]['url']['project_list'];
                ele.text = res_obj['data']['layouts'][i]['name'];

                select.appendChild(ele);
            }
        } else {
            console.log('failed', res_obj);
        }
    }
    xhr.send("");
}