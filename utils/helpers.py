def normalize(text: str) -> str:
    return text.strip().lower()


def split_ingredients(text: str):
    return [i.strip() for i in text.split(",") if i.strip()]
