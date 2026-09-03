class Scorer:
    WEIGHTS = {
        "profile_quality": 15,
        "documentation": 25,
        "activity": 25,
        "repository_quality": 25,
        "originality": 10,
    }

    GRADES = [
        (90, "A+"),
        (80, "A"),
        (70, "B"),
        (60, "C"),
        (0, "Needs Work"),
    ]

    def score(self, user):
        if not user.repos:
            breakdown = {
                criterion: (0, maximum)
                for criterion, maximum in self.WEIGHTS.items()
            }
            return 0, breakdown, "Needs Work"

        total_repos = len(user.repos)

        profile_score = 0
        if user.bio and user.bio != "Not set":
            profile_score += 5
        if user.followers and user.followers > 0:
            profile_score += 5
        if user.account_age_days and user.account_age_days > 365:
            profile_score += 5

        repos_with_descriptions = sum(
            1 for repo in user.repos if repo.has_description()
        )
        documentation_score = (
            repos_with_descriptions / total_repos
        ) * self.WEIGHTS["documentation"]

        recent_repos = sum(1 for repo in user.repos if repo.is_recent())
        activity_score = (
            recent_repos / total_repos
        ) * self.WEIGHTS["activity"]

        health_scores = [repo.health_score()[0] for repo in user.repos]
        average_health = sum(health_scores) / len(health_scores)
        repository_score = (
            average_health / 100
        ) * self.WEIGHTS["repository_quality"]

        original_repos = sum(1 for repo in user.repos if repo.is_original())
        originality_score = (
            original_repos / total_repos
        ) * self.WEIGHTS["originality"]

        total = round(
            profile_score
            + documentation_score
            + activity_score
            + repository_score
            + originality_score
        )

        breakdown = {
            "profile_quality": (round(profile_score), self.WEIGHTS["profile_quality"]),
            "documentation": (round(documentation_score), self.WEIGHTS["documentation"]),
            "activity": (round(activity_score), self.WEIGHTS["activity"]),
            "repository_quality": (round(repository_score), self.WEIGHTS["repository_quality"]),
            "originality": (round(originality_score), self.WEIGHTS["originality"]),
        }

        grade = next(grade for threshold, grade in self.GRADES if total >= threshold)
        return total, breakdown, grade
