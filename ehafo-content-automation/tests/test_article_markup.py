import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "check_article_markup.py"
SPEC = importlib.util.spec_from_file_location("check_article_markup", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ArticleMarkupTest(unittest.TestCase):
    def validate(self, html: str) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "article.html"
            path.write_text(html, encoding="utf-8")
            return MODULE.validate(path)

    def test_accepts_short_green_phrase_and_half_highlight(self) -> None:
        html = """
        <p>确认<span class="key-green" style="color:#3D8063;font-weight:500;white-space:nowrap;">申报规则</span>。</p>
        <p><span class="half-highlight" style="background-image:linear-gradient(to bottom,transparent 50%,#DCEFE7 50%);box-decoration-break:clone;-webkit-box-decoration-break:clone;">先核对通知，再准备材料。</span></p>
        """
        self.assertEqual([], self.validate(html))

    def test_rejects_long_or_repeated_green_text(self) -> None:
        html = """
        <p><span class="key-green" style="color:#3D8063;font-weight:500;white-space:nowrap;">这是一整段绿色文字</span><span class="key-green">材料要求</span></p>
        """
        errors = self.validate(html)
        self.assertIn("key-green[0]:visible_length_must_be_3_to_6", errors)
        self.assertIn("paragraph[0]:key-green_must_be_at_most_one", errors)

    def test_rejects_green_text_in_forbidden_regions(self) -> None:
        style = "color:#3D8063;font-weight:500;white-space:nowrap;"
        html = f"""
        <h2><span class="key-green" style="{style}">申报规则</span></h2>
        <p class="summary"><span class="key-green" style="{style}">材料要求</span></p>
        <p><span class="half-highlight" style="background-image:linear-gradient(to bottom,transparent 50%,#DCEFE7 50%);box-decoration-break:clone;-webkit-box-decoration-break:clone;"><span class="key-green" style="{style}">核对通知</span></span></p>
        """
        errors = self.validate(html)
        self.assertIn("key-green[0]:forbidden_region", errors)
        self.assertIn("key-green[1]:forbidden_region", errors)
        self.assertIn("key-green[2]:forbidden_region", errors)

    def test_rejects_internal_provenance_in_visible_article(self) -> None:
        html = """
        <section>
          <p>选题来源：易哈佛问题中心</p>
          <p>核验日期：2026年7月30日</p>
        </section>
        """
        errors = self.validate(html)
        self.assertIn("article:visible_topic_source_forbidden", errors)
        self.assertIn("article:visible_verification_date_forbidden", errors)


if __name__ == "__main__":
    unittest.main()
