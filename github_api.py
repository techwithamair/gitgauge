import json
import os
import urllib.error
import urllib.parse
import urllib.request


class GitHubAPIError(Exception):
    """Base error for GitHub API problems."""


class GitHubNotFoundError(GitHubAPIError):
    """Raised when a GitHub resource does not exist."""


class GitHubRateLimitError(GitHubAPIError):
    """Raised when GitHub rejects a request because of limits."""


class GitHubAPI:
    """Handles all communication with the public GitHub REST API."""

    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.token = os.environ.get("GITHUB_TOKEN")
        self.headers = self._build_headers()

    def _build_headers(self):
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "GitGauge/2.0",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get(self, url):
        request = urllib.request.Request(url, headers=self.headers)

        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                response_text = response.read().decode("utf-8")
                return json.loads(response_text)
        except urllib.error.HTTPError as error:
            if error.code == 404:
                raise GitHubNotFoundError("The requested GitHub resource was not found.")
            if error.code == 403:
                raise GitHubRateLimitError(
                    "GitHub rejected the request. Check the token or rate limit."
                )
            raise GitHubAPIError(f"GitHub returned HTTP status {error.code}.")
        except urllib.error.URLError as error:
            raise GitHubAPIError(f"Could not connect to GitHub: {error.reason}")
        except json.JSONDecodeError:
            raise GitHubAPIError("GitHub returned data that could not be read.")

    def get_user(self, username):
        safe_username = urllib.parse.quote(username.strip())
        return self.get(f"{self.BASE_URL}/users/{safe_username}")

    def get_repositories(self, username):
        safe_username = urllib.parse.quote(username.strip())
        url = (
            f"{self.BASE_URL}/users/{safe_username}/repos"
            "?per_page=100&sort=updated&direction=desc"
        )
        return self.get(url)

    def get_readme_status(self, owner, repository_name):
        safe_owner = urllib.parse.quote(owner.strip())
        safe_name = urllib.parse.quote(repository_name.strip())
        url = f"{self.BASE_URL}/repos/{safe_owner}/{safe_name}/readme"

        try:
            self.get(url)
            return "present"
        except GitHubNotFoundError:
            return "missing"
        except GitHubAPIError:
            return "not_checked"
