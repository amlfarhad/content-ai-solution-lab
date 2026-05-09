from __future__ import annotations

import html
import json
from pathlib import Path

from .catalog import summarize_catalog
from .discovery import extract_solution_themes
from .models import DemoScenario


def write_solution_brief(scenario: DemoScenario, path: str | Path) -> None:
    lines = [
        f"# {scenario.customer} Solution Brief",
        "",
        f"Industry: {scenario.industry}",
        "",
        "## Discovery Signals",
    ]
    for signal in scenario.discovery_signals:
        lines.append(f"- {signal.stakeholder}: {signal.business_problem} -> {signal.desired_outcome}")

    lines.extend(["", "## Recommended Workflows"])
    for rec in scenario.recommendations:
        lines.append(f"### {rec.workflow_name}")
        lines.append(f"- Use case: {rec.use_case}")
        lines.append(f"- Target users: {', '.join(rec.target_users)}")
        lines.append(f"- API actions: {', '.join(rec.api_actions)}")
        lines.append(f"- AI agent actions: {', '.join(rec.ai_agent_actions)}")
        lines.append(f"- Success metrics: {', '.join(rec.success_metrics)}")

    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_demo_dashboard(scenario: DemoScenario, path: str | Path) -> None:
    themes = extract_solution_themes(scenario.discovery_signals)
    catalog = summarize_catalog(scenario.content_items)
    recommendations = scenario.recommendations
    data = {
        "themes": themes,
        "catalog": catalog,
        "recommendations": [rec.workflow_name for rec in recommendations],
    }
    cards = "\n".join(
        f"""
        <section class="card">
          <p class="eyebrow">Workflow</p>
          <h2>{html.escape(rec.workflow_name)}</h2>
          <p>{html.escape(rec.use_case)}</p>
          <h3>Demo Talk Track</h3>
          <ol>{''.join(f'<li>{html.escape(step)}</li>' for step in rec.demo_steps)}</ol>
          <h3>Success Metrics</h3>
          <ul>{''.join(f'<li>{html.escape(metric)}</li>' for metric in rec.success_metrics)}</ul>
        </section>
        """
        for rec in recommendations
    )
    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(scenario.customer)} Content AI Demo</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #17202a;
      --muted: #5f6b7a;
      --line: #d7dde5;
      --blue: #0455bf;
      --green: #13795b;
      --paper: #f7f9fc;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: white;
    }}
    header {{
      padding: 42px 52px 28px;
      border-bottom: 1px solid var(--line);
      background: linear-gradient(180deg, #ffffff 0%, var(--paper) 100%);
    }}
    main {{ padding: 28px 52px 48px; display: grid; gap: 18px; }}
    h1 {{ margin: 0 0 8px; font-size: 34px; letter-spacing: 0; }}
    h2 {{ margin: 4px 0 10px; font-size: 21px; }}
    h3 {{ margin: 18px 0 8px; font-size: 13px; text-transform: uppercase; letter-spacing: .04em; }}
    p {{ margin: 0; line-height: 1.45; }}
    .sub {{ color: var(--muted); max-width: 860px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 22px; max-width: 900px; }}
    .metric {{ border: 1px solid var(--line); background: white; padding: 14px; border-radius: 6px; }}
    .metric strong {{ display: block; font-size: 25px; color: var(--blue); }}
    .metric span {{ color: var(--muted); font-size: 13px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }}
    .card {{ border: 1px solid var(--line); border-radius: 6px; padding: 20px; background: white; }}
    .eyebrow {{ color: var(--green); font-weight: 700; text-transform: uppercase; font-size: 12px; letter-spacing: .08em; margin-bottom: 8px; }}
    li {{ margin: 6px 0; line-height: 1.35; }}
    pre {{ white-space: pre-wrap; background: #101820; color: #e8eef7; border-radius: 6px; padding: 16px; overflow: auto; }}
    @media (max-width: 800px) {{
      header, main {{ padding-left: 24px; padding-right: 24px; }}
      .metrics, .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <p class="eyebrow">Solutions Engineering Demo</p>
    <h1>{html.escape(scenario.customer)} Content AI Workflow</h1>
    <p class="sub">A customer-facing demo that turns discovery notes into platform capabilities, AI-agent actions, governance controls, and measurable rollout outcomes.</p>
    <div class="metrics">
      <div class="metric"><strong>{len(scenario.content_items)}</strong><span>sample content assets</span></div>
      <div class="metric"><strong>{len(scenario.discovery_signals)}</strong><span>stakeholder discovery signals</span></div>
      <div class="metric"><strong>{len(recommendations)}</strong><span>solution workflows</span></div>
    </div>
  </header>
  <main>
    <section class="grid">
      <div class="card">
        <p class="eyebrow">Discovery Themes</p>
        <pre>{html.escape(json.dumps(themes, indent=2))}</pre>
      </div>
      <div class="card">
        <p class="eyebrow">Catalog Mix</p>
        <pre>{html.escape(json.dumps(catalog, indent=2))}</pre>
      </div>
    </section>
    {cards}
  </main>
</body>
</html>
"""
    Path(path).write_text(html_doc, encoding="utf-8")

