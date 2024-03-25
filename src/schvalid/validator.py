import os
from dataclasses import dataclass
from typing import IO, Dict, Tuple

from lxml import etree
from lxml.etree import _ElementTree

from schvalid.tools import select_xpath


@dataclass(frozen=True)
class SchematronValidationError(Exception):
    message: str
    title: str
    line: int

    def __post_init__(self):
        super().__init__(self.message)

    def __str__(self):
        return f'Schema "{self.title}", line {self.line}: "{self.message}"'


def validate_against_schematron(
    xml_input: IO, schematron_input: IO, wd: str = os.getcwd()
) -> Tuple[SchematronValidationError, ...]:
    """
    This function validates an XML file against a Schematron schema.
    It returns a tuple of SchematronValidationError objects. For a
    valid document, the tuple will be empty.

    Example
    -------

    The file :code:`zugferd_2p0_EN16931_Miete.pdf.xml` is valid against the
    Schematron schema :code:`FACTUR-X_EXTENDED.sch`. The function will return
    an empty tuple:

    >>> xml_path = "../../tests/resources/zugferd_2p0_EN16931_Miete.pdf.xml"
    >>> sch_path = "../../tests/resources/FACTUR-X_EXTENDED.sch"

    >>> with open(xml_path, "rb") as xml_file, open(sch_path, "rb") as sch_file:
    ...     result = validate_against_schematron(xml_file, sch_file, wd="../../tests/resources/")

    >>> result
    ()

    :param xml_input: The XML file to validate.
    :param schematron_input: The Schematron schema to validate against.
    :param wd: The working directory to use for resolving relative paths
        in the :code:`document()` function.
    :return: A tuple of SchematronValidationError objects.
    """

    xml_doc = etree.parse(xml_input)
    sch_doc = etree.parse(schematron_input)

    title = "Untitled Schematron Schema"
    title = next(iter(select_xpath(sch_doc, "/schema/title")), title).text

    namespaces: Dict[str, str] = {
        elem.xpath("@prefix")[0]: elem.xpath("@uri")[0]
        for elem in select_xpath(sch_doc, "/schema/ns")
    }

    result = ()

    for pattern in select_xpath(sch_doc, "/schema/pattern"):
        for rule in select_xpath(pattern, "rule"):
            context_specifier = str(rule.xpath("@context")[0])

            variables: Dict[str, str] = {
                let.xpath("@name")[0]: let.xpath("@value")[0]
                for let in select_xpath(rule, "let")
            }

            for assert_or_report in select_xpath(
                rule, "*[self::assert or self::report]"
            ):
                test = str(assert_or_report.xpath("@test")[0])
                message = assert_or_report.text.strip()

                result += check_test(
                    test,
                    message,
                    xml_doc,
                    context_specifier,
                    title,
                    variables,
                    namespaces,
                    wd,
                    is_report=assert_or_report.tag.endswith("report"),
                )

    return result


def check_test(
    test: str,
    error_message: str,
    xml_doc: _ElementTree,
    context_specifier: str,
    schema_title: str,
    variables: Dict[str, str],
    namespaces: Dict[str, str],
    wd: str,
    is_report: bool,
) -> Tuple[SchematronValidationError, ...]:
    """
    This function checks a test against an XML document and adds a
    SchematronValidationError to the returned tuple if the test
    (1) fails if :code:`is_report` is False, (2) succeeds if
    :code:`is_report` is True.

    :param test: The test to check.
    :param error_message: The error message to use in the SchematronValidationError.
    :param xml_doc: The XML document to check the test against.
    :param context_specifier: The specifier for the context in :code:`xml_doc`
        to run the test in.
    :param schema_title: The title of the Schematron schema to use in the
        SchematronValidationError.
    :param variables: The variables used in the test; a mapping from variable names
        to the string value they are bound to.
    :param namespaces: The namespaces used in the document; a mapping from namespace
        prefixes to the URIs they are bound to.
    :param wd: The working directory to use for resolving relative paths in the
        :code:`document()` function.
    :param is_report: Whether the test should fail (:code:`True`) or succeed
        (:code:`False`). In other words, if :code:`is_report` is :code:`False`,
        an error is returned if the test fails; if :code:`is_report` is :code:`True`,
        an error is returned if the test succeeds.
    :return: A tuple of SchematronValidationError objects.
    """

    result: Tuple[SchematronValidationError, ...] = ()

    for context in select_xpath(xml_doc, context_specifier, namespaces=namespaces):
        eval_result = select_xpath(
            xml_doc,
            test,
            context_elem=context,
            namespaces=namespaces,
            variables={
                var: select_xpath(
                    xml_doc,
                    value,
                    context_elem=context,
                    namespaces=namespaces,
                )
                for var, value in variables.items()
            },
            wd=wd,
        )

        if not is_report and not eval_result or is_report and eval_result:
            result += (
                SchematronValidationError(
                    error_message, schema_title, context.sourceline
                ),
            )

    return result
