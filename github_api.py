import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


class GitHubAPI:
    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.token = os.environ.get("GITHUB_TOKEN")
        if not self.token:
            print("ERROR: GITHUB_TOKEN environment variable not set.")
            print("Add GITHUB_TOKEN=your_token to your .env file.")
            sys.exit(1)

        self.headers = {
            "Authorization": f"token {self.token}",
            "User-Agent": "GitGauge/1.0",
            "Accept": "application/vnd.github.v3+json",
        }

    def get(self, url):
        try:
            request = urllib.request.Request(url, headers=self.headers)
            response = urllib.request.urlopen(request)
            raw = response.read().decode("utf-8")
            return json.loads(raw)
        except urllib.error.HTTPError as error:
            if error.code == 404:
                print(f"Not found: {url}")
            elif error.code == 403:
                print("Rate limited or bad token. Check your GITHUB_TOKEN.")
            else:
                print(f"HTTP error {error.code}: {error.reason}")
            return None
        except urllib.error.URLError as error:
            print(f"Network error: {error.reason}")
            return None

    def get_user(self, username):
        return self.get(f"{self.BASE_URL}/users/{username}")

    def get_repos(self, username):
        url = f"{self.BASE_URL}/users/{username}/repos?per_page=100"
        return self.get(url)

    def search_issues(self, language):
        query = f'label:"good first issue" language:{language} state:open'
        encoded_query = urllib.parse.quote(query)
        url = (
            f"{self.BASE_URL}/search/issues?q={encoded_query}"
            "&per_page=30&sort=created&order=desc"
        )
        result = self.get(url)
        return result["items"] if result else []
