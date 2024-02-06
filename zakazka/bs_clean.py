from bs4 import BeautifulSoup
import re

def clean_html(soup):
	""" remove all uneccesary tags or attrib hrom html """
	bad_tags = ["script", "style", "sup", "img"]
	bad_class = ["icon-help", "blue-link-small", "toolbox", "footnotes"]
	bad_ids = ["u74", "u76", "qs"]
	bad_attribs =  ["data-val-maxlength-max", "data-val-maxlength", "data-val-required", "data-val", "maxlength", "readonly"]
	
	soup_text = re.sub(r"[\r\n]+", "", str(soup))
	soup_text = re.sub(r"\(dd.mm.rrrr\)", "", soup_text, re.DOTALL)
	soup_text = re.sub(r"\(hh:mm\)", "", soup_text, re.DOTALL)
	soup_text = re.sub(r"Číslo oznámení v Úř. věst.", "Čís. oznámení", soup_text, re.DOTALL)
	soup_text = re.sub(r"Internetová adresa: \(URL\)", "URL: ", soup_text, re.DOTALL)
	soup_text = re.sub(r'<="\/\/"=""><=""=""><="--">:', "", soup_text, re.DOTALL)

	soup = BeautifulSoup(soup_text, "html.parser")
	
	def del_tags(tag, bad_tags):
		if tag.name in bad_tags:
			return True
		return False
	
	def del_class(tag, bad_class):
		for tag_class in tag.get("class", ["none_to_be_found"]):
			if tag_class in bad_class:
				return True
		return False

	def del_ids(tag, bad_ids):
		if tag.get("id", "none_to_be_found") in bad_ids:
			return True
		return False
	
	def del_empty(tag):
		if tag.contents in [[], [" "]] and tag.get("value", "") == "":
			return True
		return False
	
	def del_hidden(tag):
		if tag.get("type", "") == "hidden":
			return True
		return False
	
	def del_unselected_option(tag):
		if tag.name == "option" and not tag.get("selected", False):
			return True
		return False
	
	def remove_attrib(tag, bad_attribs):
		for attrib in list(tag.attrs):
			if attrib in bad_attribs:
				del tag[attrib]
	
	tags_to_be_removed = soup.findAll(lambda tag: 
		del_tags(tag, bad_tags) or
		del_class(tag, bad_class) or
		del_ids(tag, bad_ids) or
		del_empty(tag) or
		del_hidden(tag) or
		del_unselected_option(tag)
		)
	for tag in tags_to_be_removed:
		tag.extract()
	
	for tag in soup.findAll(True):
		remove_attrib(tag, bad_attribs)
	
	# full url adress opened in new tab
	elements = soup.findAll(lambda tag:
		tag.name == "a" and
		re.match(r"\/", tag.get("href", ""))
		)
	for element in elements:
		element["href"] = re.sub(r"^\/", "https://www.vestnikverejnychzakazek.cz/", element["href"])
		element["target"] = "_blank"
	
	return soup

if __name__ == "__main__":
	
	html_blob = """
		<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
		<html>
			<head>
			</head>

			<body>

		<form action="/cs/Form/Save" enctype="multipart/form-data" id="general" method="post" name="general"><input name="__RequestVerificationToken" type="hidden" value="tsrY0GO6tPTXKdeLHsIz3AS3WtvaPh9bQ03Ut7MlrriOVdVe54ml4WBoUJNodb8IhLeDfmvTXSN/wY+QkFJHPpEd+OxnwOXs3R3tuDkGfMKBXYA1O1c1wsPSFGdxv9oFju549Q=="/><input id="qs" name="qs" type="hidden" value="EMV/Ba7mj1dCIsFPrfbv7YTCHXSkz5eKiFtbSyMP5gD0v5kaAuhjKcPTf1VVZsB82WY1NxQpV9qXf/hOUt7LmWAx/yF03olL56rFaxqaFohWQINfD46VCFAdhxtw9EXIeCV9SlkhNvj2/zKWrkRZ//HKWV2ZyCrJT67vCF48h5prux2krJI8k34r/HhXIAomNG8kLDPaAnLcVYeyITszqyMKmGYuzt91AUmItBA9pk8QfHPhxqC9r2KA/BzP0WzR84vUyA7sJjxBFAG2NXYjZJKyjBiVvhl26BbAD3c973Fh"/><input id="formData" name="formData" type="hidden" value=""/><input data-val="true" data-val-length="D&amp;#233;lka mus&amp;#237; b&amp;#253;t maxim&amp;#225;lně 20 znak(ů)." data-val-length-max="20" id="ContractInfo_ContractNumber" name="ContractInfo.ContractNumber" type="hidden" value=""/> <div class="iform-section clear">Oddíl I: Veřejný zadavatel</div><br/>
		<div class="section">
		<text>Evidenční číslo zakázky: <a href="/SearchForm/SearchContract?contractNumber=Z2016-001875">Z2016-001875</a></text>
		<div class="iform-subsection">I.1) Název, adresa a kontaktní místo/místa</div>
		<fieldset class="form">
		<div class="form-frame">
		<div class="right border-bottom border-left">
		<div class="iform-label ">
		<label class="form-label" for="FormItems_Ic_I_1">Identifikační číslo (je-li známo)</label><a class="icon-help icon-help-hover ToolTip" id="Forms-OZNAMENIOZAKAZCE_IC_I_1ToolTip1029"></a>
		</div>
		<div class="iform-field ">
		<input class="input-readonly" id="FormItems_Ic_I_1" maxlength="255" name="FormItems.Ic_I_1" readonly="readonly" type="text" value="00231223"/>
		</div>
		<div class="clear"></div>
		</div>
		<div class="areaspec">
		<div class="iform-label ">
		<label class="form-label" for="FormItems_UredniNazev_I_1">Úřední název<span class="item_mandatory">*</span></label><a class="icon-help icon-help-hover ToolTip" id="Forms-OZNAMENIOZAKAZCE_UREDNINAZEV_I_1ToolTip1029"></a>
		</div>
		<div class="iform-field border-bottom">
		<input class="input-readonly" id="FormItems_UredniNazev_I_1" maxlength="255" name="FormItems.UredniNazev_I_1" readonly="readonly" type="text" value="Městská část Praha 17"/>
		</div>
		</div>
		<div class="field100 border-bottom">
		<div class="iform-label ">
		<label class="form-label" for="FormItems_PostovniAdresa_I_1">Poštovní adresa<span class="item_mandatory">*</span></label><a class="icon-help icon-help-hover ToolTip" id="Forms-OZNAMENIOZAKAZCE_POSTOVNIADRESA_I_1ToolTip1029"></a>
		</div>
		<div class="iform-field ">
		<input class="input-readonly" id="FormItems_PostovniAdresa_I_1" maxlength="255" name="FormItems.PostovniAdresa_I_1" readonly="readonly" type="text" value="Žalanského 291/12b"/>
		</div>
		<div class="clear"></div>
		</div>
		<div class="border-bottom left stretch">
		<div class="field22 left" style="margin-left:1px;">
		<div class="iform-label ">
		<label class="form-label" for="FormItems_Obec_I_1">Obec<span class="item_mandatory">*</span></label><a class="icon-help icon-help-hover ToolTip" id="Forms-OZNAMENIOZAKAZCE_OBEC_I_1ToolTip1029"></a>
		</div>
		<div class="iform-field border-right">
		<input class="input-readonly" id="FormItems_Obec_I_1" maxlength="100" name="FormItems.Obec_I_1" readonly="readonly" type="text" value="Praha 17"/>
		</div>
		</div>
		<div class="field22 left">
		<div class="iform-label ">
		<label class="form-label" for="FormItems_Psc_I_1">PSČ</label><a class="icon-help icon-help-hover ToolTip" id="Forms-OZNAMENIOZAKAZCE_PSC_I_1ToolTip1029"></a>
		</div>
		<div class="iform-field border-right">
		<input class="input-readonly" id="FormItems_Psc_I_1" maxlength="10" name="FormItems.Psc_I_1" readonly="readonly" type="text" value="163 00"/>
		</div>
		</div>
		<div class="field22 left">
		<div class="iform-label">
		<label class="form-label" for="FormItems_Stat_I_1">Stát<span class="item_mandatory">*</span></label><a class="icon-help icon-help-hover ToolTip" id="Forms-OZNAMENIOZAKAZCE_STAT_I_1ToolTip1029"></a>
		</div>
		<div class="iform-field currency-state">
		<select disabled="disabled" id="FormItems_Stat_I_1" name="FormItems.Stat_I_1"><option></option>
		<option value="CZ">CZ</option>
		<option value="AD">AD</option>
		<option value="AE">AE</option>
		<option value="AF">AF</option>
		<option value="AG">AG</option>
		<option value="AI">AI</option>
		<option value="AL">AL</option>
		<option selected="selected" value="CZ">CZ</option>
		</select>
		</div>
		<div class="clear">
		</div>
		</div>
		</div>
		<div class="field66 left">
		<div class="iform-label ">
		<label class="form-label" for="FormItems_KontaktniMista_I_1">Kontaktní místo</label><a class="icon-help icon-help-hover ToolTip" id="Forms-OZNAMENIOZAKAZCE_KONTAKTNIMISTA_I_1ToolTip1029"></a>
		</div>
		<div class="iform-field border-right">
		<input class="input-readonly" id="FormItems_KontaktniMista_I_1" maxlength="255" name="FormItems.KontaktniMista_I_1" readonly="readonly" type="text" value="osoba pověřená dle § 151 zákona o veřejných zakázkách č. 137/2006 Sb. v platném znění"/>
		</div>
		<div class="clear"></div>
		<div class="iform-label ">
		<label class="form-label" for="FormItems_KRukam_I_1">K rukám</label><a class="icon-help icon-help-hover ToolTip" id="Forms-OZNAMENIOZAKAZCE_KRUKAM_I_1ToolTip1029"></a>
		</div>
		<div class="iform-field border-right">
		<input class="input-readonly" id="FormItems_KRukam_I_1" maxlength="100" name="FormItems.KRukam_I_1" readonly="readonly" type="text" value="Radek Meluzin"/>
		</div>
		</div>
		<div class="field22 border-bottom">
		<div class="iform-label ">
		<label class="form-label" for="FormItems_Tel_I_1">Tel.</label><a class="icon-help icon-help-hover ToolTip" id="Forms-OZNAMENIOZAKAZCE_TEL_I_1ToolTip1029"></a>
		</div>
		<div class="iform-field ">
		<input class="input-readonly" id="FormItems_Tel_I_1" maxlength="255" name="FormItems.Tel_I_1" readonly="readonly" type="text" value="+420 274860055"/>
		</div>
		<div class="clear"></div>
		</div>
		<div class="clear"></div>
		<br/>
		<ul style="list-style-type:decimal;padding-left:20px">
		<li>Kategorie služeb ve smyslu článku 20 a přílohy II A směrnice 2004/18/ES.</li>
		</ul>
		</form></div><div class="page-breaker"></div></form>
			</body>
		</html>
		"""

	html = clean_html(BeautifulSoup(html_blob, "html.parser"))
	with open("bs_clean.html", "w", encoding="utf-8") as output_file:
		print(html.prettify(), end="\n\n", file=output_file)