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