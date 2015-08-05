create_new_layout = function(thisObj, url) {
    var cookie = getValueFromCookie('csrftoken');
    console.log('hiiiii', thisObj);

    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader('X-CSRFToken', cookie);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        console.log(res_obj);
        if (res_obj['status'] === 200) {
            console.log('changing to main page!');
            window.location=res_obj['data']['layout']['url'];
        } else {
            console.log('error happened!');
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

addListElement = function(thisObj, idParent, idListToAddElement) {
    var listToAddElement = document.getElementById(idListToAddElement);

    var childCount = listToAddElement.children.length;

    var eleLi = document.createElement('li');
    eleLi.className = "no_text";
    eleLi.id = 'command_entry_new_' + (new Date()).getTime().toString();

    var eleInput = document.createElement('input');
    eleInput.className = "command_input";
    eleInput.type = "text";
    eleInput.name = "fname";
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
