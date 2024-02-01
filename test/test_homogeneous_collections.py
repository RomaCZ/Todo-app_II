from typing import Any, List, Union


from lxml import etree

# from lxml.etree import Element
from xml.etree.ElementTree import Element
from pydantic import HttpUrl, SkipValidation, constr
from pydantic_xml import (
    BaseXmlModel,
    RootXmlModel,
    attr,
    computed_element,
    element,
    wrapped,
)

xml = """
    <Company>
        <Product>Several launch vehicles</Product>
        <Product>Starlink</Product>
        <Product>Starship</Product>
    </Company>
    """


root = etree.fromstring(xml)


class Company(BaseXmlModel):
    products: List[str] = element(tag="Product")


print(Company.from_xml_tree(root))
print(Company.from_xml_tree(root).model_dump_json())


xml = """
    <co:Company xmlns:co="http://company.org/co">
        <co:Info>
            <hq:Headquarters xmlns:hq="http://company.org/hq">
                <hq:Location>
                    <loc:City xmlns:loc="http://company.org/loc">
                        Hawthorne
                    </loc:City>
                </hq:Location>
            </hq:Headquarters>
        </co:Info>
    </co:Company>
    """


class Company(BaseXmlModel, ns="co", nsmap={"co": "http://company.org/co"}):
    city: constr(strip_whitespace=True) = wrapped(
        "Info",
        ns="co",
        entity=wrapped(
            "Headquarters/Location",
            ns="hq",
            nsmap={"hq": "http://company.org/hq"},
            entity=element(
                tag="City", ns="loc", nsmap={"loc": "http://company.org/loc"}
            ),
        ),
    )


root = etree.fromstring(xml)

print(Company.from_xml_tree(root))
print(Company.from_xml_tree(root).model_dump_json())


xml = """
    <contacts>
        <contact>https://www.youtube.com/spacex</contact>
    <contact>https://www.youtube.com/spacex</contact>
    <contact url="https://www.linkedin.com/company/spacex" />
    </contacts>
    """


class Contact(BaseXmlModel, tag="contact"):
    url: HttpUrl



class Contacts(BaseXmlModel, tag="contacts", arbitrary_types_allowed=True):
    contacts_raw: List[ Union[ str, Element ]] = element(tag="contact", exclude=True)

    @computed_element
    def parse_raw_contacts(self) -> List[Contact]:
        contacts: List[Contact] = []
        for contact_raw in self.contacts_raw:
            print(f"contact_raw: {contact_raw}")
            contact = Contact(url=contact_raw.strip())

            contacts.append(contact)

        return contacts
    

root = etree.fromstring(xml)

#print(Contacts.from_xml_tree(root))
print(Contacts.from_xml_tree(root).model_dump_json())
