class CacheTimeSettings:
    """Contains time (integer number of seconds OR datetime format)
    of expiration of cache for endpoints"""

    # If you've made a mistake
    # and wrote too big amaunt of
    # time just clean your browser
    # history =)

    USERINFO = 30
    USERINFO_JWT = USERINFO
    USERINFO_DEFAULT_TOKEN = 3600

    WELL_KNOWN_OPENID_CONFIG = 10
