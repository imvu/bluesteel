removeElements = function(elementId) {
    var element = document.getElementById(elementId);

    while(element.hasChildNodes()) {
        element.removeChild(element.firstChild);
    }
}

resetSelect = function(selectId, text) {
    removeElements(selectId);

    var select = document.getElementById(selectId);

    if (!select.classList.contains('selection_empty')) {
        select.classList.add('selection_empty');
    }

    var ele = document.createElement('option');
    ele.value = '{}';
    ele.text = text;
    ele.selected = true;
    ele.disabled = true;
    ele.hidden = true;

    select.selectedIndex = 0;
    select.appendChild(ele);
}

visualSelect = function(selectId) {
    var select = document.getElementById(selectId);
    if (!select.classList.contains('selection_empty')) {return;}
    select.classList.remove('selection_empty');
}

populateLayoutSelect = function(selectId, url) {
    resetSelect(selectId, 'select Layout...');

    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            var select = document.getElementById(selectId);

            for (var i = 0; i < res_obj['data']['layouts'].length; i++) {
                var ele = document.createElement('option');
                ele.value = JSON.stringify(res_obj['data']['layouts'][i]);
                ele.text = 'Layout: ' + res_obj['data']['layouts'][i]['name'];

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

    resetSelect(selectProjectId, 'select Project...');

    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            var select = document.getElementById(selectProjectId);

            for (var i = 0; i < res_obj['data']['projects'].length; i++) {
                var ele = document.createElement('option');
                ele.value = JSON.stringify(res_obj['data']['projects'][i]);
                ele.text = 'Project: ' + res_obj['data']['projects'][i]['name'];

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

    resetSelect(selectBranchId, 'select Branch...');

    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            var select = document.getElementById(selectBranchId);

            for (var i = 0; i < res_obj['data']['branches'].length; i++) {
                var ele = document.createElement('option');
                ele.value = JSON.stringify(res_obj['data']['branches'][i]);
                ele.text = 'Branch: ' + res_obj['data']['branches'][i]['name'];


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

    resetSelect(selectDefId, 'select Benchmark Definition...');

    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            var select = document.getElementById(selectDefId);

            for (var i = 0; i < res_obj['data']['definitions'].length; i++) {
                var ele = document.createElement('option');
                ele.value = JSON.stringify(res_obj['data']['definitions'][i]);
                ele.text = 'Definition: ' + res_obj['data']['definitions'][i]['name'];

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

    resetSelect(selectWorkerId, 'select Worker...');

    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            var select = document.getElementById(selectWorkerId);

            for (var i = 0; i < res_obj['data']['workers'].length; i++) {
                var ele = document.createElement('option');
                ele.value = JSON.stringify(res_obj['data']['workers'][i]);
                ele.text = 'Worker: ' + res_obj['data']['workers'][i]['name'];

                select.appendChild(ele);
            }
        } else {
            console.log('failed', res_obj);
        }
    }
    xhr.send("");
}

populateData = function(elementID, data) {
    var element = document.getElementById(elementID);
    if (element === undefined) {console.log('Element to populate data not found!'); return;}

    var upCard = document.createElement('div');
    upCard.className = 'upper_card white_card card_padding_small';

    var title = document.createElement('div');
    title.className = 'title centered';
    title.innerText = 'STACKED BENCHMARK EXECUTIONS';

    upCard.appendChild(title);
    element.appendChild(upCard);

    for (var i = 0; i < data.length; i++) {
        var stackCard = document.createElement('div');
        if (i >= (data.length - 1)) {
            stackCard.className = 'lower_card white_card card_padding_small';
        } else {
            stackCard.className = 'middle_card white_card card_padding_small';
        }

        var chartTitle = document.createElement('div');
        chartTitle.className = 'command';
        chartTitle.innerText = data[i].id;

        var chartCanvas = document.createElement('canvas');
        var chartId = 'chart-' + i;
        chartCanvas.id = chartId;
        chartCanvas.width = 1050;
        chartCanvas.height = 220;

        stackCard.appendChild(chartTitle);
        stackCard.appendChild(chartCanvas);
        element.appendChild(stackCard);

        setTimeout(function(chartID, data) {
            stackedchartVerticalBars(chartID, data);
        },
        i * 300,
        chartId,
        data[i]['data']
        );
    }
}

populateDataEmpty = function(elementID, message) {
    var element = document.getElementById(elementID);
    if (element === undefined) {console.log('Element to populate data not found!'); return;}

    var normalCard = document.createElement('div');
    normalCard.className = 'card white_card card_padding_small';

    var title = document.createElement('div');
    title.className = 'normal centered';
    title.innerText = message;

    normalCard.appendChild(title);
    element.appendChild(normalCard);

}

tryPopulateCharts = function(selLayoutId, selProjectId, selBranchId, selDefinitionId, selWorkerId) {
    removeElements('data_container');

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

    var url = '/main/execution/stacked/project/{0}/branch/{1}/definition/{2}/worker/{3}/quick/';
    url = url.replace('{0}', jsonProject['id']);
    url = url.replace('{1}', jsonBranch['id']);
    url = url.replace('{2}', jsonDefinition['id']);
    url = url.replace('{3}', jsonWorker['id']);

    var xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {

            if (res_obj['data']['stacked_executions'].length > 0) {
                removeElements('data_container');
                populateData('data_container', res_obj['data']['stacked_executions']);
            } else {
                removeElements('data_container');
                populateDataEmpty('data_container', 'There are no results on this combination of options.');
            }

        } else {
            console.log('failed', res_obj);
        }
    }
    xhr.send("");

    populateDataEmpty('data_container', 'Retreiving data...');
}

