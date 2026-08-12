#!/usr/bin/env python3
"""Apply content upgrades to lesson HTML files."""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from upgrades_part1 import CAPTIONS as C1
from upgrades_part1 import UPGRADES as U1
from upgrades_part2 import CAPTIONS as C2
from upgrades_part2 import UPGRADES as U2

ROOT = Path(__file__).resolve().parents[1]
LESSONS = [
    (1, "01-networking-foundations"),
    (2, "02-connecting-networks"),
    (3, "03-ec2-load-balancing"),
    (4, "04-storage-architecture"),
    (5, "05-databases-caching"),
    (6, "06-iam-organizations"),
    (7, "07-app-data-security"),
    (8, "08-serverless-apis"),
    (9, "09-containers-compute"),
    (10, "10-messaging-events"),
    (11, "11-resilience-dr"),
    (12, "12-edge-global"),
    (13, "13-data-analytics"),
    (14, "14-migration-hybrid"),
    (15, "15-monitoring-ops"),
    (16, "16-cost-optimization"),
    (17, "17-final-patterns"),
]
UPGRADES = {**U1, **U2}
CAPTIONS = {**C1, **C2}


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def render_visual_rules(rules: list[tuple[str, str]]) -> str:
    parts = ['    <div class="visual-rules">']
    for i, (title, para) in enumerate(rules, 1):
        mark = ["①", "②", "③", "④"][i - 1]
        parts.append(
            f"      <div><span>{mark}</span><b>{esc(title)}</b><p>{esc(para)}</p></div>"
        )
    parts.append("    </div>")
    return "\n".join(parts)


def render_scenarios(lesson: int, scenarios: list[dict]) -> str:
    tabs = []
    panels = []
    for i, sc in enumerate(scenarios):
        active = " active" if i == 0 else ""
        tabs.append(
            f'<button type="button" onclick="showScenario({lesson},{i},this)" '
            f'class="scenario-tab{active}">{esc(sc["tab"])}</button>'
        )
        reasons = "".join(
            f'<span>{j}</span> {esc(r)}'
            + (" <b>→</b>" if j < 3 else "")
            for j, r in enumerate(sc["reason"], 1)
        )
        panels.append(
            f'<div class="scenario-panel{active}" id="sc-{lesson}-{i}">\n'
            f'          <div class="scenario-label">WORKED SCENARIO</div>'
            f'<h3>{esc(sc["title"])}</h3>\n'
            f'          <p>{esc(sc["body"])}</p>\n'
            f'          <div class="reason-strip">{reasons}</div>\n'
            f"        </div>"
        )
    return (
        '    <div class="section-kicker">04 · WORKED SCENARIOS</div>'
        "<h2>Apply the concepts as an architect</h2>\n"
        f'    <div class="scenario-tabs">{"".join(tabs)}</div>'
        + "".join(panels)
    )


def render_quiz(lesson: int, quiz: list[dict]) -> str:
    cards = []
    for i, item in enumerate(quiz, 1):
        qid = f"q-{lesson}-{i}"
        opts = []
        for oi, opt in enumerate(item["options"]):
            correct = "true" if oi == item["correct"] else "false"
            opts.append(
                f'<button type="button" class="option" onclick="answer(this,{correct},\'{qid}\')">'
                f"{esc(opt)}</button>"
            )
            letter = chr(65 + item["correct"])
        cards.append(
            f'<div class="quiz-card"><div class="qtop"><span>Q{i}</span><b>{esc(item["q"])}</b></div>'
            + "".join(opts)
            + f'\n        <div class="feedback" id="{qid}"><strong>Answer: {letter}.</strong> '
            f'{esc(item["explain"])}</div></div>'
        )
    return (
        '    <div class="section-kicker">06 · KNOWLEDGE CHECK</div>'
        "<h2>Five SAA-style questions</h2>\n    "
        + "".join(cards)
    )


def patch_lesson(n: int, slug: str) -> None:
    path = ROOT / "lessons" / f"{slug}.html"
    text = path.read_text()
    data = UPGRADES[n]

    # Visual rules
    text = re.sub(
        r'<div class="visual-rules">.*?</div>\s*(?=</div>\s*\n\s*<div class="lesson-section" id="deep)',
        render_visual_rules(data["visual_rules"]) + "\n  ",
        text,
        count=1,
        flags=re.S,
    )

    # Caption in SVG footer text nodes that contain our earlier captions or generic ones
    if n in CAPTIONS:
        text = re.sub(
            r'(<text x="560" y="440"[^>]*>)(.*?)(</text>)',
            lambda m: m.group(1) + esc(CAPTIONS[n]) + m.group(3),
            text,
            count=1,
        )

    # Scenarios section body (from kicker through end of scenario panels, before decoder)
    text = re.sub(
        r'(<div class="lesson-section" id="scenario-\d+">\s*)'
        r'.*?'
        r'(?=</div>\s*\n\s*<div class="lesson-section" id="decoder)',
        lambda m: m.group(1) + "\n" + render_scenarios(n, data["scenarios"]) + "\n  ",
        text,
        count=1,
        flags=re.S,
    )

    # Quiz section
    text = re.sub(
        r'(<div class="lesson-section" id="quiz-\d+">\s*)'
        r'.*?'
        r'(?=</div>\s*\n\s*<div class="complete">)',
        lambda m: m.group(1) + "\n" + render_quiz(n, data["quiz"]) + "\n  ",
        text,
        count=1,
        flags=re.S,
    )

    # Add simple SVG callout note after arch closing if not present
    callout = data.get("svg_note")
    if callout and 'class="svg-note"' not in text:
        text = text.replace(
            "</div>\n    <div class=\"visual-rules\">",
            f'</div>\n    <div class="info-note svg-note"><b>Diagram cue:</b> {esc(callout)}</div>\n    <div class="visual-rules">',
            1,
        )

    path.write_text(text)
    print(f"upgraded {path.name}")


def main() -> None:
    for n, slug in LESSONS:
        if n not in UPGRADES:
            raise SystemExit(f"missing upgrades for lesson {n}")
        patch_lesson(n, slug)
    print("all lessons upgraded")


if __name__ == "__main__":
    main()
