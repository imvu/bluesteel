executeAndReload = function(url, stringToSend) {
    var cookie = getValueFromCookie('csrftoken');

    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader('X-CSRFToken', cookie);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            location.reload();
        } else {
            console.log(res_obj);
        }
    }
    xhr.send(stringToSend);
}


executeAndRedirect = function(url, stringToSend) {
    var cookie = getValueFromCookie('csrftoken');

    var xhr = new XMLHttpRequest();
    xhr.open("POST", url, true);
    xhr.setRequestHeader('X-CSRFToken', cookie);
    xhr.onloadend = function(response) {
        var res_obj = JSON.parse(xhr.response);

        if (res_obj['status'] === 200) {
            window.location=res_obj['data']['redirect'];
        } else {
            console.log(res_obj);
        }
    }
    xhr.send(stringToSend);
}
