# schvalid

This project implements an ISO Schematron (based on XPath 3) validator in pure Python.
It is based on the excellent [elementpath](https://github.com/sissaschool/elementpath)
library.

## Example

The following snippet asserts that the validated XML document satisfies the
specified Schematron schema.

```python
from schvalid import validate_against_schematron

xml_path = "tests/resources/zugferd_2p0_EN16931_Miete.pdf.xml"
sch_path = "tests/resources/FACTUR-X_EXTENDED.sch"

with open(xml_path, "rb") as xml_file, open(sch_path, "rb") as sch_file:
    result = validate_against_schematron(xml_file, sch_file, wd="tests/resources/")

assert result == ()
```

The function `validate_against_schematron` returns an empty tuple if the validation
succeeds. Otherwise, it returns a tuple of error messages (`schvalid.SchematronValidationError`
objects):

```python
from schvalid import validate_against_schematron

xml_path = "tests/resources/zugferd_2p0_EN16931_Miete.pdf.invalid.xml"
sch_path = "tests/resources/FACTUR-X_EXTENDED.sch"

with open(xml_path, "rb") as xml_file, open(sch_path, "rb") as sch_file:
    result = validate_against_schematron(xml_file, sch_file, wd="tests/resources/")
    
expected = (
    'Schema "Schema for FACTUR-X; 1.0; EN16931-CONFORMANT-EXTENDED", line 323: "Invoice total amount with VAT (BT-112) = Invoice total amount without VAT (BT-109) + Invoice total VAT amount (BT-110)."',
    'Schema "Schema for FACTUR-X; 1.0; EN16931-CONFORMANT-EXTENDED", line 323: "Amount due for payment (BT-115) = Invoice total amount with VAT (BT-112) -Paid amount (BT-113) +Rounding amount (BT-114)."',
    'Schema "Schema for FACTUR-X; 1.0; EN16931-CONFORMANT-EXTENDED", line 281: "Attribute @schemeName\' marked as not used in the given context."',
)

assert tuple(map(str, result)) == expected
```

## Installation

`schvalid` requires Python 3.10.

To install `schvalid`, run

```shell
pip install schvalid
```

To install it locally for testing, check this repository out and run

```shell
pip install -e .[test]
```

## License and Maintainer

This project is licensed under the GNU GENERAL PUBLIC LICENSE v3.
It is maintained by [Dominic Steinhöfel](https://www.dominic-steinhoefel.de).