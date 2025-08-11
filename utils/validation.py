import re

def is_strong_password(password: str) -> tuple[bool, str]:
    """
    Checks if a password meets strong complexity requirements.

    A strong password must:
    - Be at least 12 characters long.
    - Contain at least one uppercase letter.
    - Contain at least one lowercase letter.
    - Contain at least one number.
    - Contain at least one special character from the set [!@#$%^&*()_+-=[]{};':"\\|,.<>/?].

    Returns:
        tuple[bool, str]: A tuple containing a boolean indicating if the password is strong,
                          and a message describing the result.
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters long."

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."

    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False, "Password must contain at least one special character."

    return True, "Password is strong."