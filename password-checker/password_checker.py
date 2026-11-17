"""Evaluate password strength using length and character variety."""

import getpass
import string


MINIMUM_LENGTH = 8


def calculate_score(password: str) -> int:
    """Return one point for the length requirement and each character type."""
    checks = (
        len(password) >= MINIMUM_LENGTH,
        any(character.islower() for character in password),
        any(character.isupper() for character in password),
        any(character.isdigit() for character in password),
        any(character in string.punctuation for character in password),
    )
    return sum(checks)


def check_password_strength(password: str) -> str:
    """Return Weak, Moderate, or Strong for a password."""
    score = calculate_score(password)

    if score <= 2:
        return "Weak"
    if score <= 4:
        return "Moderate"
    return "Strong"


def main() -> None:
    password = getpass.getpass("Enter a password to check: ")
    print(f"Password strength: {check_password_strength(password)}")


if __name__ == "__main__":
    main()
