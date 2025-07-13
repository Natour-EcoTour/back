"""
Helper function to retrieve the client's IP address from the request.
"""


def get_client_ip(request):
    """Try to get the client's real IP address."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
