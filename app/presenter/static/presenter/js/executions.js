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

visualSelect = function(selectId) {
    var select = document.getElementById(selectId);
    if (!select.classList.contains('selection_empty')) {return;}
    select.classList.remove('selection_empty');
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
                ele.value = JSON.stringify(res_obj['data']['branches'][i]);
                ele.text = res_obj['data']['branches'][i]['name'];


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

            for (var i = 0; i < res_obj['data']['definitions'].length; i++) {
                var ele = document.createElement('option');
                ele.value = JSON.stringify(res_obj['data']['definitions'][i]);
                ele.text = res_obj['data']['definitions'][i]['name'];

                select.appendChild(ele);
            }
        } else {
            console.log('failed', res_obj);
        }
    }
    xhr.send("");
}

populateBenchmarkWorkerSelect = function(selectWorkerId, value, propertyName) {
    var jsonValue = JSON.parse(value);
    if (!('url' in jsonValue)) {console.log('url key not found on jsonValue', jsonValue); return;}
    if (!(propertyName in jsonValue['url'])) {console.log('propertyName key not found on jsonValue[url]', jsonValue); return;}
    var url = jsonValue['url'][propertyName];

    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            var select = document.getElementById(selectWorkerId);

            resetSelect(selectWorkerId, 'select Worker...');

            for (var i = 0; i < res_obj['data']['workers'].length; i++) {
                var ele = document.createElement('option');
                ele.value = JSON.stringify(res_obj['data']['workers'][i]);
                ele.text = res_obj['data']['workers'][i]['name'];

                select.appendChild(ele);
            }
        } else {
            console.log('failed', res_obj);
        }
    }
    xhr.send("");
}

tryPopulateCharts = function(selLayoutId, selProjectId, selBranchId, selDefinitionId, selWorkerId) {
    var selLayout = document.getElementById(selLayoutId);
    if (selLayout === undefined) {console.log('No select Layout found!'); return;}
    var jsonLayout = JSON.parse(selLayout.options[selLayout.selectedIndex].value);
    if (!('id' in jsonLayout)) {console.log('id key not found on jsonLayout', jsonLayout); return;}

    var selProject = document.getElementById(selProjectId);
    if (selProject === undefined) {console.log('No select Project found!'); return;}
    var jsonProject = JSON.parse(selProject.options[selProject.selectedIndex].value);
    if (!('id' in jsonProject)) {console.log('id key not found on jsonProject', jsonProject); return;}

    var selBranch = document.getElementById(selBranchId);
    if (selBranch === undefined) {console.log('No select Branch found!'); return;}
    var jsonBranch = JSON.parse(selBranch.options[selBranch.selectedIndex].value);
    if (!('id' in jsonBranch)) {console.log('id key not found on jsonBranch', jsonBranch); return;}

    var selDefinition = document.getElementById(selDefinitionId);
    if (selDefinition === undefined) {console.log('No select Definition found!'); return;}
    var jsonDefinition = JSON.parse(selDefinition.options[selDefinition.selectedIndex].value);
    if (!('id' in jsonDefinition)) {console.log('id key not found on jsonDefinition', jsonDefinition); return;}

    var selWorker = document.getElementById(selWorkerId);
    if (selWorker === undefined) {console.log('No select Worker found!'); return;}
    var jsonWorker = JSON.parse(selWorker.options[selWorker.selectedIndex].value);
    if (!('id' in jsonWorker)) {console.log('id key not found on jsonWorker', jsonWorker); return;}


    // Change here

}
