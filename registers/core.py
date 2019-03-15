EMPTY_ROOT_HASH = "sha-256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" # NOQA
SHA256_PREFIX = "sha-256"

__version__ = "0.1.0"


def format_timestamp(dt):
    """
    Formats a UTC datetime as a RFC3339 timestamp.

    Warning: UTC timezone is assumed.
    """
    return "{}Z".format(dt.isoformat(timespec='seconds'))
