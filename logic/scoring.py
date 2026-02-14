def calculate_confidence(match_percent: float, missing_count: int):
    """
    Confidence score based on match % and number of missing ingredients.
    
    Logic:
    - Start with match_percent as base
    - Penalize more heavily for many missing ingredients
    - First 2 missing: small penalty (2 pts each)
    - 3-5 missing: medium penalty (4 pts each)
    - 6+ missing: large penalty (6 pts each)
    - Never goes below 0
    """
    if missing_count == 0:
        return round(match_percent, 2)

    penalty = 0
    for i in range(missing_count):
        if i < 2:
            penalty += 2
        elif i < 5:
            penalty += 4
        else:
            penalty += 6

    confidence = match_percent - penalty
    return max(0, round(confidence, 2))