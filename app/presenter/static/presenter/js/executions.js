removeElements = function(elementId) {
    var element = document.getElementById(elementId);

    while(element.hasChildNodes()) {
        element.removeChild(element.firstChild);
    }
}

resetSelect = function(selectId, text) {
    removeElements(selectId);

    var select = document.getElementById(selectId);

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
    upCard.className = 'upper_card white_card card_fill card_padding_small';

    var title = document.createElement('div');
    title.className = 'title centered';
    title.innerText = 'STACKED BENCHMARK EXECUTIONS';

    upCard.appendChild(title);
    element.appendChild(upCard);

    for (var i = 0; i < data.length; i++) {
        var stackCard = document.createElement('div');
        if (i >= (data.length - 1)) {
            stackCard.className = 'lower_card white_card card_fill card_padding_small';
        } else {
            stackCard.className = 'middle_card white_card card_fill card_padding_small';
        }

        var chartTitle = document.createElement('div');
        chartTitle.className = 'command';
        chartTitle.innerText = data[i].id;

        var chartCanvas = document.createElement('canvas');
        var chartId = 'chart-' + i;
        chartCanvas.id = chartId;
        chartCanvas.width = 1150;
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

    // {% if entry.obj.visual_type != 'unknown' %}
    //     {% if forloop.first %}
    //     <div class="middle_card white_card card_padding_large card_medium">
    //         <div class="grid grid-pad-2">
    //             <div class="grid-col-1-1 grid-cell-pad-2-10">
    //                 <div class="list_label">COMMAND</div>
    //             </div>
    //             <div class="grid-col-1-1 grid-cell-pad-2-10">
    //                 <div class="command">{{res.command}}</div>
    //             </div>
    //         </div>
    //         <br/>
    //     {% endif %}

    //     {% if entry.obj.visual_type == 'vertical_bars' %}
    //         <div class="grid grid-pad-2">
    //             <div class="grid-col-1-1 grid-cell-pad-2-10">
    //                 <div class="command">{{entry.obj.id}}</div>
    //             </div>
    //             <div class="grid-col-1-1 grid-cell-pad-2-10">
    //                 <canvas id="chart-{{forloop.counter0}}" width="540" height="220"></canvas>
    //                 <script>chartVerticalBars('chart-{{forloop.counter0}}', {{entry.json|safe}});</script>
    //             </div>
    //         </div>
    //     {% elif entry.obj.visual_type == 'text' %}
    //         <div class="grid grid-pad-2">
    //             <div class="grid-col-1-1 grid-cell-pad-2-10">
    //                 <div class="command break_line">{{entry.obj.data}}</div>
    //             </div>
    //         </div>
    //     {% endif %}
    //     {% if res.out.count > 0 %}
    //     <br/>
    //     <br/>
    //     {% endif %}

    //     {% if forloop.last %}
    //     </div>
    //     {% endif %}
    // {% endif %}

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
            console.log(res_obj['data']);

            removeElements('data_container');
            populateData('data_container', res_obj['data']['stacked_executions']);

        } else {
            console.log('failed', res_obj);
        }
    }
    xhr.send("");

}
