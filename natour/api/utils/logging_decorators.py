"""
Simple logging decorators for API views.
"""
import logging
import functools
from .get_ip import get_client_ip

logger = logging.getLogger("django")


def api_logger(operation_name):
    """
    Simple decorator for automatic API logging.

    Args:
        operation_name (str): Name of the operation (e.g., "photo_creation", "user_login")
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapper(request, *args, **kwargs):
            ip = get_client_ip(request)
            user = getattr(request, 'user', None)
            user_info = f"{user.username} (ID: {user.id})" if user and user.is_authenticated else "anonymous user"

            logger.info(
                "%s request started by %s (IP: %s)",
                operation_name, user_info, ip
            )

            try:
                response = view_func(request, *args, **kwargs)

                logger.info(
                    "%s completed successfully by %s (IP: %s) - Status: %s",
                    operation_name, user_info, ip, response.status_code
                )

                return response

            except Exception as e:
                logger.error(
                    "%s failed for %s (IP: %s): %s",
                    operation_name, user_info, ip, str(e)
                )
                raise

        return wrapper
    return decorator


def log_validation_error(operation_name, request, errors):
    """Helper function for logging validation errors consistently."""
    ip = get_client_ip(request)
    user = getattr(request, 'user', None)
    user_info = f"{user.username} (ID: {user.id})" if user and user.is_authenticated else "anonymous user"

    logger.warning(
        "%s validation failed for %s (IP: %s): %s",
        operation_name, user_info, ip, errors
    )
