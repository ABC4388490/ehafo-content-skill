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

    def test_rejects_visible_reference_attribution_and_nonofficial_links(self) -> None:
        html = """
        <p>参考文章汇总的往年渠道主要分成三类。</p>
        <section>
          <p>内容参考</p>
          <a href="https://www.ehafo.com/exam/questions/certificate-claim">医学考试指南</a>
          <a href="https://mp.weixin.qq.com/s/example">其他公众号文章</a>
        </section>
        """
        errors = self.validate(html)
        self.assertIn("article:visible_content_reference_forbidden", errors)
        self.assertIn("article:visible_nonofficial_source_link_forbidden", errors)

    def test_accepts_official_source_link_when_needed(self) -> None:
        html = """
        <section class="official-sources">
          <p>官方依据</p>
          <a href="https://www.gov.cn/zhengce/example.html">正式通知</a>
        </section>
        """
        self.assertEqual([], self.validate(html))

    def test_rejects_fixed_footer_without_app_link(self) -> None:
        html = """
        <img src="{{ARTICLE_FOOTER_URL}}" alt="易哈佛" />
        """
        self.assertIn(
            "article:fixed_footer_link_missing",
            self.validate(html),
        )

    def test_accepts_fixed_footer_with_app_link(self) -> None:
        html = """
        <a href="https://quiz.yiqizuoti.com/index-94528774.html#/quiz/index">
          <img src="../public/ehafo-article-footer.png" alt="易哈佛" />
        </a>
        """
        self.assertEqual([], self.validate(html))

    def test_rejects_fixed_footer_with_wrong_link(self) -> None:
        html = """
        <a href="https://example.com/">
          <img src="../public/ehafo-article-footer.png" alt="易哈佛" />
        </a>
        """
        self.assertIn(
            "article:fixed_footer_link_target_invalid",
            self.validate(html),
        )


if __name__ == "__main__":
    unittest.main()
