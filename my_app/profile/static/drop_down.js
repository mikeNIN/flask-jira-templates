/**
 * Created by Michal Freygant on 10/28/16.
 */

var sr_categories;

function set_sr_cat (categories) {
    sr_categories = JSON.parse(categories);
}

var fill_child_categories = function (e) {
    e.preventDefault();
    var target = e.target;
    if (target.tagName === "SELECT"){
        var selected_value = target.options[target.selectedIndex].value;
        var drop_child = document.getElementById('customfield_11603_child');

        while (drop_child.options.length) {
            drop_child.remove(0);
        }

        if (selected_value === '') {
            console.log("null");
            drop_child.options[0] = new Option('None', '')
        }

        else {
        var child_options = sr_categories[selected_value];
        for (var i=0; i < child_options.length; i++) {
        var z = document.createElement("option");
        z.setAttribute("value", child_options[i]);
        var t = document.createTextNode(child_options[i]);
        z.appendChild(t);
        drop_child.appendChild(z);
        }
        }
    }
};

function init() {
    var drop_main = document.getElementById('customfield_11603');
    if (drop_main != null) {
        drop_main.addEventListener("click", fill_child_categories);

        // clear flask default in parent list
        var first_option_parent = drop_main.options[0];
        first_option_parent.removeAttribute("value");
        first_option_parent.setAttribute("value", '');
        first_option_parent.innerHTML = "None";

        // clear flask default in child list
        var drop_child = document.getElementById('customfield_11603_child');
        var first_option_child = drop_child.options[0];
        first_option_child.removeAttribute("value");
        first_option_child.setAttribute("value", '');
        first_option_child.innerHTML = "None";
    }
}

document.addEventListener("DOMContentLoaded", init, false);