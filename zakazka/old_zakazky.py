from bs4 import BeautifulSoup
from functools import wraps
from geturl_II import geturl
from utility import BeautifulSoupMakeTag
from utility import debug_decorator



bs_new = BeautifulSoupMakeTag().new_tag

@debug_decorator()
class ParseNazev:
	""" vrátí string název """

	def __init__(self, soup):
		self.soup = soup

	def step_a(self):
		element = self.soup.find(lambda tag:
			tag.name == "div" and
			"iform-subsection" in tag.get("class", []) and
			"II.1) Popis" in tag.stripped_strings
			)
		sub_element = element.find_next_sibling("fieldset")
		return sub_element.find("div", class_="form-frame")

	def step_b(self, element):
		return element.find(lambda tag:
			tag.name == "textarea" and
			tag.get("id", "").startswith(
				"FormItems_NazevPridelenyZakazceVerejnymZadavatelem")
			)

	def step_c(self, element):
		return element.get_text(strip=True)


def old_zakazka2dict(soup, url=""):
	zakazka_dict = {}
	zakazka_dict["typ"] = "" 
	zakazka_dict["predp_hodnota_bez_dph"] = ""
	zakazka_dict["predp_hodnota_popis"] = ""
	zakazka_dict["obec"] = ""
	zakazka_dict["nazev_vz"] = ""
	zakazka_dict["datum_uverejneni"] = ""
	zakazka_dict["evidencni_cislo"] = ""
	zakazka_dict["typ_formulare"] = ""
	zakazka_dict["druh_zakazky"] = None
	zakazka_dict["nazev"] = ""
	zakazka_dict["misto_zakazky_nuts_parsed"] = ""
	zakazka_dict["rizeni"] = ""
	zakazka_dict["lhuta_pro_nabidky"] = ""
	zakazka_dict["url"] = url
	
	
	
	debug_container = bs_new("div", id="debug_container")

	zakazka_dict["nazev_vz"] = ParseNazev(soup, debug_container)

	zakazka_dict["debug"] = debug_container
	zakazka_dict["zdroj"] = "zdroj zakázky"
	
	return zakazka_dict


def main():
	debug_file = open("old_zakazka_debug.html", "w", encoding='utf-8')

	url_list = [
		"https://old.vestnikverejnychzakazek.cz/cs/Form/Display/680913",
		"https://old.vestnikverejnychzakazek.cz/cs/Form/Display/680976",
		"https://old.vestnikverejnychzakazek.cz/cs/Form/Display/681099"]

	for url in url_list:
		content = geturl(url)
		soup = BeautifulSoup(content, "html.parser")
		element = soup.find("div", id="content")
		zakazka_dict = old_zakazka2dict(element, url)
		print(zakazka_dict, file=debug_file)
		print("*"*100, file=debug_file)


if __name__ == "__main__":
	main()
