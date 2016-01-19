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

    var eleDiv = document.createElement('div');
    eleDiv.className = "container_input";

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
    eleDiv.appendChild(eleInput)
    eleLi.appendChild(eleDiv);
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

    executeAndReload(form.action, JSON.stringify(obj));
}

saveLayout = function(idFormLayout) {
    var form = document.getElementById(idFormLayout);

    obj = {};
    obj['name'] = form.elements['layout_name'].value;
    obj['active'] = (form.elements['layout_active'].value == 1) ? true : false;
    obj['project_index_path'] = parseInt(form.elements['layout_project_index_path'].value);

    executeAndReload(form.action, JSON.stringify(obj));
}
