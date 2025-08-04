import collections
collections.Callable = collections.abc.Callable


from bs4 import BeautifulSoup
from nuts import parse_nuts

# from geturl import geturl
from geturl_II import geturl
from bs_clean import clean_html
from vestnik2url import vestnik2zakazky_list, zakazka_detail, Zakazka
from old_zakazky import old_zakazka2dict
import re
from functools import wraps

from utility import BeautifulSoupMakeTag
from utility import debug_decorator
from datetime import datetime, timedelta

from zakazky_II_html import make_html, zakazka_dict2html

import requests
import json

from time import sleep
from pprint import pprint


import subprocess
import sys

# subprocess.check_call([sys.executable, "-m", "pip", "install", "devtools"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "pygments"])
# subprocess.check_call([sys.executable, "-m", "pip", "install", "tenacity"])


from devtools import debug as pprint


from vvz import VvzCrawler


bs_new = BeautifulSoupMakeTag().new_tag


def vvz_zakazka2dict(soup):
    pass


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
        
        element = self.zakazka["data"]["ND-Root"]
        
        #"ORG-0002"
        #"ORG-0003"

        try:
            poradi = element["ND-ContractingParty"][0]["ND-Buyer"]["OPT-300-Procedure-Buyer"]
            # id="ND-Root.ND-ContractingParty.1.ND-Buyer.OPT-300-Procedure-Buyer"
        except KeyError:
            poradi = element["ND-ContractingParty"][0]["ND-ServiceProvider"]["OPT-300-Procedure-Buyer"]
            # id="ND-Root.ND-ContractingParty.0.ND-ServiceProvider.OPT-300-Procedure-Buyer"

                
        #poradi = int(poradi.split("-")[1])-1
                 

        return (element, poradi)
        
    def step_b(self, acko):
        element, poradi = acko
        organizations = element["ND-RootExtension"]["ND-Organizations"]["ND-Organization"]
        for organization in organizations:
            if organization["ND-Company"]["OPT-200-Organization-Company"] == poradi:
                return organization["ND-Company"]["BT-500-Organization-Company"]
    def step_c(self, element):
        return element

@debug_decorator()
class ParseNezpracovaneZmeny:
    """ vrátí string Nezpracovane Zmeny """
    def __init__(self, zakazka):
        self.zakazka = zakazka
    def step_a(self):
        try:
            element = self.zakazka["data"]["ND-Root"]["ND-RootExtension"]["ND-Changes"]["ND-Change"]
        except KeyError:
            element = [{}]
        
        return element
        
    def step_b(self, elements):
        value = ''
        for element in elements:
            for key in element.keys():
                if isinstance(element[key], str):
                    element[key] = element[key].replace("Původní ", "<br/><br/><b>Původní</b> ").replace("Aktuální ", "<br/><b>Aktuální</b> ")
                    element[key] = element[key].replace("Změna ", "<br/><br/><b style='color:red;'>Změna</b> ")
                    element[key] = element[key].replace("<br/><br/><br/><br/>", "<br/><br/>")

                    
                if not isinstance(element[key], bool):
                    if not isinstance(element[key], list):
                        value += f"{element[key]}<br/>"
        if not value:
            return "nic"
        return value
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
    def __init__(self, zakazka):
        self.zakazka = zakazka
    def step_a(self):
        createdAt = self.zakazka["createdAt"]
        updatedAt = self.zakazka.get("updatedAt", createdAt)  # nevím jestli takto musím, možná má i nová zakaázka updatedat?

        return max(datetime.fromisoformat(createdAt), datetime.fromisoformat(updatedAt))

    def step_b(self, element):
        #"2024-02-07T14:01:00+01:00"  
        return element

    def step_c(self, element):
        date_only = element.date()
        euro_date = date_only.strftime('%d/%m/%Y')


        return euro_date

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
        return self.zakazka["data"]["ND-Root"]["ND-ProcedureProcurementScope"]

    def step_b(self, element):
        return element['BT-23-Procedure']
    def step_c(self, element):
        druh_zakazky_translate = {
            'works': "Stavební práce",
            'supplies': "Dodávky",
            'services': "Služby"
            }
        return druh_zakazky_translate[element]

@debug_decorator()
class ParseNazev:
    """ vrátí string název """
    def __init__(self, zakazka):
        self.zakazka = zakazka
    def step_a(self):
        element =  self.zakazka["data"]["ND-Root"]
        try:
            return element["ND-ProcedureProcurementScope"]["BT-21-Procedure"]
        except KeyError:
            return element["ND-Lot"][0]["ND-LotProcurementScope"]["BT-21-Lot"]

            
    def step_b(self, element):
        
        return element
    def step_c(self, element):
        return element

@debug_decorator()
class ParseKodNuts:
    """ vrátí string kód NUTS """
    def __init__(self, zakazka):
        self.zakazka = zakazka
    def step_a(self):
        return self.zakazka["data"]["ND-Root"]["ND-Lot"][0]
    def step_b(self, element):
        nuts_element = element["ND-LotProcurementScope"]["ND-LotPlacePerformance"][0]["ND-LotPerformanceAddress"]
        if "BT-5071-Lot" in nuts_element.keys():
            return nuts_element["BT-5071-Lot"]
        # https://vvz.nipez.cz/vyhledat-formular/157a705f-6ae6-404c-81d3-5c79e0c6676b
        nuts_element = self.zakazka["data"]["ND-Root"]["ND-ProcedureProcurementScope"]["ND-ProcedurePlacePerformanceAdditionalInformation"][0]["ND-ProcedurePlacePerformance"]
        
        return nuts_element["BT-5071-Procedure"]
    
    
    
    
    
    def step_c(self, element):
        
        return parse_nuts(element)

@debug_decorator()
class ParseRizeni:
    """ vrátí string řízení """
    def __init__(self, zakazka):
        self.zakazka = zakazka
    def step_a(self):
        element = self.zakazka["data"]["ND-Root"]
        return element["ND-ProcedureTenderingProcess"]["BT-105-Procedure"]
    def step_b(self, element):
        return 'otevřené' if element == "open" else 'užší'
    def step_c(self, element):
        return element

@debug_decorator()
class ParseLhutaNabidky:
    """ vrátí string lhůta pro nabídky """
    def __init__(self, zakazka):
        self.zakazka = zakazka
    def step_a(self):
        element = self.zakazka["data"]["ND-Root"]["ND-Lot"][0]["ND-LotTenderingProcess"]
        if "ND-PublicOpening" in element.keys():
            return element["ND-PublicOpening"]["BT-132(d)-Lot"]
        elif "ND-SubmissionDeadline" in element.keys():
            return element["ND-SubmissionDeadline"]["BT-131(d)-Lot"]
        else:
            return element["ND-ParticipationRequestPeriod"]["BT-1311(d)-Lot"]
        
        
    def step_b(self, date):
        parsed_date = datetime.strptime(date.split("+")[0], '%Y-%m-%d')
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
        element = self.zakazka["data"]["ND-Root"]
        

        if "ND-ProcedureValueEstimate" in element["ND-ProcedureProcurementScope"].keys():
            hodnota = element["ND-ProcedureProcurementScope"]["ND-ProcedureValueEstimate"]["BT-27-Procedure"].get('_value', None)
        else:
            hodnota = element["ND-Lot"][0]["ND-LotProcurementScope"]["ND-LotValueEstimate"]["BT-27-Lot"].get('_value', None)



        mena = 'CZK'
        return hodnota, mena
        
    def step_b(self, hodnoty):
        hodnota, mena = hodnoty
        parsed_hodnota = self.float2format(self.value2float(str(hodnota)), mena)
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


def vvz_zakazka2dict(zakazka, zakazka_vyhledavani):
    
    debug_file = open("zakazka2dict_debug.html", "w", encoding='utf-8')
    debug_container = bs_new("div", id="debug_container")
    print("debug_container: ", debug_container, file=debug_file)

    zakazka_dict = {}
    
    
    hodnoty = ParseCena(zakazka, debug_container)
    if hodnoty:
        zakazka_dict['hodnota'], zakazka_dict["predp_hodnota_bez_dph"] = hodnoty
    else:
        zakazka_dict['hodnota'], zakazka_dict["predp_hodnota_bez_dph"] = None, "neuvedeno"
    print("predp_hodnota_bez_dph: ", zakazka_dict["predp_hodnota_bez_dph"], file=debug_file)
    
    zakazka_dict["predp_hodnota_popis"] = "neuvedeno"
    

    zakazka_dict["nezpracovano"] = ParseNezpracovaneZmeny(zakazka, debug_container)
    print("nezpracovano: ", zakazka_dict["nezpracovano"], file=debug_file)
    
    

    
    zakazka_dict["obec"] = ParseKodNuts(zakazka, debug_container)
    print("obec: ", zakazka_dict["obec"], file=debug_file)
    
    zakazka_dict["zadavatel"] = ParseZadavatel(zakazka, debug_container)
    print("zadavatel: ", zakazka_dict["zadavatel"], file=debug_file)
    
    zakazka_dict["nazev_vz"] = ParseNazev(zakazka, debug_container)
    print("nazev_vz: ", zakazka_dict["nazev_vz"], file=debug_file)
    
    zakazka_dict["datum_uverejneni"] = ParseDatumUverejneni(zakazka, debug_container)
    print("datum_uverejneni: ", zakazka_dict["datum_uverejneni"], file=debug_file)
    if zakazka.get('predchozi_vyhledavani', None):

        zakazka_dict["datum_uverejneni"] = f'{zakazka_dict["datum_uverejneni"]} (uveřejnění po provedeném vyhledávání)'

    
    zakazka_dict["evidencni_cislo"] = zakazka_vyhledavani["data"]["evCisloZakazkyVvz"]
    print("evidencni_cislo: ", zakazka_dict["evidencni_cislo"], file=debug_file)
    
    zakazka_dict["typ_formulare"] = 'řádný' if not zakazka_vyhledavani["data"]["formularOpravuje"] else 'opravný'
    print("typ_formulare: ", zakazka_dict["typ_formulare"], file=debug_file)
    
    
    druh_formulare_translate = {
        "4": "Předběžné oznámení – obecná veřejná zakázka",
        "5": "Předběžné oznámení – sektorová veřejná zakázka",
        "6": "Předběžné oznámení – veřejná zakázka v oblasti obrany nebo bezpečnosti",
        "7": "Předběžné oznámení použité za účelem zkrácení lhůty pro podání nabídek – obecná veřejná zakázka",
        "8": "Předběžné oznámení použité za účelem zkrácení lhůty pro podání nabídek – sektorová veřejná zakázka",
        "9": "Předběžné oznámení použité za účelem zkrácení lhůty pro podání nabídek – veřejná zakázka v oblasti obrany nebo bezpečnosti",
        "10": "Předběžné oznámení použité jako výzva k projevení předběžného zájmu – obecná veřejná zakázka",
        "11": "Předběžné oznámení použité jako výzva k projevení předběžného zájmu – sektorová veřejná zakázka",
        "12": "Předběžné oznámení použité jako výzva k projevení předběžného zájmu – veřejná zakázka ve zjednodušeném režimu",
        "13": "Předběžné oznámení použité jako výzva k projevení předběžného zájmu – sektorová veřejná zakázka ve zjednodušeném režimu",
        "14": "Předběžné oznámení použité jako výzva k projevení předběžného zájmu – koncese ve zjednodušeném režimu",
        "15": "Oznámení o zavedení systému kvalifikace – sektorová veřejná zakázka",
        "16": "Oznámení o zahájení zadávacího řízení – obecná veřejná zakázka",
        "17": "Oznámení o zahájení zadávacího řízení – sektorová veřejná zakázka",
        "18": "Oznámení o zahájení zadávacího řízení – veřejná zakázka v oblasti obrany nebo bezpečnosti",
        "19": "Oznámení o zahájení koncesního řízení",
        "20": "Oznámení o zahájení zadávacího řízení – veřejná zakázka ve zjednodušeném režimu",
        "21": "Oznámení o zahájení zadávacího řízení – sektorová veřejná zakázka ve zjednodušeném režimu",
        "22": "Oznámení o poddodávce – veřejná zakázka v oblasti obrany nebo bezpečnosti",
        "23": "Oznámení o zahájení soutěže o návrh",
        "24": "Oznámení o zahájení soutěže o návrh – relevantní činnost",
        "25": "Dobrovolné oznámení o záměru uzavřít smlouvu – obecná veřejná zakázka",
        "26": "Dobrovolné oznámení o záměru uzavřít smlouvu – sektorová veřejná zakázka",
        "27": "Dobrovolné oznámení o záměru uzavřít smlouvu – veřejná zakázka v oblasti obrany nebo bezpečnosti",
        "28": "Dobrovolné oznámení o záměru uzavřít koncesní smlouvu",
        "29": "Oznámení o výsledku zadávacího řízení – obecná veřejná zakázka",
        "30": "Oznámení o výsledku zadávacího řízení – sektorová veřejná zakázka",
        "31": "Oznámení o výsledku zadávacího řízení – veřejná zakázka v oblasti obrany nebo bezpečnosti",
        "32": "Oznámení o výsledku koncesního řízení",
        "33": "Oznámení o výsledku zadávacího řízení – veřejná zakázka ve zjednodušeném režimu",
        "34": "Oznámení o výsledku zadávacího řízení – sektorová veřejná zakázka ve zjednodušeném režimu",
        "35": "Oznámení o výsledku koncesního řízení – koncese ve zjednodušeném režimu",
        "36": "Oznámení o výsledku soutěže o návrh",
        "37": "Oznámení o výsledku soutěže o návrh – relevantní činnost",
        "38": "Oznámení o změně závazku ze smlouvy – obecná veřejná zakázka",
        "39": "Oznámení o změně závazku ze smlouvy – sektorová veřejná zakázka",
        "40": "Oznámení o změně závazku ze smlouvy – koncese",
        "F01": "Předběžné oznámení",
        "F02": "Oznámení o zahájení zadávacího řízení",
        "F03": "Oznámení o výsledku zadávacího řízení",
        "F04": "Pravidelné předběžné oznámení – veřejné služby",
        "F05": "Oznámení o zahájení zadávacího řízení – veřejné služby",
        "F06": "Oznámení o výsledku zadávacího řízení – veřejné služby",
        "F07": "Systém kvalifikace - veřejné služby",
        "F08": "Oznámení na profilu zadavatele",
        "F12": "Oznámení soutěže o návrh",
        "F13": "Výsledky soutěže o návrh",
        "F14": "Oprava - Oznámení změn nebo dodatečných informací",
        "F15": "Oznámení o dobrovolné průhlednosti ex ante",
        "F16": "Oznámení předběžných informací – obrana a bezpečnost",
        "F17": "Oznámení o zakázce – obrana a bezpečnost",
        "F18": "Oznámení o zadání zakázky – obrana a bezpečnost",
        "F19": "Oznámení o subdodávce – obrana a bezpečnost",
        "F20": "Oznámení o změně",
        "F21": "Sociální a jiné zvláštní služby – veřejné zakázky",
        "F22": "Sociální a jiné zvláštní služby – veřejné služby",
        "F23": "Sociální a jiné zvláštní služby – koncese",
        "F24": "Oznámení o zahájení koncesního řízení",
        "F25": "Oznámení o výsledku koncesního řízení",
        "CZ01": "Předběžné oznámení podlimitního zadávacího řízení",
        "CZ02": "Oznámení o zahájení podlimitního zadávacího řízení",
        "CZ03": "Oznámení o výsledku podlimitního zadávacího řízení",
        "CZ04": "Oprava národního formuláře",
        "CZ07": "Oznámení o zahájení nabídkového řízení pro výběr dopravce k uzavření smlouvy o veřejných službách v přepravě cestujících",
        "E1": "Předběžná tržní konzultace",
        "E6": "Oznámení o změně závazku ze smlouvy – veřejná zakázka v oblasti obrany nebo bezpečnosti",
    }
                    
    
    zakazka_dict["druh_formulare"] = druh_formulare_translate[zakazka_vyhledavani["data"]["druhFormulare"]]
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
    
    zakazka_dict["url"] = f"https://vvz.nipez.cz/formulare-zakazky/{zakazka_vyhledavani["data"]["evCisloZakazkyVvz"]}"
    print("url: ", zakazka_dict["url"], file=debug_file)
    
    
    zakazka_dict["cislo_formulare"] = zakazka_dict['evidencni_cislo']
    print("cislo_formulare: ", zakazka_dict["cislo_formulare"], file=debug_file)

    zakazka_dict["cislo_souvisejiciho_formulare"] = "zakazka['evCisloFormulareVvz']"
    print("cislo_souvisejiciho_formulare: ", zakazka_dict["cislo_souvisejiciho_formulare"], file=debug_file)
    
    zakazka_dict["formulare_zakazky"] = ''
    print("formulare_zakazky: ", zakazka_dict["formulare_zakazky"], file=debug_file)
    
    print("debug_container: ", debug_container, file=debug_file)
    
    print("-"*20, end="\n\n", file=debug_file)
    
    
    zakazka_dict["debug"] = debug_container
    zakazka_dict["zdroj"] = ''
    
    return zakazka_dict


def main():
    user_date_from = datetime.strptime("03.08.2025", "%d.%m.%Y").date()
    user_date_to = datetime.strptime("05.08.2025", "%d.%m.%Y").date()
    # user_date_to = user_date_from + timdelta(days=1)

    crawler = VvzCrawler()

    processed_zakazky_list = []
    zakazky_list = []
    

    # aktuální datum
    query = {
        "date_from": user_date_from,
        "date_to": user_date_to + timedelta(days=1),
        "druh_vz": "PRACE",
    }
    zakazky_list += crawler.get_search_results(query, mock=False)

    query = {
        "date_from": user_date_from,
        "date_to": user_date_to + timedelta(days=1),
        "druh_vz": "SLUZBY",
    }
    sluzby = crawler.get_search_results(query, mock=False)
    for sluzba in sluzby:
        sluzba["from_sluzby"] = True
        zakazky_list.append(sluzba)
    print(len(zakazky_list))

    if user_date_from == user_date_to:
        html, left_panel, debug_panel, right_panel = make_html(
            search_date=f"{user_date_from.strftime('%d/%m/%Y')}"
        )
    else:
        html, left_panel, debug_panel, right_panel = make_html(
            search_date=f"{user_date_from.strftime('%d/%m/%Y')} - {user_date_to.strftime('%d/%m/%Y')}"
        )
    # debug_panel.append(get_aktuality())

    stopka = 0
    for zakazka in zakazky_list:
        stopka = stopka + 1

        if stopka > 10:
            #break
            pass

        if not zakazka["data"]["evCisloZakazkyVvz"] == "Z2024-006189":
            #continue
            pass

        if not zakazka["data"]["evCisloZakazkyVvz"] == "Z2024-002021":
            #continue
            pass
        
        # chybne zadavatele
        if not zakazka["data"]["evCisloZakazkyVvz"] in ["Z2023-043251", "Z2024-006687"]:
            #continue
            pass

        # zakazky s chybnymi lhutami pro nabidky
        if not zakazka["data"]["evCisloZakazkyVvz"] in ["Z2024-006889", "Z2024-006885"]:
            #continue
            pass

        # zakazky s ND-root
        if not zakazka["data"]["evCisloZakazkyVvz"] in ["Z2024-007209"]:
            #continue
            pass
        

        # zakazky s chybnou opravou
        if not zakazka["data"]["evCisloZakazkyVvz"] in ["Z2023-058929"]:
            #continue
            pass
        
        if not zakazka["data"]["evCisloZakazkyVvz"] in ["Z2023-038652", "Z2024-007513"]:
            #continue
            pass
        
        
        # zakazky s zadavatel po 24.04.2025
        if not zakazka["data"]["evCisloZakazkyVvz"] in ["Z2025-016517"]:
            # continue
            pass
        


        # print(zakazka)
        # "Z2024-006189"
        print(zakazka["data"]["evCisloZakazkyVvz"])

        form_submissions = crawler.get_form_submissions(
            form_vvz_id=zakazka["data"]["evCisloZakazkyVvz"], mock=False
        )
        
        # 6e999b1c-ca1a-4f7b-b677-7537f2064565
        form_detail = crawler.get_form_detail(
            form_submission=zakazka["id"], mock=False
            #form_submission="6e999b1c-ca1a-4f7b-b677-7537f2064565", mock=False
        )
        
        #form_schema = crawler.get_form_schema(
        #    form_schema="/api/form_schemas/d4831dca-2fa3-4a7c-9102-c4114083cad9",
        #    mock=False,
        #)


        zakazka_dict = vvz_zakazka2dict(form_detail[0], form_submissions[0])
        #zakazka_dict['komentar'] = zakazka_content.get('komentar', 'Neuvedeno')
        zakazka_dict['komentar'] = 'Neuvedeno'


        if zakazka_dict.get("druh_formulare", "").startswith("Oznámení o výsledku"):
            continue
        if zakazka_dict.get("druh_formulare", "").startswith("Oznámení o změně závazku ze smlouvy"):
            continue


        if zakazka_dict['lhuta_pro_nabidky']:
            if (datetime.strptime(zakazka_dict['lhuta_pro_nabidky'], '%d/%m/%Y') - datetime.strptime(zakazka_dict['datum_uverejneni'], '%d/%m/%Y')) <= timedelta(days=7):

                zakazka_dict['komentar'] = '<b>Patrně chyba lhůty pro nabídky!</b>'



        print("*" * 10)
        print(user_date_from)
        print(datetime.strptime(zakazka_dict['datum_uverejneni'], '%d/%m/%Y').date())
        if datetime.strptime(zakazka_dict['datum_uverejneni'], '%d/%m/%Y').date() == user_date_from:
            zakazka_dict["datum_uverejneni"] = f'{zakazka_dict["datum_uverejneni"]} (uveřejnění po provedeném vyhledávání)'
    



        if zakazka_dict["nezpracovano"] == "nic":
            zakazka_dict["nezpracovano"] = ""
        if zakazka_dict["nezpracovano"]:
            if zakazka_dict['komentar'] == 'Neuvedeno':
                zakazka_dict['komentar'] = ''
            zakazka_dict['komentar'] += zakazka_dict["nezpracovano"]


        if zakazka.get("from_sluzby", False):
            zakazka_dict["misto_zakazky_nuts_parsed"] = "PROJEKTOVÉ PRÁCE"
            zachovat = False
            for vyzadane_slovo in vyzadane_projektovky:
                if not zakazka_dict.get("nazev_vz", None): 
                    zachovat = True
                elif not zachovat and vyzadane_slovo.lower() in zakazka_dict.get("nazev_vz", "nazev_vz").lower():
                    zachovat = True
            if not zachovat:
                continue
            else:
                left_panel.append(zakazka_dict2html(zakazka_dict))
        
        



        if zakazka_dict['hodnota']:
            if float(zakazka_dict['hodnota']) >= 30000000.00:
                left_panel.append(zakazka_dict2html(zakazka_dict))
        else:
            left_panel.append(zakazka_dict2html(zakazka_dict))
        
        sleep(1)
        


        print("*" * 10)

    with open("zakazky_II_html.html", mode="w", encoding="utf-8") as file:
        file.write(str(html))
        pass


if __name__ == "__main__":
    vyzadane_projektovky = [
        "Projekt",
        "Projekční",
        "Modernizace",
        "PD",
        "Komplexní",
        "Výstavba",
        "transformace",
        "úpravy",
        "kanalizace",
        "kanaliza",
        "rekonstrukce",
        "rekonstr",
        "Pozemkové",
        "Vypracování",
        "Vyprac",
        "KoPÚ",
        "Produktové",
        "Prod",
        "Dokumentace",
        "Dokume",
        "revitalizace",
        "PDPS",
        "Stavby",
        "Stavb",
        "Povolení",
        "Provádění",
        "Provád",
        "Zpracování",
        "Zprac",
        "Rozšíření",
        "STS",
        "DUR",
        "SEZ",
        "Sanac",
        "Zelezn",
        "Železn",
        "Napoj",
        "Silnic",
        "DIAMO",
        "ekolog",
        "opatření",
        "sklad",
        "sana",
        "kontami",
    ]
    import sys
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[logging.FileHandler("my_log.log", mode="w"), logging.StreamHandler()],
    )

    main()
