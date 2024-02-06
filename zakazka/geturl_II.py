import urllib.request
import urllib.parse
import http.cookiejar
from time import sleep

import os
os.environ["PYTHONHTTPSVERIFY"] = "0"


def geturl(url, data=None, cookies=True):
    sleep(3)

    if cookies:
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    else:
        opener = urllib.request.build_opener()

    opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    if data:
        data = urllib.parse.urlencode(data)
        data = data.encode('ascii')
    
    content = ""
    attemp = 1
    retries = 3
    
    while content == "" and attemp <= retries:
        try:
            resource = opener.open(url, data=data, timeout=115)
            content = resource.read()
        except Exception as error:
            print(f"URL: {url}\nAttemp: {attemp} from {retries}; Error: {error}")
            sleep(retries**attemp)
        attemp +=1

    return content


def get_url_test_orig():
    debug = open("geturl_II_debug.html", mode="w", encoding="utf-8")
    html_code = open("geturl_II_html_code.html", mode="w", encoding="utf-8")


    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    data = urllib.parse.urlencode({
        "FormType": "",
        "FormNumber": "",
        "FormDatePublishedFrom": "24.10.2016",
        "FormDatePublishedTo": "24.10.2016",
        "ContactName": "",
        "ContactAddress": "",
        "ContactNationalId": "",
        "ContactCaActivity": "",
        "ContactCeActivity": "",
        "ContactCaType": "",
        "ProcedureType": "",
        "ProcedureTimeLimit": "",
        "ContractTitle": "",
        "ContractType": "WORKS",
        "FormOldContractFlag": "false",
        "ContractNumber": "",
        "CpvCode": "",
        "ObjectMainSite": "",
        "ObjectTimeframeFromFrom": "",
        "ObjectTimeframeFromTo": "",
        "ObjectNutsCode": "",
        "ObjectTimeframeToFrom": "",
        "ObjectTimeframeToTo": "",
        "WinnerOfficialName": "",
        "WinnerNacionalId": ""
        })
    data = data.encode('ascii')
    resource = opener.open("https://www.vestnikverejnychzakazek.cz/SearchForm/Search?SearchFormGrid-sort=&SearchFormGrid-page=1&SearchFormGrid-pageSize=500&SearchFormGrid-group=&SearchFormGrid-filter=", data=data, timeout=115)
    
    print("data: ", data, end="\n", file=debug)
    print("code: ", resource.getcode(), end="\n", file=debug)
    print("headers: ", resource.getheaders(), end="\n", file=debug)
    
    content = resource.read().decode('utf-8', errors='replace')
     
    print("opener: ", opener, end="\n", file=debug)
    print("resource.status: ", resource.status, end="\n", file=debug)
    print("resource.info(): ", resource.info(), end="\n", file=debug)
    print("dict(resource.info()): ", dict(resource.info()), end="\n", file=debug)
    print("resource.headers: ", resource.headers, end="\n", file=debug)
    print("resource.info().get_content_charset(): ", resource.info().get_content_charset(), end="\n", file=debug)
    print("resource.getcode(): ", resource.getcode(), end="\n", file=debug)
    print("resource.geturl(): ", resource.geturl(), end="\n", file=debug)
    print("cj: ", cj, end="\n", file=debug)
    print("cj._cookies: ", cj._cookies, end="\n", file=debug)
    print("resource: ", resource, end="\n", file=debug)

    print("content: ", content, end="\n", file=html_code)

def get_url_test():
    debug = open("geturl_II_debug.html", mode="w", encoding="utf-8")
    html_code = open("geturl_II_html_code.html", mode="w", encoding="utf-8")


    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    urllib.request.install_opener(opener)


    params = {
	"FormType": "",
	"FormNumber": "",
	"FormDatePublishedFrom": "05.01.2021",
	"FormDatePublishedTo": "05.01.2021",
	"ContactName": "",
	"ContactAddress": "",
	"ContactNationalId": "",
	"ContactCaActivity": "",
	"ContactCeActivity": "",
	"ContactCaType": "",
	"ProcedureType": "",
	"ProcedureTimeLimit": "",
	"ContractTitle": "",
	"ContractType": "",
	"FormOldContractFlag": "false",
	"ContractNumber": "",
	"CpvCode": "",
	"ObjectMainSite": "",
	"ObjectTimeframeFromFrom": "",
	"ObjectTimeframeFromTo": "",
	"ObjectNutsCode": "",
	"ObjectTimeframeToFrom": "",
	"ObjectTimeframeToTo": "",
	"WinnerOfficialName": "",
	"WinnerNacionalId": ""
    }

    DATA = urllib.parse.urlencode(params)
    DATA = DATA.encode('utf-8')




    request = urllib.request.Request("https://www.vestnikverejnychzakazek.cz/SearchForm/Search?SearchFormGrid-sort=&SearchFormGrid-page=1&SearchFormGrid-pageSize=500&SearchFormGrid-group=&SearchFormGrid-filter=", DATA)
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    request.add_header("User-Agent", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:33.0) Gecko/20100101 Firefox/33.0")
    resource = urllib.request.urlopen(request)








    content = resource.read().decode('utf-8', errors='replace')
     
    print("opener: ", opener, end="\n", file=debug)
    print("resource.status: ", resource.status, end="\n", file=debug)
    print("resource.info(): ", resource.info(), end="\n", file=debug)
    print("dict(resource.info()): ", dict(resource.info()), end="\n", file=debug)
    print("resource.headers: ", resource.headers, end="\n", file=debug)
    print("resource.info().get_content_charset(): ", resource.info().get_content_charset(), end="\n", file=debug)
    print("resource.getcode(): ", resource.getcode(), end="\n", file=debug)
    print("resource.geturl(): ", resource.geturl(), end="\n", file=debug)
    print("cj: ", cj, end="\n", file=debug)
    print("cj._cookies: ", cj._cookies, end="\n", file=debug)
    print("resource: ", resource, end="\n", file=debug)

    print("content: ", content, end="\n", file=html_code)

if __name__ == "__main__":
	print("ti")
	get_url_test()
