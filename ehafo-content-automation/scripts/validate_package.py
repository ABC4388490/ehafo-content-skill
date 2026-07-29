#!/usr/bin/env python3
"""Validate an Ehafo content package before automatic release."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


HIGH_RISK_TERMS = (
    "报名", "审核", "缴费", "准考证", "考试时间", "成绩", "证书",
    "学历", "专业要求", "实习", "工作年限", "免考", "费用", "合格线",
)
BANNED_MARKETING = (
    "包过", "必过", "稳过", "100%通过", "百分百通过", "保证拿证",
    "一次上岸", "命题组内部", "内部押题", "考前原题", "官方指定",
)
REQUIRED_TOP = (
    "status", "topic", "audience", "problem", "action", "verification_date",
    "claims", "topic_selection", "user_task", "user_test", "value_evidence",
    "format_decision", "outputs",
)
REQUIRED_CLAIM = (
    "id", "text", "risk", "exam", "year", "region", "official",
    "source_org", "source_title", "source_url", "source_publish_date",
    "retrieved_date", "source_scope_exam", "source_scope_year",
    "source_scope_region", "conflict",
)
SCORE_WEIGHTS = {
    "immediate_usefulness": 25,
    "audience_reach": 20,
    "loss_prevention": 20,
    "actionability": 20,
    "current_relevance": 15,
}
VAGUE_SCORE_REASON_PATTERNS = (
    r"感觉",
    r"应该",
    r"大概",
    r"可能很多",
    r"大家都",
    r"很重要",
)
WEAK_DEFLECTION_PATTERNS = (
    r"自行查询",
    r"自己去问",
    r"以当地为准",
    r"咨询当地",
)
ALLOWED_JOURNEY_TYPES = {
    "chronological", "decision_path", "comparison", "checklist",
}
BRAND_PROMO_ASSET = "assets/ehafo-brand-promo.png"
BRAND_PROMO_SHA256 = (
    "56f998e0802d34b23077036160f380e4fd14bda1fbf5e192fae8222f69f1343c"
)


def valid_date(value: object) -> bool:
    try:
        date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return False
    return True


def visible_length(value: str) -> int:
    return len(re.sub(r"\s+", "", value))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path)
    args = parser.parse_args()

    try:
        data = json.loads(args.package.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)]}, ensure_ascii=False))
        return 2

    errors: list[str] = []
    for key in REQUIRED_TOP:
        if key not in data or data[key] in (None, "", []):
            errors.append(f"missing:{key}")

    status = data.get("status")
    allowed_statuses = {
        "DRAFT_PASS", "VALUE_UNPROVEN", "AUTO_RELEASE", "BLOCKED"
    }
    if status not in allowed_statuses:
        errors.append("invalid:status")

    user_task = data.get("user_task", {})
    if not isinstance(user_task, dict):
        errors.append("user_task_must_be_object")
    else:
        for key in (
            "current_state", "core_question", "desired_outcome",
            "must_answer", "next_action", "success_without_other_guide",
        ):
            if key not in user_task or user_task[key] in (None, "", []):
                errors.append(f"user_task:missing:{key}")
        must_answer = user_task.get("must_answer", [])
        if not isinstance(must_answer, list) or not must_answer:
            errors.append("user_task:must_answer_must_be_nonempty_list")
        if user_task.get("success_without_other_guide") is not True:
            errors.append("user_task:must_be_complete_without_other_guide")

    user_test = data.get("user_test", {})
    if not isinstance(user_test, dict):
        errors.append("user_test_must_be_object")
    else:
        for key in (
            "audience_identified", "next_action_understood",
            "must_answer_coverage", "requires_other_guide",
            "critical_new_questions", "verdict",
        ):
            if key not in user_test:
                errors.append(f"user_test:missing:{key}")
        coverage = user_test.get("must_answer_coverage", [])
        if not isinstance(coverage, list):
            errors.append("user_test:coverage_must_be_list")
            coverage = []
        task_questions = set(map(str, user_task.get("must_answer", []))) if isinstance(user_task, dict) else set()
        covered_questions: set[str] = set()
        for index, item in enumerate(coverage):
            if not isinstance(item, dict):
                errors.append(f"user_test.coverage[{index}]:must_be_object")
                continue
            question = str(item.get("question", ""))
            covered_questions.add(question)
            if item.get("answered") is not True:
                errors.append(f"user_test.coverage[{index}]:not_answered")
            if visible_length(str(item.get("location", ""))) < 2:
                errors.append(f"user_test.coverage[{index}]:location_required")
        if task_questions != covered_questions:
            errors.append("user_test:coverage_must_match_user_task")
        test_pass = (
            user_test.get("audience_identified") is True
            and user_test.get("next_action_understood") is True
            and user_test.get("requires_other_guide") is False
            and user_test.get("critical_new_questions") == []
            and user_test.get("verdict") == "pass"
        )
        if status in ("VALUE_UNPROVEN", "AUTO_RELEASE") and not test_pass:
            errors.append("status_requires_passing_user_test")
        if status == "DRAFT_PASS" and test_pass:
            errors.append("draft_pass_requires_unresolved_user_test")

    value_evidence = data.get("value_evidence", {})
    if not isinstance(value_evidence, dict):
        errors.append("value_evidence_must_be_object")
    else:
        for key in (
            "status", "comparable_content", "success_criteria",
            "observation_window",
        ):
            if key not in value_evidence:
                errors.append(f"value_evidence:missing:{key}")
        evidence_status = value_evidence.get("status")
        if evidence_status not in ("unproven", "validated"):
            errors.append("value_evidence:invalid_status")
        if status == "AUTO_RELEASE":
            if evidence_status != "validated":
                errors.append("auto_release_requires_validated_value_evidence")
            if not value_evidence.get("comparable_content"):
                errors.append("auto_release_requires_comparable_content")
            if not value_evidence.get("success_criteria"):
                errors.append("auto_release_requires_success_criteria")
            if not str(value_evidence.get("observation_window", "")).strip():
                errors.append("auto_release_requires_observation_window")
        if status == "VALUE_UNPROVEN" and evidence_status != "unproven":
            errors.append("value_unproven_requires_unproven_evidence")

    verification_date = data.get("verification_date")
    if not valid_date(verification_date):
        errors.append("invalid:verification_date")

    claim_ids: set[str] = set()
    for index, claim in enumerate(data.get("claims", [])):
        prefix = f"claims[{index}]"
        for key in REQUIRED_CLAIM:
            if key not in claim or claim[key] in (None, ""):
                errors.append(f"{prefix}:missing:{key}")
        claim_id = str(claim.get("id", ""))
        if claim_id in claim_ids:
            errors.append(f"{prefix}:duplicate_id:{claim_id}")
        claim_ids.add(claim_id)

        text = str(claim.get("text", ""))
        risk = claim.get("risk")
        if risk not in ("high", "low"):
            errors.append(f"{prefix}:invalid:risk")
        implied_high = any(term in text for term in HIGH_RISK_TERMS)
        if implied_high and risk != "high":
            errors.append(f"{prefix}:risk_should_be_high")

        if risk == "high" or implied_high:
            if claim.get("official") is not True:
                errors.append(f"{prefix}:high_risk_requires_official_source")
            parsed = urlparse(str(claim.get("source_url", "")))
            if parsed.scheme != "https" or not parsed.netloc:
                errors.append(f"{prefix}:invalid_official_url")
            if claim.get("conflict") is not False:
                errors.append(f"{prefix}:source_conflict")
            if claim.get("exam") != claim.get("source_scope_exam"):
                errors.append(f"{prefix}:exam_scope_mismatch")
            if claim.get("year") != claim.get("source_scope_year"):
                errors.append(f"{prefix}:year_scope_mismatch")
            if claim.get("region") != claim.get("source_scope_region"):
                errors.append(f"{prefix}:region_scope_mismatch")

        for key in ("source_publish_date", "retrieved_date"):
            if not valid_date(claim.get(key)):
                errors.append(f"{prefix}:invalid:{key}")
        if verification_date and claim.get("retrieved_date") != verification_date:
            errors.append(f"{prefix}:retrieved_date_mismatch")

    outputs = data.get("outputs", {})
    if not isinstance(outputs, dict) or not outputs:
        errors.append("outputs_must_be_nonempty_object")
        output_text = ""
    else:
        output_text = json.dumps(outputs, ensure_ascii=False)

    selection = data.get("topic_selection", {})
    if not isinstance(selection, dict):
        errors.append("topic_selection_must_be_object")
    else:
        selection_mode = selection.get("mode")
        if selection_mode not in ("auto", "user_selected"):
            errors.append("invalid:topic_selection:mode")
        if not str(selection.get("selected_reason", "")).strip():
            errors.append("topic_selection:selected_reason_required")
        if selection_mode == "auto":
            candidates = selection.get("candidates", [])
            selected_id = str(selection.get("selected_id", ""))
            if not isinstance(candidates, list) or not candidates:
                errors.append("topic_selection:auto_requires_candidates")
                candidates = []
            candidate_ids: list[str] = []
            eligible: list[tuple[str, float, dict]] = []
            for index, candidate in enumerate(candidates):
                prefix = f"topic_selection.candidates[{index}]"
                if not isinstance(candidate, dict):
                    errors.append(f"{prefix}:must_be_object")
                    continue
                for key in (
                    "id", "topic", "audience", "problem", "action",
                    "evidence_status", "valid_now", "hard_gate_passed",
                    "time_override", "scores", "score_reasons", "total_score",
                ):
                    if key not in candidate or candidate[key] in (None, ""):
                        errors.append(f"{prefix}:missing:{key}")
                candidate_id = str(candidate.get("id", ""))
                candidate_ids.append(candidate_id)
                scores = candidate.get("scores", {})
                reasons = candidate.get("score_reasons", {})
                if not isinstance(scores, dict) or set(scores) != set(SCORE_WEIGHTS):
                    errors.append(f"{prefix}:invalid:scores")
                    continue
                if not isinstance(reasons, dict) or set(reasons) != set(SCORE_WEIGHTS):
                    errors.append(f"{prefix}:invalid:score_reasons")
                    continue
                if any(not str(reasons[key]).strip() for key in SCORE_WEIGHTS):
                    errors.append(f"{prefix}:score_reason_required")
                for key in SCORE_WEIGHTS:
                    reason = str(reasons.get(key, "")).strip()
                    if visible_length(reason) < 12:
                        errors.append(f"{prefix}:score_reason_too_vague:{key}")
                    if any(
                        re.search(pattern, reason)
                        for pattern in VAGUE_SCORE_REASON_PATTERNS
                    ):
                        errors.append(f"{prefix}:unsupported_score_reason:{key}")
                if any(
                    not isinstance(scores[key], int) or not 0 <= scores[key] <= 5
                    for key in SCORE_WEIGHTS
                ):
                    errors.append(f"{prefix}:scores_must_be_integers_0_to_5")
                    continue
                if any(scores[key] == 0 for key in SCORE_WEIGHTS):
                    zero_value_gap = True
                else:
                    zero_value_gap = False
                calculated = sum(
                    scores[key] / 5 * weight
                    for key, weight in SCORE_WEIGHTS.items()
                )
                reported = candidate.get("total_score")
                if not isinstance(reported, (int, float)) or abs(reported - calculated) > 0.01:
                    errors.append(f"{prefix}:total_score_mismatch")
                    continue
                if (
                    candidate.get("hard_gate_passed") is True
                    and candidate.get("valid_now") is True
                    and candidate.get("evidence_status") == "verified"
                    and calculated >= 65
                    and not zero_value_gap
                ):
                    eligible.append((candidate_id, calculated, candidate))
            if len(candidate_ids) != len(set(candidate_ids)):
                errors.append("topic_selection:duplicate_candidate_id")
            if selected_id not in candidate_ids:
                errors.append("topic_selection:selected_id_not_found")
            else:
                selected_candidate = next(
                    item for item in candidates
                    if isinstance(item, dict) and str(item.get("id", "")) == selected_id
                )
                for package_key, candidate_key in (
                    ("topic", "topic"),
                    ("audience", "audience"),
                    ("problem", "problem"),
                    ("action", "action"),
                ):
                    if data.get(package_key) != selected_candidate.get(candidate_key):
                        errors.append(
                            f"topic_selection:selected_{candidate_key}_mismatch"
                        )
            overrides = [
                item for item in eligible
                if item[2].get("time_override") is True and item[1] >= 75
            ]
            pool = overrides or eligible
            if not pool:
                errors.append("topic_selection:no_eligible_candidate")
            else:
                ranked = sorted(
                    pool,
                    key=lambda item: (
                        item[1],
                        item[2]["scores"]["loss_prevention"],
                        item[2]["scores"]["immediate_usefulness"],
                        item[2]["scores"]["audience_reach"],
                        item[2]["scores"]["actionability"],
                    ),
                    reverse=True,
                )
                if selected_id != ranked[0][0]:
                    errors.append("topic_selection:selected_candidate_not_highest_value")

    decision = data.get("format_decision", {})
    allowed_formats = {"news", "article", "cards"}
    selected = decision.get("selected", []) if isinstance(decision, dict) else []
    if (
        not isinstance(decision, dict)
        or not isinstance(selected, list)
        or not selected
        or any(item not in allowed_formats for item in selected)
        or len(selected) != len(set(selected))
    ):
        errors.append("invalid:format_decision:selected")
        selected = []
    if isinstance(outputs, dict) and set(outputs) != set(selected):
        errors.append("outputs_must_match_selected_formats")

    rejected = decision.get("rejected", {}) if isinstance(decision, dict) else {}
    expected_rejected = allowed_formats - set(selected)
    if not isinstance(rejected, dict) or set(rejected) != expected_rejected:
        errors.append("rejected_formats_must_be_explained")
    elif any(not str(reason).strip() for reason in rejected.values()):
        errors.append("rejected_format_reason_required")

    card_count = decision.get("card_count") if isinstance(decision, dict) else None
    if not isinstance(card_count, int) or card_count < 0:
        errors.append("invalid:format_decision:card_count")
    elif "cards" not in selected and card_count != 0:
        errors.append("card_count_must_be_zero_when_cards_rejected")
    elif "cards" in selected and card_count < 1:
        errors.append("card_count_must_be_positive")

    if "cards" in selected and isinstance(outputs, dict):
        cards = outputs.get("cards", {})
        items = cards.get("items", []) if isinstance(cards, dict) else []
        visual_spec = cards.get("visual_spec", {}) if isinstance(cards, dict) else {}
        brand_promo = cards.get("brand_promo", {}) if isinstance(cards, dict) else {}
        journey_type = cards.get("journey_type") if isinstance(cards, dict) else None
        journey_reason = cards.get("journey_reason") if isinstance(cards, dict) else None
        cover_promises = cards.get("cover_promises", []) if isinstance(cards, dict) else []
        if journey_type not in ALLOWED_JOURNEY_TYPES:
            errors.append("cards:invalid_or_missing_journey_type")
        if visible_length(str(journey_reason or "")) < 10:
            errors.append("cards:journey_reason_too_weak")
        if not isinstance(visual_spec, dict):
            errors.append("cards:visual_spec_must_be_object")
        else:
            if visual_spec.get("background_type") != "solid":
                errors.append("cards:background_must_be_solid")
            if visual_spec.get("background_image") is not False:
                errors.append("cards:background_image_forbidden")
            if visual_spec.get("people_or_illustration") is not False:
                errors.append("cards:people_or_illustration_forbidden")
            if visual_spec.get("logo_mode") not in (
                "programmatic_overlay", "asset_blocked"
            ):
                errors.append("cards:invalid_logo_mode")
        if not isinstance(brand_promo, dict):
            errors.append("cards:brand_promo_must_be_object")
        else:
            expected_brand_promo = {
                "required": True,
                "placement": "append_after_content",
                "asset_path": BRAND_PROMO_ASSET,
                "transform": "none",
                "sha256": BRAND_PROMO_SHA256,
            }
            for key, expected in expected_brand_promo.items():
                if brand_promo.get(key) != expected:
                    errors.append(f"cards:invalid_brand_promo:{key}")
        if not isinstance(items, list) or len(items) != card_count:
            errors.append("cards_items_must_match_card_count")
        else:
            module_ids: list[str] = []
            for index, item in enumerate(items):
                if not isinstance(item, dict):
                    errors.append(f"cards.items[{index}]:must_be_object")
                    continue
                for key in (
                    "module_id", "title", "body", "user_value", "role",
                    "question", "answer", "next_action",
                ):
                    if not str(item.get(key, "")).strip():
                        errors.append(f"cards.items[{index}]:missing:{key}")
                if visible_length(str(item.get("question", ""))) < 6:
                    errors.append(f"cards.items[{index}]:question_too_weak")
                if visible_length(str(item.get("answer", ""))) < 8:
                    errors.append(f"cards.items[{index}]:answer_too_weak")
                if visible_length(str(item.get("next_action", ""))) < 6:
                    errors.append(f"cards.items[{index}]:next_action_too_weak")
                action_text = " ".join(
                    str(item.get(key, ""))
                    for key in ("body", "answer", "next_action")
                )
                if any(
                    re.search(pattern, action_text)
                    for pattern in WEAK_DEFLECTION_PATTERNS
                ) and visible_length(str(item.get("official_entry", ""))) < 6:
                    errors.append(
                        f"cards.items[{index}]:regional_variance_requires_official_entry"
                    )
                expected_role = "cover_and_content" if index == 0 else "content"
                if item.get("role") != expected_role:
                    errors.append(
                        f"cards.items[{index}]:role_must_be:{expected_role}"
                    )
                if index == 0:
                    for key in ("hook", "payoff"):
                        if visible_length(str(item.get(key, ""))) < 6:
                            errors.append(f"cards.items[0]:missing_or_weak:{key}")
                    generic_cover_terms = (
                        "材料关系", "内容总览", "知识整理", "内容整理"
                    )
                    if any(
                        term in str(item.get("title", ""))
                        for term in generic_cover_terms
                    ):
                        errors.append("cards.items[0]:generic_cover_title")
                module_ids.append(str(item.get("module_id", "")))
            if len(module_ids) != len(set(module_ids)):
                errors.append("cards_module_ids_must_be_unique")
            if not isinstance(cover_promises, list) or not 1 <= len(cover_promises) <= 4:
                errors.append("cards:cover_promises_must_be_1_to_4")
            else:
                promise_ids: list[str] = []
                fulfilled_modules: set[str] = set()
                for index, promise in enumerate(cover_promises):
                    prefix = f"cards.cover_promises[{index}]"
                    if not isinstance(promise, dict):
                        errors.append(f"{prefix}:must_be_object")
                        continue
                    promise_id = str(promise.get("id", "")).strip()
                    promise_text = str(promise.get("text", "")).strip()
                    fulfilled_by = promise.get("fulfilled_by", [])
                    if not promise_id:
                        errors.append(f"{prefix}:missing:id")
                    if visible_length(promise_text) < 6:
                        errors.append(f"{prefix}:text_too_weak")
                    if not isinstance(fulfilled_by, list) or not fulfilled_by:
                        errors.append(f"{prefix}:fulfilled_by_required")
                        fulfilled_by = []
                    unknown_modules = set(map(str, fulfilled_by)) - set(module_ids)
                    if unknown_modules:
                        errors.append(
                            f"{prefix}:unknown_modules:" +
                            ",".join(sorted(unknown_modules))
                        )
                    promise_ids.append(promise_id)
                    fulfilled_modules.update(map(str, fulfilled_by))
                if len(promise_ids) != len(set(promise_ids)):
                    errors.append("cards:duplicate_cover_promise_id")
                content_modules = set(module_ids[1:])
                if card_count > 1 and not content_modules.issubset(fulfilled_modules):
                    errors.append("cards:content_module_not_tied_to_cover_promise")

    for phrase in BANNED_MARKETING:
        if phrase in output_text:
            errors.append(f"banned_phrase:{phrase}")

    for name, content in outputs.items() if isinstance(outputs, dict) else []:
        if isinstance(content, dict):
            title = str(content.get("title", ""))
            if title and visible_length(title) > 20:
                errors.append(f"{name}:title_over_20_chars")

    cited = set(re.findall(r"\bC\d{2,}\b", output_text))
    unknown = cited - claim_ids
    if unknown:
        errors.append("unknown_claim_ids:" + ",".join(sorted(unknown)))

    result = {"ok": not errors, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
