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

    var wrapDiv = document.createElement('div');
    wrapDiv.id = startName.toString() + (new Date()).getTime().toString() + '_new';

    var eleComDiv = document.createElement('div');
    eleComDiv.className = "grid-col-7-8 grid-cell-pad-2-10";

    var eleContainerInput = document.createElement('div');
    eleContainerInput.className = "container_input";

    var eleInput = document.createElement('input');
    eleInput.className = "command_input";
    eleInput.type = "text";
    eleInput.name = wrapDiv.id;
    eleInput.value = "<edit command here>";
    eleInput.maxlength = "255";

    var eleIconDiv = document.createElement('div');
    eleIconDiv.className = "grid-col-1-8 grid-cell-pad-2-10";

    var eleButton = document.createElement('button');
    eleButton.className = "btn_icon icon_gray";
    eleButton.onclick = createRemoveListElementCallback(wrapDiv.id);

    var eleI = document.createElement('i');
    eleI.className = "fa fa-times-circle fa-2x";

    eleButton.appendChild(eleI);
    eleIconDiv.appendChild(eleButton);
    eleContainerInput.appendChild(eleInput);
    eleComDiv.appendChild(eleContainerInput);
    wrapDiv.appendChild(eleComDiv);
    wrapDiv.appendChild(eleIconDiv);

    listToAddElement.appendChild(wrapDiv);
}

saveProject = function(idFormProject) {
    var form = document.getElementById(idFormProject);

    obj = {};
    obj['name'] = form.elements['project_name'].value;
    obj['git_project_folder_search_path'] = form.elements['git_project_folder_search_path'].value;
    obj['clone'] = [];
    obj['fetch'] = [];

    for (var i = 0; i < form.elements.length; i++) {
        var element = form.elements[i];
        if (element.name.startsWith("command_CLONE")) {
            obj['clone'].push(element.value);
        } else if (element.name.startsWith("command_FETCH")) {
            obj['fetch'].push(element.value);
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
