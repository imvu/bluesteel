create_new_benchmark_definition = function(thisObj, url) {
    var cookie = getValueFromCookie('csrftoken');

    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader('X-CSRFToken', cookie);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            console.log(res_obj);
            window.location=res_obj['data']['redirect'];
        } else {
        }
    }
    xhr.send("");
    thisObj.onclick = function() {};
}

saveBenchmarkDefinition = function(idFormBenchmarkDefinition) {
    var form = document.getElementById(idFormBenchmarkDefinition);

    console.log(form.elements);

    obj = {};
    obj['name'] = form.elements['name_active'].value;
    obj['layout_id'] = parseInt(form.elements['layout_active'].value);
    obj['project_id'] = parseInt(form.elements['project_active'].value);
    obj['command_list'] = [];
    obj['max_fluctuation_percent'] = '-1';

    for (var i = 0; i < form.elements.length; i++) {
        var element = form.elements[i];
        if (element.name.startsWith("command_")) {
            obj['command_list'].push(element.value);
        } else if (element.name.startsWith("max_fluctuation_percent")) {
            obj['max_fluctuation_percent'] = parseInt(element.value);
        }
    }

    executeAndReload(form.action, JSON.stringify(obj));
}

deleteBenchmarkDefinition = function(delete_url) {

    var cookie = getValueFromCookie('csrftoken');

    var xhr = new XMLHttpRequest();
    xhr.open("POST", delete_url, true);
    xhr.setRequestHeader('X-CSRFToken', cookie);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            console.log('benchmark definition saved!');
            window.location=res_obj['data']['redirect'];
        } else {
            console.log('error happened!', res_obj['data']);
        }
    }
    xhr.send(JSON.stringify(obj));
}

changeSelectProjectInfo = function(thisObj, url_editable, projectSelectTagId) {
    var cookie = getValueFromCookie('csrftoken');

    url_editable = url_editable.replace("<0>", thisObj.value);
    console.log(thisObj.value, url_editable);

    var xhr = new XMLHttpRequest();
    xhr.open("GET", url_editable, true);
    xhr.setRequestHeader('X-CSRFToken', cookie);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        console.log(res_obj);
        if (res_obj['status'] === 200) {
            var select = document.getElementById(projectSelectTagId);

            while(select.hasChildNodes()) {
                select.removeChild(select.firstChild);
            }

            for (var i = 0; i < res_obj['data']['projects'].length; i++) {
                var ele = document.createElement('option');
                ele.value = res_obj['data']['projects'][i]['id'];
                ele.text = res_obj['data']['projects'][i]['name'];

                select.appendChild(ele);
            }

            console.log('project info received!');
        } else {
            console.log('error happened!', res_obj['data']);
        }
    }
    xhr.send("");
}
