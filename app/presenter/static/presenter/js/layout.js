create_new_layout = function(thisObj, url) {
    var cookie = getValueFromCookie('csrftoken');

    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader('X-CSRFToken', cookie);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            window.location=res_obj['data']['layout']['url'];
        } else {
        }
    }
    xhr.send("");
    thisObj.onclick = function() {};
}

removeListElement = function(idElementToRemove) {
    var elementToRemove = document.getElementById(idElementToRemove);
    var parent = elementToRemove.parentNode;
    parent.removeChild(elementToRemove);
}

createRemoveListElementCallback = function(idElementToRemove) {
    return function() {removeListElement(idElementToRemove);};
}

addListElement = function(thisObj, idParent, idListToAddElement, startName) {
    var listToAddElement = document.getElementById(idListToAddElement);

    var childCount = listToAddElement.children.length;

    var eleLi = document.createElement('li');
    eleLi.className = "no_text";
    eleLi.id = startName.toString() + (new Date()).getTime().toString() + '_new';

    var eleInput = document.createElement('input');
    eleInput.className = "command_input";
    eleInput.type = "text";
    eleInput.name = eleLi.id;
    eleInput.value = "<edit command here>";
    eleInput.maxlength = "255";

    var eleButton = document.createElement('button');
    eleButton.className = "btn_icon icon_gray";
    eleButton.onclick = createRemoveListElementCallback(eleLi.id);

    var eleI = document.createElement('i');
    eleI.className = "fa fa-times-circle fa-2x";

    eleButton.appendChild(eleI);
    eleLi.appendChild(eleInput);
    eleLi.appendChild(eleButton);
    listToAddElement.appendChild(eleLi);
}

saveProject = function(idFormProject) {
    var form = document.getElementById(idFormProject);

    obj = {};
    obj['name'] = form.elements['project_name'].value;
    obj['clone'] = [];
    obj['fetch'] = [];
    obj['pull'] = [];

    var keys = Object.keys(form.elements);

    for (var i = 0; i < keys.length; i++) {
        var key = keys[i];
        if (key.startsWith("command_CLONE")) {
            obj['clone'].push(form.elements[key].value);
        } else if (key.startsWith("command_FETCH")) {
            obj['fetch'].push(form.elements[key].value);
        } else if (key.startsWith("command_PULL")) {
            obj['pull'].push(form.elements[key].value);
        }
    }

    var cookie = getValueFromCookie('csrftoken');

    var xhr = new XMLHttpRequest();
    xhr.open("POST", form.action, true);
    xhr.setRequestHeader('X-CSRFToken', cookie);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            console.log('project saved!');
        } else {
            console.log('error happened!');
        }
    }
    xhr.send(JSON.stringify(obj));
    // thisObj.onclick = function() {};
}

saveLayout = function(idFormLayout) {
    var form = document.getElementById(idFormLayout);

    obj = {};
    obj['name'] = form.elements['layout_name'].value;
    obj['collect_commits_path'] = form.elements['layout_collect_commits_path'].value;

    var cookie = getValueFromCookie('csrftoken');

    var xhr = new XMLHttpRequest();
    xhr.open("POST", form.action, true);
    xhr.setRequestHeader('X-CSRFToken', cookie);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            console.log('layout saved!');
        } else {
            console.log('error happened!', res_obj);
        }
    }
    xhr.send(JSON.stringify(obj));
    // thisObj.onclick = function() {};
}

addProjectToLayout = function(addProjectUrl) {
    var cookie = getValueFromCookie('csrftoken');

    var xhr = new XMLHttpRequest();
    xhr.open("POST", addProjectUrl, true);
    xhr.setRequestHeader('X-CSRFToken', cookie);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            console.log('default project created!');
            window.location=res_obj['data']['redirect'];
        } else {
            console.log('error happened!', res_obj);
        }
    }
    xhr.send("");
}
