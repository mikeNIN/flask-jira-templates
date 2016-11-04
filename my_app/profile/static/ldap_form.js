/**
 * Created by Michal Freygant on 10/19/16.
 */

var search_result;

function init(){
    
    var form = document.getElementById('my-form');
    
    
    
    
}


    $('form').submit(function (e) {
        e.preventDefault();
        // get user name to search
        var name_to_search = $('input[name=user_search]').val();

        var proceed = false;
        if (name_to_search === "") {
            name_to_search.css('border-color', 'red');
            proceed = false;
        }

        if (proceed) {
            $.getJSON('/_search_user', {
                in_string: name_to_search
            }, function (data) {
                // $("#result").text(data.result);
                search_result = data.result;
                populate_select();
            });
            return false;
        }
    });

    function process_results(input) {
        if (input.length == 0) {
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
        if (users == -1) {
            message = "Found 0 entries!";
            message_span.innerHTML = message;
        } else {
            var users_len = Object.keys(users).length;
            message = "Found " + users_len + " entries";
            message_span.innerHTML = message;
            // get parent in drop-down
            var ul = document.getElementById("ldap_results");
            // let's remove old li elements if present
            while (document.getElementById("ldap_element") != undefined) {
                var child = document.getElementById("ldap_element");
                ul.removeChild(child);
            }
            // get info to list

            for (var i = 0; i < users_len; i++) {
                var key = Object.keys(users)[i];
                console.log(key);
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
            ul.className = ul.className.replace(/hidden/, '');
        }
        message_span.className = message_span.className.replace(/hidden/, '');

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

document.addEventListener("DOMContentLoaded", init, false);
