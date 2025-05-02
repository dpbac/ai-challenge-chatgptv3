def adjust_scores(raw_scores, reuse_preferences):
    for theme, reuse in reuse_preferences.items():
        if reuse == "Yes":
            raw_scores[theme] = raw_scores.get(theme, 0) + 2
        elif reuse == "No":
            raw_scores[theme] = raw_scores.get(theme, 0) - 2
    return raw_scores

def normalize_scores(scores):
    total = sum(max(0, v) for v in scores.values())
    return {k: int((max(0, v) / total) * 100) if total > 0 else 0 for k, v in scores.items()}
