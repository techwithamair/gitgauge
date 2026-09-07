import html


APP_CSS = """
<style>
:root {
    --gg-bg: #06101d;
    --gg-sidebar: #081523;
    --gg-card: #0b1828;
    --gg-border: #203047;
    --gg-green: #22c55e;
    --gg-blue: #3b82f6;
    --gg-purple: #a855f7;
    --gg-amber: #f59e0b;
    --gg-text: #f8fafc;
    --gg-secondary: #a8b3c5;
}

.stApp {
    background: var(--gg-bg);
    color: var(--gg-text);
}

[data-testid="stSidebar"] {
    background: var(--gg-sidebar);
    border-right: 1px solid var(--gg-border);
}

.block-container {
    max-width: 1500px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.gg-brand {
    font-size: 1.8rem;
    font-weight: 750;
    margin-bottom: 0;
}

.gg-brand span {
    color: var(--gg-green);
}

.gg-subtitle {
    color: var(--gg-secondary);
    margin-top: 0;
}

.gg-card {
    background: var(--gg-card);
    border: 1px solid var(--gg-border);
    border-radius: 12px;
    padding: 18px;
    min-height: 112px;
}

.gg-profile {
    background: var(--gg-card);
    border: 1px solid var(--gg-border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 18px;
}

.gg-metric-value {
    font-size: 1.8rem;
    font-weight: 750;
    color: var(--gg-text);
}

.gg-metric-label {
    color: var(--gg-secondary);
    font-size: 0.86rem;
}

.gg-success {
    border-left: 3px solid var(--gg-green);
}

.gg-warning {
    border-left: 3px solid var(--gg-amber);
}

.gg-action {
    border-left: 3px solid var(--gg-blue);
}

.gg-muted {
    color: var(--gg-secondary);
}

.stButton > button,
.stDownloadButton > button,
.stLinkButton > a {
    border-radius: 8px;
}

@media (max-width: 800px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>
"""


def safe_text(value):
    return html.escape(str(value or ""))


def metric_card(label, value, accent="green"):
    accent_class = "gg-success"
    if accent == "warning":
        accent_class = "gg-warning"
    elif accent == "blue":
        accent_class = "gg-action"

    return f"""
    <div class="gg-card {accent_class}">
        <div class="gg-metric-value">{safe_text(value)}</div>
        <div class="gg-metric-label">{safe_text(label)}</div>
    </div>
    """


def profile_card(portfolio):
    details = []
    if portfolio.location:
        details.append(portfolio.location)
    if portfolio.company:
        details.append(portfolio.company)
    details.append(f"Joined {portfolio.joined_date_text()}")
    detail_text = " • ".join(details)

    return f"""
    <div class="gg-profile">
        <h2>{safe_text(portfolio.username)}</h2>
        <h4 class="gg-muted">{safe_text(portfolio.name)}</h4>
        <p>{safe_text(portfolio.bio or 'No bio provided')}</p>
        <p class="gg-muted">{safe_text(detail_text)}</p>
    </div>
    """
