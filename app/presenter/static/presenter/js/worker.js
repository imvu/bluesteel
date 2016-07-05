saveWorker = function(idFormProject) {
    var form = document.getElementById(idFormProject);

    obj = {};
    obj['description'] = form.elements['worker_description'].value;
    obj['git_feeder'] = form.elements['worker_git_feeder'].value === "yes";
    obj['max_feed_reports'] = parseInt(form.elements['max_feed_reports'].value);

    console.log(obj, form.action);

    executeAndReload(form.action, JSON.stringify(obj));
}
