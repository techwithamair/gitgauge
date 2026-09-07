import html


APP_CSS = """
<style>
:root {
    --gg-bg: #050b15;
    --gg-sidebar: #07111f;
    --gg-card: #0b1625;
    --gg-border: #203047;
    --gg-green: #43d66b;
    --gg-blue: #3b82f6;
    --gg-purple: #8b5cf6;
    --gg-amber: #f5b82e;
    --gg-text: #f4f7fb;
    --gg-secondary: #a6b2c5;
}

.stApp {
    background: radial-gradient(circle at 80% -10%, rgba(37, 99, 235, 0.09), transparent 34%), var(--gg-bg);
    color: var(--gg-text);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071321 0%, #07101c 100%);
    border-right: 1px solid var(--gg-border);
    min-width: 280px;
    max-width: 280px;
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding: 1.4rem 1rem; }
.block-container { max-width: 1480px; padding: 2.1rem 2.2rem 3rem; }
h1, h2, h3, h4, p { color: var(--gg-text); }
h1 { letter-spacing: -0.035em; font-size: 2rem !important; }
h2 { letter-spacing: -0.02em; }

.gg-brand-row { display: flex; align-items: center; gap: 10px; margin-bottom: 2px; }
.gg-logo {
    width: 38px; height: 38px; display: grid; place-items: center;
    border: 2px solid var(--gg-green); border-radius: 50%;
    color: var(--gg-green); font-size: 1.15rem;
    box-shadow: 0 0 22px rgba(67, 214, 107, 0.12);
}
.gg-brand { font-size: 1.75rem; font-weight: 800; margin: 0; letter-spacing: -0.04em; }
.gg-brand span { color: var(--gg-green); }
.gg-subtitle { color: var(--gg-secondary); margin: 0 0 0.3rem; font-size: 0.88rem; }

.gg-page-head {
    display: flex; justify-content: space-between; align-items: flex-start;
    margin-bottom: 1.15rem;
}
.gg-page-title { font-size: 2rem; font-weight: 760; line-height: 1.1; }
.gg-page-subtitle { color: var(--gg-secondary); margin-top: 0.35rem; }
.gg-api { color: #cbd5e1; font-size: 0.83rem; white-space: nowrap; padding-top: 0.45rem; }
.gg-api-dot { color: var(--gg-green); font-size: 1.2rem; vertical-align: -1px; }

.gg-card, [data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(145deg, rgba(14, 27, 45, 0.96), rgba(8, 18, 31, 0.96));
    border: 1px solid var(--gg-border) !important;
    border-radius: 10px !important;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
}
[data-testid="stVerticalBlockBorderWrapper"] { padding: 1rem; }

.gg-profile {
    min-height: 178px; padding: 24px; display: grid;
    grid-template-columns: 98px minmax(230px, 1fr) minmax(390px, 1.25fr);
    gap: 24px; align-items: center; margin-bottom: 16px;
}
.gg-avatar {
    width: 92px; height: 92px; border-radius: 50%; object-fit: cover;
    border: 3px solid rgba(255, 255, 255, 0.1);
}
.gg-profile-name { font-size: 1.55rem; font-weight: 760; margin-bottom: 2px; }
.gg-profile-real-name { color: #d7deea; font-size: 1rem; }
.gg-profile-meta { color: var(--gg-secondary); font-size: 0.84rem; margin-top: 13px; }
.gg-profile-bio { color: #d7deea; font-size: 0.9rem; margin-top: 13px; line-height: 1.55; }
.gg-profile-link { color: var(--gg-green); font-size: 0.86rem; margin-top: 10px; }
.gg-profile-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.gg-mini-stat {
    background: rgba(18, 34, 54, 0.8); border: 1px solid #26364c;
    border-radius: 8px; padding: 13px 14px;
}
.gg-mini-icon { color: var(--gg-blue); font-size: 0.86rem; }
.gg-mini-number { font-size: 1.35rem; font-weight: 760; margin-left: 7px; }
.gg-mini-label { display: block; color: var(--gg-secondary); font-size: 0.75rem; margin-top: 5px; }

.gg-metric-card { min-height: 112px; padding: 18px; position: relative; overflow: hidden; }
.gg-metric-card::after {
    content: ""; position: absolute; inset: auto -25px -35px auto;
    width: 92px; height: 92px; border-radius: 50%;
    background: currentColor; opacity: 0.035;
}
.gg-metric-icon {
    display: inline-grid; place-items: center; width: 31px; height: 31px;
    border-radius: 7px; margin-bottom: 10px; background: rgba(59, 130, 246, 0.12);
}
.gg-metric-value { font-size: 1.65rem; font-weight: 780; line-height: 1; }
.gg-metric-label { color: var(--gg-secondary); font-size: 0.8rem; margin-top: 7px; }
.gg-green { color: var(--gg-green); }
.gg-blue { color: #54a3ff; }
.gg-purple { color: #a78bfa; }
.gg-amber { color: var(--gg-amber); }
.gg-section-title { font-size: 1.05rem; font-weight: 700; margin-bottom: 14px; }
.gg-muted { color: var(--gg-secondary); }

.gg-check, .gg-observation, .gg-rec {
    border: 1px solid #23344b; background: rgba(13, 27, 44, 0.8);
    border-radius: 8px; padding: 13px 15px; margin-bottom: 9px;
}
.gg-check { display: flex; gap: 11px; align-items: flex-start; }
.gg-check-icon { font-weight: 800; color: var(--gg-green); }
.gg-check.warning .gg-check-icon { color: var(--gg-amber); }
.gg-check-title { font-weight: 650; font-size: 0.9rem; }
.gg-check-detail { color: var(--gg-secondary); font-size: 0.78rem; margin-top: 2px; }
.gg-observation { border-left: 3px solid var(--gg-blue); color: #d8e0ec; font-size: 0.87rem; }

.gg-rec { padding: 16px; border-left: 3px solid var(--gg-green); }
.gg-rec-number {
    float: left; width: 28px; height: 28px; display: grid; place-items: center;
    border: 1px solid var(--gg-green); border-radius: 50%; color: var(--gg-green);
    margin-right: 12px; font-weight: 700;
}
.gg-rec-body { margin-left: 41px; }
.gg-rec-title { font-weight: 700; }
.gg-rec-copy { color: var(--gg-secondary); font-size: 0.82rem; margin-top: 5px; line-height: 1.45; }
.gg-impact { color: var(--gg-amber); font-size: 0.72rem; margin-top: 7px; text-transform: uppercase; }

.gg-repo-card { padding: 17px; margin-bottom: 11px; }
.gg-repo-title { font-weight: 720; color: #f8fafc; }
.gg-repo-description { color: var(--gg-secondary); min-height: 38px; font-size: 0.83rem; margin: 7px 0 12px; }
.gg-pill {
    display: inline-block; padding: 3px 8px; margin: 0 5px 5px 0;
    border-radius: 999px; background: rgba(59, 130, 246, 0.12);
    color: #8fc3ff; font-size: 0.7rem;
}
.gg-repo-meta { color: #c4cedd; font-size: 0.76rem; word-spacing: 7px; }
.gg-readme-placeholder {
    min-height: 430px; padding: 32px; display: grid; place-items: center;
    text-align: center; color: var(--gg-secondary);
}

div[data-testid="stRadio"] > label { color: var(--gg-secondary); font-size: 0.76rem; }
div[data-testid="stRadio"] [role="radiogroup"] { gap: 4px; }
div[data-testid="stRadio"] [role="radiogroup"] label {
    padding: 9px 11px; border-radius: 7px; transition: background 0.15s ease;
}
div[data-testid="stRadio"] [role="radiogroup"] label:hover { background: #102037; }
div[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(34, 197, 94, 0.28), rgba(34, 197, 94, 0.13));
    border-left: 3px solid var(--gg-green);
}
.stButton > button, .stDownloadButton > button, .stLinkButton > a {
    border-radius: 7px; border-color: #2b3a50; min-height: 2.55rem;
}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {
    background: linear-gradient(135deg, #21b957, #38d46f);
    border: 0; color: white; font-weight: 650;
}
[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"],
[data-baseweb="select"] > div {
    background: #091321 !important; border-color: #2a3a52 !important;
    border-radius: 7px !important;
}
[data-testid="stDataFrame"] { border: 1px solid var(--gg-border); border-radius: 8px; overflow: hidden; }
hr { border-color: #213047 !important; }

@media (max-width: 900px) {
    .block-container { padding: 1.2rem 1rem 2rem; }
    .gg-profile { grid-template-columns: 78px 1fr; }
    .gg-avatar { width: 72px; height: 72px; }
    .gg-profile-stats { grid-column: 1 / -1; }
    .gg-page-head { display: block; }
}
</style>
"""


def safe_text(value):
    return html.escape(str(value or ""))


def page_header(title, subtitle, connected):
    status = "API Connected" if connected else "Public API"
    return f"""
    <div class="gg-page-head">
        <div>
            <div class="gg-page-title">{safe_text(title)}</div>
            <div class="gg-page-subtitle">{safe_text(subtitle)}</div>
        </div>
        <div class="gg-api"><span class="gg-api-dot">●</span> {status} &nbsp; ◉</div>
    </div>
    """


def metric_card(label, value, accent="green", icon="◆"):
    return f"""
    <div class="gg-card gg-metric-card gg-{safe_text(accent)}">
        <div class="gg-metric-icon">{safe_text(icon)}</div>
        <div class="gg-metric-value">{safe_text(value)}</div>
        <div class="gg-metric-label">{safe_text(label)}</div>
    </div>
    """


def profile_card(portfolio, original_count, total_stars):
    details = []
    if portfolio.location:
        details.append("⌖ " + portfolio.location)
    if portfolio.company:
        details.append("▣ " + portfolio.company)
    details.append("▦ Joined " + portfolio.joined_date_text())

    stats = [
        ("▣", portfolio.public_repo_count, "Public Repos"),
        ("♙", portfolio.followers, "Followers"),
        ("♙", portfolio.following, "Following"),
        ("★", total_stars, "Total Stars"),
        ("◇", original_count, "Original Projects"),
        ("↗", portfolio.public_repo_count - original_count, "Forks"),
    ]
    stat_html = ""
    for icon, number, label in stats:
        stat_html += f"""
        <div class="gg-mini-stat">
            <span class="gg-mini-icon">{icon}</span>
            <span class="gg-mini-number">{safe_text(number)}</span>
            <span class="gg-mini-label">{safe_text(label)}</span>
        </div>
        """

    return f"""
    <div class="gg-card gg-profile">
        <img class="gg-avatar" src="{safe_text(portfolio.avatar_url)}" alt="GitHub avatar">
        <div>
            <div class="gg-profile-name">{safe_text(portfolio.username)}</div>
            <div class="gg-profile-real-name">{safe_text(portfolio.name)}</div>
            <div class="gg-profile-meta">{' &nbsp; '.join(safe_text(item) for item in details)}</div>
            <div class="gg-profile-bio">{safe_text(portfolio.bio or 'No public bio provided.')}</div>
            <div class="gg-profile-link">↗ View GitHub Profile</div>
        </div>
        <div class="gg-profile-stats">{stat_html}</div>
    </div>
    """


def checklist_item(item):
    warning_class = "warning" if item["status"] != "success" else ""
    symbol = "!" if warning_class else "✓"
    return f"""
    <div class="gg-check {warning_class}">
        <div class="gg-check-icon">{symbol}</div>
        <div>
            <div class="gg-check-title">{safe_text(item['title'])}</div>
            <div class="gg-check-detail">{safe_text(item['detail'])}</div>
        </div>
    </div>
    """


def recommendation_card(number, recommendation):
    names = recommendation.get("affected_repositories", [])
    affected = ""
    if names:
        affected = f"<div class='gg-rec-copy'>Repositories: {safe_text(', '.join(names))}</div>"
    return f"""
    <div class="gg-rec">
        <div class="gg-rec-number">{number}</div>
        <div class="gg-rec-body">
            <div class="gg-rec-title">{safe_text(recommendation['title'])}</div>
            <div class="gg-rec-copy"><b>Evidence:</b> {safe_text(recommendation['evidence'])}</div>
            <div class="gg-rec-copy"><b>Next step:</b> {safe_text(recommendation['action'])}</div>
            {affected}
            <div class="gg-impact">Actionable portfolio improvement</div>
        </div>
    </div>
    """


def repository_card(repository, recent_days):
    language = repository.language or "Not detected"
    repo_type = "Fork" if repository.is_fork else "Original"
    activity = "Recent" if repository.is_recent(recent_days) else "Inactive"
    description = repository.description or "No description provided."
    return f"""
    <div class="gg-card gg-repo-card">
        <div class="gg-repo-title">▣ {safe_text(repository.name)}</div>
        <div class="gg-repo-description">{safe_text(description)}</div>
        <span class="gg-pill">{safe_text(language)}</span>
        <span class="gg-pill">{repo_type}</span>
        <span class="gg-pill">{activity}</span>
        <div class="gg-repo-meta">★ {repository.stars} &nbsp; Updated {safe_text(repository.pushed_date_text())}</div>
    </div>
    """
