def calculate_confidence(match_percent: float, missing_count: int):
    penalty = missing_count * 2
    confidence = match_percent - penalty
    return max(0, round(confidence, 2))