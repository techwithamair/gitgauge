from datetime import datetime, timedelta, timezone


def parse_github_date(date_text):
    """Convert a GitHub date string into a timezone-aware datetime."""
    if not date_text:
        return None
    return datetime.fromisoformat(date_text.replace("Z", "+00:00"))


class Repository:
    """Represents one public GitHub repository."""

    def __init__(self, data):
        self.name = data.get("name", "Unnamed repository")
        self.full_name = data.get("full_name", self.name)
        self.description = data.get("description")
        self.url = data.get("html_url", "")
        self.language = data.get("language")
        self.stars = data.get("stargazers_count", 0)
        self.is_fork = data.get("fork", False)
        self.topics = data.get("topics", [])
        self.visibility = data.get("visibility", "public")
        self.created_at = parse_github_date(data.get("created_at"))
        self.pushed_at = parse_github_date(data.get("pushed_at"))
        self.is_archived = data.get("archived", False)
        self.readme_status = "not_checked"

    def has_description(self):
        return bool(self.description and self.description.strip())

    def is_original(self):
        return not self.is_fork

    def is_recent(self, days=180):
        if self.pushed_at is None:
            return False
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return self.pushed_at >= cutoff

    def has_topics(self):
        return len(self.topics) > 0

    def has_readme(self):
        return self.readme_status == "present"

    def pushed_date_text(self):
        if self.pushed_at is None:
            return "Unavailable"
        return self.pushed_at.strftime("%b %d, %Y")


class Portfolio:
    """Stores one GitHub profile and its public repositories."""

    def __init__(self, profile_data, repositories):
        self.username = profile_data.get("login", "")
        self.name = profile_data.get("name") or self.username
        self.avatar_url = profile_data.get("avatar_url", "")
        self.profile_url = profile_data.get("html_url", "")
        self.bio = profile_data.get("bio")
        self.location = profile_data.get("location")
        self.company = profile_data.get("company")
        self.followers = profile_data.get("followers", 0)
        self.following = profile_data.get("following", 0)
        self.public_repo_count = profile_data.get("public_repos", 0)
        self.created_at = parse_github_date(profile_data.get("created_at"))
        self.repositories = repositories

    def original_repositories(self):
        originals = []
        for repository in self.repositories:
            if repository.is_original():
                originals.append(repository)
        return originals

    def forked_repositories(self):
        forks = []
        for repository in self.repositories:
            if repository.is_fork:
                forks.append(repository)
        return forks

    def recent_repositories(self, days=180):
        recent = []
        for repository in self.original_repositories():
            if repository.is_recent(days):
                recent.append(repository)
        return recent

    def joined_date_text(self):
        if self.created_at is None:
            return "Unavailable"
        return self.created_at.strftime("%b %Y")
