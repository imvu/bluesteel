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
    obj['layout_id'] = parseInt(form.elements['layout_active'].value);
    obj['project_id'] = parseInt(form.elements['project_active'].value);
    obj['command_list'] = [];

    var keys = Object.keys(form.elements);

    for (var i = 0; i < keys.length; i++) {
        var key = keys[i];
        if (key.startsWith("command_")) {
            obj['command_list'].push(form.elements[key].value);
        }
    }

    console.log(obj);
    console.log(form.action);

    var cookie = getValueFromCookie('csrftoken');

    var xhr = new XMLHttpRequest();
    xhr.open("POST", form.action, true);
    xhr.setRequestHeader('X-CSRFToken', cookie);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            console.log('benchmark definition saved!');
        } else {
            console.log('error happened!', res_obj['data']);
        }
        location.reload();
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
