import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_package.py"
SPEC = importlib.util.spec_from_file_location("validate_package", SCRIPT)
validate_package = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validate_package)


class ProductionGateTests(unittest.TestCase):
    def valid_acceptance_gate(self):
        return {
            dimension: {
                "result": "pass",
                "evidence": f"{dimension}已完成可核验的成品检查",
            }
            for dimension in validate_package.ACCEPTANCE_GATE_DIMENSIONS
        }

    def test_accepts_complete_universal_acceptance_gate(self):
        self.assertEqual(
            validate_package.validate_acceptance_gate(
                self.valid_acceptance_gate(), "VALUE_UNPROVEN"
            ),
            [],
        )

    def test_release_rejects_missing_or_unpassed_acceptance_dimension(self):
        gate = self.valid_acceptance_gate()
        gate.pop("delivery_integrity")
        gate["mobile_readability"]["result"] = "revise"
        errors = validate_package.validate_acceptance_gate(
            gate, "VALUE_UNPROVEN"
        )
        self.assertIn(
            "acceptance_gate:missing:delivery_integrity",
            errors,
        )
        self.assertIn(
            "acceptance_gate:release_requires_pass:mobile_readability",
            errors,
        )

    def test_draft_requires_revise_and_blocked_requires_blocked_result(self):
        gate = self.valid_acceptance_gate()
        self.assertIn(
            "acceptance_gate:draft_requires_revise",
            validate_package.validate_acceptance_gate(gate, "DRAFT_PASS"),
        )
        gate["unresolved_questions"]["result"] = "revise"
        self.assertEqual(
            validate_package.validate_acceptance_gate(gate, "DRAFT_PASS"),
            [],
        )
        self.assertIn(
            "acceptance_gate:blocked_requires_blocked_result",
            validate_package.validate_acceptance_gate(gate, "BLOCKED"),
        )

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

    def test_article_accepts_zero_body_illustrations(self):
        self.assertEqual(
            validate_package.validate_article_illustrations({"illustrations": []}),
            [],
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
            "article:body_illustrations_must_be_0_to_2",
            validate_package.validate_article_illustrations(article),
        )

    def valid_article_structure(self):
        return {
            "core_question": "纸质证书是否轮到本人报名地发放，下一步怎样办理",
            "out_of_scope": ["不汇总全国各省往年领取方式"],
            "modules": [
                {
                    "module_id": "main-path",
                    "necessity": "required",
                    "task": "给出确认并办理纸质证书的唯一主路径",
                    "task_type": "action",
                }
            ],
        }

    def test_article_structure_accepts_one_required_module(self):
        self.assertEqual(
            validate_package.validate_article_structure(
                self.valid_article_structure()
            ),
            [],
        )

    def test_article_structure_requires_explicit_out_of_scope(self):
        structure = self.valid_article_structure()
        structure["out_of_scope"] = []
        self.assertIn(
            "article.structure:out_of_scope_required",
            validate_package.validate_article_structure(structure),
        )

    def test_article_structure_rejects_multi_task_module(self):
        structure = self.valid_article_structure()
        structure["modules"][0]["task_type"] = ["action", "evidence"]
        self.assertIn(
            "article.structure.modules[0]:exactly_one_task_type_required",
            validate_package.validate_article_structure(structure),
        )

    def test_article_structure_rejects_required_after_supplementary(self):
        structure = self.valid_article_structure()
        structure["modules"] = [
            {
                "module_id": "exception",
                "necessity": "supplementary",
                "task": "说明信息异常时的处理方式",
                "task_type": "exception",
            },
            {
                "module_id": "main-path",
                "necessity": "required",
                "task": "给出确认并办理纸质证书的唯一主路径",
                "task_type": "action",
            },
        ]
        self.assertIn(
            "article.structure:required_module_after_supplementary",
            validate_package.validate_article_structure(structure),
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

    def test_cover_rejects_wrapped_or_overlong_copy(self):
        cover = self.valid_cover()
        cover["cover_copy"] = "领取先看\n报名地"
        self.assertIn(
            "article.cover:cover_copy_must_be_single_line",
            validate_package.validate_article_cover(cover),
        )

        cover = self.valid_cover()
        cover["cover_copy"] = "卫" * 11
        self.assertIn(
            "article.cover:cover_copy_must_be_6_to_10_chars",
            validate_package.validate_article_cover(cover),
        )

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
