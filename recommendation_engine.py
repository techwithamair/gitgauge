class RecommendationEngine:
    """Creates recommendations backed by analyzer evidence."""

    def __init__(self, analyzer):
        self.analyzer = analyzer

    def generate(self):
        recommendations = []
        possible = [
            self.profile_recommendation(),
            self.description_recommendation(),
            self.topics_recommendation(),
            self.readme_recommendation(),
            self.activity_recommendation(),
        ]

        for recommendation in possible:
            if recommendation is not None:
                recommendations.append(recommendation)
        return recommendations

    def profile_recommendation(self):
        if self.analyzer.portfolio.bio:
            return None
        return self._make_recommendation(
            "Add a short GitHub bio",
            "The public GitHub profile has no bio.",
            "A bio gives visitors immediate context about your interests.",
            "Add one sentence describing what you study, build, or want to learn.",
        )

    def description_recommendation(self):
        repositories = self.analyzer.get_missing_descriptions()
        if not repositories:
            return None
        names = self._repository_names(repositories)
        return self._make_recommendation(
            "Add missing repository descriptions",
            f"{len(names)} original repositories have no description.",
            "Descriptions help visitors understand a project before opening it.",
            "Add one sentence explaining the problem, solution, and main technology.",
            names,
        )

    def topics_recommendation(self):
        repositories = self.analyzer.get_missing_topics()
        if not repositories:
            return None
        names = self._repository_names(repositories)
        return self._make_recommendation(
            "Add accurate repository topics",
            f"{len(names)} original repositories do not list topics.",
            "Topics make the technologies and purpose easier to discover.",
            "Add two to five accurate topics such as python or streamlit.",
            names,
        )

    def readme_recommendation(self):
        repositories = self.analyzer.get_missing_readmes()
        if not repositories:
            return None
        names = self._repository_names(repositories)
        return self._make_recommendation(
            "Add README documentation",
            f"{len(names)} checked original repositories have no README.",
            "A README explains what the project does and how someone can run it.",
            "Use the README Builder to create a starter, then verify every detail.",
            names,
        )

    def activity_recommendation(self):
        counts = self.analyzer.get_counts()
        if counts["original"] == 0 or counts["recent"] > 0:
            return None
        return self._make_recommendation(
            "Review inactive original projects",
            f"No original repository was pushed within {self.analyzer.recent_days} days.",
            "Recent maintenance helps visitors identify projects you still support.",
            "Update a current project meaningfully or archive old projects.",
        )

    def _make_recommendation(self, title, evidence, why, action, repositories=None):
        return {
            "title": title,
            "evidence": evidence,
            "why": why,
            "action": action,
            "affected_repositories": repositories or [],
        }

    def _repository_names(self, repositories):
        names = []
        for repository in repositories:
            names.append(repository.name)
        return names
