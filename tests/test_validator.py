import unittest

from schvalid.validator import validate_against_schematron, SchematronValidationError


class TestValidator(unittest.TestCase):
    def test_valid_zugferd_invoice(self):
        xml_path = "resources/zugferd_2p0_EN16931_Miete.pdf.xml"
        sch_path = "resources/FACTUR-X_EXTENDED.sch"

        with open(xml_path, "rb") as xml_file, open(sch_path, "rb") as sch_file:
            result = validate_against_schematron(xml_file, sch_file, wd="resources/")

        self.assertFalse(result)

    def test_invalid_zugferd_invoice(self):
        xml_path = "resources/zugferd_2p0_EN16931_Miete.pdf.invalid.xml"
        sch_path = "resources/FACTUR-X_EXTENDED.sch"

        with open(xml_path, "rb") as xml_file, open(sch_path, "rb") as sch_file:
            result = validate_against_schematron(xml_file, sch_file, wd="resources/")

        print("\n".join(map(str, result)))

        self.assertTrue(result)
        self.assertEqual(
            (
                SchematronValidationError(
                    "Invoice total amount with VAT (BT-112) = "
                    + "Invoice total amount without VAT (BT-109) + Invoice total VAT amount (BT-110).",
                    "Schema for FACTUR-X; 1.0; EN16931-CONFORMANT-EXTENDED",
                    323,
                ),
                SchematronValidationError(
                    "Amount due for payment (BT-115) = "
                    + "Invoice total amount with VAT (BT-112) -Paid amount (BT-113) +Rounding amount (BT-114).",
                    "Schema for FACTUR-X; 1.0; EN16931-CONFORMANT-EXTENDED",
                    323,
                ),
                SchematronValidationError(
                    message="Attribute @schemeName' marked as not used in the given context.",
                    title="Schema for FACTUR-X; 1.0; EN16931-CONFORMANT-EXTENDED",
                    line=281,
                ),
            ),
            result,
        )


if __name__ == "__main__":
    unittest.main()
