#!/usr/bin/env python3
"""Check reusable Ehafo article emphasis markup before delivery."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


FIXED_FOOTER_TARGET = "https://quiz.yiqizuoti.com/index-94528774.html#/quiz/index"


def visible_length(value: str) -> int:
    return len(re.sub(r"\s+", "", value))


class ArticleMarkupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[dict[str, object]] = []
        self.green_items: list[dict[str, object]] = []
        self.highlight_items: list[dict[str, object]] = []
        self.paragraph_green_counts: list[int] = []
        self.visible_text: list[str] = []
        self.links: list[str] = []
        self.fixed_footer_links: list[str | None] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if tag == "img":
            source = values.get("src", "")
            if "ARTICLE_FOOTER_URL" in source or source.endswith(
                "ehafo-article-footer.png"
            ):
                active_link = next(
                    (
                        str(parent["href"])
                        for parent in reversed(self.stack)
                        if parent["tag"] == "a" and parent["href"]
                    ),
                    None,
                )
                self.fixed_footer_links.append(active_link)
        classes = set(values.get("class", "").split())
        parent_tags = {str(parent["tag"]) for parent in self.stack}
        parent_classes = {
            name
            for parent in self.stack
            for name in parent["classes"]
        }
        item: dict[str, object] = {
            "tag": tag,
            "classes": classes,
            "style": values.get("style", "").lower().replace(" ", ""),
            "href": values.get("href", ""),
            "text": [],
            "green_count": 0,
            "forbidden_green_region": bool(
                parent_tags.intersection({"h1", "h2", "h3"})
                or parent_classes.intersection(
                    {"summary", "official-sources", "half-highlight"}
                )
            ),
        }
        self.stack.append(item)
        if "key-green" in classes:
            self.green_items.append(item)
            for parent in reversed(self.stack[:-1]):
                if parent["tag"] == "p":
                    parent["green_count"] = int(parent["green_count"]) + 1
                    break
        if "half-highlight" in classes:
            self.highlight_items.append(item)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack:
            return
        item = self.stack.pop()
        if item["tag"] == "p":
            self.paragraph_green_counts.append(int(item["green_count"]))
        if self.stack:
            self.stack[-1]["text"].extend(item["text"])

    def handle_data(self, data: str) -> None:
        self.visible_text.append(data)
        for item in self.stack:
            item["text"].append(data)


def validate(path: Path) -> list[str]:
    parser = ArticleMarkupParser()
    parser.feed(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    visible_text = "".join(parser.visible_text)
    if "选题来源" in visible_text:
        errors.append("article:visible_topic_source_forbidden")
    if "核验日期" in visible_text:
        errors.append("article:visible_verification_date_forbidden")
    if any(
        phrase in visible_text
        for phrase in ("内容参考", "参考文章", "本文参考", "参考了")
    ):
        errors.append("article:visible_content_reference_forbidden")
    nonofficial_source_link = False
    for link in parser.links:
        parsed = urlparse(link)
        host = parsed.netloc.lower()
        if host == "mp.weixin.qq.com" or (
            host in {"ehafo.com", "www.ehafo.com"}
            and parsed.path.startswith("/exam/questions/")
        ):
            nonofficial_source_link = True
    if nonofficial_source_link:
        errors.append("article:visible_nonofficial_source_link_forbidden")

    for link in parser.fixed_footer_links:
        if link is None:
            errors.append("article:fixed_footer_link_missing")
        elif link != FIXED_FOOTER_TARGET:
            errors.append("article:fixed_footer_link_target_invalid")

    for index, item in enumerate(parser.green_items):
        text = "".join(item["text"])
        length = visible_length(text)
        style = str(item["style"])
        if not 3 <= length <= 6:
            errors.append(f"key-green[{index}]:visible_length_must_be_3_to_6")
        if item["forbidden_green_region"]:
            errors.append(f"key-green[{index}]:forbidden_region")
        for required in ("color:#3d8063", "font-weight:500", "white-space:nowrap"):
            if required not in style:
                errors.append(f"key-green[{index}]:missing_style:{required}")

    for index, count in enumerate(parser.paragraph_green_counts):
        if count > 1:
            errors.append(f"paragraph[{index}]:key-green_must_be_at_most_one")

    for index, item in enumerate(parser.highlight_items):
        style = str(item["style"])
        required = (
            "linear-gradient(tobottom,transparent50%,#dcefe750%)",
            "box-decoration-break:clone",
            "-webkit-box-decoration-break:clone",
        )
        for value in required:
            if value not in style:
                errors.append(f"half-highlight[{index}]:missing_style:{value}")
        if "key-green" in str(item["classes"]):
            errors.append(f"half-highlight[{index}]:must_not_stack_key_green")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    args = parser.parse_args()
    errors = validate(args.html)
    print(json.dumps({"ok": not errors, "errors": errors}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
