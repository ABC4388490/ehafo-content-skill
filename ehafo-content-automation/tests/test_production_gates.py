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

    def test_accepts_separate_cover_and_illustration_gates(self):
        illustration = self.valid_gate()
        cover = self.valid_gate()
        cover["asset_type"] = "article_cover"
        cover["template_type"] = "article_cover"
        self.assertEqual(
            validate_package.validate_production_gates([cover, illustration]), []
        )

    def test_rejects_duplicate_gate_types(self):
        gate = self.valid_gate()
        self.assertIn(
            "production_gates:duplicate_asset_type:article_illustration",
            validate_package.validate_production_gates([gate, gate.copy()]),
        )

    def test_article_rejects_zero_body_illustrations(self):
        self.assertIn(
            "article:body_illustrations_must_be_1_to_2",
            validate_package.validate_article_illustrations({"illustrations": []}),
        )

    def test_article_accepts_one_or_two_body_illustrations(self):
        one = {
            "illustrations": [
                {
                    "path": "output/rule-path.png",
                    "unique_information": "展示规则核对的先后路径",
                }
            ]
        }
        two = {
            "illustrations": [
                {
                    "path": "output/rule-path.png",
                    "unique_information": "展示规则核对的先后路径",
                },
                {
                    "path": "output/evidence-chain.png",
                    "unique_information": "展示成果与证明材料的对应关系",
                },
            ]
        }
        self.assertEqual(validate_package.validate_article_illustrations(one), [])
        self.assertEqual(validate_package.validate_article_illustrations(two), [])

    def test_article_rejects_three_body_illustrations(self):
        article = {
            "illustrations": [
                {"path": f"output/figure-{index}.png", "unique_information": f"独有信息{index}"}
                for index in range(3)
            ]
        }
        self.assertIn(
            "article:body_illustrations_must_be_1_to_2",
            validate_package.validate_article_illustrations(article),
        )

    def test_article_rejects_locked_brand_assets_as_body_illustrations(self):
        article = {
            "illustrations": [
                {
                    "path": "assets/ehafo-article-header.png",
                    "unique_information": "品牌顶部图",
                }
            ]
        }
        self.assertIn(
            "article.illustrations[0]:locked_brand_asset_not_counted",
            validate_package.validate_article_illustrations(article),
        )

    def valid_cover(self):
        return {
            "publication_role": "article_cover",
            "cover_copy": "先查4层文件",
            "title": "申报正高，论文还必须发吗？",
            "digest": "国家政策已破除唯论文，但具体要求仍要逐层核对。",
            "wide": {
                "path": "output/cover-wide.png",
                "width": 900,
                "height": 383,
            },
            "square": {
                "path": "output/cover-square.png",
                "width": 500,
                "height": 500,
            },
            "visual_spec": {
                "background_type": "solid",
                "palette_id": "action_green",
                "background_color": "#175941",
                "primary_color": "#FFFDF6",
                "accent_color": "#F6D96B",
            },
            "thumbnail_readability": "pass",
        }

    def test_accepts_valid_article_cover(self):
        self.assertEqual(validate_package.validate_article_cover(self.valid_cover()), [])

    def test_cover_rejects_wrong_dimensions_and_low_contrast(self):
        cover = self.valid_cover()
        cover["wide"]["height"] = 500
        cover["visual_spec"]["primary_color"] = "#2B6A54"
        errors = validate_package.validate_article_cover(cover)
        self.assertIn("article.cover.wide:must_be_900x383", errors)
        self.assertIn("article.cover:primary_contrast_below_4_5", errors)

    def test_cover_rejects_overlong_digest_and_repeated_paths(self):
        cover = self.valid_cover()
        cover["digest"] = "摘" * 121
        cover["square"]["path"] = cover["wide"]["path"]
        errors = validate_package.validate_article_cover(cover)
        self.assertIn("article.cover:digest_exceeds_120", errors)
        self.assertIn("article.cover:wide_and_square_paths_must_differ", errors)

    def test_cover_rejects_unknown_or_modified_palette(self):
        cover = self.valid_cover()
        cover["visual_spec"]["palette_id"] = "custom_purple"
        errors = validate_package.validate_article_cover(cover)
        self.assertIn("article.cover:unknown_palette_id", errors)

        cover = self.valid_cover()
        cover["visual_spec"]["background_color"] = "#123456"
        errors = validate_package.validate_article_cover(cover)
        self.assertIn("article.cover:palette_colors_must_match:action_green", errors)

    def test_cover_accepts_all_three_fixed_palettes(self):
        for palette_id, colors in validate_package.COVER_PALETTES.items():
            cover = self.valid_cover()
            cover["visual_spec"].update(colors)
            cover["visual_spec"]["palette_id"] = palette_id
            self.assertEqual(validate_package.validate_article_cover(cover), [])


if __name__ == "__main__":
    unittest.main()
