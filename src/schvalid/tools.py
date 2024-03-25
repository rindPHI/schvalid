import os
import re
from typing import Optional, Any, Mapping, IO

import elementpath
from elementpath.xpath3 import XPath3Parser
from lxml import etree
from lxml.etree import _Element, _ElementTree


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


XMLElement = _Element | _ElementTree

DOCUMENT_FUNCTION_PATTERN = re.compile(
    r"\s*document\s*\(\s*'(?P<q1>[^']+)'\s*\)|"
    + r'\s*document\s*\(\s*"(?P<q2>[^"]+)"\s*\)'
)


def select_xpath(
    xml_file: IO | XMLElement,
    xpath: str,
    context_elem: Optional[XMLElement] = None,
    namespaces: Optional[Mapping[str, str]] = None,
    variables=None,
    wd: str = os.getcwd(),
) -> Any:
    """
    This function selects nodes from an XML file using an XPath expression.

    :param xml_file: The XML file to select nodes from.
    :param xpath: The XPath expression to use.
    :param context_elem: The context element to use for the XPath expression.
        The default is the current context :code:`.`.
    :param namespaces: The namespaces used in the document: a mapping of
        prefixes to URIs.
    :param variables: The variables used in the XPath expression: a mapping
        of variable names to concrete values.
    :param wd: The working directory to use for the :code:`document` function,
        which allows loading an external XML resource document.
    :return: A list with XPath nodes or a basic type for
        expressions based on a function or literal.
    """

    variables = variables or {}

    parser = etree.XMLParser()
    parser.resolvers.add(FileResolver())

    document_function_match = DOCUMENT_FUNCTION_PATTERN.match(xpath)
    if document_function_match:
        q1, q2 = document_function_match.group("q1", "q2")
        if not wd.endswith(os.sep):
            wd += os.sep
        with open(wd + (q1 or q2), "rb") as external_xml_file:
            xml_doc = etree.parse(external_xml_file, parser)

        xpath = xpath[document_function_match.end() :]

        # A context element is not supported with document() function.
        context_elem = None
    else:
        xml_doc = (
            xml_file
            if isinstance(xml_file, XMLElement)
            else etree.parse(xml_file, parser)
        )

    return (
        elementpath.select(
            xml_doc,
            xpath,
            parser=XPath3Parser,
            namespaces=namespaces,
            item=context_elem,
            variables=variables,
        )
        if context_elem is not None
        else elementpath.select(
            xml_doc,
            xpath,
            parser=XPath3Parser,
            namespaces=namespaces,
            variables=variables,
        )
    )
