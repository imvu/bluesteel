change_branch_merge_target = function(thisObj, url, current_branch) {
    var cookie = getValueFromCookie('csrftoken');

    obj = {}
    obj['current_branch_name'] = current_branch;
    obj['target_branch_name'] = thisObj.options[thisObj.selectedIndex].value;

    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader('X-CSRFToken', cookie);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            location.reload();
        } else {
        }
    }
    console.log('branches change:', obj);
    xhr.send(JSON.stringify(obj));
    thisObj.onchange = function() {};
}
