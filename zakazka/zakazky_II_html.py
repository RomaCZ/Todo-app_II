from bs4 import BeautifulSoup
from utility import BeautifulSoupMakeTag



bs_new = BeautifulSoupMakeTag().new_tag

def make_html(search_date="09/02/2016 - 09/02/2016"):
	html = bs_new("html")
	head = bs_new("head", parent_=html)
	body = bs_new("body", onload="on_load()", parent_=html)

	bs_new("title", string_=" ".join(["HOCHTIEF - zakázky", search_date]), parent_=head)
	bs_new("meta", charset="utf-8", parent_=head)
	bs_new("meta", content="no-cache", httpequiv_="Pragma", parent_=head)
	bs_new("meta", content="-1", httpequiv_="Expires", parent_=head)
	with open("zakazky_II_html.css", mode="r", encoding="utf-8") as css:
		bs_new("style", string_=css.read(), parent_=head)
	with open("zakazky_II_html.js", mode="r", encoding="utf-8") as js:
		bs_new("script", string_=js.read(), parent_=head)

	header = bs_new("div", id="header", parent_=body)
	
	buttons = bs_new("span", id="buttons", parent_=header)
	auto_hide = bs_new("label", onclick="hide_zakazky(this)", class_="switch", string_="\u2193 Skryj přidané", parent_=buttons)
	bs_new("input", id="auto_hide", type="checkbox", checked="true", parent_=auto_hide)
	zakazka_hide = bs_new("label", onclick="hide_zakazky(this)", class_="switch", string_="Skryj zakázky", parent_=buttons)
	bs_new("input", id="zakazka_hide", type="checkbox", parent_=zakazka_hide)
	projektovka_hide = bs_new("label", onclick="hide_zakazky(this)", class_="switch", string_="Skryj projektovky", parent_=buttons)
	bs_new("input", id="projektovka_hide", type="checkbox", parent_=projektovka_hide)
	bs_new("button", onclick="select_content(this)", string_="Mark Date",  parent_=buttons)
	bs_new("button", onclick="show_debug()", string_="Debug \u2622",  parent_=buttons)
	bs_new("button", onclick="resize(true)", string_="Resize \u2943",  parent_=buttons)
	bs_new("button", onclick="reload()", string_="Reload \u21BB",  parent_=buttons)
	
	bs_new("span", id="date", string_=" ".join(["HOCHTIEF - zakázky", search_date]), parent_=header)
	counter = bs_new("span", id="counter", string_="Označeno ", parent_=header)
	bs_new("span", id="counter_a", string_="?", parent_=counter)
	bs_new("span", string_=" z ", parent_=counter)
	bs_new("span", id="counter_b", string_="?", parent_=counter)
	bs_new("span", string_=" zakázek a z ", parent_=counter)
	bs_new("span", id="counter_c", string_="?", parent_=counter)
	bs_new("span", string_=" projektovek.", parent_=counter)
	
	left_panel = bs_new("div", id="left_panel", parent_=body)

	right_panel = bs_new("div", id="right_panel", parent_=body)

	content = bs_new("div", id="content", parent_=body)
	bs_new("div", id="content_inner", parent_=content)

	debug_panel = bs_new("div", id="debug_panel", style="display: none;", parent_=body)

	bs_new("div", id="debug_container", style="display:None;", parent_=body)

	bs_new("div", id="footer", parent_=body)
	
	right_panel_inner = bs_new("div", id="right_panel_inner", class_="inner", style="font: 11.0pt Calibri, sans-serif;", parent_=right_panel)
	
	nuts_list = (
		"Zakázky s komentářem",
		"Česká republika",
		"Praha",
		"Hlavní město Praha",
		"Střední Čechy",
		"Středočeský kraj",
		"Jihozápad",
		"Jihočeský kraj",
		"Plzeňský kraj",
		"Severozápad",
		"Karlovarský kraj",
		"Ústecký kraj",
		"Severovýchod",
		"Liberecký kraj",
		"Královéhradecký kraj",
		"Pardubický kraj",
		"Jihovýchod",
		"Vysočina",
		"Jihomoravský kraj",
		"Střední Morava",
		"Olomoucký kraj",
		"Zlínský kraj",
		"Moravskoslezský kraj",
		"---",
		"PROJEKTOVÉ PRÁCE")
	for nut in nuts_list:
		kraj = bs_new("span", id=nut.upper(), class_="kraj", style="display:none;", parent_=right_panel_inner)
		kraj_text = bs_new("span", string_=nut.upper(), style="font-weight: bold; text-decoration: underline;", parent_=kraj)
		bs_new("br", parent_=kraj)
	
		if nut == "Zakázky s komentářem":
			kraj["style"] = "display:none; background: red;"
		
		if nut == "PROJEKTOVÉ PRÁCE":
			kraj_text["style"] = "font-weight: bold; text-decoration: underline; color: lime;"

	
	return html, left_panel, debug_panel, right_panel

def zakazka_dict2html(zakazka_dict):

	form_stavebni_prace = (
		{"text": "Evidenční číslo: ", "key": "evidencni_cislo"},

		{"text": "Místo zakázky: ", "key": "misto_zakazky_nuts_parsed",
			"class": "misto_zakazky_nuts_parsed",
			"class_parent": "hidden_whole"},

		{"text": "Druh zakazky: ", "key": "druh_zakazky",
			"class_parent": "hidden_whole"},

		{"text": "Typ formuláře: ", "key": "typ_formulare"},

		{"text": "Druh formuláře: ", "key": "druh_formulare"},

		{"text": "Zadavatel: ", "key": "zadavatel"},

		{"text": "Název VZ: ", "key": "nazev_vz",
			"class": "nazev_vz"},

		{"text": "Předp. hodnota bez DPH: ", "key": "predp_hodnota_bez_dph",
			"class": "price"},

		{"text": "predp_hodnota_popis: ", "key": "predp_hodnota_popis",
			"class_parent": "hidden_whole"},

		{"text": "Druh řízení: ", "key": "rizeni",
			"class": "rizeni"},

		{"text": "Lhůta pro nabídky/žádosti: ", "key": "lhuta_pro_nabidky",
			"class": "date"},

		{"text": "Datum uveřejnění: ",
			"key": "datum_uverejneni"}
		)

	form_predbezne_oznameni = (
		{"text": "Evidenční číslo: ", "key": "evidencni_cislo"},

		{"text": "Místo zakázky: ", "key": "misto_zakazky_nuts_parsed",
			"class": "misto_zakazky_nuts_parsed",
			"class_parent": "hidden_whole"},

		{"text": "Druh zakazky: ", "key": "druh_zakazky",
			"class_parent": "hidden_whole"},

		{"text": "Druh řízení: ", "key": "druh_formulare",
			"class": "druh_rizeni"},

		{"text": "Typ formuláře: ", "key": "typ_formulare"},

		{"text": "Zadavatel: ", "key": "zadavatel"},

		{"text": "Název VZ: ", "key": "nazev_vz",
			"class": "nazev_vz"},

		{"text": "Předp. hodnota bez DPH: ", "key": "predp_hodnota_bez_dph",
			"class": "price"},

		{"text": "predp_hodnota_popis: ", "key": "predp_hodnota_popis",
			"class_parent": "hidden_whole"},

		{"text": "Předpokládané datum zahájení zadávacího řízení: ",
			"key": "lhuta_pro_nabidky",
			"class": "date"},

		{"text": "Datum uveřejnění: ", "key": "datum_uverejneni"}
		)

	form_sluzby = (
		{"text": "Evidenční číslo: ", "key": "evidencni_cislo"},

		{"text": "Místo zakázky: ", "key": "misto_zakazky_nuts_parsed",
			"class": "misto_zakazky_nuts_parsed",
			"class_parent": "hidden_whole"},

		{"text": "Druh zakazky: ", "key": "druh_zakazky",
			"class": "druh_zakazky",
			"class_parent": "hidden_whole"},

		{"text": "Typ formuláře: ", "key": "typ_formulare"},

		{"text": "Druh formuláře: ", "key": "druh_formulare"},

		{"text": "Zadavatel: ", "key": "zadavatel"},

		{"text": "Název VZ: ", "key": "nazev_vz",
			"class": "nazev_vz"},

		{"text": "Předp. hodnota bez DPH: ", "key": "predp_hodnota_bez_dph",
			"class": "price"},

		{"text": "predp_hodnota_popis: ", "key": "predp_hodnota_popis",
			"class_parent": "hidden_whole"},

		{"text": "Druh řízení: ", "key": "rizeni",
			"class": "rizeni"},

		{"text": "Lhůta pro nabídky/žádosti: ", "key": "lhuta_pro_nabidky",
			"class": "date"},

		{"text": "Datum uveřejnění: ", "key": "datum_uverejneni"}
		)

	form_dict = {"Stavební práce": form_stavebni_prace,
		"Předběžné oznámení": form_predbezne_oznameni,
		"Služby": form_sluzby,
		None: form_stavebni_prace}

	zakazka_html = bs_new("span",
		class_="zakazka",
		id="".join(["l_", zakazka_dict.get("evidencni_cislo", "")]),
		style="display: block;")
	
	menu = bs_new("div", class_="menu", parent_=zakazka_html)
	bs_new("span",
		string_=zakazka_dict.get("evidencni_cislo", ""), parent_=menu)
	bs_new("span", class_="pridat",
		string_="\u2716", title="Přidat", parent_=menu)
	bs_new("span", class_="zdroj",
		string_="\u2605", title="Zobraz zdroj", parent_=menu)
	bs_new("span", class_="debug",
		string_="\u272A", title="Zobraz debug info", parent_=menu)

	data = bs_new("div", class_="data", parent_=zakazka_html)
	for form in form_dict.get(zakazka_dict.get("druh_zakazky", "Stavební práce"), form_dict[None]):
		wrapper = bs_new("div",
			class_=" ".join(
				filter(None, ["wrapper", form.get("class_parent")])),
			parent_=data)

		popis = bs_new("div", class_="popis",
			string_=form["text"], parent_=wrapper)
		if zakazka_dict.get(form["key"], None) in (None, "---", "Neuvedeno"):
			popis["class"] = " ".join(["popis", "missing"])
		elif "formulář byl zneplatněn" in str(zakazka_dict.get(form["key"], None)):
			popis["class"] = " ".join(["popis", "warning"])
			
		hodnota = bs_new("div",
			class_=" ".join(filter(None, ["hodnota", form.get("class")])),
			contenteditable="true",
			string_=zakazka_dict.get(form["key"]),
			parent_=wrapper)
	
	url_wrapper = bs_new("div", class_="wrapper", parent_=data)
	bs_new("div", class_="popis", string_="Formulář: ", parent_=url_wrapper)
	url = bs_new("div", class_="hodnota url", parent_=url_wrapper)
	bs_new("a", href=zakazka_dict.get("url", ""),
		string_=zakazka_dict.get("url", ""), parent_=url)
	
	komentar = bs_new("div", class_="wrapper", parent_=data)
	bs_new("div", class_="popis", string_="Komentář: ", parent_=komentar)
	bs_new("div", class_="hodnota komentar",
		string_=zakazka_dict.get("komentar", "Neuvedeno"), contenteditable="true", parent_=komentar)
	
	delimeter = bs_new("div", parent_=data)
	delimeter_span = bs_new("span", parent_=delimeter)
	bs_new("br", parent_=delimeter_span)
	
	debug = bs_new("div", class_="zakazka_debug",
		style="display:None;", parent_=zakazka_html)
	bs_new("h1", string_="Zakázka debug", parent_=debug)
	debug.append(zakazka_dict.get("debug", ""))
	
	zdroj = bs_new("div", class_="zakazka_zdroj",
		style="display:None;", parent_=zakazka_html)
	bs_new("h1", string_="Zakázka zdroj", parent_=zdroj)
	zdroj.append(zakazka_dict.get("zdroj", ""))
	
	bs_new("br", parent_=zakazka_html)

	return zakazka_html

if __name__ == "__main__":

	html, left_panel, debug_panel, right_panel = make_html()
	
	zakazka_dict = {}
	zakazka_dict["typ"] = "oznameni" 
	zakazka_dict["predp_hodnota_bez_dph"] = "300 000 000.00 CZK"
	zakazka_dict["predp_hodnota_popis"] = "hodnota je predpokladana; fixní"
	zakazka_dict["obec"] = "PRAHA"
	zakazka_dict["nazev_vz"] = "Městská část Praha 17"
	zakazka_dict["datum_uverejneni"] = "07/07/2016"
	zakazka_dict["evidencni_cislo"] = "518660"
	zakazka_dict["typ_formulare"] = "Opravný"
	zakazka_dict["druh_zakazky"] = "Oznámení o zakázce"
	zakazka_dict["nazev"] = "Víceúčelové sportovní centrum Na Chobotě"
	zakazka_dict["misto_zakazky_nuts_parsed"] = "HLAVNÍ MĚSTO PRAHA"
	zakazka_dict["rizeni"] = "Otevřené"
	zakazka_dict["lhuta_pro_nabidky"] = "12/07/2016"
	zakazka_dict["url"] = "www.fjfjfj.com"
	zakazka_dict["debug"] = "debug zakázky"
	zakazka_dict["zdroj"] = "zdroj zakázky"

	left_panel.append(zakazka_dict2html(zakazka_dict))
	
	with open("zakazky_II_html.html", mode="w", encoding="utf-8") as file:
		
		file.write(str(html))

