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

    obj = {};
    obj['name'] = form.elements['name_active'].value;
    obj['layout_id'] = parseInt(form.elements['layout_active'].value);
    obj['project_id'] = parseInt(form.elements['project_active'].value);
    obj['priority'] = parseInt(form.elements['priority_state'].value);
    obj['active'] = (1 === parseInt(form.elements['active_state'].value));
    obj['command_list'] = [];
    obj['max_fluctuation_percent'] = '-1';
    obj['max_weeks_old_notify'] = '-1';
    obj['max_benchmark_date'] = {};
    obj['max_benchmark_date']['year'] = 1970;
    obj['max_benchmark_date']['month'] = 1;
    obj['max_benchmark_date']['day'] = 1;
    obj['overrides'] = [];
    obj['work_passes'] = [];

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

            var value = parseInt(element.value);
            var ignore = value < 0;

            overrides[inpId]['override_value'] = Math.max(value, 0);
            overrides[inpId]['ignore_fluctuation'] = ignore;
        } else if (element.name.startsWith("work_pass_")) {
            var wp = {};
            wp['id'] = parseInt(element.id);
            wp['allowed'] = element.checked;
            obj['work_passes'].push(wp);
        } else if (element.name.startsWith("max_benchmark_date_year")) {
            obj['max_benchmark_date']['year'] = parseInt(element.value);
        } else if (element.name.startsWith("max_benchmark_date_month")) {
            obj['max_benchmark_date']['month'] = parseInt(element.value);
        } else if (element.name.startsWith("max_benchmark_date_day")) {
            obj['max_benchmark_date']['day'] = parseInt(element.value);
        }
    }

    for (var key in overrides) {
        if (!overrides.hasOwnProperty(key)) {continue;}
        if (overrides[key]['result_id'].startsWith('<') && overrides[key]['result_id'].endsWith('>')) {continue;}

        obj['overrides'].push(overrides[key]);
    }

    console.log(obj);

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


isYearLeap = function(year) {
    return ((year % 4 == 0) && (year % 100 != 0)) || (year % 400 == 0);
}

daysInMonth = function(year, month) {
    var febDays = isYearLeap(year) ? 29 : 28;
    var days = [31, febDays, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

    return days[month];
}

populateSelectYears = function(id_select_year, current_year, min_year, max_year) {
    var sel_year = document.getElementById(id_select_year);

    while(sel_year.hasChildNodes()) {
        sel_year.removeChild(sel_year.firstChild);
    }

    var count = max_year - min_year;
    var index = 0;

    var c_year = parseInt(current_year);

    for (var i = 0; i < count; i++) {
        var ele = document.createElement('option');
        var year = i + min_year;
        ele.value = year;
        ele.text = year;

        if (year === c_year) {
            index = i;
        }

        sel_year.appendChild(ele);
    }

    sel_year.options[index].selected = true;
}

populateSelectMonths = function(id_select_month, current_month) {
    var months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    var months_count = months.length;

    var sel_month = document.getElementById(id_select_month);

    while(sel_month.hasChildNodes()) {
        sel_month.removeChild(sel_month.firstChild);
    }

    for (var i = 0; i < months_count; i++) {
        var ele = document.createElement('option');
        ele.value = i + 1;
        ele.text = months[i];

        sel_month.appendChild(ele);
    }

    sel_month.options[current_month - 1].selected = true;

}

populateSelectDays = function(id_select_day, year, month, current_slected_day) {
    var sel_day = document.getElementById(id_select_day);
    var days_count = daysInMonth(year, month);

    while(sel_day.hasChildNodes()) {
        sel_day.removeChild(sel_day.firstChild);
    }

    if (current_slected_day > days_count) {
        current_slected_day = days_count;
    }

    for (var i = 0; i < days_count; i++) {
        var ele = document.createElement('option');
        ele.value = i + 1;
        ele.text = i + 1;

        sel_day.appendChild(ele);
    }

    sel_day.options[current_slected_day - 1].selected = true;
}

changeBenchmarkMaxDate = function(thisObj, id_select_year, id_select_month, id_select_day, change_year, change_month, change_day) {
    var sel_year = document.getElementById(id_select_year);
    var sel_month = document.getElementById(id_select_month);
    var sel_day = document.getElementById(id_select_day);

    if (change_year || change_month) {
        populateSelectDays(id_select_day, sel_year.value, sel_month.value - 1, sel_day.value);
    }
}



