"""Shared label predicates for separating phones from earphones."""


def is_phone_label(label: str) -> bool:
    return label.lower().strip() in {"phone", "cell phone", "smartphone"}
