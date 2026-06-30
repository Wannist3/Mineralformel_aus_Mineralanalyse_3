import unittest

from mineral_formula import calculate_mineral_formula, example_data


class MineralFormulaTests(unittest.TestCase):
    def test_olivine_formula_is_displayed_in_standard_order(self):
        result = calculate_mineral_formula(example_data["Olivin"], 4, "Olivin")
        self.assertEqual(result["formula"], "Mg₁.₈₃Fe²⁺₀.₂₁SiO4")


if __name__ == "__main__":
    unittest.main()
