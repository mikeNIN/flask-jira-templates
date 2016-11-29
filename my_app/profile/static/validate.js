/**
 * Created by mikenin on 10/28/16.
 */

function check_input(text) {
	var tester = /(^[1-9]h\s?\d+m?$)|(^\d+m?)$/i;
	var trimmed = text.trim();
  var result = tester.exec(trimmed);
  console.log(result);
}


function init() {
	document.getElementById("info_icon").addEventListener("click", showInfo, false);


var form = document.forms.myform
	var elem = form.elements

form.onsubmit = function () {
	console.log(elem.time_spent.value);
  check_input(elem.time_spent.value);
  return false;
}

function showInfo(e) {

	info = document.getElementById("info_text");
  info.style.display = info.style.display === 'none' ? '' : 'none';
}


}

document.addEventListener("DOMContentLoaded", init, false);