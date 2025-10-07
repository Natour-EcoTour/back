import re


def mask_email(email, keep_local=2, mask_len=4, mask_char='*'):
    """
    Function to mask an email address for privacy (LGPD).
    """
    m = re.match(r'^([^@]+)@[^@]+(\..+)$', email)
    if not m:
        return email
    local, domain_rest = m.groups()
    return f"{local[:keep_local]}{mask_char*mask_len}@{mask_char*mask_len}{domain_rest}"
