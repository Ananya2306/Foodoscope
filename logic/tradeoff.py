def generate_tradeoff_line(match_percent: float, missing_count: int):

    if missing_count == 0:
        return "✅ Perfect ingredient match. No substitutions required."

    if match_percent >= 90:
        return f"✅ Excellent match ({match_percent}%). Minor substitutions needed."

    if match_percent >= 70:
        return f"🟡 Good match ({match_percent}%). {missing_count} substitution(s) required."

    if match_percent >= 50:
        return f"🟠 Moderate match ({match_percent}%). {missing_count} ingredient(s) missing."

    return f"🔴 Low match ({match_percent}%). {missing_count} ingredient(s) missing — consider a different recipe."