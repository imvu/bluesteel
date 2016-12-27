resetSelect = function(selectId, text) {
    var select = document.getElementById(selectId);

    while(select.hasChildNodes()) {
        select.removeChild(select.firstChild);
    }

    var ele = document.createElement('option');
    ele.value = '{}';
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
                ele.value = JSON.stringify(res_obj['data']['layouts'][i]);
                ele.text = res_obj['data']['layouts'][i]['name'];

                select.appendChild(ele);
            }
        } else {
            console.log('failed', res_obj);
        }
    }
    xhr.send("");
}

populateProjectSelect = function(selectProjectId, value, propertyName) {
    var jsonValue = JSON.parse(value);
    if (!('url' in jsonValue)) {console.log('url key not found on jsonValue', jsonValue); return;}
    if (!(propertyName in jsonValue['url'])) {console.log('propertyName key not found on jsonValue[url]', jsonValue); return;}
    var url = jsonValue['url'][propertyName];

    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            var select = document.getElementById(selectProjectId);

            resetSelect(selectProjectId, 'select Project...');

            for (var i = 0; i < res_obj['data']['projects'].length; i++) {
                var ele = document.createElement('option');
                ele.value = JSON.stringify(res_obj['data']['projects'][i]);
                ele.text = res_obj['data']['projects'][i]['name'];

                select.appendChild(ele);
            }
        } else {
            console.log('failed', res_obj);
        }
    }
    xhr.send("");
}

populateBranchSelect = function(selectBranchId, value, propertyName) {
    var jsonValue = JSON.parse(value);
    if (!('url' in jsonValue)) {console.log('url key not found on jsonValue', jsonValue); return;}
    if (!(propertyName in jsonValue['url'])) {console.log('propertyName key not found on jsonValue[url]', jsonValue); return;}
    var url = jsonValue['url'][propertyName];

    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            var select = document.getElementById(selectBranchId);

            resetSelect(selectBranchId, 'select Branch...');

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

populateBenchmarkDefinitionSelect = function(selectDefId, value, propertyName) {
    var jsonValue = JSON.parse(value);
    if (!('url' in jsonValue)) {console.log('url key not found on jsonValue', jsonValue); return;}
    if (!(propertyName in jsonValue['url'])) {console.log('propertyName key not found on jsonValue[url]', jsonValue); return;}
    var url = jsonValue['url'][propertyName];

    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            var select = document.getElementById(selectDefId);

            resetSelect(selectDefId, 'select Benchmark Definition...');

            // for (var i = 0; i < res_obj['data']['branches'].length; i++) {
            //     var ele = document.createElement('option');
            //     ele.text = res_obj['data']['branches'][i]['name'];
            //     ele.id = res_obj['data']['branches'][i]['id'];

            //     select.appendChild(ele);
            // }
        } else {
            console.log('failed', res_obj);
        }
    }
    xhr.send("");
}
