class ExcludeMetricsFilter:
    """
    A filter to exclude logs that contain 'GET /metrics'.
    This is useful for avoiding clutter in
    """

    def filter(self, record):
        """
        Filter out log records that contain 'GET /metrics'.
        """
        return 'GET /metrics' not in getattr(record, 'msg', '')
