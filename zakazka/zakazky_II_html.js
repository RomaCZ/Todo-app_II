// http://jshint.com/

"use strict";

function hide_zakazky(event) {
	
	var button = event.getElementsByTagName("input");
	
	if (!button.length) { // bylo spuštěno tlačítkem přidat na zakázce
		if (document.getElementById("auto_hide").checked) {
			event.parentNode.parentNode.style.display = "none";
			}
		return;
		}

	var button_hide_pridane = document.getElementById("auto_hide").checked;
	var button_hide_zakazka = document.getElementById("zakazka_hide").checked;
	var button_hide_projektovka = document.getElementById("projektovka_hide").checked;
	
	var elements = document.getElementById("left_panel").getElementsByClassName("zakazka");
	for (var i=0, i_max=elements.length; i<i_max; i=i+1) {
		
		var je_to_projektovka = elements[i].querySelectorAll(
			".misto_zakazky_nuts_parsed option[value='PROJEKTOVÉ PRÁCE']:checked"
			).length;
		
		var je_pridano = elements[i].getElementsByClassName("pridat")[0].title !== "Přidat";
		
	
		if (
			(button[0].id === "auto_hide" && button_hide_pridane && je_pridano) ||
			(button_hide_zakazka && !je_to_projektovka) || 
			(button_hide_projektovka && je_to_projektovka)) {
			
			elements[i].style.display = "none";
			}
		
		else if (
			(!button_hide_zakazka && !je_to_projektovka) ||
			(!button_hide_projektovka && je_to_projektovka)) {
			
			if (button_hide_pridane && je_pridano) {
				continue;
				}
			
			elements[i].style.display = "block";
			}
		}
	}

function highlight(arg, only_clear=false) {
	var target_id = "dummy_value_to_remove_all_highlights"
	if (only_clear == false) {
		target_id = this.id;
		if (target_id === "") { return; }
		}

	var elements = document.getElementsByClassName("zakazka");

	for (var i=0, i_max=elements.length; i<i_max; i=i+1) {

		if (elements[i].id.indexOf(target_id) >= 0) {
			elements[i].classList.add("highlighted");
			}
		else {
			elements[i].classList.remove("highlighted");				
			}
		}
	}

function left2right(zakazka_node) {
	var zakazka_id = "r" + zakazka_node.id;
	var zakazka_right_panel = document.getElementById(zakazka_id);
	var element = zakazka_node.getElementsByTagName("select")[0];
	var kraj_right_panel_id = element.options[element.selectedIndex].text;
	var kraj_right_panel = document.getElementById(kraj_right_panel_id);

	if (zakazka_right_panel) {
		zakazka_right_panel.parentNode.removeChild(zakazka_right_panel);
		return false;
		}

	var new_zakazka = document.createElement("span");
	new_zakazka.id = zakazka_id;
	new_zakazka.className = "zakazka";

	var wrapper_all = zakazka_node.getElementsByClassName("wrapper");
	var delimeter = document.createElement("br");
	
	for (var i=0, i_max = wrapper_all.length; i<i_max; i=i+1) {
		
		if (wrapper_all[i].classList.contains("hidden_whole")) {
			continue;
			}

		var popis = wrapper_all[i].getElementsByClassName("popis")[0];
		var hodnota = wrapper_all[i].getElementsByClassName("hodnota")[0];
		var new_line = document.createElement("span");
		new_line.innerHTML = popis.textContent;
		
		var new_line_child = document.createElement("span");
		new_line_child.innerHTML = hodnota.textContent;

		if (hodnota.classList.contains("url")) {
			new_line_child.innerHTML = "<a href='" + 
				hodnota.textContent + "'>" + 
				hodnota.textContent + 
				"</a>";
			}

		if (hodnota.classList.contains("nazev_vz")) {
			new_line_child.style.color = "red";
			new_line_child.style.fontWeight = "bold";
			}
		
		if (hodnota.classList.contains("druh_rizeni")) {
			new_line_child.style.color = "#006FBF";
			new_line_child.style.fontWeight = "bold";
			}
		
		//classList hodnota rizeni
/* 		if (hodnota.classList.contains("rizeni")) {
			if (hodnota.textContent == "užší") {
				if (kraj_right_panel_id != "PROJEKTOVÉ PRÁCE") {
					new_line_child.style.backgroundColor = "yellow";
					}
				}
			} */

		if (hodnota.classList.contains("rizeni_oznameni")) {
			new_line_child.style.color = "#006FBF";
			new_line_child.style.fontWeight = "bold";
			}

		if (hodnota.classList.contains("komentar")) {
			if (hodnota.textContent.trim() == "Neuvedeno") {
				continue;
				}
			else {
				kraj_right_panel = document.getElementById("ZAKÁZKY S KOMENTÁŘEM");
				new_line_child.innerHTML = "Místo zakázky: " + 
					kraj_right_panel_id + 
					"; " + 
					new_line_child.innerHTML;
				}
			}

		new_line.appendChild(new_line_child);
		new_zakazka.appendChild(new_line);
		
		delimeter = document.createElement("br");
		new_zakazka.appendChild(delimeter);
		}
	
	new_zakazka.appendChild(document.createElement("br"));

	kraj_right_panel.appendChild(new_zakazka);
	return true;
	}

function make_count() {
	document.getElementById("counter_a").innerHTML = document.getElementById("right_panel")
		.getElementsByClassName("zakazka").length;
	
	document.getElementById("counter_b").innerHTML = document.querySelectorAll(
		".misto_zakazky_nuts_parsed option[value]:checked:not([value='PROJEKTOVÉ PRÁCE'])"
		).length;
	
	document.getElementById("counter_c").innerHTML = document.querySelectorAll(
		".misto_zakazky_nuts_parsed option[value='PROJEKTOVÉ PRÁCE']:checked"
		).length;
	}

function reload() {
	document.body.reload = 1;
	window.location.href = window.location.href.replace(/#.*$/, '');
	}

function resize(force_resize) {
	var set_innerHeight = window.innerHeight - 60 + "px";
		
	document.getElementById("left_panel").style.height = set_innerHeight;
	document.getElementById("content").style.height = set_innerHeight;
	document.getElementById("right_panel").style.height = set_innerHeight;
	
	if (force_resize) {
		resize_columns(document.getElementById("left_panel").style.width == "50%");
		}
	else {
		resize_columns(window.innerWidth > 1000);
		}
	}

function resize_columns(bolean) {
	//tmp = (foo==1 ? true : false);
	
	document.getElementById("left_panel").style.width = bolean ? "25%" : "50%";
	
	var style_2_column = " \
		#right_panel { \
			width: 25%!important; \
			} \
		#content { \
			width: 50%!important; \
			clear: none!important; \
			} \
		";
	var style_3_column = " \
		#right_panel { \
			width: 50%!important; \
			} \
		#content { \
			width: 100%!important; \
			clear: both!important; \
			} \
		";
	var userInject = document.createElement('style');
	userInject.setAttribute("type", "text/css");
	userInject.textContent = bolean ? style_2_column : style_3_column;
	document.body.appendChild(userInject);
	}

function select_content(event) {
	event.innerHTML = (event.innerHTML === "Mark Date") ? "Mark Form" : "Mark Date";
	var toSelect = document.getElementById(
		(event.innerHTML !== "Mark Date") ? "date" : "right_panel_inner");

	highlight("arg", true);
	if (window.getSelection) { // all browsers, except IE before version 9
		var selection = window.getSelection();
		var rangeToSelect = document.createRange();
		rangeToSelect.selectNodeContents (toSelect);
		selection.removeAllRanges();
		selection.addRange (rangeToSelect);
		}
	else if (document.body.createTextRange) { // Internet Explorer
		var rangeToSelect = document.body.createTextRange();
		rangeToSelect.moveToElementText (toSelect);
		rangeToSelect.select();
		}
	}

function show_debug() {
	document.getElementById("content_inner").innerHTML = 
		document.getElementById("debug_panel").innerHTML;
	}

function show_hide_kraj() {
	var elements = document.getElementById("right_panel_inner").getElementsByClassName("kraj");
	var elements_length;
	for (var i=0, i_max=elements.length; i<i_max; i=i+1) {
		elements_length = elements[i].getElementsByTagName("span").length;
		elements[i].style.display = (elements_length >1) ? "block" : "none";
		}
	}

function hashFnv32a(str, asString, seed) {
    /*jshint bitwise:false */
    var i, l,
        hval = (seed === undefined) ? 0x811c9dc5 : seed;

    for (i = 0, l = str.length; i < l; i++) {
        hval ^= str.charCodeAt(i);
        hval += (hval << 1) + (hval << 4) + (hval << 7) + (hval << 8) + (hval << 24);
		}
    if (asString){
        // Convert to 8 digit hex string
        return ("0000000" + (hval >>> 0).toString(16)).substr(-8);
		}
    return hval >>> 0;
	}

function random_ID() {
	var elements = document.getElementsByClassName("zakazka");

	for (var i=0, i_max=elements.length; i<i_max; i=i+1) {
		elements[i].id = "l_" + hashFnv32a(elements[i].innerHTML, true)
		}
	}

function make_clickable() {
	
	function pridat_odebrat() {
		var pridano = left2right(this.parentNode.parentNode);
		this.innerHTML = pridano ? "&#10004;" : "&#10006;";
		this.title = pridano ? "Odebrat" : "Přidat";
		show_hide_kraj();
		hide_zakazky(this);
		make_count();
		}

	function zobraz_zdroj() {
		var source = this.parentNode.parentNode;
		source = source.getElementsByClassName("zakazka_zdroj")[0];
		document.getElementById("content_inner").innerHTML = source.innerHTML;
		}

	function zobraz_debug() {
		var source = this.parentNode.parentNode;
		source = source.getElementsByClassName("zakazka_debug")[0];
		document.getElementById("content_inner").innerHTML = source.innerHTML;
		}

	var elements = document.getElementById("left_panel").getElementsByTagName("span");
	for (var i=0, i_max=elements.length; i<i_max; i=i+1) {
		switch (elements[i].className) {
			case "pridat":
				elements[i].addEventListener("click", pridat_odebrat);
				break;

			case "zdroj":
				elements[i].addEventListener("click", zobraz_zdroj);
				break;

			case "debug":
				elements[i].addEventListener("click", zobraz_debug);
				break;

			case "zakazka":
				elements[i].addEventListener("click", highlight);
				break;
			}
		}
	}

function make_right_panel_clickable() {
	document.querySelector('#right_panel_inner').addEventListener('click', function (event) {
		var element = event.target
		if (element.classList.contains("zakazka")) {
			//pass
			}
		else if (element.parentNode.classList.contains("zakazka")) {
			element = element.parentNode;
			}
		else if (element.parentNode.parentNode.classList.contains("zakazka")) {
			element = element.parentNode.parentNode;
			}
		else {
			return
			}
		element = document.getElementById(element.id.substring(1))
		element.scrollIntoView({block: "start", behavior: "smooth"});
		document.body.scrollIntoView(true)
		})
	}

function remove_comment() {

	function remove() {
		var element_node = this.parentNode.getElementsByClassName("hodnota komentar")[0];
		element_node.innerHTML = "neuvedeno"
		}

	var zakazky = document.getElementById("left_panel").getElementsByClassName("hodnota komentar");
	var button = document.createElement("button");
	button.appendChild(document.createTextNode("\u270E"));
	for (var i=0, i_max=zakazky.length; i<i_max; i=i+1) {
		zakazky[i].parentNode.insertBefore(button.cloneNode(true), zakazky[i])
			.addEventListener("click", remove);
		}
	}

function date2pretty_date() {

	function pretty_date() {
		var element_node = this.parentNode.getElementsByClassName("hodnota")[0];
		// (uveřejnění po provedeném vyhledávání)
		var [element_node_date, element_node_text] = element_node.innerHTML.split(" (uve");
		element_node.innerHTML = element_node_date.replace(/[ \u00A0 &nbsp;]/g, "").replace(/\./g, "/");
		if (element_node_text) {
			element_node.innerHTML = element_node.innerHTML + " (uveřejnění po provedeném vyhledávání)"
			}
		}

	var zakazky = document.getElementById("left_panel").getElementsByClassName("hodnota date");
	var button = document.createElement("button");
	button.appendChild(document.createTextNode("\u270E"));
	for (var i=0, i_max=zakazky.length; i<i_max; i=i+1) {
		zakazky[i].parentNode.insertBefore(button.cloneNode(true), zakazky[i])
			.addEventListener("click", pretty_date);
		}
	}

function price2pretty_price() {

	function pretty_price() {
		var element_node = this.parentNode.getElementsByClassName("hodnota")[0];
		var element_value = element_node.innerHTML.replace(/[ \u00A0 &nbsp;]/g, "")
			.replace(/,/g, ".");
		element_node.innerHTML = parseFloat(element_value).toFixed(2)
			.replace(/(\d)(?=(\d{3})+\.)/g, "$1 ") + " CZK";
		}

	var zakazky = document.getElementById("left_panel").getElementsByClassName("hodnota price");
	var button = document.createElement("button");
	button.appendChild(document.createTextNode("\u270E"));
	for (var i=0, i_max=zakazky.length; i<i_max; i=i+1) {
		zakazky[i].parentNode.insertBefore(button.cloneNode(true), zakazky[i])
			.addEventListener("click", pretty_price);
			
		}
	}

function kraje2listbox() {
	var oblasti = document.getElementById("right_panel_inner")
		.getElementsByClassName("kraj");
	var listbox = document.createElement("select");
	var option = document.createElement("option");
	listbox.className = "misto_zakazky_nuts_parsed";
	//listbox.size = 30;
	for (var i=0, i_max=oblasti.length; i<i_max; i=i+1) {
		option.text = option.value = oblasti[i].id.toUpperCase();
		listbox.add(option.cloneNode(true));
		}
	var zakazky = document.getElementById("left_panel")
		.getElementsByClassName("misto_zakazky_nuts_parsed");
	for (var i=0, i_max=zakazky.length; i<i_max; i=i+1) {
		var listbox_clone = listbox.cloneNode(true);
		listbox_clone.value = zakazky[i].innerHTML.toUpperCase();
		zakazky[i].parentNode.replaceChild(listbox_clone, zakazky[i]);
		}
	}

function rizeni2listbox() {
	
	function pretty_rizeni(event) {
		var element_node = this.parentNode.getElementsByClassName("hodnota")[0];
		element_node.innerHTML = this.value.slice(1).trim();
		}

	var listbox = document.createElement("select");
	listbox.className = "select_rizeni";
	var option = document.createElement("option");
	var listbox_options = ["\u270E ", "\u270E otevřené", "\u270E užší"];
	for (var i=0, i_max=listbox_options.length; i<i_max; i=i+1) {
		option.text = listbox_options[i];
		listbox.add(option.cloneNode(true));
		}
	var zakazky = document.getElementById("left_panel")
		.getElementsByClassName("hodnota rizeni");
	for (var i=0, i_max=zakazky.length; i<i_max; i=i+1) {
		zakazky[i].parentNode.insertBefore(listbox.cloneNode(true), zakazky[i])
			.addEventListener("change", pretty_rizeni);
		}
	}

function on_load() {
	random_ID();
	date2pretty_date();
	remove_comment();
	kraje2listbox();
	make_clickable();
	make_right_panel_clickable()
	make_count();
	price2pretty_price();
	resize();
	rizeni2listbox();
	show_debug();
	window.addEventListener('resize', function(event){ resize(); });
	window.addEventListener("beforeunload", function (e) {
		if (!document.body.reload) {
			var confirmationMessage = "\o/";
			e.returnValue = confirmationMessage;     // Gecko and Trident
			return confirmationMessage;              // Gecko and WebKit
			}
		});

	date2pretty_date = undefined;
	kraje2listbox = undefined;
	make_clickable = undefined;
	make_right_panel_clickable = undefined;
	on_load = undefined;
	price2pretty_price = undefined;
	rizeni2listbox = undefined;
	}