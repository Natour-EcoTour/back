"""
Module for creating a new password for a user.
"""

import string
import secrets


def create_new_password(length=8):
    """
    Create a new random password.
    """
    if length < 8:
        raise ValueError("Password length must be at least 8 characters.")

    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits

    all_characters = lowercase + uppercase + digits
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits)
    ]

    password += [secrets.choice(all_characters) for _ in range(length - 3)]
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)
