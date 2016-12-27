resetSelect = function(selectId, text) {
    var select = document.getElementById(selectId);

    while(select.hasChildNodes()) {
        select.removeChild(select.firstChild);
    }

    var ele = document.createElement('option');
    ele.id = '-1';
    ele.value = '-1';
    ele.text = text;
    ele.selected = true;
    ele.disabled = true;
    ele.hidden = true;

    select.appendChild(ele);
}

populateLayoutSelect = function(selectId, url) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            var select = document.getElementById(selectId);

            resetSelect(selectId, 'select Layout...');

            for (var i = 0; i < res_obj['data']['layouts'].length; i++) {
                var ele = document.createElement('option');
                ele.value = res_obj['data']['layouts'][i]['url']['project_list'];
                ele.text = res_obj['data']['layouts'][i]['name'];
                ele.id = res_obj['data']['layouts'][i]['id'];

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
            var select = document.getElementById(selectProjectId);

            resetSelect(selectProjectId, 'select Project...');

            for (var i = 0; i < res_obj['data']['projects'].length; i++) {
                var ele = document.createElement('option');
                ele.value = res_obj['data']['projects'][i]['url']['project_branch_list'];
                ele.text = res_obj['data']['projects'][i]['name'];
                ele.id = res_obj['data']['projects'][i]['id'];

                select.appendChild(ele);
            }
        } else {
            console.log('failed', res_obj);
        }
    }
    xhr.send("");
}

populateBranchSelect = function(selectBranchId, url) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            var select = document.getElementById(selectBranchId);

            resetSelect(selectBranchId, 'select Project...');

            for (var i = 0; i < res_obj['data']['branches'].length; i++) {
                var ele = document.createElement('option');
                ele.text = res_obj['data']['branches'][i]['name'];
                ele.id = res_obj['data']['branches'][i]['id'];

                select.appendChild(ele);
            }
        } else {
            console.log('failed', res_obj);
        }
    }
    xhr.send("");
}
