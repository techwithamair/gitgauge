import os

from dotenv import load_dotenv

load_dotenv()

import plotly.express as px
import streamlit as st

from ai_service import AIService, AIServiceError
from github_api import GitHubAPI, GitHubAPIError, GitHubNotFoundError
from models import Portfolio, Repository
from portfolio_analyzer import PortfolioAnalyzer
from recommendation_engine import RecommendationEngine
from ui_styles import (
    APP_CSS,
    checklist_item,
    metric_card,
    page_header,
    profile_card,
    recommendation_card,
    repository_card,
)


RECENT_DAYS = 180
README_CHECK_LIMIT = 20

st.set_page_config(
    page_title="GitGauge",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(APP_CSS, unsafe_allow_html=True)


def initialize_state():
    defaults = {
        "page_navigation": "Overview",
        "portfolio": None,
        "analysis": None,
        "recommendations": [],
        "ai_summary": None,
        "generated_readme": "",
        "selected_repository": None,
        "last_error": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_portfolio(username):
    api = GitHubAPI()
    profile_data = api.get_user(username)
    repository_data = api.get_repositories(username)

    repositories = []
    for item in repository_data:
        repositories.append(Repository(item))

    checked_count = 0
    for repository in repositories:
        if repository.is_original() and checked_count < README_CHECK_LIMIT:
            repository.readme_status = api.get_readme_status(username, repository.name)
            checked_count += 1

    return Portfolio(profile_data, repositories)


def analyze_username(username):
    clean_username = username.strip()
    if not clean_username:
        st.session_state.last_error = "Enter a GitHub username first."
        return

    try:
        portfolio = fetch_portfolio(clean_username)
        analyzer = PortfolioAnalyzer(portfolio, RECENT_DAYS)
        analysis = analyzer.analyze()
        recommendations = RecommendationEngine(analyzer).generate()

        st.session_state.portfolio = portfolio
        st.session_state.analysis = analysis
        st.session_state.recommendations = recommendations
        st.session_state.ai_summary = None
        st.session_state.generated_readme = ""
        st.session_state.selected_repository = None
        st.session_state.last_error = None
    except GitHubNotFoundError:
        st.session_state.last_error = f"GitHub user '{clean_username}' was not found."
    except GitHubAPIError as error:
        st.session_state.last_error = str(error)


def navigation_label(page_name):
    labels = {
        "Overview": "⌂  Overview",
        "Repositories": "▣  Repositories",
        "Recommendations": "☆  Recommendations",
        "README Builder": "▤  README Builder",
    }
    return labels[page_name]


def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="gg-brand-row">
                <div class="gg-logo">⌁</div>
                <p class="gg-brand">Git<span>Gauge</span></p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<p class="gg-subtitle">GitHub Portfolio Inspector</p>', unsafe_allow_html=True)
        st.divider()

        with st.form("username_form"):
            username = st.text_input(
                "GitHub username",
                placeholder="e.g. techwithamair",
            )
            submitted = st.form_submit_button(
                "Analyze Portfolio",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            with st.spinner("Analyzing public GitHub data..."):
                analyze_username(username)

        st.divider()
        page = st.radio(
            "Navigation",
            ["Overview", "Repositories", "Recommendations", "README Builder"],
            key="page_navigation",
            format_func=navigation_label,
            label_visibility="collapsed",
        )

        st.divider()
        if os.environ.get("GITHUB_TOKEN"):
            st.success("GitHub API connected")
        else:
            st.warning("GitHub token not configured")

        st.caption("GitGauge evaluates portfolio presentation signals, not developer ability.")
        return page


def change_page(page_name):
    st.session_state.page_navigation = page_name


def render_empty_state():
    st.markdown(
        page_header(
            "GitHub Portfolio Inspector",
            "Objective portfolio signals for students preparing for technical recruiting.",
            bool(os.environ.get("GITHUB_TOKEN")),
        ),
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        st.subheader("Analyze a public GitHub profile")
        st.write(
            "Enter a GitHub username in the sidebar to see repository activity, "
            "documentation gaps, languages, project health, and practical next steps."
        )
        st.info("GitGauge reports public facts. It does not score or rank developer ability.")


def render_metric_row(counts):
    columns = st.columns(4)
    cards = [
        ("Public Repositories", counts["total"], "blue", "▣"),
        ("Original Projects", counts["original"], "green", "◇"),
        ("Forked Repositories", counts["forks"], "purple", "⑂"),
        ("Recently Updated", counts["recent"], "amber", "↗"),
    ]

    for index, card in enumerate(cards):
        label, value, accent, icon = card
        columns[index].markdown(
            metric_card(label, value, accent, icon),
            unsafe_allow_html=True,
        )


def render_checklist(checklist):
    st.markdown('<div class="gg-section-title">Repository Health Checklist</div>', unsafe_allow_html=True)
    for item in checklist:
        st.markdown(checklist_item(item), unsafe_allow_html=True)


def render_language_chart(language_counts):
    st.markdown('<div class="gg-section-title">Languages Used</div>', unsafe_allow_html=True)
    if not language_counts:
        st.info("No primary languages were detected in original repositories.")
        return

    chart_data = {
        "Language": list(language_counts.keys()),
        "Repositories": list(language_counts.values()),
    }
    figure = px.pie(
        chart_data,
        names="Language",
        values="Repositories",
        hole=0.58,
        color_discrete_sequence=["#3B82F6", "#F59E0B", "#A855F7", "#22C55E"],
    )
    figure.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#F8FAFC",
        legend_title_text="",
    )
    st.plotly_chart(figure, use_container_width=True)


def repository_rows(repositories):
    rows = []
    for repository in repositories:
        rows.append(
            {
                "Repository": repository.name,
                "Description": repository.description or "No description",
                "Language": repository.language or "Not detected",
                "Stars": repository.stars,
                "Updated": repository.pushed_date_text(),
                "Type": "Original" if repository.is_original() else "Fork",
                "Activity": "Recent" if repository.is_recent(RECENT_DAYS) else "Inactive",
            }
        )
    return rows


def render_overview(portfolio, analysis, recommendations):
    st.markdown(
        page_header(
            "Portfolio Overview",
            "A clear view of public GitHub activity and portfolio presentation.",
            bool(os.environ.get("GITHUB_TOKEN")),
        ),
        unsafe_allow_html=True,
    )

    total_stars = sum(repository.stars for repository in portfolio.repositories)
    st.markdown(
        profile_card(portfolio, analysis["counts"]["original"], total_stars),
        unsafe_allow_html=True,
    )

    render_metric_row(analysis["counts"])
    st.write("")

    checklist_column, language_column = st.columns(2)
    with checklist_column:
        with st.container(border=True):
            render_checklist(analysis["checklist"])
    with language_column:
        with st.container(border=True):
            render_language_chart(analysis["language_counts"])

    observation_column, project_column = st.columns(2)
    with observation_column:
        with st.container(border=True):
            st.markdown('<div class="gg-section-title">Objective Observations</div>', unsafe_allow_html=True)
            for observation in analysis["observations"]:
                st.markdown(
                    f'<div class="gg-observation">{observation}</div>',
                    unsafe_allow_html=True,
                )

    with project_column:
        with st.container(border=True):
            st.markdown('<div class="gg-section-title">Most-Starred Projects</div>', unsafe_allow_html=True)
            top_repositories = analysis["top_repositories"][:3]
            if top_repositories:
                for repository in top_repositories:
                    st.markdown(repository_card(repository, RECENT_DAYS), unsafe_allow_html=True)
            else:
                st.info("No original repositories are available to display.")

    with st.container(border=True):
        st.markdown('<div class="gg-section-title">Recommended Next Actions</div>', unsafe_allow_html=True)
        if recommendations:
            for number, recommendation in enumerate(recommendations[:2], 1):
                st.markdown(recommendation_card(number, recommendation), unsafe_allow_html=True)
        else:
            st.success("No improvements were triggered by the current rules.")

    action_one, action_two = st.columns(2)
    action_one.button(
        "View Recommendations",
        on_click=change_page,
        args=("Recommendations",),
        use_container_width=True,
    )
    action_two.button(
        "Open README Builder",
        on_click=change_page,
        args=("README Builder",),
        type="primary",
        use_container_width=True,
    )


def filter_repositories(repositories, search_text, repo_type, language, sort_option):
    filtered = []
    search_value = search_text.strip().lower()

    for repository in repositories:
        description = repository.description or ""
        matches_search = (
            search_value in repository.name.lower()
            or search_value in description.lower()
        )
        matches_type = (
            repo_type == "All"
            or (repo_type == "Original" and repository.is_original())
            or (repo_type == "Forks" and repository.is_fork)
        )
        repository_language = repository.language or "Not detected"
        matches_language = language == "All" or repository_language == language

        if matches_search and matches_type and matches_language:
            filtered.append(repository)

    def star_key(repository):
        return repository.stars

    def updated_key(repository):
        if repository.pushed_at is None:
            return 0
        return repository.pushed_at.timestamp()

    def name_key(repository):
        return repository.name.lower()

    if sort_option == "Most starred":
        filtered.sort(key=star_key, reverse=True)
    elif sort_option == "Recently updated":
        filtered.sort(key=updated_key, reverse=True)
    elif sort_option == "Oldest update":
        filtered.sort(key=updated_key)
    else:
        filtered.sort(key=name_key)

    return filtered


def render_repository_details(repository):
    st.subheader(repository.name)
    st.write(f"**Description:** {repository.description or 'No description'}")
    st.write(f"**Type:** {'Original' if repository.is_original() else 'Fork'}")
    st.write(f"**Language:** {repository.language or 'Not detected'}")
    st.write(f"**Stars:** {repository.stars}")
    st.write(f"**Updated:** {repository.pushed_date_text()}")
    topics = ", ".join(repository.topics) if repository.topics else "No topics"
    st.write(f"**Topics:** {topics}")

    st.divider()
    st.write("**Portfolio checks**")
    if repository.has_description():
        st.success("Description added")
    else:
        st.warning("Description missing")
    if repository.is_recent(RECENT_DAYS):
        st.success("Recently active")
    else:
        st.warning("Not updated recently")
    if repository.is_original():
        st.success("Original project")
    else:
        st.info("Forked repository")
    if repository.has_topics():
        st.success("Topics added")
    else:
        st.warning("Repository topics missing")
    if repository.readme_status == "present":
        st.success("README found")
    elif repository.readme_status == "missing":
        st.warning("README missing")
    else:
        st.info("README was not checked")

    if repository.url:
        st.link_button("Open on GitHub", repository.url, use_container_width=True)
    if repository.is_original():
        st.button(
            "Build README",
            on_click=change_page,
            args=("README Builder",),
            type="primary",
            use_container_width=True,
        )


def render_repositories(portfolio, analysis):
    st.markdown(
        page_header(
            "Repository Analysis",
            "Explore project activity, documentation, languages, and repository health.",
            bool(os.environ.get("GITHUB_TOKEN")),
        ),
        unsafe_allow_html=True,
    )
    render_metric_row(analysis["counts"])
    st.write("")

    languages = ["All"]
    for repository in portfolio.repositories:
        language = repository.language or "Not detected"
        if language not in languages:
            languages.append(language)

    search_column, type_column, language_column, sort_column = st.columns([2, 1, 1, 1])
    search_text = search_column.text_input("Search repositories")
    repo_type = type_column.selectbox("Repository type", ["All", "Original", "Forks"])
    language = language_column.selectbox("Language", languages)
    sort_option = sort_column.selectbox(
        "Sort by",
        ["Most starred", "Recently updated", "Oldest update", "Name"],
    )

    filtered = filter_repositories(
        portfolio.repositories,
        search_text,
        repo_type,
        language,
        sort_option,
    )

    table_column, details_column = st.columns([2, 1])
    with table_column:
        with st.container(border=True):
            st.markdown(
                f'<div class="gg-section-title">Repository Performance '
                f'<span class="gg-muted">({len(filtered)} found)</span></div>',
                unsafe_allow_html=True,
            )
            if filtered:
                st.dataframe(
                    repository_rows(filtered[:20]),
                    use_container_width=True,
                    hide_index=True,
                    height=420,
                )
            else:
                st.info("No repositories match these filters.")

    with details_column:
        with st.container(border=True):
            if filtered:
                names = [repository.name for repository in filtered]
                selected_name = st.selectbox("Inspect repository", names)
                selected_repository = None
                for repository in filtered:
                    if repository.name == selected_name:
                        selected_repository = repository
                        break
                st.session_state.selected_repository = selected_repository
                render_repository_details(selected_repository)
            else:
                st.info("Select a repository after changing the filters.")


def positive_facts(portfolio, analysis):
    facts = []
    counts = analysis["counts"]
    if portfolio.bio:
        facts.append("GitHub bio is complete.")
    if counts["original"] > 0:
        facts.append(f"{counts['original']} repositories are original.")
    if counts["recent"] > 0:
        facts.append(f"{counts['recent']} original repositories were recently updated.")
    if analysis["language_counts"]:
        top_language = next(iter(analysis["language_counts"]))
        facts.append(f"{top_language} is clearly represented.")
    return facts


def render_recommendations(portfolio, analysis, recommendations):
    st.markdown(
        page_header(
            "Recommendations",
            "Fact-based, actionable improvements for your public GitHub portfolio.",
            bool(os.environ.get("GITHUB_TOKEN")),
        ),
        unsafe_allow_html=True,
    )

    metric_columns = st.columns(3)
    metric_columns[0].markdown(metric_card("Actions Suggested", len(recommendations), "amber", "☆"), unsafe_allow_html=True)
    metric_columns[1].markdown(metric_card("Need Descriptions", len(analysis["missing_descriptions"]), "blue", "▤"), unsafe_allow_html=True)
    metric_columns[2].markdown(metric_card("Recently Active", analysis["counts"]["recent"], "green", "↗"), unsafe_allow_html=True)
    st.write("")

    action_column, summary_column = st.columns([2, 1])
    with action_column:
        with st.container(border=True):
            st.markdown('<div class="gg-section-title">Top Priorities</div>', unsafe_allow_html=True)
            if not recommendations:
                st.success("No improvements were triggered by the current rules.")
            for number, recommendation in enumerate(recommendations, 1):
                st.markdown(
                    recommendation_card(number, recommendation),
                    unsafe_allow_html=True,
                )

    with summary_column:
        with st.container(border=True):
            st.markdown('<div class="gg-section-title">What Is Already Strong</div>', unsafe_allow_html=True)
            facts = positive_facts(portfolio, analysis)
            if facts:
                for fact in facts:
                    st.success(fact)
            else:
                st.info("No positive presentation signal was detected by the current rules.")

        with st.container(border=True):
            st.markdown('<div class="gg-section-title">AI Portfolio Summary</div>', unsafe_allow_html=True)
            if st.button("Generate factual summary", use_container_width=True):
                try:
                    service = AIService()
                    st.session_state.ai_summary = service.generate_portfolio_summary(
                        portfolio,
                        analysis,
                        recommendations,
                    )
                except AIServiceError as error:
                    st.error(str(error))

            if st.session_state.ai_summary:
                st.info(st.session_state.ai_summary)
                st.caption("Generated only from the facts shown by GitGauge.")


def render_readme_builder(portfolio):
    st.markdown(
        page_header(
            "README Builder",
            "Create a polished, editable README starter without inventing project details.",
            bool(os.environ.get("GITHUB_TOKEN")),
        ),
        unsafe_allow_html=True,
    )

    originals = portfolio.original_repositories()
    if not originals:
        st.info("No original repositories are available for README generation.")
        return

    names = [repository.name for repository in originals]
    default_index = 0
    selected = st.session_state.selected_repository
    if selected is not None and selected.name in names:
        default_index = names.index(selected.name)

    form_column, preview_column = st.columns(2)
    with form_column:
        with st.container(border=True):
            st.markdown('<div class="gg-section-title">Project Details</div>', unsafe_allow_html=True)
            with st.form("readme_form"):
                repository_name = st.selectbox("Repository", names, index=default_index)
                repository = None
                for item in originals:
                    if item.name == repository_name:
                        repository = item
                        break

                st.caption(
                    f"Detected: {repository.language or 'Not detected'} • "
                    f"{repository.visibility.title()} • Original"
                )
                problem = st.text_area("What problem does this project solve?")
                features = st.text_area("Main features", help="Enter one feature per line.")
                technologies = st.text_input("Technologies used")
                installation = st.text_input("Installation command")
                run_command = st.text_input("Run command")
                additional = st.text_area("Anything else to include? (optional)")
                submitted = st.form_submit_button(
                    "Generate README",
                    type="primary",
                    use_container_width=True,
                )

            st.caption("The AI uses only repository facts and the details you provide.")

            if submitted:
                if not problem.strip() or not features.strip():
                    st.warning("Enter the project's problem and at least one feature.")
                else:
                    details = {
                        "problem": problem.strip(),
                        "features": features.strip(),
                        "technologies": technologies.strip(),
                        "installation": installation.strip(),
                        "run_command": run_command.strip(),
                        "additional": additional.strip(),
                    }
                    try:
                        service = AIService()
                        with st.spinner("Generating README starter..."):
                            st.session_state.generated_readme = service.generate_readme(
                                repository,
                                details,
                            )
                    except AIServiceError as error:
                        st.error(str(error))

    with preview_column:
        with st.container(border=True):
            st.markdown('<div class="gg-section-title">Live README Preview</div>', unsafe_allow_html=True)
            if st.session_state.generated_readme:
                preview_tab, markdown_tab = st.tabs(["Preview", "Markdown"])
                with preview_tab:
                    st.markdown(st.session_state.generated_readme)
                with markdown_tab:
                    st.code(st.session_state.generated_readme, language="markdown")

                st.download_button(
                    "Download README.md",
                    data=st.session_state.generated_readme,
                    file_name="README.md",
                    mime="text/markdown",
                    type="primary",
                    use_container_width=True,
                )
                st.warning("Review and correct every project detail before publishing.")
            else:
                st.markdown(
                    """
                    <div class="gg-card gg-readme-placeholder">
                        <div>
                            <div style="font-size:2.5rem">▤</div>
                            <h3>Your README preview will appear here</h3>
                            <p class="gg-muted">Choose a repository and describe your real project details.</p>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def main():
    initialize_state()
    page = render_sidebar()

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    portfolio = st.session_state.portfolio
    analysis = st.session_state.analysis
    recommendations = st.session_state.recommendations

    if portfolio is None or analysis is None:
        render_empty_state()
        return

    if page == "Overview":
        render_overview(portfolio, analysis, recommendations)
    elif page == "Repositories":
        render_repositories(portfolio, analysis)
    elif page == "Recommendations":
        render_recommendations(portfolio, analysis, recommendations)
    else:
        render_readme_builder(portfolio)


if __name__ == "__main__":
    main()
