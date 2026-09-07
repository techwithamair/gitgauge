class Recommender:
    ADVICE = {
        "profile_quality": {
            "title": "Complete your GitHub profile",
            "why": "Recruiters check your bio, profile picture, and account details in the first few seconds",
            "action": "Add a bio describing what you build, ensure you have a profile picture, and fill in your location",
        },
        "documentation": {
            "title": "Add descriptions to your repositories",
            "why": "Recruiters may skip repos with no description because the purpose is unclear",
            "action": "Add a one-line description to each repo explaining what it does and what technology it uses",
        },
        "activity": {
            "title": "Push recent commits to your repositories",
            "why": "Recent meaningful work shows that you are actively building and improving projects",
            "action": "Make at least one meaningful commit to your main projects this week",
        },
        "repository_quality": {
            "title": "Improve your top repository health scores",
            "why": "Individual repo quality affects the overall impression more than repo count",
            "action": "Focus on your top 3 repos: add descriptions, keep them active, and add a README",
        },
        "originality": {
            "title": "Add more original projects",
            "why": "Original projects show what you can design and build yourself",
            "action": "Build and push at least one original project that solves a real problem",
        },
    }

    PRIORITY_THRESHOLDS = {"HIGH": 10, "MEDIUM": 5, "LOW": 1}

    def recommend(self, user, breakdown):
        recommendations = []
        losses = {
            criterion: maximum - earned
            for criterion, (earned, maximum) in breakdown.items()
        }
        sorted_criteria = sorted(
            losses.items(), key=lambda item: item[1], reverse=True
        )

        for criterion, lost_points in sorted_criteria:
            if lost_points == 0:
                continue

            if lost_points >= self.PRIORITY_THRESHOLDS["HIGH"]:
                priority = "HIGH"
            elif lost_points >= self.PRIORITY_THRESHOLDS["MEDIUM"]:
                priority = "MEDIUM"
            else:
                priority = "LOW"

            advice = self.ADVICE[criterion]
            action = self._personalise(criterion, user, advice["action"])
            recommendations.append(
                {
                    "priority": priority,
                    "criterion": criterion,
                    "title": advice["title"],
                    "why": advice["why"],
                    "action": action,
                    "score_impact": f"+{lost_points} points",
                }
            )

        return recommendations

    def _personalise(self, criterion, user, base_action):
        if criterion == "documentation":
            missing = [repo for repo in user.repos if not repo.has_description()]
            if missing:
                return f"{len(missing)} of your repos have no description. {base_action}"
        if criterion == "activity":
            stale = [repo for repo in user.repos if not repo.is_recent()]
            if stale:
                return f"{len(stale)} repos have not been updated in 6 months. {base_action}"
        if criterion == "originality":
            forks = [repo for repo in user.repos if not repo.is_original()]
            if forks:
                return f"{len(forks)} of your repos are forks. {base_action}"
        return base_action
