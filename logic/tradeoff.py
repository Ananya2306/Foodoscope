def generate_tradeoff_line(match_percent: float, missing_count: int):
    """
    Generates a human-readable explanation of the recipe match quality
    with actionable advice based on how many ingredients are missing.
    """

    if missing_count == 0:
        return "✅ Perfect match — you have everything needed. Start cooking!"

    if match_percent >= 90:
        return (
            f"✅ Excellent match ({match_percent}%). "
            f"Only {missing_count} minor ingredient(s) missing — easy to substitute or skip."
        )

    if match_percent >= 75:
        return (
            f"🟡 Strong match ({match_percent}%). "
            f"{missing_count} ingredient(s) missing. Check the substitutes — "
            f"most can be replaced without affecting the dish significantly."
        )

    if match_percent >= 60:
        return (
            f"🟠 Moderate match ({match_percent}%). "
            f"{missing_count} ingredient(s) missing. The dish is doable but "
            f"some substitutes may alter the flavor profile."
        )

    if match_percent >= 40:
        return (
            f"🔴 Low match ({match_percent}%). "
            f"{missing_count} ingredient(s) missing. Consider picking up key "
            f"ingredients from the store, or try a different recipe."
        )

    return (
        f"⛔ Very low match ({match_percent}%). "
        f"{missing_count} ingredients missing — this recipe needs significant "
        f"shopping. Try searching with your available ingredients instead."
    )