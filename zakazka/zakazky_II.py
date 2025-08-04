from bs4 import BeautifulSoup
from .nuts import parse_nuts
#from geturl import geturl
from .geturl_II import geturl
from .bs_clean import clean_html
from .vestnik2url import vestnik2zakazky_list, zakazka_detail, Zakazka
from .old_zakazky import old_zakazka2dict
import re
from functools import wraps

from .utility import BeautifulSoupMakeTag
from .utility import debug_decorator
from datetime import datetime, timedelta

from .zakazky_II_html import make_html, zakazka_dict2html

import requests
import json

from time import sleep
from pprint import pprint


import subprocess
import sys

#subprocess.check_call([sys.executable, "-m", "pip", "install", "devtools"])
#subprocess.check_call([sys.executable, "-m", "pip", "install", "pygments"])
#subprocess.check_call([sys.executable, "-m", "pip", "install", "tenacity"])


from devtools import debug as pprint
from devtools import debug as print

# import pickle
# from testovaci_formulare import testovaci_formulare
# with open("testovaci_bloby.pickle", "rb") as handle:
    # testovaci_bloby = pickle.load(handle)


    
bs_new = BeautifulSoupMakeTag().new_tag

def vvz_zakazka2dict(zakazka):

    print("f"*20)
    pprint(zakazka)
    print("f"*20)
    
    debug_file = open("zakazka2dict_debug.html", "w", encoding='utf-8')
    debug_container = bs_new("div", id="debug_container")

    zakazka_dict = {}
    
    
    hodnoty = ParseCena(zakazka, debug_container)
    if hodnoty:
        zakazka_dict['hodnota'], zakazka_dict["predp_hodnota_bez_dph"] = hodnoty
    else:
        zakazka_dict['hodnota'], zakazka_dict["predp_hodnota_bez_dph"] = None, "neuvedeno"
    print("predp_hodnota_bez_dph: ", zakazka_dict["predp_hodnota_bez_dph"], file=debug_file)
    
    zakazka_dict["predp_hodnota_popis"] = "neuvedeno"
    
    
    zakazka_dict["obec"] = ParseKodNuts(zakazka, debug_container)
    print("obec: ", zakazka_dict["obec"], file=debug_file)
    
    zakazka_dict["zadavatel"] = ParseZadavatel(zakazka, debug_container)
    print("zadavatel: ", zakazka_dict["zadavatel"], file=debug_file)
    
    zakazka_dict["nazev_vz"] = ParseNazev(zakazka, debug_container)
    print("nazev_vz: ", zakazka_dict["nazev_vz"], file=debug_file)
    
    zakazka_dict["datum_uverejneni"] = zakazka['datumUverejneniVvz']
    print("datum_uverejneni: ", zakazka_dict["datum_uverejneni"], file=debug_file)
    parsed_date = datetime.fromisoformat(zakazka_dict["datum_uverejneni"])
    date_only = parsed_date.date()
    euro_date = date_only.strftime('%d/%m/%Y')
    zakazka_dict["datum_uverejneni"] = euro_date
    print("datum_uverejneni: ", zakazka_dict["datum_uverejneni"], file=debug_file)
    if zakazka['predchozi_vyhledavani']:
        zakazka_dict["datum_uverejneni"] = f'{zakazka_dict["datum_uverejneni"]} (uveřejnění po provedeném vyhledávání)'
    
    
    
    zakazka_dict["evidencni_cislo"] = zakazka['evCisloZakazkyVvz']
    print("evidencni_cislo: ", zakazka_dict["evidencni_cislo"], file=debug_file)
    
    zakazka_dict["typ_formulare"] = 'řádný' if zakazka['evCisloZakazkyVvz'][1:] == zakazka['evCisloFormulareVvz'][1:] else 'opravný'
    print("typ_formulare: ", zakazka_dict["typ_formulare"], file=debug_file)
    
    
    druh_formulare_translate = {
        'F01': 'Předběžné oznámení',
        'F02': 'Oznámení o zahájení zadávacího řízení',
        'F03': 'Oznámení o výsledku zadávacího řízení',
        'F04': 'Pravidelné předběžné oznámení – veřejné služby',
        'F05': 'Oznámení o zahájení zadávacího řízení – veřejné služby',
        'F06': 'Oznámení o výsledku zadávacího řízení – veřejné služby',
        'F07': 'Systém kvalifikace - veřejné služby ',
        'F08': 'Oznámení na profilu zadavatele',
        'F12': 'Oznámení soutěže o návrh',
        'F13': 'Výsledky soutěže o návrh',
        'F14': 'Oprava - Oznámení změn nebo dodatečných informací',
        'F15': 'Oznámení o dobrovolné průhlednosti ex ante',
        'F16': 'Oznámení předběžných informací – obrana a bezpečnost',
        'F17': 'Oznámení o zakázce – obrana a bezpečnost',
        'F18': 'Oznámení o zadání zakázky – obrana a bezpečnost',
        'F19': 'Oznámení o subdodávce – obrana a bezpečnost',
        'F20': 'Oznámení o změně',
        'F21': 'Sociální a jiné zvláštní služby – veřejné zakázky',
        'F22': 'Sociální a jiné zvláštní služby – veřejné služby',
        'F23': 'Sociální a jiné zvláštní služby – koncese',
        'F24': 'Oznámení o zahájení koncesního řízení',
        'F25': 'Oznámení o výsledku koncesního řízení',
        'CZ01': 'Předběžné oznámení podlimitního zadávacího řízení',
        'CZ02': 'Oznámení o zahájení podlimitního zadávacího řízení',
        'CZ03': 'Oznámení o výsledku podlimitního zadávacího řízení',
        'CZ04': 'Oprava národního formuláře',
        'CZ07': 'Oznámení o zahájení nabídkového řízení pro výběr dopravce k uzavření smlouvy o veřejných službách v přepravě cestujících'
        }
    
    
    zakazka_dict["druh_formulare"] = druh_formulare_translate[zakazka['druhFormulare']]
    print("druh_formulare: ", zakazka_dict["druh_formulare"], file=debug_file)
    
    
    zakazka_dict["druh_zakazky"] = ParseDruhZakazky(zakazka, debug_container)
    print("druh_zakazky: ", zakazka_dict["druh_zakazky"], file=debug_file)
    if zakazka_dict["druh_formulare"] and zakazka_dict["druh_formulare"].startswith("Předběžné oznámení"):
        zakazka_dict["druh_zakazky"] = "Předběžné oznámení"

    zakazka_dict["misto_zakazky_nuts_parsed"] = ParseKodNuts(zakazka, debug_container)
    print("misto_zakazky_nuts_parsed: ", zakazka_dict["misto_zakazky_nuts_parsed"], file=debug_file)
    if zakazka_dict["druh_zakazky"] == "Služby":
        zakazka_dict["misto_zakazky_nuts_parsed"] = "PROJEKTOVÉ PRÁCE"
    
    zakazka_dict["rizeni"] = ParseRizeni(zakazka, debug_container)
    print("rizeni: ", zakazka_dict["rizeni"], file=debug_file)
    
    zakazka_dict["lhuta_pro_nabidky"] = ParseLhutaNabidky(zakazka, debug_container)
    print("lhuta_pro_nabidky: ", zakazka_dict["lhuta_pro_nabidky"], file=debug_file)
    
    zakazka_dict["url"] = f"https://vvz.nipez.cz/formulare-zakazky/{zakazka['evCisloZakazkyVvz']}"
    print("url: ", zakazka_dict["url"], file=debug_file)
    
    
    zakazka_dict["cislo_formulare"] = zakazka['evCisloZakazkyVvz']
    print("cislo_formulare: ", zakazka_dict["cislo_formulare"], file=debug_file)

    zakazka_dict["cislo_souvisejiciho_formulare"] = zakazka['evCisloFormulareVvz']
    print("cislo_souvisejiciho_formulare: ", zakazka_dict["cislo_souvisejiciho_formulare"], file=debug_file)
    
    zakazka_dict["formulare_zakazky"] = ''
    print("formulare_zakazky: ", zakazka_dict["formulare_zakazky"], file=debug_file)
    
    print("debug_container: ", debug_container, file=debug_file)
    
    print("-"*20, end="\n\n", file=debug_file)
    
    
    zakazka_dict["debug"] = debug_container
    zakazka_dict["zdroj"] = ''
    
    return zakazka_dict

def nipez_zakazka2dict(json):
    debug_file = open("zakazka2dict_debug.html", "w", encoding='utf-8')
    debug_container = bs_new("div", id="debug_container")

    zakazka_dict = {}
    
    zakazka_dict["predp_hodnota_bez_dph"] = json['predpokladHodnota']
    print("predp_hodnota_bez_dph: ", zakazka_dict["predp_hodnota_bez_dph"], file=debug_file)
    
    zakazka_dict["predp_hodnota_popis"] = "neuvedeno"
    
    zakazka_dict["obec"] = json['hlavniMistoNUTS']
    print("obec: ", zakazka_dict["obec"], file=debug_file)
    
    zakazka_dict["zadavatel"] = json['zadavatelNazev']
    print("zadavatel: ", zakazka_dict["zadavatel"], file=debug_file)
    
    zakazka_dict["nazev_vz"] = json['nazev']
    print("nazev_vz: ", zakazka_dict["nazev_vz"], file=debug_file)
    
    zakazka_dict["datum_uverejneni"] = json['datumProfil']
    print("datum_uverejneni: ", zakazka_dict["datum_uverejneni"], file=debug_file)
    parsed_date = datetime.strptime(zakazka_dict["datum_uverejneni"], '%Y-%m-%dT%H:%M:%S')
    date_only = parsed_date.date()
    euro_date = date_only.strftime('%d/%m/%Y')
    zakazka_dict["datum_uverejneni"] = euro_date
    print("datum_uverejneni: ", zakazka_dict["datum_uverejneni"], file=debug_file)
    
    zakazka_dict["evidencni_cislo"] = json['kod']
    print("evidencni_cislo: ", zakazka_dict["evidencni_cislo"], file=debug_file)
    
    zakazka_dict["typ_formulare"] = json['typVZ']
    print("typ_formulare: ", zakazka_dict["typ_formulare"], file=debug_file)
    
    zakazka_dict["druh_formulare"] = json['druhZRNazev']
    print("druh_formulare: ", zakazka_dict["druh_formulare"], file=debug_file)
    
    zakazka_dict["druh_zakazky"] = json['druhZRNazev']
    print("druh_zakazky: ", zakazka_dict["druh_zakazky"], file=debug_file)
    
    zakazka_dict["misto_zakazky_nuts_parsed"] = json['hlavniMistoNUTS']
    print("misto_zakazky_nuts_parsed: ", zakazka_dict["misto_zakazky_nuts_parsed"], file=debug_file)
    
    zakazka_dict["rizeni"] = json['druhZRNazev']
    print("rizeni: ", zakazka_dict["rizeni"], file=debug_file)
    
    zakazka_dict["lhuta_pro_nabidky"] = json['podaniLhuta']
    print("lhuta_pro_nabidky: ", zakazka_dict["lhuta_pro_nabidky"], file=debug_file)
    parsed_date = datetime.strptime(zakazka_dict["lhuta_pro_nabidky"], '%Y-%m-%dT%H:%M:%S')
    date_only = parsed_date.date()
    euro_date = date_only.strftime('%d/%m/%Y')
    zakazka_dict["lhuta_pro_nabidky"] = euro_date
    print("lhuta_pro_nabidky: ", zakazka_dict["lhuta_pro_nabidky"], file=debug_file)
    
    
    url_part = json['kod'].replace('/', '-')
    zakazka_dict["url"] = f"https://nen.nipez.cz/verejne-zakazky/p:vz:datumPosledniUver=/detail-zakazky/{url_part}"
    print("url: ", zakazka_dict["url"], file=debug_file)
    
    
    zakazka_dict["cislo_formulare"] = json['nipezPredmetuKod']
    print("cislo_formulare: ", zakazka_dict["cislo_formulare"], file=debug_file)

    zakazka_dict["cislo_souvisejiciho_formulare"] = json['kodZakazkaProfil']
    print("cislo_souvisejiciho_formulare: ", zakazka_dict["cislo_souvisejiciho_formulare"], file=debug_file)
    
    zakazka_dict["formulare_zakazky"] = ''
    print("formulare_zakazky: ", zakazka_dict["formulare_zakazky"], file=debug_file)
    
    print("debug_container: ", debug_container, file=debug_file)
    
    print("-"*20, end="\n\n", file=debug_file)
    
    
    zakazka_dict["debug"] = debug_container
    zakazka_dict["zdroj"] = ''
    
    return zakazka_dict



# find any reference to the div's with id like: 'post-#'.
#.findAll('div', id=lambda x: x and x.startswith('post-'))

# all tags, that have two attributes
#.findAll(lambda tag: len(tag.attrs) == 2)

# return tag witg class="section"
#.findAll(lambda tag: 
#        "section" in tag.get("class", "") and 
#        tag.find("div", class_="iform-subsection")
#        )


debug_container = None

@debug_decorator(vebrose=False)
class ParseFormulareZakazky:
    """ vrátí tabulku forumáře zakázky """
    def __init__(self, cislo_zakazky):
        self.url = "".join(["https://www.vestnikverejnychzakazek.cz/SearchForm/SearchContract?contractNumber=", cislo_zakazky])
    def step_a(self):
        #content, headers, response = geturl(self.url)
        content = geturl(self.url)
        return BeautifulSoup(content, "html.parser").find("div", id="content")
    def step_b(self, element):
        return element
    def step_c(self, element):
        return element.find("div", id="SearchFormGrid")

@debug_decorator()
class ParseObec:
    """ vrátí string obec """
    def __init__(self, soup):
        self.soup = soup
    def step_a(self):
        element = self.soup.find(lambda tag: 
            tag.name == "div" and
            "iform-subsection" in tag.get("class", []) and
            "I.1) Název a adresa" in tag.stripped_strings
            )
        return element.find_next_sibling("fieldset").find("div", class_="form-frame")
    def step_b(self, element):
        return element.find("input", id="Body_AddressContractingBody_0__Town")
    def step_c(self, element):
        return element.get("value")
        
@debug_decorator()
class ParseZadavatel:
    """ vrátí string zadavatel """
    def __init__(self, zakazka):
        self.zakazka = zakazka
    def step_a(self):
        if 'CONTRACTING_BODY' in self.zakazka.keys():
            element = self.zakazka['CONTRACTING_BODY']['ADDRESS_CONTRACTING_BODY']['OFFICIALNAME']
        else:
            element = self.zakazka['CONTRACTING_AUTHORITY']['ADDRESS_CONTRACTING_BODY']['OFFICIALNAME']
        return element
        
    def step_b(self, element):
        return element
    def step_c(self, element):
        return element

@debug_decorator()
class ParseCisloZakazky:
    """ vrátí string evidenční číslo zakázky """
    def __init__(self, soup):
        self.soup = soup
    def step_a(self):
        element = self.soup.find("div", id="u71")
        return element
    def step_b(self, element):
        return re.search(r"Evidenční číslo zakázky: <a href.*?>(.*?)<", str(element), re.DOTALL)
    def step_c(self, element):
        return element.group(1).strip()

@debug_decorator()
class ParseCisloFormulare:
    """ vrátí string evidenční číslo formuláře """
    def __init__(self, soup):
        self.soup = soup
    def step_a(self):
        element = self.soup.find("div", id="u71")
        return element
    def step_b(self, element):
        return re.search(r"Evidenční číslo formuláře:(.*?)<", str(element), re.DOTALL)
    def step_c(self, element):
        return element.group(1).strip()

@debug_decorator()
class ParseCisloSouvisejicihoFormulare:
    """ vrátí string evidenční číslo souvisejiciho formuláře, nebo Neuvedeno """
    def __init__(self, soup):
        self.soup = soup
    def step_a(self):
        return self.soup
    def step_b(self, element):
        return element.find("div", id="u71")
    def step_c(self, element):
        element = re.search(r"Evidenční číslo souvisejícího formuláře: <span.*?>(.*?)<", str(element), re.DOTALL)
        if element:
            return element.group(1).strip()
        else:
            return "Neuvedeno"

@debug_decorator()
class ParseDatumUverejneni:
    """ vrátí string datum uveřejnění """
    def __init__(self, soup):
        self.soup = soup
    def step_a(self):
        return self.soup.find("div", id="u71")
    def step_b(self, element):
        return re.search(r"Datum uveřejnění ve VVZ: (\d{2}.\d{2}.\d{4})<", str(element), re.DOTALL)
    def step_c(self, element):
        return re.sub(r"\.", "/", element.group(1).strip())

@debug_decorator()
class ParseTypFormulare:
    """ vrátí string typ formuláře """
    def __init__(self, soup):
        self.soup = soup
    def step_a(self):
        result = self.soup.find("div", id="u71").find_next_sibling("div", class_="text-right")
        if not result:
            result = self.soup.find("form", method="post")
        return result
    def step_b(self, element):
        return element.find("h1")
    def step_c(self, element):
        element_h1 = element.get_text(strip=True)
        return "opravný" if re.search("oprava", element_h1, re.IGNORECASE) else "řádný"

@debug_decorator()
class ParseDruhFormulare:
    """ vrátí string druh formuláře """
    def __init__(self, soup):
        self.soup = soup
    def step_a(self):
        result = self.soup.find("div", id="u71").find_next_sibling("div", class_="text-right")
        if not result:
            result = self.soup.find("form", method="post")
        return result
    def step_b(self, element):
        return [element.find("h1"), element.find("h2")]
    def step_c(self, element):
        element_h1 = element[0].get_text(strip=True)
        text = element_h1 if element_h1 != "Oprava" else element[1].get_text(strip=True)
        return re.sub(r"^CZ[0-9][0-9] - ", "", text)

@debug_decorator()
class ParseDruhZakazky:
    """ vrátí string druh zakázky """
    def __init__(self, zakazka):
        self.zakazka = zakazka
    def step_a(self):
        if 'TYPE_CONTRACT' in self.zakazka['OBJECT_CONTRACT'].keys():
            element = self.zakazka['OBJECT_CONTRACT']['TYPE_CONTRACT']['@CTYPE']
        else:
            if 'TYPE_CONTRACT CTYPE' in self.zakazka['OBJECT_CONTRACT'].keys():
                element = self.zakazka['OBJECT_CONTRACT']['TYPE_CONTRACT CTYPE']
            else:
                element = self.zakazka['OBJECT_CONTRACT']['TYPE_CONTRACT']['@CTYPE']
        return element
        
    def step_b(self, element):
        return element
    def step_c(self, element):
        druh_zakazky_translate = {
            'WORKS': "Stavební práce",
            'SUPPLIES': "Dodávky",
            'SERVICES': "Služby"
            }
        return druh_zakazky_translate[element]

@debug_decorator()
class ParseNazev:
    """ vrátí string název """
    def __init__(self, zakazka):
        self.zakazka = zakazka
    def step_a(self):
        return self.zakazka['OBJECT_CONTRACT']['TITLE']
        
    def step_b(self, element):
        if isinstance(element, dict):
            element = element['P']
        return element
    def step_c(self, element):
        return element

@debug_decorator()
class ParseKodNuts:
    """ vrátí string kód NUTS """
    def __init__(self, zakazka):
        self.zakazka = zakazka
    def step_a(self):
        return self.zakazka['OBJECT_CONTRACT']
    def step_b(self, element):
        if 'NUTS' in element.keys():
            return element['NUTS']['@CODE']
        else:
           return element['OBJECT_DESCR']['NUTS']['@CODE']
    def step_c(self, element):
        return parse_nuts(element)

@debug_decorator()
class ParseRizeni:
    """ vrátí string řízení """
    def __init__(self, zakazka):
        self.zakazka = zakazka
    def step_a(self):
        return self.zakazka['PROCEDURE']
    def step_b(self, element):
        return 'otevřené' if 'PT_OPEN' in element.keys() else 'užší'
    def step_c(self, element):
        return element

@debug_decorator()
class ParseLhutaNabidky:
    """ vrátí string lhůta pro nabídky """
    def __init__(self, zakazka):
        self.zakazka = zakazka
    def step_a(self):
        return self.zakazka['PROCEDURE']['DATE_RECEIPT_TENDERS']
    def step_b(self, date):
        parsed_date = datetime.strptime(date, '%Y-%m-%d')
        return parsed_date.date()
    def step_c(self, date):
        return date.strftime('%d/%m/%Y')

@debug_decorator()
class ParseCena:
    """ vrátí dict cena """
    def __init__(self, zakazka):
        self.zakazka = zakazka
        
        def value2float(value):
            cena = re.sub("( )+", "", value)
            cena = re.sub("[\.,]", ".", cena.strip())
            return float(cena)
        self.value2float = value2float
        
        def float2format(float, mena=""):
            mena = "" if not mena else " " + mena
            cena = "{:,.2f}".format(float).replace(",", " ")
            return "%s%s" % (cena, mena)
        self.float2format = float2format
        
        def currency2czk(float, mena=""):
            if not mena or mena == "CZK":
                return float
            else:
                return float * 27.0
        self.currency2czk = currency2czk
            
    def step_a(self):
        hodnota = self.zakazka['OBJECT_CONTRACT'].get('VAL_ESTIMATED_TOTAL', None)
        
        #https://vvz.nipez.cz/formulare-zakazky/Z2023-048511
        if not hodnota:
            hodnota = self.zakazka['OBJECT_CONTRACT'].get('OBJECT_DESCR', {}).get('VAL_OBJECT', ).get('#text', None)
        mena = 'CZK'
        if isinstance(hodnota, dict):
            hodnota = self.zakazka['OBJECT_CONTRACT'].get('VAL_ESTIMATED_TOTAL', {'#text': ''})['#text']
            mena = self.zakazka['OBJECT_CONTRACT'].get('VAL_ESTIMATED_TOTAL', {'@CURRENCY': ''})['@CURRENCY']
        return hodnota, mena
        
    def step_b(self, hodnoty):
        hodnota, mena = hodnoty
        parsed_hodnota = self.float2format(self.value2float(hodnota), mena)
        if parsed_hodnota:
            return hodnota, parsed_hodnota
        return hodnota, ""
    def step_c(self, hodnoty):
        hodnota, parsed_hodnota = hodnoty
        return hodnota, parsed_hodnota

@debug_decorator()
class ParseURL:
    """ vrátí string URL """
    def __init__(self, soup):
        self.soup = soup
    def step_a(self):
        element = self.soup.find("div", id="u71")
        return element
    def step_b(self, element):
        return element.find("a", class_="blue-link")
    def step_c(self, element):
        return "".join(["https://www.vestnikverejnychzakazek.cz", re.sub(r"PrintTxt", "Display", element.get("href"))])

def get_aktuality():
    url = "https://www.vestnikverejnychzakazek.cz/Actuality/List"
    #content, headers, response  = geturl(url)
    content = geturl(url)
    soup = BeautifulSoup(content, "html.parser").find("div", id="content")
    
    return clean_html(soup.find("tbody"))
  
def main_offline():
        
    html, left_panel, debug_panel, right_panel = make_html(search_date="")

    #content, headers, response = geturl("https://www.vestnikverejnychzakazek.cz/Form102/Display/537")
    #print(content.decode("utf-8"), file=open("form_537.html", "w", encoding='utf-8'))
    #html_blob = open("form_537.html", "r", encoding='utf-8').read()

    for key in testovaci_formulare:
        if key != "https://www.vestnikverejnychzakazek.cz/Form02/Display/106":
            continue
            pass
        print(key)

        soup = BeautifulSoup(testovaci_bloby[key], "html.parser").find("div", id="content")

        left_panel.append(zakazka_dict2html(zakazka2dict(soup)))

    with open("zakazky_II_html.html", mode="w", encoding="utf-8") as file:
        file.write(str(html))





def main():

    user_date_from = datetime.strptime('27.01.2024', "%d.%m.%Y").date()
    user_date_to = datetime.strptime('30.01.2024', "%d.%m.%Y").date()
    #user_date_to = user_date_from + timdelta(days=1)
    
    processed_zakazky_list = []
    zakazky_list = []
    
    
    # předchozí den
    formulare = ['F01', 'F02', 'F04', 'F05', 'F14', 'F16', 'F17', 'F19', 'F20', 'CZ01', 'CZ02', 'CZ04']
    for formular in formulare:
        zakazky_list += vestnik2zakazky_list(
            user_date_from=user_date_from - timedelta(days=1),
            user_time_from="17:30:00",
            user_date_to=user_date_from,
            user_time_to="00:00:00",
            druhFormulare=formular,
            druhVz='PRACE',
            )
        sleep(1)
    
    zakazky_list += vestnik2zakazky_list(
        user_date_from=user_date_from - timedelta(days=1),
        user_time_from="17:30:00",
        user_date_to=user_date_from,
        user_time_to="00:00:00",
        druhVz='SLUZBY',
        )
    for zakazka in zakazky_list:
        zakazka["predchozi_vyhledavani"] = True
    
    
    # aktuální datum
    formulare = ['F01', 'F02', 'F04', 'F05', 'F14', 'F16', 'F17', 'F19', 'F20', 'CZ01', 'CZ02', 'CZ04']
    for formular in formulare:
        zakazky_list += vestnik2zakazky_list(
            user_date_from=user_date_from,
            user_time_from="00:00:00",
            user_date_to=user_date_to + timedelta(days=1),
            user_time_to="00:00:00",
            druhFormulare=formular,
            druhVz='PRACE',
            )
        sleep(1)
    
    zakazky_list += vestnik2zakazky_list(
        user_date_from=user_date_from,
        user_time_from="00:00:00",
        user_date_to=user_date_to + timedelta(days=1),
        user_time_to="00:00:00",
        druhVz='SLUZBY',
        )
    
    
    
    print(len(zakazky_list))
    pprint(zakazky_list)
    
    
    if user_date_from == user_date_to:
        html, left_panel, debug_panel, right_panel = make_html(search_date=f"{user_date_from.strftime('%d/%m/%Y')}")
    else:
        html, left_panel, debug_panel, right_panel = make_html(search_date=f"{user_date_from.strftime('%d/%m/%Y')} - {user_date_to.strftime('%d/%m/%Y')}")
    #debug_panel.append(get_aktuality())
    
    
    stopka = 0
    for zakazka in zakazky_list:
        stopka = stopka + 1
        
        
        
        if stopka > 5:
            #continue
            pass
        
        print(zakazka)
        print(zakazka['data']['evCisloZakazkyVvz'])
        
        
        
        if zakazka['data']['evCisloZakazkyVvz'] in processed_zakazky_list:
            print('už máme')
            continue
        
        processed_zakazky_list.append(zakazka['data']['evCisloZakazkyVvz'])
        
        zk = Zakazka(id=zakazka['data']['evCisloZakazkyVvz'])
    
        zk.parse_main_zakazka()
        #pprint(zk.zakazka_dict, width=999)
        
        
        print('typ formulare: ', zk.zakazka_dict['FORMULAR'].get('@FORM', 'chybi'))
        if zk.zakazka_dict['FORMULAR'].get('@FORM', 'chybi') in ['F03', 'F06', 'CZ03']:
            print('přeskočeno pro Oznámení o výsledku')
            continue
        
        
        zk.parse_main_form()
        #pprint(zk.changes_mapping, width=999)
        
        zk.process_changes()
        print('typ formulare: ', zk.zakazka_dict['FORMULAR'].get('@FORM', 'chybi'))
        if zk.zakazka_dict['FORMULAR'].get('@FORM', 'chybi') in ['F03', 'F06', 'CZ03']:
            print('přeskočeno pro Oznámení o výsledku')
            continue
        
        zk.make_changes()
        pprint(zk.return_zakazka_dict(), width=999)
        
        zakazka_content = zk.return_zakazka_dict()
        zakazka_content['datumUverejneniVvz'] = zakazka['data']['datumUverejneniVvz']
        zakazka_content['druhFormulare'] = zakazka['data']['druhFormulare']
        zakazka_content['evCisloZakazkyVvz'] = zakazka['data']['evCisloZakazkyVvz']
        zakazka_content['evCisloFormulareVvz'] = zakazka['variableId']
        zakazka_content['predchozi_vyhledavani'] = zakazka.get('predchozi_vyhledavani', False)
        print('\nzakazka_content\n')
        print(zakazka_content)
        
        zakazka_dict = vvz_zakazka2dict(zakazka_content)
        zakazka_dict['komentar'] = zakazka_content.get('komentar', 'Neuvedeno')
        
        
        pprint(zakazka_dict, width=999)
        
        if zakazka_dict.get("druh_formulare", "").startswith("Oznámení o výsledku"):
            continue
        
        
        
        
        print(zakazka_dict)
        if zakazka_dict["druh_zakazky"] == "Služby":
            zachovat = False
            for vyzadane_slovo in vyzadane_projektovky:
                if not zakazka_dict.get("nazev_vz", None): 
                    zachovat = True
                elif not zachovat and vyzadane_slovo.lower() in zakazka_dict.get("nazev_vz", "nazev_vz").lower():
                    zachovat = True
            if not zachovat:
                continue
                #pass

        if zakazka_dict['hodnota']:
            #if float(zakazka_dict['hodnota']) >= 30.00:
            if float(zakazka_dict['hodnota']) >= 30000000.00:
                left_panel.append(zakazka_dict2html(zakazka_dict))
        else:
            left_panel.append(zakazka_dict2html(zakazka_dict))
        sleep(2)
        
        print("*" * 10)

    with open("zakazky_II_html.html", mode="w", encoding="utf-8") as file:
        file.write(str(html))



if __name__ == "__main__":
    vyzadane_projektovky = [
        'Projekt',
        'Projekční',
        'Modernizace',
        'PD',
        'Komplexní',
        'Výstavba',
        'transformace',
        'úpravy',
        'kanalizace',
        'kanaliza',
        'rekonstrukce',
        'rekonstr',
        'Pozemkové',
        'Vypracování',
        'Vyprac',
        'KoPÚ',
        'Produktové',
        'Prod',
        'Dokumentace',
        'Dokume',
        'revitalizace',
        'PDPS',
        'Stavby',
        'Stavb',
        'Povolení',
        'Provádění',
        'Provád',
        'Zpracování',
        'Zprac',
        'Rozšíření',
        'STS',
        'DUR',
        'SEZ',
        'Sanac',
        'Zelezn',
        'Železn',
        'Napoj',
        'Silnic',
        'DIAMO',
        'ekolog',
        'opatření',
        'sklad',
        'sana',
        'kontami',
        ]
 
    main()

