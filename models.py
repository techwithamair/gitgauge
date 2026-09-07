from collections import Counter
from datetime import datetime, timedelta


class Repo:
    HEALTH_WEIGHTS = {
        "documentation": 25,
        "activity": 30,
        "popularity": 15,
        "originality": 20,
        "completeness": 10,
    }

    def __init__(self, repo_dict):
        self.name = repo_dict["name"]
        self.description = repo_dict.get("description")
        self.language = repo_dict.get("language")
        self.stars = repo_dict["stargazers_count"]
        self.forks = repo_dict["forks_count"]
        self.open_issues = repo_dict["open_issues_count"]
        self.is_fork = repo_dict["fork"]
        self.html_url = repo_dict["html_url"]

        self.pushed_at = datetime.strptime(
            repo_dict["pushed_at"].replace("Z", ""), "%Y-%m-%dT%H:%M:%S"
        )
        self.created_at = datetime.strptime(
            repo_dict["created_at"].replace("Z", ""), "%Y-%m-%dT%H:%M:%S"
        )

    def is_recent(self):
        cutoff = datetime.utcnow() - timedelta(days=180)
        return self.pushed_at > cutoff

    def has_description(self):
        return self.description is not None and self.description.strip() != ""

    def is_original(self):
        return not self.is_fork

    def age_in_days(self):
        return (datetime.utcnow() - self.created_at).days

    def health_score(self):
        breakdown = {
            "documentation": self.HEALTH_WEIGHTS["documentation"] if self.has_description() else 0,
            "activity": self.HEALTH_WEIGHTS["activity"] if self.is_recent() else 0,
            "popularity": self.HEALTH_WEIGHTS["popularity"] if self.stars > 0 else 0,
            "originality": self.HEALTH_WEIGHTS["originality"] if self.is_original() else 0,
            "completeness": self.HEALTH_WEIGHTS["completeness"] if self.open_issues > 0 else 0,
        }
        return sum(breakdown.values()), breakdown


class User:
    def __init__(self, username, api):
        self.username = username
        self.api = api
        self.name = None
        self.bio = None
        self.followers = None
        self.following = None
        self.public_repos = None
        self.avatar_url = None
        self.account_age_days = None
        self.repos = []
        self.language_breakdown = {}
        self.top_language = None

    def fetch(self):
        if self.repos:
            return

        profile = self.api.get_user(self.username)
        if not profile:
            return

        self.name = profile.get("name") or "Not set"
        self.bio = profile.get("bio") or "Not set"
        self.followers = profile["followers"]
        self.following = profile["following"]
        self.public_repos = profile["public_repos"]
        self.avatar_url = profile.get("avatar_url")

        created_at = datetime.strptime(
            profile["created_at"].replace("Z", ""), "%Y-%m-%dT%H:%M:%S"
        )
        self.account_age_days = (datetime.utcnow() - created_at).days

        raw_repos = self.api.get_repos(self.username)
        self.repos = [Repo(repo) for repo in raw_repos] if raw_repos else []
        self._compute_language_breakdown()

    def _compute_language_breakdown(self):
        original_repos = [repo for repo in self.repos if repo.is_original()]
        languages = [repo.language for repo in original_repos if repo.language]

        if not languages:
            return

        counts = Counter(languages)
        total = sum(counts.values())
        top_five = counts.most_common(5)
        self.language_breakdown = {
            language: round(count / total * 100, 1)
            for language, count in top_five
        }
        self.top_language = top_five[0][0] if top_five else None
