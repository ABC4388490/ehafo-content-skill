import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_package.py"
SPEC = importlib.util.spec_from_file_location("validate_package", SCRIPT)
validate_package = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validate_package)


class ProductionGateTests(unittest.TestCase):
    def valid_gate(self):
        return {
            "declared_before_generation": True,
            "asset_type": "article_illustration",
            "template_type": "article_illustration",
            "scope_verified": True,
            "locked_assets_verified": True,
            "acceptance": {
                "content_accuracy": "pass",
                "readable_size": "pass",
                "aspect_ratio": "pass",
                "asset_integrity": "pass",
                "mobile_preview": "pass",
            },
        }

    def test_accepts_all_four_gates(self):
        self.assertEqual(
            validate_package.validate_production_gates(self.valid_gate()), []
        )

    def test_rejects_mixed_template(self):
        gate = self.valid_gate()
        gate["template_type"] = "service_account_cards"
        self.assertIn(
            "production_gates:template_type_must_match_asset_type",
            validate_package.validate_production_gates(gate),
        )

    def test_rejects_any_missing_acceptance_dimension(self):
        gate = self.valid_gate()
        gate["acceptance"]["mobile_preview"] = "fail"
        self.assertIn(
            "production_gates:acceptance_not_passed:mobile_preview",
            validate_package.validate_production_gates(gate),
        )


if __name__ == "__main__":
    unittest.main()
