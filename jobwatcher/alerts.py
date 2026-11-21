"""Optional email alerts for newly observed matching roles.

The daily workflow calls this module after rebuilding the snapshot. It is a
no-op until RESEND_API_KEY, ALERT_EMAIL, and ALERT_FROM_EMAIL are configured
as repository secrets.
"""

from __future__ import annotations

import html
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


def _read(path: str | Path) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _rows(history: list[dict], status: dict) -> list[dict]:
    date = status.get("latest_run_date", "")
    return [
        row for row in history
        if row.get("first_seen") == date
        and not row.get("first_run")
        and row.get("is_us")
        and row.get("in_role")
        and not row.get("removed_date")
    ]


def build_alert(history: list[dict], status: dict) -> tuple[str, str, str]:
    rows = _rows(history, status)
    date = status.get("latest_run_date", "")
    subject = f"Job Watcher: {len(rows)} new finance roles · {date}"
    if not rows:
        text = f"No new U.S. finance / early-career roles were added on {date}."
        return subject, text, f"<p>{html.escape(text)}</p>"
    lines = [f"{len(rows)} new U.S. finance / early-career roles were added on {date}.", ""]
    cards = []
    for row in rows[:25]:
        salary = f" · {row.get('salary_text')}" if row.get("salary_text") else ""
        line = f"- {row.get('title')} — {row.get('employer')} · {row.get('location')}{salary}\n  {row.get('apply_url')}"
        lines.append(line)
        cards.append(
            f"<li><a href=\"{html.escape(row.get('apply_url', ''), quote=True)}\">{html.escape(row.get('title', ''))}</a>"
            f" — {html.escape(row.get('employer', ''))} · {html.escape(row.get('location', ''))}"
            f"{(' · ' + html.escape(row.get('salary_text', ''))) if row.get('salary_text') else ''}</li>"
        )
    if len(rows) > 25:
        lines.extend(["", f"…and {len(rows) - 25} more. See the full tracker online."])
    return subject, "\n".join(lines), f"<p>{len(rows)} new U.S. finance / early-career roles were added on <strong>{html.escape(date)}</strong>.</p><ul>{''.join(cards)}</ul>"


def send_alert(*, history_path: str | Path = "data/processed/history.json", status_path: str | Path = "data/processed/status.json") -> bool:
    api_key = os.getenv("RESEND_API_KEY")
    recipients = [item.strip() for item in os.getenv("ALERT_EMAIL", "").split(",") if item.strip()]
    sender = os.getenv("ALERT_FROM_EMAIL")
    if not api_key or not recipients or not sender:
        return False
    history = _read(history_path)
    status = _read(status_path)
    subject, text, body = build_alert(history, status)
    payload = json.dumps({"from": sender, "to": recipients, "subject": subject, "text": text, "html": body}).encode("utf-8")
    request = Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=30):
        return True


def main() -> None:
    print(json.dumps({"sent": send_alert()}))


if __name__ == "__main__":
    main()
