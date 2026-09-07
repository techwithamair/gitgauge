from datetime import datetime


def find_issues(language, api):
    return api.search_issues(language)


def approachability(issue):
    comment_score = max(0, 50 - issue["comments"] * 5)
    created_at = datetime.strptime(
        issue["created_at"].replace("Z", ""), "%Y-%m-%dT%H:%M:%S"
    )
    days_old = (datetime.utcnow() - created_at).days
    age_score = max(0, 50 - days_old * 0.5)
    return round(comment_score + age_score)


def rank_issues(issues):
    return sorted(issues, key=approachability, reverse=True)
