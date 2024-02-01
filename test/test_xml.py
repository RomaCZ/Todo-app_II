import pathlib
from datetime import date
from enum import Enum
from typing import Dict, List, Literal, Optional, Set, Tuple

import pydantic as pd
from pydantic import HttpUrl, conint

from pydantic_xml import BaseXmlModel, RootXmlModel, attr, element, wrapped


xml = pathlib.Path("./test/mock_data/vvz/get_content_public_url.xml").read_bytes()

from lxml import etree

root = etree.fromstring(xml)
for elem in root.getiterator():
    elem.tag = etree.QName(elem).localname

etree.cleanup_namespaces(root)
print(etree.tostring(root).decode())


class ADDRESSCONTRACTINGBODY(BaseXmlModel, tag="ADDRESS_CONTRACTING_BODY"):
    title: str = element(tag="TITLE", default="")


class OBJECT_CONTRACT(BaseXmlModel, tag="CONTRACTING_AUTHORITY"):
    ADDRESS_CONTRACTING_BODY: ADDRESSCONTRACTINGBODY
    URL_GENERAL: str = element(tag="URL_GENERAL", default="dfsfsd")
    URL_PROFILE: str = element(tag="URL_PROFILE", default="dfsfsd")
    title: str = element(tag="TITLE", default="")
    ssss: str = element(tag="TITLEs", default="ssssssssss")
    # URL_GENERAL: str = element(tag='URL_GENERAL')


class F04(BaseXmlModel, tag=r"cz_F04"):
    OBJECT_CONTRACT: OBJECT_CONTRACT


class Formular(BaseXmlModel, tag="FORMULAR"):
    cz_F04: F04


form = Formular.from_xml_tree(root)

print(form)
