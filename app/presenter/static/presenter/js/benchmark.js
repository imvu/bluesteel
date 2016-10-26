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

createInputElement = function(className, name, maxLength, defaultText) {
    var eleDiv = document.createElement('div');
    eleDiv.className = className;

    var eleCont = document.createElement('div');
    eleCont.className = "container_input";

    var eleInput = document.createElement('input');
    eleInput.className = "command_input";
    eleInput.type = "text";
    eleInput.name = name;
    eleInput.value = defaultText;
    eleInput.maxlength = maxLength.toString();

    eleCont.appendChild(eleInput);
    eleDiv.appendChild(eleCont);
    return eleDiv;
}

createSelectElement = function(className, name, count, template) {
    var eleDiv = document.createElement('div');
    eleDiv.className = className;

    var eleCont = document.createElement('div');
    eleCont.className = "container_input";

    var eleSelect = document.createElement('select');
    eleSelect.className = "selection individual";
    eleSelect.name = name;

    for (var i = 0; i < count; i++) {
        var value = template.replace("{0}", i.toString());
        var eleOption = document.createElement('option');
        eleOption.value = i;
        eleOption.text = value;
        eleSelect.appendChild(eleOption);
    }

    eleCont.appendChild(eleSelect);
    eleDiv.appendChild(eleCont);
    return eleDiv;
}

createButtonElement = function(className, buttonIconClass, callback) {
    var eleDiv = document.createElement('div');
    eleDiv.className = className;//;

    var eleButton = document.createElement('button');
    eleButton.className = "btn_icon icon_gray";
    eleButton.onclick = callback;

    var eleI = document.createElement('i');
    eleI.className = buttonIconClass;

    eleButton.appendChild(eleI);
    eleDiv.appendChild(eleButton);

    return eleDiv;
}

createFlucRemoveListElementCallback = function(idElementToRemove) {
    return function() {removeListElement(idElementToRemove);};
}

addFluctuationOverride = function(idListToAddElement, startName) {
    var listToAddElement = document.getElementById(idListToAddElement);

    var childCount = listToAddElement.children.length;

    var stringTail = (new Date()).getTime().toString() + '_new';

    var wrapDiv = document.createElement('div');
    wrapDiv.id = startName.toString() + stringTail;

    var eleResultId = createInputElement('grid-col-3-8 grid-cell-pad-5-10', 'override_result_id_' + stringTail, 32, '<edit here>');
    var eleSelectFluc = createSelectElement('grid-col-4-8 grid-cell-pad-5-10', 'max_override_fluctuation_percent_' + stringTail, 101, '{0}% - Maximum Fluctuation');
    var eleRemoveButton = createButtonElement('grid-col-1-8 grid-cell-pad-5-10', 'fa fa-times-circle fa-2x', createFlucRemoveListElementCallback(wrapDiv.id));

    wrapDiv.appendChild(eleResultId);
    wrapDiv.appendChild(eleSelectFluc);
    wrapDiv.appendChild(eleRemoveButton);

    listToAddElement.appendChild(wrapDiv);
}

saveBenchmarkDefinition = function(idFormBenchmarkDefinition) {
    var form = document.getElementById(idFormBenchmarkDefinition);

    console.log(form.elements);

    obj = {};
    obj['name'] = form.elements['name_active'].value;
    obj['layout_id'] = parseInt(form.elements['layout_active'].value);
    obj['project_id'] = parseInt(form.elements['project_active'].value);
    obj['active'] = (1 === parseInt(form.elements['active_state'].value))
    obj['command_list'] = [];
    obj['max_fluctuation_percent'] = '-1';
    obj['max_weeks_old_notify'] = '-1';
    obj['overrides'] = [];

    var overrides = {};

    for (var i = 0; i < form.elements.length; i++) {
        var element = form.elements[i];
        if (element.name.startsWith("command_")) {
            obj['command_list'].push(element.value);
        } else if (element.name.startsWith("max_fluctuation_percent")) {
            obj['max_fluctuation_percent'] = parseInt(element.value);
        } else if (element.name.startsWith("max_weeks_old_notify")) {
            obj['max_weeks_old_notify'] = parseInt(element.value);
        } else if (element.name.startsWith("override_result_id")) {
            var inpId = element.name.replace("override_result_id_", "");
            if (overrides[inpId] === undefined) {overrides[inpId] = {};}

            overrides[inpId]['result_id'] = element.value;
        } else if (element.name.startsWith("max_override_fluctuation_percent")) {
            var inpId = element.name.replace("max_override_fluctuation_percent_", "");
            if (overrides[inpId] === undefined) {overrides[inpId] = {};}

            if (element.value.startsWith('<') && element.value.endsWith('>')) {continue;}

            overrides[inpId]['override_value'] = parseInt(element.value);
        }
    }

    for (var key in overrides) {
        if (!overrides.hasOwnProperty(key)) {continue;}
        if (overrides[key]['result_id'].startsWith('<') && overrides[key]['result_id'].endsWith('>')) {continue;}

        obj['overrides'].push(overrides[key]);
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
