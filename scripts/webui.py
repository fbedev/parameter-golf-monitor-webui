#!/usr/bin/env python3
"""Web UI server for Parameter Golf Monitor.

Run:
    python3 scripts/webui.py
Then open http://127.0.0.1:8000
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import monitor


ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "web"


@dataclass
class QueryOptions:
    mode: str = "open"
    since: str | None = None
    records_only: bool = False
    include_suspect: bool = False
    top: int | None = None
    me: str | None = None
    suspect_threshold: float = monitor.SUSPECT_SCORE_THRESHOLD


class WebUIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def _send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _parse_options(self, parsed) -> QueryOptions:
        qs = parse_qs(parsed.query)

        def truthy(value: str | None) -> bool:
            if value is None:
                return False
            return value.lower() in {"1", "true", "yes", "on"}

        mode = qs.get("mode", ["open"])[0]
        if mode not in {"open", "merged", "all"}:
            mode = "open"

        top_value = qs.get("top", [None])[0]
        try:
            top = int(top_value) if top_value else None
        except (TypeError, ValueError):
            top = None

        threshold_value = qs.get("suspect_threshold", [None])[0]
        try:
            threshold = float(threshold_value) if threshold_value else monitor.SUSPECT_SCORE_THRESHOLD
        except (TypeError, ValueError):
            threshold = monitor.SUSPECT_SCORE_THRESHOLD

        me = qs.get("me", [None])[0]
        if me:
            me = me.strip() or None

        since = qs.get("since", [None])[0]
        if since:
            since = since.strip() or None

        return QueryOptions(
            mode=mode,
            since=since,
            records_only=truthy(qs.get("records_only", [None])[0]),
            include_suspect=truthy(qs.get("include_suspect", [None])[0]),
            top=top,
            me=me,
            suspect_threshold=threshold,
        )

    def _fetch_entries(self, options: QueryOptions) -> tuple[list[dict[str, Any]], int]:
        all_prs: list[dict[str, Any]] = []

        if options.mode in {"merged", "all"}:
            closed = monitor.fetch_prs(state="closed", per_page=100)
            merged = [pr for pr in closed if pr.get("merged_at")]
            all_prs.extend(merged)

        if options.mode in {"open", "all"}:
            open_prs = monitor.fetch_prs(state="open", per_page=100)
            all_prs.extend(open_prs)

        show_all_types = options.mode == "all"
        entries, suspect_count = monitor.format_leaderboard(
            all_prs,
            show_all_types=show_all_types,
            since=options.since,
            records_only=options.records_only,
            include_suspect=options.include_suspect,
            suspect_threshold=options.suspect_threshold,
        )
        return entries, suspect_count

    @staticmethod
    def _with_rank(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        ranked: list[dict[str, Any]] = []
        rank = 0
        for entry in entries:
            item = dict(entry)
            if item.get("score") is not None:
                rank += 1
                item["rank"] = rank
            else:
                item["rank"] = None
            item["techniques"] = monitor.extract_techniques(item.get("body", ""))
            ranked.append(item)
        return ranked

    @staticmethod
    def _compute_stats(entries: list[dict[str, Any]], options: QueryOptions, suspect_count: int) -> dict[str, Any]:
        scored = [e for e in entries if e.get("score") is not None]
        best = min(scored, key=lambda e: e["score"]) if scored else None

        you = None
        if options.me:
            for entry in entries:
                if entry.get("author", "").lower() == options.me.lower():
                    you = entry
                    break

        return {
            "total": len(entries),
            "scored": len(scored),
            "best": {
                "score": best["score"],
                "number": best["number"],
                "author": best["author"],
            }
            if best
            else None,
            "suspect_count": suspect_count,
            "you": {
                "rank": you.get("rank"),
                "score": you.get("score"),
                "number": you.get("number"),
                "gap_to_best": (you["score"] - best["score"]) if (you and best and you.get("score") is not None) else None,
            }
            if you
            else None,
        }

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/api/leaderboard":
            try:
                options = self._parse_options(parsed)
                entries, suspect_count = self._fetch_entries(options)
                entries = self._with_rank(entries)

                if options.top and options.top > 0:
                    filtered: list[dict[str, Any]] = []
                    scored_shown = 0
                    for entry in entries:
                        is_me = bool(options.me and entry.get("author", "").lower() == options.me.lower())
                        if entry.get("score") is not None:
                            if scored_shown < options.top or is_me:
                                filtered.append(entry)
                            if scored_shown < options.top:
                                scored_shown += 1
                        elif is_me:
                            filtered.append(entry)
                    entries = filtered

                payload = {
                    "generated_at": datetime.now().isoformat(timespec="seconds"),
                    "mode": options.mode,
                    "filters": {
                        "since": options.since,
                        "records_only": options.records_only,
                        "include_suspect": options.include_suspect,
                        "top": options.top,
                        "me": options.me,
                        "suspect_threshold": options.suspect_threshold,
                    },
                    "stats": self._compute_stats(entries, options, suspect_count),
                    "entries": [
                        {k: v for k, v in entry.items() if k != "body"}
                        for entry in entries
                    ],
                }
                self._send_json(200, payload)
                return
            except Exception as exc:  # pragma: no cover
                self._send_json(500, {"error": str(exc)})
                return

        if parsed.path == "/":
            self.path = "/index.html"

        super().do_GET()


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), WebUIHandler)
    print(f"Serving Parameter Golf Monitor Web UI on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
