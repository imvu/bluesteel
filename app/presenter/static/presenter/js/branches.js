change_branch_merge_target = function(thisObj, url, current_branch) {
    obj = {}
    obj['current_branch_name'] = current_branch;
    obj['target_branch_name'] = thisObj.options[thisObj.selectedIndex].value;

    executeAndReload(url, JSON.stringify(obj));
}
