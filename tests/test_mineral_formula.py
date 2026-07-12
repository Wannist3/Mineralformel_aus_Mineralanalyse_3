import tempfile
import unittest
from pathlib import Path

from mineral_formula import calculate_mineral_formula, example_data, find_data_file


class MineralFormulaTests(unittest.TestCase):
    def test_olivine_formula_is_displayed_in_standard_order(self):
        result = calculate_mineral_formula(example_data["Olivin"], 4, "Olivin")
        self.assertEqual(result["formula"], "Mg₁.₈₃Fe²⁺₀.₂₁SiO4")

    def test_find_data_file_finds_csv_in_search_tree(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target_dir = root / "data"
            target_dir.mkdir()
            csv_path = target_dir / "MRMinerals.csv"
            csv_path.write_text("Mineralgruppe\nOlivin\n", encoding="utf-8")

            self.assertEqual(find_data_file("MRMinerals.csv", search_dirs=[target_dir]), csv_path)


if __name__ == "__main__":
    unittest.main()
