# GitGauge

GitHub Profile Auditor and Beginner Issue Finder

GitGauge scores your GitHub profile against recruiter-visible criteria, tells you
what to fix, and finds beginner-friendly open-source issues to work on next.
Runs as a terminal tool and as a Streamlit web app using the same core engine.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Architecture](#architecture)
- [File Structure](#file-structure)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Scoring Methodology](#scoring-methodology)
- [Honest Limitations](#honest-limitations)
- [What's Next](#whats-next)

---

## Overview

I built GitGauge to solve a problem I noticed: most CS students applying for
internships have GitHub profiles that are weak not because they cannot code, but
because they do not know what a recruiter actually looks at. Empty descriptions,
stale repos, no bio, no real contributions outside their own account.

GitGauge fixes that in two ways. The audit mode scores your profile and tells you
exactly what to fix. The Find Me Work mode searches GitHub for real open issues
tagged as beginner-friendly and ranks them by how approachable they are. If your
profile is weak on contributions, you get a direct list of places to start — the
tool closes its own loop.

---

## Features

| Feature | Description |
|---|---|
| Profile Score | Scores a GitHub profile out of 100 across five weighted categories |
| Letter Grade | A+, A, B, C, or Needs Work based on the overall score |
| Per-Repo Health | Every repository scored individually out of 100 |
| Language Breakdown | Language percentages across original non-fork repos |
| Score Breakdown | Exactly where points were earned and lost per category |
| Priority Recommendations | HIGH, MEDIUM, and LOW fixes with problem, reason, and action |
| Recruiter Summary | Strengths and weaknesses in plain language |
| Issue Finder | Searches GitHub for open good-first-issue tickets by language |
| Approachability Ranking | Hand-written insertion sort ranking issues by comment count and age |
| Caching with TTL | Caches profile data for 24 hours to avoid repeat API calls |
| Terminal UI | Full formatted report with progress bars and aligned layout |
| Streamlit Dashboard | Four-tab browser interface powered by the same core engine |

---

## How It Works

**Audit mode:**

1. Fetch — pulls profile info and public repos from the GitHub API
2. Score — evaluates each repo individually then rolls up to an overall profile score
3. Breakdown — shows earned vs maximum points per category and per repo
4. Advise — ranks weakest areas and generates prioritised recommendations
5. Summarise — produces a recruiter-style strengths and weaknesses summary
6. Cache — stores results locally for 24 hours for instant repeat lookups

**Find Me Work mode:**

1. Search — queries GitHub for open issues labelled good first issue in your language
2. Score — rates each issue by comment count and age
3. Sort — orders them with a hand-written insertion sort, best first
4. Display — shows the top 10 with direct links

---

## Architecture

```mermaid
flowchart TD
    A[GitHub API] --> B[User]
    A --> C[find_issues]

    B --> D[Scorer]
    B --> G[(cache.json)]

    D --> E[Recommender]
    E --> F[Reporter]

    C --> H[approachability + my_sort]
    C --> G

    H --> F
```

The core engine has no dependency on Streamlit. The same classes power both
the terminal and the browser. No logic is duplicated between main.py and app.py.

---

## File Structure

```
GitGauge/
├── github_api.py     — All GitHub API communication
├── models.py         — Repo and User classes
├── scorer.py         — Profile scoring logic
├── recommender.py    — Priority recommendation engine
├── issues.py         — Issue search, approachability scoring, hand-written sort
├── cache.py          — Local caching with 24-hour TTL
├── reporter.py       — Terminal formatted output
├── main.py           — Terminal entry point
├── app.py            — Streamlit browser interface
├── .env              — GITHUB_TOKEN (never committed)
└── .gitignore        — .env, cache.json, __pycache__
```

---

## Tech Stack

- Python 3.7+
- GitHub REST API
- `urllib` for HTTP requests (built-in, no requests library)
- `datetime`, `json`, `os`, `collections` — all built-in
- Streamlit for the browser interface

---

## Getting Started

### Prerequisites

- Python 3.7+
- A free GitHub Personal Access Token from github.com/settings/tokens
  (no scopes needed for public data)

### Installation

```bash
git clone https://github.com/yourusername/gitgauge.git
cd gitgauge
pip install streamlit python-dotenv
```

### Configuration

Create a `.env` file in the project root:

```
GITHUB_TOKEN=your_token_here
```

This file is listed in `.gitignore` and is never committed.

---

## Usage

### Terminal

```bash
python main.py
```

```
========================================
           GITGAUGE
   GitHub Developer Analytics
========================================

1) Audit a GitHub profile
2) Find good first issues
3) Quit

Choice:
```

Option 1 — enter any GitHub username and get the full audit report including
the overall score and grade, language breakdown with visual bars, per-category
score breakdown, individual repo health scores, recruiter summary, prioritised
recommendations, and top 10 beginner issues to work on next.

Option 2 — enter a language and get the top 10 most approachable open
good-first-issue tickets with direct links.

### Streamlit

```bash
streamlit run app.py
```

Opens in the browser with four tabs:

| Tab | Contents |
|---|---|
| Profile | Score, grade, language chart, bio, follower count |
| Breakdown | Per-category progress bars, repo health score table |
| Recruiter Summary | Strengths, weaknesses, expandable recommendation cards |
| Find Me Work | Ranked beginner issues as clickable cards |

---

## Scoring Methodology

All scores are transparent heuristics based on observable signals. Nothing is
AI-generated or predicted. Every number can be traced back to the raw API data.

**Profile score — five categories totalling 100 points:**

| Category | What is measured |
|---|---|
| Profile Quality | Bio present, has followers, account age |
| Documentation | Percentage of repos with a description |
| Activity | Percentage of repos pushed to in the last 6 months |
| Repository Quality | Average health score across all repos |
| Originality | Percentage of repos that are not forks |

**Per-repo health score — five criteria totalling 100 points:**

| Criterion | What is measured |
|---|---|
| Documentation | Repo has a non-empty description |
| Activity | Pushed to in the last 6 months |
| Popularity | Has at least one star |
| Originality | Not a fork |
| Completeness | Has open issues, which signals active development |

**Issue approachability:**
Scored from comment count (fewer is less crowded) and issue age (newer is more
likely to have active maintainers). This is an estimate, not a prediction.

---

## Honest Limitations

GitGauge scores presentation, not engineering quality. A high score means the
profile looks good in a recruiter's 10-second skim. It says nothing about code
quality, algorithm depth, or actual skill.

Up to 100 repos are fetched. Accounts with more than 100 repos only have the
first 100 analysed.

Public repos only. Private repositories are not accessible without additional
OAuth scopes.

Approachability is an estimate. Issue ranking is based on signals observable
from the API. It does not account for how fast a maintainer responds or the
internal culture of a project.

Language detection is GitHub's own. Percentages reflect how GitHub classifies
each repository, which occasionally misclassifies mixed-content repos.

---

## What's Next

Stage 2 adds cohort mode — score an entire group of GitHub profiles, rank each
person by percentile across categories, visualise the cohort distribution with
Matplotlib, and export individual reports as Markdown files. Built on Pandas
and NumPy.
