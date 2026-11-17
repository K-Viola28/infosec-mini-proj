import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from password_checker import calculate_score, check_password_strength


def test_short_password_missing_length_requirement_is_moderate():
    assert calculate_score("aB1!") == 4
    assert check_password_strength("aB1!") == "Moderate"


def test_password_with_all_requirements_is_strong():
    password = "Secure123!"

    assert calculate_score(password) == 5
    assert check_password_strength(password) == "Strong"


def test_password_with_some_character_types_is_moderate():
    assert check_password_strength("password") == "Weak"
    assert check_password_strength("password1") == "Moderate"
