from datetime import date, datetime
from bs4 import BeautifulSoup
from .geturl_II import geturl
import urllib.parse as urllib
import re
import time
from time import sleep
from requests import Request, Session
import json
import requests
from pathlib import PurePosixPath

from pprint import pprint
import copy
from copy import deepcopy




import subprocess
import sys
#subprocess.check_call([sys.executable, "-m", "pip", "install", "tenacity"])


from tenacity import retry, stop_after_attempt, wait_exponential


session = Session()
version = '2.0'

def get_date():

    def input2date(od_do = (True,)):

        ordinal_today = date.today().toordinal()
        date_dict = {
            'a': {
                'pozice': 0,
                'text': 'dnes' },
            'b': {
                'pozice': 1,
                'text': 'vcera' },
            'c': {
                'pozice': 2,
                'text': 'predevcirem' },
            'd': {
                'pozice': 3,
                'text': 'pred predevcirem' } }
        for date_key in sorted(date_dict):
            date_object = date.fromordinal(ordinal_today - date_dict[date_key]['pozice'])
            numbers = date_object.strftime('%d/%m/%Y')
            name = date_object.strftime('%A')
            note = date_dict[date_key]['text']
            print(f'''Moznost {date_key} = {numbers} - {name}; {note}''')
        if od_do:
            print('Moznost (e) = od - do; zad├ín├ş v rozsahu')
        text = 'Vyber [a, b, c, d], nebo napis datum dd/mm/rrrr: '
        user_input = input(text)
        if od_do and user_input == 'e':
            return 'e'
        if None.get(user_input, False):
            user_input = date.fromordinal(ordinal_today - date_dict.get(user_input)['pozice'])
    # WARNING: Decompyle incomplete

    user_date_from = input2date()
    if user_date_from == 'e':
        print('Zad├ín├ş od')
        user_date_from = input2date(False, **('od_do',))
        print('Zad├ín├ş do')
        user_date_to = input2date(False, **('od_do',))
    else:
        user_date_to = user_date_from
    hledani_od = user_date_from.strftime('%d/%m/%Y')
    hledani_do = user_date_to.strftime('%d/%m/%Y')
    print(f'''Hledani bude od {hledani_od} do {hledani_do}''')
    readable_date = f'''{hledani_od} - {hledani_do}'''
    return (user_date_from, user_date_to, readable_date)


   #vestnik2zakazky_list(user_date_from=user_date_from, user_date_to=user_date_to, druhVz='SLUZBY')
def vestnik2zakazky_list(user_date_from, user_time_from, user_date_to, user_time_to, druhFormulare=None, druhVz='PRACE', zakazky_list=None):
    url = 'https://api.vvz.nipez.cz/api/submissions/search'
    params = {
        'page': '1',
        'limit': '100',
        'form': 'vz',
        'workflowPlace': 'UVEREJNENO_VVZ',
        'data.datumUverejneniVvz[gte]': user_date_from.strftime(f'%Y-%m-%dT{user_time_from}+02:00'),
        'data.datumUverejneniVvz[lte]': user_date_to.strftime(f'%Y-%m-%dT{user_time_to}+02:00'),
        'data.druhVz': druhVz,
        'order[data.datumUverejneniVvz]': 'DESC' }
    if druhFormulare:
        params['data.druhFormulare'] = druhFormulare
    payload = {}
    headers = {
        'authority': 'api.vvz.nipez.cz',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'cs-CZ,cs;q=0.5',
        'cache-control': 'no-cache',
        'origin': 'https://vvz.nipez.cz',
        'pragma': 'no-cache',
        'referer': 'https://vvz.nipez.cz/',
        'sec-ch-ua': '"Brave";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36' }
    if not zakazky_list:
        zakazky_list = []
    response = requests.request('GET', url, params=params, headers=headers)
    response_json = response.json()
    return(response_json)


def zakazka_detail(zakazka):

    submission = PurePosixPath(zakazka['submissionVersion']).parts[-1]
    url = f'''https://api.vvz.nipez.cz/api/submission_attachments?limit=50&submissionVersion={submission}'''
    headers = {
        'authority': 'api.vvz.nipez.cz',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'cs-CZ,cs;q=0.5',
        'cache-control': 'no-cache',
        'origin': 'https://vvz.nipez.cz',
        'pragma': 'no-cache',
        'referer': 'https://vvz.nipez.cz/',
        'sec-ch-ua': '"Brave";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36' }
    response = requests.request('GET', url, headers=headers)
    response_json = response.json()
    url = f'''https://api.vvz.nipez.cz/download/submission_attachments/public/{response_json[0]['publicId']}'''
    response = requests.request('GET', url, headers=headers)
    namespaces = {
        'n1': None,
        'v1': None,
        'ted': None,
        'dtt': None,
        'n2021': None,
        'cztw': None }
    zakazka_dict = xmltodict.parse(response.text, process_namespaces=False, namespaces=namespaces)
    pprint(zakazka_dict)
    
    zakazka_content = copy.deepcopy(zakazka_dict['FORMULAR'])
    
    for k, v in zakazka_content.items():
        print(k)
        if type(zakazka_content[k]) is dict:
            for kk, vv in zakazka_content[k].items():
                print(f'{k}: {kk}')
                zakazka_dict['FORMULAR'][kk] = vv
    
    
    return zakazka_dict['FORMULAR']


def get_zakazka_historie(zakazka_id):
    submission = PurePosixPath(zakazka['submissionVersion']).parts[-1]
    url = f'''https://api.vvz.nipez.cz/api/submission_attachments?limit=50&submissionVersion={submission}'''
    print(url)
    headers = {
        'authority': 'api.vvz.nipez.cz',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'cs-CZ,cs;q=0.5',
        'cache-control': 'no-cache',
        'origin': 'https://vvz.nipez.cz',
        'pragma': 'no-cache',
        'referer': 'https://vvz.nipez.cz/',
        'sec-ch-ua': '"Brave";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36' }
    response = requests.request('GET', url, headers, **('headers',))
    response_json = response.json()
    url = f'''https://api.vvz.nipez.cz/download/submission_attachments/public/{response_json[0]['publicId']}'''
    response = requests.request('GET', url, headers, **('headers',))
    print(response.text)
    namespaces = {
        'n1': None,
        'v1': None,
        'ted': None,
        'dtt': None,
        'n2021': None,
        'cztw': None }
    zakazka_dict = xmltodict.parse(response.text, False, namespaces, **('process_namespaces', 'namespaces'))
    zakazka = zakazka_dict
    # zakazka = next((lambda .0: Warning: block stack is not empty!
# for k, v in .0:
# if not k.startswith('@'):
# vcontinueNone)(zakazka_dict['FORMULAR'].items()))
    pprint(zakazka)
    print('**********')
    return zakazka
   


class Zakazka():
    def __init__(self, id='Z2023-044773'):
        self.zakazka_dict = {}
        self.zakazka_json = {}
        self.changes = []
        self.changes_mapping = []
        self.search_json = {}
        self.id = id
        self.nipez_url = 'https://api.vvz.nipez.cz'
        self.params = {
            'page': '1',
            'limit': '200',
            'form': 'vz',
            'data.evCisloZakazkyVvz': self.id,
            'order[data.datumUverejneniVvz]': 'DESC',
            'order[createdAt]': 'DESC'}
        self.headers = {
            'authority': 'api.vvz.nipez.cz',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'cs-CZ,cs;q=0.5',
            'cache-control': 'no-cache',
            'origin': 'https://vvz.nipez.cz',
            'pragma': 'no-cache',
            'referer': 'https://vvz.nipez.cz/',
            'sec-ch-ua': '"Brave";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
        self.xml_namespaces = {
            'n1': None,
            'ns2': None,
            'ns3': None,
            'ns5': None,
            'ns10': None,
            'v1': None,
            'ted': None,
            'dtt': None,
            'n2021': None,
            'cztw': None}
        self.download_zakazka_list()
    
    @retry(stop=stop_after_attempt(4), # Maximum number of retries
        wait=wait_exponential(multiplier=1, min=1, max=60) # Exponential backoff
        )
    def download_zakazka_list(self):
        search_url = f"{self.nipez_url}/api/submissions/search"
        response = requests.request('GET', search_url, params=self.params, headers=self.headers)
        #print(response)
        search_json = response.json()
        #print(search_json)
        self.zakazka_json = search_json.pop()
        self.search_json = search_json[::-1]
    
    
    @retry(stop=stop_after_attempt(4), # Maximum number of retries
        wait=wait_exponential(multiplier=1, min=1, max=60) # Exponential backoff
        )
    def download_json(self, submissionVersion):
        json_url = f"{self.nipez_url}/api/submission_attachments?limit=50"
        json_url = f"{json_url}&submissionVersion={submissionVersion}"
        response = requests.request('GET', json_url, headers=self.headers)
        response_json = response.json()
        return response_json
    
    @retry(stop=stop_after_attempt(4), # Maximum number of retries
        wait=wait_exponential(multiplier=1, min=1, max=60) # Exponential backoff
        )    
    def download_xml(self, contentPublicUrl):
        xml_url = f"{self.nipez_url}{contentPublicUrl}"
        #print(xml_url)
        response = requests.request('GET', xml_url, headers=self.headers)
        #print("fffffff\n", response.text)
        response_dict = xmltodict.parse(response.text, 
            process_namespaces=False,
            namespaces=self.xml_namespaces)
        return response_dict

    def parse_main_zakazka(self):
        response_json = self.download_json(self.zakazka_json['submissionVersion'])
        response_dict = self.download_xml(response_json[0]["contentPublicUrl"])
        response_content = copy.deepcopy(response_dict['FORMULAR'])
        for key, value in response_content.items():
            if type(value) is dict:
                for sub_key, sub_value in value.items():
                    response_dict['FORMULAR'][sub_key] = sub_value #možná zbytečné
                    response_dict[sub_key] = sub_value
        self.zakazka_dict = response_dict
        if 'cz_F03' in response_content.keys():
            self.zakazka_dict['FORMULAR']['@FORM'] = 'CZ03'
        
    @retry(stop=stop_after_attempt(2), # Maximum number of retries
        wait=wait_exponential(multiplier=1, min=1, max=60) # Exponential backoff
        )
    def parse_main_form(self):
        form_url = f"{self.nipez_url}/api/form_schemas/"
        form_url = f"{form_url}{self.zakazka_json['data']['souvisejiciFormSchemaId']}"
        response = requests.request('GET', form_url, headers=self.headers)
        form_json = response.json()

        print(form_json)
        
        label = ""
        
        for element in form_json['schema']['layout']['elements']:
            if 'label' in element.keys():
                if element.get('type', 'element type undefined') == 'Group':
                    
                    label = element['label']
                    
                    #print(label)
            
            
            for i, sub_element in enumerate(element.get('elements', [])):
                if sub_element.get('text'):
                    label = sub_element.get('text')
                
                sub_scope = sub_element.get('scope', sub_element.get('scopeRef'))
                if sub_scope:
                    #print(" ", label, " ", sub_element.get('type'), " ", sub_element.get('label'), " ", sub_scope)
                    form = {
                        'type': sub_element.get('type'),
                        'label': sub_element.get('label'),
                        'scope': sub_scope,
                        'section': label
                        }
                    self.changes_mapping.append(form)
                
                for j, sub2_element in enumerate(sub_element.get('elements', [])):
                    sub2_scope = sub2_element.get('scope', sub2_element.get('scopeRef'))
                    if sub2_scope:
                        #print("   ", label, " ", sub2_element.get('type'), " ", sub2_element.get('label'), " ", sub2_scope)
                        form = {
                            'type': sub2_element.get('type'),
                            'label': sub2_element.get('label'),
                            'scope': sub2_scope,
                            'section': label
                            }
                        self.changes_mapping.append(form)
                
                    for k, sub3_element in enumerate(sub2_element.get('elements', [])):
                        sub3_scope = sub3_element.get('scope', sub3_element.get('scopeRef'))
                        if sub3_scope:
                            #print("   ", label, " ", sub3_element.get('type'), " ", sub3_element.get('label'), " ", sub3_scope)
                            form = {
                                'type': sub3_element.get('type'),
                                'label': sub3_element.get('label'),
                                'scope': sub3_scope,
                                'section': label
                                }
                            self.changes_mapping.append(form)
            
    
    def process_changes(self):
        #pprint(self.search_json)
        nested_changes = []
        changes = []
        try:
            for entry in self.search_json:
                response_json = self.download_json(entry['submissionVersion'])
                response_dict = self.download_xml(response_json[0]["contentPublicUrl"])
                pprint(response_dict)
                
                #print('formular', response_dict['FORMULAR'])
                
                for key, value in response_dict['FORMULAR'].items():
                    if key.startswith('F') and response_dict['FORMULAR'][key].get('@FORM', 'nenalezeno') in ['F03', 'F06']:
                        self.zakazka_dict['FORMULAR']['@FORM'] = response_dict['FORMULAR'][key].get('@FORM', 'nenalezeno')
                        return
                    
                    if key.lower() == 'cz_F03'.lower():
                        print('je to CZ03')
                        self.zakazka_dict['FORMULAR']['@FORM'] = 'CZ03'
                        return
                    
                    
                    
                    
                    print(key)
                    if type(value) is not dict:
                        continue
                    for sub_key, sub_value in value.items():
                        if sub_key == 'CHANGES':
                            print(type(sub_value['CHANGE']))
                            print("\n\n\n\n")
                            if type(sub_value['CHANGE']) is list:
                                nested_changes.extend(sub_value['CHANGE'])
                            else:
                                nested_changes.append(sub_value['CHANGE'])
                #break
            pprint(nested_changes)
            
            
            
            
            for change in nested_changes:
                if 'WHAT' not in change.keys():
                    continue
                change['NEW_VALUE'] = {}
                change['OLD_VALUE'] = {}
                for change_key, change_value in change['WHAT'].items():
                    if change_key.startswith('NEW_'):
                        new_key = change_key.replace('NEW_', '')
                        change['NEW_VALUE'][new_key] = change_value
                        change['OLD_VALUE'][new_key] = change['WHAT'][f'OLD_{new_key}']
            
            print('nove změny')
            pprint(nested_changes)
            
            
            
            
            
            
            for change in nested_changes:
                print(nested_changes)
                for change_key in change['NEW_VALUE'].keys():
                    
                    # zk = Zakazka(id='Z2023-044782')     # nebyly nalezeny změny?
                    # [{'WHAT': {'NEW_DATE': '2023-11-14', 'OLD_DATE': '2023-11-07'},
                      # 'WHERE': {'LABEL': 'Lhůta pro doručení nabídek nebo žádostí o účast',
                                # 'LOT_NO': 'III.3.1)',
                                # 'SECTION': 'III.'}},
                    section = change['WHERE']['SECTION']
                    lot_no = change['WHERE'].get('LOT_NO', '')
                    print(lot_no)
                    print("\n\n\n")
                    
                    if section in lot_no:
                        section = lot_no
                    
                    new_change = {
                        'key': change_key,
                        'new_value': change['NEW_VALUE'][change_key],
                        'old_value': change['OLD_VALUE'][change_key],
                        'label': change['WHERE'].get('LABEL'),
                        'section': section,
                        'scope': None
                        }
                    #pprint(new_change)
                    
                    
                    
                    for form in self.changes_mapping:
                        if form['section'].startswith(new_change['section']):
                            if new_change['key'].lower() == form['type'].lower():
                                new_change['scope'] = form['scope']
                            
                    
                    
                    
                    
                    
                    
                    changes.append(new_change)
                    #break
                #break
            
            self.changes = changes
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}, {err.args=}")
            self.zakazka_dict["komentar"] = "Nazpracované změny!"

    def make_changes(self):
        def nested_get(dic, keys):    
            for key in keys:
                dic = dic[key]
            return dic
        
        def nested_set(dic, keys, value):
            for key in keys[:-1]:
                dic = dic.setdefault(key, {})
            dic[keys[-1]] = value
        
        try:
            for change in self.changes:
                print(change['scope'])
                #'#/PROCEDURE/OPENING_CONDITION/TIME_OPENING_TENDERS'
                scope = change['scope'].replace('ted___', '').split('/')
                scope[0] = 'FORMULAR'
                print(nested_get(self.zakazka_dict, scope))
                nested_set(self.zakazka_dict, scope, change['new_value'])
                print(nested_get(self.zakazka_dict, scope))
        except Exception as err:
            print(f"make_changes Unexpected {err=}, {type(err)=}, {err.args=}")
            self.zakazka_dict["komentar"] = "Nazpracované změny!"
            
    def return_zakazka_dict(self):
        return self.zakazka_dict

def zpracuj_zmeny(zmeny_dict):
    zmeny = zmeny_dict.get('CHANGES', {'CHANGE': []})['CHANGE']
    zmena_dict = {}
    for zmena in zmeny:
        print(zmena['NEW_VALUE'])
        print(zmena['OLD_VALUE'])
        print(zmena['WHERE'])
        if 'Lhůta pro doručení' in zmena['WHERE']['LABEL']:
            zmena_dict['PROCEDURE'] = {
                'DATE_RECEIPT_TENDERS': zmena['NEW_VALUE']['DATE'] }
            continue
    pprint(zmena_dict)
    return None


if __name__ == '__main__':
    #zk = Zakazka(id='Z2019-044079')     # divná zakákázka se změnama
    #zk = Zakazka(id='Z2022-005690')     # divná zakákázka se změnama v průběhu oznámení o výsledku
    #zk = Zakazka(id='Z2020-017797')      # v průběhu oznámení o výsledku
    #zk = Zakazka(id='Z2023-012843')
    #zk = Zakazka(id='Z2023-043999')
    #zk = Zakazka(id='Z2018-002794')     # oznámení o výsledku - nezajímá nás
    #zk = Zakazka(id='Z2020-017797')     # oznámení o výsledku ale až v prostředku změn - nezajímá nás
    #zk = Zakazka(id='Z2023-048511')     # chybí cena?
    #zk = Zakazka(id='Z2023-040469')     # špatně změny
    #zk = Zakazka(id='Z2022-008516')     # oznámení o výsledku  CZ03
    #zk = Zakazka(id='Z2021-017546')     # obsahuje oznámení o výsledku  CZ03
    #zk = Zakazka(id='Z2023-046895')     # obsahuje oznámení o výsledku  CZ03
    #zk = Zakazka(id='Z2023-044782')     # nebyly nalezeny změny?
    
    #zk = Zakazka(id='Z2023-053410')     # zakázka je dvakrát pod různým označením
    #zk = Zakazka(id='Z2023-053420')     # zakázka je dvakrát pod různým označením
    
    zk = Zakazka(id='Z2023-050632')      # špatně rozpoznané změny data pro nabídku
    
    
    
    #zk = Zakazka()
    
    zk.parse_main_zakazka()
    print('tu')
    pprint(zk.zakazka_dict, width=999)
    print('tam')
    print('form', zk.zakazka_dict['FORMULAR'].get('@FORM', 'chybi'))
    
    pprint(zk.zakazka_json)
    
    zk.parse_main_form()
    pprint(zk.changes_mapping, width=999)
    
    
    
    zk.process_changes()
    
    
    
    zk.make_changes()
    pprint(zk.zakazka_dict, width=999)

