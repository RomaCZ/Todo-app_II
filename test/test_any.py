from typing import Any, Dict, List, Union


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
    <OuterModel>
        <AnyHolder>https://www.youtube.com/spacex</AnyHolder>
        <AnyHolder>https://www.youtube.com/spacex</AnyHolder>
    <AnyHolder><a>https://www.gfdg.com</a></AnyHolder>
    </OuterModel>
    """

root = etree.fromstring(xml)



class AnyHolder(BaseXmlModel):
    any_attrs: Dict[str, str]

class OuterModel(BaseXmlModel, arbitrary_types_allowed=True):
    any_holder_raw:  List[ Union[ str, Element ]] = element(tag='AnyHolder', exclude=True)

    @computed_element
    def any_holder(self) -> AnyHolder:
        #print(self)
        #print(dir(self))
        print("turning into computed_element")
        
        print(self.any_holder_raw)
        print(type(self.any_holder_raw))

        
        return AnyHolder(any_attrs={"a": "b"})


#print(OuterModel.from_xml_tree(root))
print(OuterModel.from_xml_tree(root).model_dump_json())




