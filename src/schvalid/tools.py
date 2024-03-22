from typing import Tuple, Optional, Any, Mapping

import elementpath
from elementpath.xpath3 import XPath3Parser
from lxml import etree
from lxml import isoschematron
from lxml.etree import _XSLTResultTree


class FileResolver(etree.Resolver):
    def __init__(self, *additional_locations: str):
        super().__init__()
        self.additional_locations = additional_locations

    def resolve(self, url, pubid, context):
        assert isinstance(url, str)
        url = next(
            (
                location
                for location in self.additional_locations
                if location.endswith(url)
            ),
            url,
        )

        return self.resolve_filename(url, context)


def validate_against_schematron(
    xml_file_path: str, schematron_file_path: str, *additional_locations: str
) -> Tuple[bool, _XSLTResultTree]:
    with (
        open(schematron_file_path, "rb") as schematron_file,
        open(xml_file_path, "rb") as xml_file,
    ):
        parser = etree.XMLParser()
        parser.resolvers.add(FileResolver(*additional_locations))
        xml_doc = etree.parse(xml_file, parser)
        sch_doc = etree.parse(schematron_file, parser)

        schematron = isoschematron.Schematron(sch_doc, store_report=True)
        result = schematron.validate(xml_doc)

        return result, schematron.validation_report


def validate_against_xsd(
    xml_file_path: str, xsd_path: str
) -> Tuple[bool, Optional[str]]:
    with open(xsd_path, "rb") as xsd_file, open(xml_file_path, "rb") as xml_file:
        parser = etree.XMLParser()
        parser.resolvers.add(FileResolver())
        xml_doc = etree.parse(xml_file, parser)
        xmlschema_doc = etree.parse(xsd_file, parser)

        xmlschema = etree.XMLSchema(xmlschema_doc)
        result = xmlschema.validate(xml_doc)

        return result, str(xmlschema.error_log.last_error)


def select_xpath(
    xml_file_path: str,
    xpath: str,
    context_xpath=".",
    namespaces: Optional[Mapping[str, str]] = None,
) -> Any:
    """

    :param xml_file_path:
    :param xpath:
    :param context_xpath:
    :param namespaces:
    :return: A list with XPath nodes or a basic type for
        expressions based on a function or literal.
    """

    with open(xml_file_path, "rb") as xml_file:
        parser = etree.XMLParser()
        parser.resolvers.add(FileResolver())
        xml_doc = etree.parse(xml_file, parser)

        context_elems = elementpath.select(
            xml_doc,
            context_xpath,
            parser=XPath3Parser,
            namespaces=namespaces,
        )

        return tuple(
            filter(
                lambda elem: not isinstance(elem, list) or elem,
                tuple(
                    elementpath.select(
                        xml_doc,
                        xpath,
                        parser=XPath3Parser,
                        namespaces=namespaces,
                        item=context_elem
                    )
                    for context_elem in context_elems
                )
            )
        )
