import os

from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from groq import Groq

from github_api import GitHubAPI
from issues import approachability, find_issues, rank_issues
from models import User
from recommender import Recommender
from scorer import Scorer


st.set_page_config(page_title="GitGauge", page_icon="📊", layout="wide")

api = GitHubAPI()
scorer = Scorer()
recommender = Recommender()
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def generate_ai_summary(score, grade, breakdown, recommendations):
    top_recommendations = [item["title"] for item in recommendations[:3]]
    prompt = f"""
A developer's GitHub profile scored {score}/100 with grade {grade}.
Score breakdown: {breakdown}
Top recommendations: {top_recommendations}

Write a 3-4 sentence plain English summary of this profile for the developer.
Be specific and honest. Mention the grade, strongest area, and biggest weakness.
Avoid fluff and focus on useful facts.
"""
    try:
        response = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
        )
        return response.choices[0].message.content
    except Exception:
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_and_analyze(username):
    user = User(username, api)
    user.fetch()
    if not user.repos:
        return None
    score, breakdown, grade = scorer.score(user)
    recommendations = recommender.recommend(user, breakdown)
    return user, score, breakdown, grade, recommendations


with st.sidebar:
    st.title("GitGauge")
    st.caption("GitHub profile auditor")
    st.divider()
    username = st.text_input("GitHub username", placeholder="e.g. torvalds")
    analyze_button = st.button("Analyze", type="primary", use_container_width=True)
    st.divider()
    language = st.selectbox(
        "Find issues in",
        ["python", "javascript", "java", "go", "rust", "c", "typescript", "cpp"],
    )
    find_button = st.button("Find issues", use_container_width=True)


if analyze_button and username:
    result = fetch_and_analyze(username.strip().lower())

    if not result:
        st.error(f"Could not find GitHub user: {username}")
    else:
        user, score, breakdown, grade, recommendations = result
        profile_tab, score_tab, recruiter_tab, work_tab = st.tabs(
            ["Profile", "Score Breakdown", "Recruiter Summary", "Find Me Work"]
        )

        with profile_tab:
            column_one, column_two, column_three = st.columns(3)
            column_one.metric("GitGauge Score", f"{score} / 100")
            column_two.metric("Grade", grade)
            column_three.metric("Repositories", user.public_repos)
            st.progress(score / 100)

            column_four, column_five, column_six = st.columns(3)
            column_four.metric("Followers", f"{user.followers:,}")
            column_five.metric("Following", user.following)
            column_six.metric("Account age", f"{user.account_age_days // 365} years")
            st.divider()

            if user.language_breakdown:
                st.subheader("Language breakdown")
                st.bar_chart(user.language_breakdown)

            st.info(f"Bio: {user.bio}")
            st.divider()
            st.subheader("AI summary")
            with st.spinner("Generating summary..."):
                summary = generate_ai_summary(
                    score, grade, breakdown, recommendations
                )
            if summary:
                st.write(summary)
            else:
                st.caption("Summary unavailable.")

        with score_tab:
            st.subheader("Category scores")
            for criterion, (earned, maximum) in breakdown.items():
                label = criterion.replace("_", " ").title()
                label_column, score_column = st.columns([4, 1])
                label_column.write(f"**{label}**")
                score_column.write(f"{earned} / {maximum}")
                st.progress(earned / maximum if maximum else 0)

            st.divider()
            st.subheader("Top repo health scores")
            repository_data = sorted(
                [
                    {
                        "Repository": repo.name,
                        "Score": repo.health_score()[0],
                        "Language": repo.language or "—",
                        "Stars": repo.stars,
                        "Recent": "Yes" if repo.is_recent() else "No",
                        "Description": "Yes" if repo.has_description() else "No",
                    }
                    for repo in user.repos
                ],
                key=lambda item: item["Score"],
                reverse=True,
            )
            st.dataframe(repository_data[:10], use_container_width=True)

        with recruiter_tab:
            strengths_column, weaknesses_column = st.columns(2)
            with strengths_column:
                st.subheader("Strengths")
                strengths = [
                    criterion
                    for criterion, (earned, maximum) in breakdown.items()
                    if maximum > 0 and earned >= maximum * 0.8
                ]
                if strengths:
                    for strength in strengths:
                        st.success(strength.replace("_", " ").title())
                else:
                    st.caption("No strong areas yet.")

            with weaknesses_column:
                st.subheader("Areas to improve")
                weaknesses = [
                    criterion
                    for criterion, (earned, maximum) in breakdown.items()
                    if maximum > 0 and earned < maximum * 0.5
                ]
                if weaknesses:
                    for weakness in weaknesses:
                        st.warning(weakness.replace("_", " ").title())
                else:
                    st.caption("Looking good overall.")

            st.divider()
            st.subheader("Recommendations")
            if not recommendations:
                st.success("Your profile looks strong. Keep it up.")
            else:
                for recommendation in recommendations:
                    icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[
                        recommendation["priority"]
                    ]
                    label = (
                        f"{icon} [{recommendation['priority']}] "
                        f"{recommendation['title']} — {recommendation['score_impact']}"
                    )
                    with st.expander(label):
                        st.write(f"**Why it matters:** {recommendation['why']}")
                        st.write(f"**Action:** {recommendation['action']}")

        with work_tab:
            if user.top_language:
                st.caption(
                    f"Suggested because your top language is {user.top_language}"
                )


if find_button:
    with st.spinner(f"Searching {language} issues..."):
        issues = find_issues(language, api)
        ranked_issues = rank_issues(issues)

    if not ranked_issues:
        st.warning("No issues found. Try a different language.")
    else:
        st.subheader(f"Top beginner issues — {language}")
        for position, issue in enumerate(ranked_issues[:10], 1):
            score_value = approachability(issue)
            with st.container():
                issue_column, score_column = st.columns([5, 1])
                issue_column.markdown(
                    f"**{position}. [{issue['title']}]({issue['html_url']})**"
                )
                score_column.metric("Score", score_value)
                st.caption(f"💬 {issue['comments']} comments")
                st.divider()
