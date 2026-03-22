# Parameter Golf Monitor

Track the [openai/parameter-golf](https://github.com/openai/parameter-golf) competition leaderboard from your terminal.

Fetches open/merged PRs from GitHub's public API, extracts `val_bpb` scores, and displays a ranked leaderboard. Zero dependencies (Python 3 stdlib only), no authentication required.

## Quick Start

```bash
# Full leaderboard
python3 scripts/monitor.py

# Highlight your PRs
python3 scripts/monitor.py --me <your-github-username>

# Top 10 record attempts only
python3 scripts/monitor.py --top 10 --records-only

# Live polling every 5 minutes
python3 scripts/monitor.py --watch 5 --me <your-github-username>
```

## Web UI

```bash
python3 scripts/webui.py
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000).

The Web UI supports:
- open / merged / open+merged mode
- records-only and include-suspect filters
- top-N filtering
- since-date filtering
- highlighting your GitHub username with rank and gap context

### Deploy on Railway

This repo is Railway-ready:
- `Procfile` defines the start command: `python3 scripts/webui.py`
- `scripts/webui.py` reads Railway's `PORT` environment variable

Steps:
1. Push this repo to GitHub.
2. In Railway, create a new project from the repo.
3. Deploy (Railway will run the `web` process from `Procfile`).
4. Open the generated Railway URL.

## Options

| Flag | Description |
|------|-------------|
| `--me USER` | Highlight your GitHub username, show rank + gap to #1 |
| `--top N` | Show only top N scored entries |
| `--records-only` | Exclude non-record submissions |
| `--merged` | Show merged PRs only |
| `--all` | Show both open and merged PRs |
| `--since YYYY-MM-DD` | Filter by creation date |
| `--json` | JSON output for piping |
| `--watch MIN` | Poll every N minutes (Ctrl+C to stop) |

## Example

```
$ python3 scripts/monitor.py --me dexhunter --top 5

[2026-03-20 02:17:15] Parameter Golf Leaderboard (open PRs)

Rank   val_bpb     PR  Status    Author              Date        Title
----------------------------------------------------------------------------------------------------
   1   1.15390  #135   open      unnir               2026-03-19  Record: OrthoInit + Int6 MLP3x + BigramHash + SmearGate
   2   1.15800  #106   open      krammnic            2026-03-19  record: 1.158
   3   1.15850  #122   open      mtybadger           2026-03-19  Record: Sliding Window Eval, 2048 Vocab Size
   4   1.15930  #150   open      yahya010            2026-03-20  [WIP] Record: Int6 QAT + BigramHash + MLP 1344
   5   1.15940  #128   open      rsavitt             2026-03-19  Record: Int6 MLP3x + STE QAT + Sliding Window
  11   1.16019  #156   open      dexhunter           2026-03-20  Int6 STE + NorMuon + SWA + Sliding Window  <--

Best: val_bpb=1.15390 (#135 by unnir)
Total: 56 PRs, 40 with scores

You (dexhunter): rank #11, val_bpb=1.16019, gap to #1: +0.00629
```

## Claude Code Skill

This is also a [Claude Code skill](https://github.com/anthropics/skills). Add the `parameter-golf-monitor/` directory to your project or `~/.claude/skills/` and Claude will automatically use it when you ask about the competition leaderboard.

## Rate Limits

Uses the unauthenticated GitHub API (60 requests/hour). Each check uses 1-2 requests. Polling every 5 minutes uses ~12-24 requests/hour.

## License

Apache 2.0 — see [LICENSE.txt](LICENSE.txt)
