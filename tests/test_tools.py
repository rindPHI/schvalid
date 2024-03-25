import os
import unittest

from schvalid.tools import select_xpath


class TestTools(unittest.TestCase):
    def test_select_xpath_basic_zugferd_constraint(self):
        namespaces = {
            "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
            "qdt": "urn:un:unece:uncefact:data:standard:QualifiedDataType:100",
            "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
            "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
        }

        zugferd_constraint = "(ram:BasisAmount)"

        with open("resources/zugferd_2p0_EN16931_Miete.pdf.xml", "rb") as xml_file:
            context = select_xpath(
                xml_file,
                "//ram:ApplicableHeaderTradeSettlement/ram:ApplicableTradeTax",
                namespaces=namespaces,
            )[0]

        with open("resources/zugferd_2p0_EN16931_Miete.pdf.xml", "rb") as xml_file:
            self.assertTrue(
                select_xpath(
                    xml_file,
                    zugferd_constraint,
                    context_elem=context,
                    namespaces=namespaces,
                ),
            )

    def test_select_xpath_complex_zugferd_vat_constraint(self):
        namespaces = {
            "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
            "qdt": "urn:un:unece:uncefact:data:standard:QualifiedDataType:100",
            "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
            "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
        }

        zugferd_constraint = """
(
    round(.[normalize-space(upper-case(ram:TypeCode)) = 'VAT']/xs:decimal(ram:RateApplicablePercent)) = 0 
    and (round(xs:decimal(ram:CalculatedAmount)) = 0)
)
or (
    round(.[normalize-space(upper-case(ram:TypeCode)) = 'VAT']/xs:decimal(ram:RateApplicablePercent)) != 0 
    and (
        (abs(xs:decimal(ram:CalculatedAmount)) - 1 < 
            round(
                abs(xs:decimal(ram:BasisAmount))
                * (
                    .[normalize-space(upper-case(ram:TypeCode)) = 'VAT']/xs:decimal(ram:RateApplicablePercent) 
                    div 100
                ) * 10 * 10
             ) div 100 ) 
        and (
            abs(xs:decimal(ram:CalculatedAmount)) + 1 >
                round(
                    abs(xs:decimal(ram:BasisAmount)) 
                    * (
                        .[normalize-space(upper-case(ram:TypeCode)) = 'VAT']/xs:decimal(ram:RateApplicablePercent) div 100
                    ) * 10 * 10
                ) div 100 
        )
    )) 
or (
    not(exists(.[normalize-space(upper-case(ram:TypeCode))='VAT']/xs:decimal(ram:RateApplicablePercent))) 
    and (round(xs:decimal(ram:CalculatedAmount)) = 0)
)"""

        with open("resources/zugferd_2p0_EN16931_Miete.pdf.xml", "rb") as xml_file:
            context = select_xpath(
                xml_file,
                "//ram:ApplicableHeaderTradeSettlement/ram:ApplicableTradeTax",
                namespaces=namespaces,
            )[0]

        with open("resources/zugferd_2p0_EN16931_Miete.pdf.xml", "rb") as xml_file:
            self.assertEqual(
                True,
                select_xpath(
                    xml_file,
                    zugferd_constraint,
                    context_elem=context,
                    namespaces=namespaces,
                ),
            )

    def test_select_xpath_complex_zugferd_total_valid_constraint(self):
        namespaces = {
            "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
            "qdt": "urn:un:unece:uncefact:data:standard:QualifiedDataType:100",
            "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
            "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
        }

        # Invoice total amount with VAT (BT-112) =
        #     Invoice total amount without VAT (BT-109) + Invoice total VAT amount (BT-110).
        zugferd_constraint = """
        (
            ram:GrandTotalAmount = round(
                  ram:TaxBasisTotalAmount * 100 
                + ram:TaxTotalAmount[@currencyID=/rsm:CrossIndustryInvoice/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/ram:InvoiceCurrencyCode] * 100
                + 0
            ) div 100
        ) or (
            (ram:GrandTotalAmount = ram:TaxBasisTotalAmount) 
            and not (
                ram:TaxTotalAmount[@currencyID=/rsm:CrossIndustryInvoice/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/ram:InvoiceCurrencyCode]
            )
        )"""

        with open("resources/zugferd_2p0_EN16931_Miete.pdf.xml", "rb") as xml_file:
            context = select_xpath(
                xml_file,
                "//ram:SpecifiedTradeSettlementHeaderMonetarySummation",
                namespaces=namespaces,
            )[0]

        with open("resources/zugferd_2p0_EN16931_Miete.pdf.xml", "rb") as xml_file:
            self.assertEqual(
                True,
                select_xpath(
                    xml_file,
                    zugferd_constraint,
                    context_elem=context,
                    namespaces=namespaces,
                ),
            )

    def test_select_xpath_complex_zugferd_total_invalid_constraint(self):
        namespaces = {
            "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
            "qdt": "urn:un:unece:uncefact:data:standard:QualifiedDataType:100",
            "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
            "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
        }

        # Invoice total amount with VAT (BT-112) =
        #     Invoice total amount without VAT (BT-109) + Invoice total VAT amount (BT-110).
        zugferd_constraint = """
        (
            ram:GrandTotalAmount = round(
                  ram:TaxBasisTotalAmount * 100 
                + ram:TaxTotalAmount[@currencyID=/rsm:CrossIndustryInvoice/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/ram:InvoiceCurrencyCode] * 100
                + 0
            ) div 100
        ) or (
            (ram:GrandTotalAmount = ram:TaxBasisTotalAmount) 
            and not (
                ram:TaxTotalAmount[@currencyID=/rsm:CrossIndustryInvoice/rsm:SupplyChainTradeTransaction/ram:ApplicableHeaderTradeSettlement/ram:InvoiceCurrencyCode]
            )
        )"""

        with open(
            "resources/zugferd_2p0_EN16931_Miete.pdf.invalid.xml", "rb"
        ) as xml_file:
            context = select_xpath(
                xml_file,
                "//ram:SpecifiedTradeSettlementHeaderMonetarySummation",
                namespaces=namespaces,
            )[0]

        with open(
            "resources/zugferd_2p0_EN16931_Miete.pdf.invalid.xml", "rb"
        ) as xml_file:
            self.assertEqual(
                False,
                select_xpath(
                    xml_file,
                    zugferd_constraint,
                    context_elem=context,
                    namespaces=namespaces,
                ),
            )


if __name__ == "__main__":
    unittest.main()
