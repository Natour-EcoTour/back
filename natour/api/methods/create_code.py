"""
Module for creating a new code for email verification.
"""

import string
import secrets


def create_code():
    """
    Generates a random 5-character code consisting of lowercase letters and digits.
    """
    chars = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(5))
