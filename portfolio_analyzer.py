from collections import Counter


class PortfolioAnalyzer:
    """Calculates objective facts about a GitHub portfolio."""

    def __init__(self, portfolio, recent_days=180):
        self.portfolio = portfolio
        self.recent_days = recent_days

    def get_counts(self):
        return {
            "total": len(self.portfolio.repositories),
            "original": len(self.portfolio.original_repositories()),
            "forks": len(self.portfolio.forked_repositories()),
            "recent": len(self.portfolio.recent_repositories(self.recent_days)),
        }

    def get_language_counts(self):
        language_counter = Counter()
        for repository in self.portfolio.original_repositories():
            language = repository.language or "Not detected"
            language_counter[language] += 1
        return dict(language_counter.most_common())

    def get_missing_descriptions(self):
        missing = []
        for repository in self.portfolio.original_repositories():
            if not repository.has_description():
                missing.append(repository)
        return missing

    def get_missing_topics(self):
        missing = []
        for repository in self.portfolio.original_repositories():
            if not repository.has_topics():
                missing.append(repository)
        return missing

    def get_missing_readmes(self):
        missing = []
        for repository in self.portfolio.original_repositories():
            if repository.readme_status == "missing":
                missing.append(repository)
        return missing

    def get_top_repositories(self, limit=5):
        candidates = []
        for repository in self.portfolio.original_repositories():
            if not repository.is_archived:
                candidates.append(repository)

        def repository_sort_key(repository):
            pushed_timestamp = 0
            if repository.pushed_at is not None:
                pushed_timestamp = repository.pushed_at.timestamp()
            return repository.stars, pushed_timestamp

        candidates.sort(key=repository_sort_key, reverse=True)
        return candidates[:limit]

    def build_checklist(self):
        checklist = []
        descriptions = self.get_missing_descriptions()
        topics = self.get_missing_topics()
        readmes = self.get_missing_readmes()
        counts = self.get_counts()

        if self.portfolio.bio:
            checklist.append(self._check("success", "Bio complete", "Your bio is visible."))
        else:
            checklist.append(self._check("warning", "Bio missing", "Add a short GitHub bio."))

        if counts["original"] > 0:
            detail = f"{counts['original']} original repositories found."
            checklist.append(self._check("success", "Original work found", detail))
        else:
            checklist.append(self._check("warning", "No original work found", "Only forks were found."))

        if descriptions:
            detail = f"{len(descriptions)} original repositories need descriptions."
            checklist.append(self._check("warning", "Descriptions need attention", detail))
        else:
            checklist.append(self._check("success", "Descriptions added", "Original repositories have descriptions."))

        if counts["recent"] > 0:
            detail = f"{counts['recent']} original repositories were updated recently."
            checklist.append(self._check("success", "Recent activity found", detail))
        else:
            checklist.append(self._check("warning", "No recent projects", "No original repository was updated recently."))

        if topics:
            detail = f"{len(topics)} original repositories have no topics."
            checklist.append(self._check("warning", "Topics need attention", detail))
        else:
            checklist.append(self._check("success", "Topics added", "Original repositories have topics."))

        if readmes:
            detail = f"{len(readmes)} checked repositories have no README."
            checklist.append(self._check("warning", "READMEs need attention", detail))

        return checklist

    def build_observations(self):
        observations = []
        counts = self.get_counts()
        descriptions = self.get_missing_descriptions()
        topics = self.get_missing_topics()
        languages = self.get_language_counts()

        if counts["original"] == 0:
            observations.append("No original public repositories were found.")
        else:
            observations.append(
                f"{counts['recent']} of {counts['original']} original repositories "
                f"were updated within the last {self.recent_days} days."
            )

        if descriptions:
            observations.append(
                f"{len(descriptions)} original repositories are missing descriptions."
            )
        else:
            observations.append("All original repositories have descriptions.")

        if languages:
            top_language = next(iter(languages))
            observations.append(
                f"{top_language} is the most common primary repository language."
            )

        if topics:
            observations.append(
                f"{len(topics)} original repositories do not have topics."
            )
        return observations

    def analyze(self):
        return {
            "counts": self.get_counts(),
            "language_counts": self.get_language_counts(),
            "checklist": self.build_checklist(),
            "observations": self.build_observations(),
            "missing_descriptions": self.get_missing_descriptions(),
            "missing_topics": self.get_missing_topics(),
            "missing_readmes": self.get_missing_readmes(),
            "top_repositories": self.get_top_repositories(),
        }

    def _check(self, status, title, detail):
        return {"status": status, "title": title, "detail": detail}
