def generate_tradeoff_line(match_percent: float, missing_count: int):

    if missing_count == 0:
        return "Perfect ingredient match. No substitutions required."

    return (
        f"{match_percent}% ingredient compatibility. "
        f"{missing_count} substitution(s) required."
    )
