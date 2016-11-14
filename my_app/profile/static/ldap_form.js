/**
 * Created by Michal Freygant on 10/19/16.
 */

var search_result;
var new_input = true;

function init() {
    var form = document.getElementById('ldap_search');
    form.addEventListener("submit", search_ldap, false);
    form.addEventListener("change", clear_all, false);
}

var handleResponse = function (status, response) {
    var response_parsed = JSON.parse(response);
    search_result = response_parsed['result'];
    populate_select();
    new_input = false;
}

var handleStateChange = function () {
    try{
        switch (httpRequest.readyState) {
            case 0 : // UNINITIALIZED
            case 1 : // LOADING
            case 2 : // LOADED
            case 3 : // INTERACTIVE
            break;
            case 4 : //COMPLETED
                handleResponse(httpRequest.status, httpRequest.responseText);
                break;
            default : alert("error");
        }
    }
    catch (e) {
        alert('Caught Exception: ' + e.description);
    }
}

function search_ldap(e) {
    e.preventDefault();
    //get input element
    var name_input = document.getElementById("user_search");
    // get user name to search
    var name_to_search = document.getElementById("user_search").value;

    var proceed = true;
    if (name_to_search === "") {
        name_input.setAttribute("style", "border-color: red");
        proceed = false;
    }
    if (proceed) {
        name_input.setAttribute("style", "border-color: none");
        httpRequest = new XMLHttpRequest();
        if (!httpRequest) {
            alert('Giving up :( Cannot create an XMLHTTP instance');
            return false;
        }
        var body = document.getElementsByTagName("BODY")[0];
        var url = body.dataset.root;
        var params = {'username': name_to_search};
        httpRequest.open('POST', url);
        //send headers
        httpRequest.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
        // call function on state change
        httpRequest.onreadystatechange = handleStateChange;
        httpRequest.send(JSON.stringify(params));
    }
}

function process_results(input) {
    if (Object.keys(input).length === 0 && input.constructor === Object) {
        return -1;
    } else {
        var users = {};
        for (var i in input) {
            //noinspection JSUnresolvedVariable,JSUnfilteredForInLoop
            users[i] = input[i].sAMAccountName;
        }
        return users
    }
}

function populate_select() {
    var message_span = document.getElementById("ldap_search_info");
    var users = process_results(search_result);
    var message = "";
    var ul = document.getElementById("ldap_results");
    if (users == -1) {
        message = "Found 0 entries!";
        message_span.innerHTML = message;
        ul.className = ul.className.replace(/nothidden/, 'hidden');

    } else {
        var users_len = Object.keys(users).length;
        message = "Found " + users_len + " entries";
        message_span.innerHTML = message;
        // get parent in drop-down
        // let's remove old li elements if present
        while (document.getElementById("ldap_element") != undefined) {
            var child = document.getElementById("ldap_element");
            ul.removeChild(child);
        }
        // get info to list

        for (var i = 0; i < users_len; i++) {
            var key = Object.keys(users)[i];
            var val = users[key];
            var text = key + " - " + val;
            // create li element
            var li = document.createElement("LI");
            li.setAttribute("value", key);
            li.setAttribute("id", "ldap_element");
            // create a element as child of li
            var a = document.createElement("A");
            var node = document.createTextNode(text);
            a.setAttribute("href", "#");
            a.appendChild(node);
            li.appendChild(a);
            ul.appendChild(li);
        }
        ul.className = ul.className.replace(/hidden/, 'nothidden');
    }
    message_span.className = message_span.className.replace(/hidden/, ' ');

    var parent = document.getElementById("ldap_results");
    parent.addEventListener("click", fill_fields);
}

function fill_fields(e) {
    // get click target
    var el = e.target;
    // get target value (username)
    var key_user = el.parentNode.getAttribute("value");
    // loop through users json with key and get values
    for (var i in search_result[key_user]) {
        if (document.querySelector("#" + i) != undefined) {
            var ldap_attr = document.querySelector("#" + i);
            //noinspection JSUnfilteredForInLoop
            ldap_attr.setAttribute("value", search_result[key_user][i]);
        }
    }
}

function clear_all() {
    if (!new_input){
        var div_results = document.getElementById("ldap_user_info").getElementsByTagName("div");
        for (var i=0; i < div_results.length; i++){
            if (div_results[i].className === "col-md-4") {
                var input_el = div_results[i].getElementsByTagName('input')[0];
                input_el.removeAttribute("value");
            }
        }
    }
}

document.addEventListener("DOMContentLoaded", init, false);
