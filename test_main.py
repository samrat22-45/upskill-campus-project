import os
import tempfile
import unittest
from unittest.mock import patch

import main


class BankingUtilityTests(unittest.TestCase):
    def test_money_to_cents_whole_rupees(self):
        self.assertEqual(main.money_to_cents("250"), 25000)

    def test_money_to_cents_paise(self):
        self.assertEqual(main.money_to_cents("99.50"), 9950)

    def test_reject_zero_and_negative_amounts(self):
        for value in ("0", "-1", "0.00"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    main.money_to_cents(value)

    def test_reject_more_than_two_decimal_places(self):
        with self.assertRaises(ValueError):
            main.money_to_cents("10.555")

    def test_pin_hash_and_verify(self):
        salt, digest = main.hash_pin("1234")
        self.assertTrue(main.verify_pin("1234", salt, digest))
        self.assertFalse(main.verify_pin("9999", salt, digest))

    def test_format_money(self):
        self.assertEqual(main.format_money(12345), "₹123.45")


if __name__ == "__main__":
    unittest.main()
