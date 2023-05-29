import bcrypt

def hash_password(password: str) -> str:
        bts = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hash_password = bcrypt.hashpw(bts, salt)
        return str(hash_password).strip("b'")


CLIENT_IDS = {
    1: "test_client",
    2: "double_test",
    3: "santa",
    4: "krampus",
    5: "frodo",
    6: "aragorn",
    7: "iron_man",
    8: "spider_man",
    9: "thor",
    10: "samuel",
}

CLIENT_HASH_PASSWORDS = {
    1: hash_password("test_password"),
    2: hash_password("double_password"),
    3: hash_password("christmas_forever"),
    4: hash_password("no_to_christmas"),
    5: hash_password("one_ring_to_rule_them_all"),
    6: hash_password("son_of_aratorn"),
    7: hash_password("best_avenger"),
    8: hash_password("the_beginner"),
    9: hash_password("god_of_thunder"),
    10: hash_password("just_a_guy"),
}

# It's not correct, according to factories
# client_id <-> username relation may be different from test to test
CLIENT_USERNAMES = {
    1: "TestClient",
    2: "Doubl",
    3: "SantaClaus",
    4: "Krampus",
    5: "FrodoBaggins",
    6: "Aragorn",
    7: "TonyStark",
    8: "PeterParker",
    9: "Thor",
    10: "SamuelGamgy",
}

USER_CLAIM_TYPE = [
    "name",
    "given_name",
    "family_name",
    "middle_name",
    "nickname",
    "preferred_username",
    "profile",
    "picture",
    "website",
    "email",
    "email_verified",
    "gender",
    "birthdate",
    "zoneinfo",
    "locale",
    "phone_number",
    "phone_number_verified",
    "address",
    "updated_at",
    "aud",
    "exp",
    "iat",
    "iss",
    "sub",
]

TYPES_OF_GRANTS = [
    "authorization_code",
    "refresh_token",
    "password",
    "urn:ietf:params:oauth:grant-type:device_code",
]

API_SECRET_TYPE = [
    "sha256",
    "sha512",
]

API_CLAIM_TYPE = [
    "string",
]

API_SCOPE_CLAIM_TYPE = [
    "name",
    "family_name",
    "middle_name",
    "nickname",
    "preferred_username",
    "profile_picture",
    "website",
    "gender",
    "birthdate",
    "zone_info",
    "locale",
    "updated_at",
]

DEFAULT_USER_CLAIMS = {
    1: "Daniil",
    2: "Ibragim",
    3: "Krats",
    4: "-el-",
    5: "Nagibator2000",
    6: "Graf",
    7: "werni_stenu",
    8: "https://i1.sndcdn.com/artworks-000094489636-qzznk3-t500x500.jpg",
    9: "https://www.instagram.com/daniilkrats/",
    10: "danya.krats87@gmail.com",
    11: True,
    12: "Attack Helicopter",
    13: "02/01/2000",
    14: "GMT+1",
    15: "Warsaw",
    16: "+48510143314",
    17: False,
    18: "5 Snowdon View, Ffordd Caergybi, Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch LL61 5SX, Wielka Brytania",
    19: 1234567890,
}

CLIENT_SECRETS = {
    1: "past",
    2: "play",
    3: "health",
    4: "address",
    5: "their",
    6: "line",
    7: "film",
    8: "light",
    9: "position",
    10: "themselves",
}

CLIENT_SCOPES = {
    1: "openid",
    2: "openid email",
    3: "openid profile",
    4: "openid email",
    5: "openid profile",
    6: "openid profile",
    7: "openid",
    8: "openid profile",
    9: "openid profile",
    10: "openid email",
}

ROLES = [
    "Programmer, applications",
    "Journalist, broadcasting",
    "Freight forwarder",
    "Air cabin crew",
    "Scientist, research (maths)",
]

ACCESS_TOKEN_TYPES = ["jwt", "reference"]

PROTOCOL_TYPES = [
    "open_id_connect",
]

REFRESH_TOKEN_EXPIRATION_TYPES = [
    "absolute",
    "sliding",
]

REFRESH_TOKEN_USAGE = ["one_time_only", "reuse"]

IDENTITY_PROVIDERS = [
    {
        "name": "github",
        "auth_endpoint_link": "https://github.com/login/oauth/authorize",
        "token_endpoint_link": "https://github.com/login/oauth/access_token",
        "userinfo_link": "https://api.github.com/user",
        "internal_redirect_uri": "http://127.0.0.1:8000/authorize/oidc/github",
        "provider_icon": "fa-github",
    },
    {
        "name": "facebook",
        "auth_endpoint_link": "https://www.facebook.com/v16.0/dialog/oauth",
        "token_endpoint_link": "https://graph.facebook.com/v16.0/oauth/access_token",
        "userinfo_link": "https://graph.facebook.com/debug_token",
        "internal_redirect_uri": "http://127.0.0.1:8000/authorize/oidc/facebook",
        "provider_icon": "fa-facebook",
    },
    {
        "name": "linkedin",
        "auth_endpoint_link": "https://www.linkedin.com/oauth/v2/authorization",
        "token_endpoint_link": "https://www.linkedin.com/oauth/v2/accessToken",
        "userinfo_link": "https://api.linkedin.com/v2/userinfo",
        "internal_redirect_uri": "http://127.0.0.1:8000/authorize/oidc/linkedin",
        "provider_icon": "fa-linkedin",
    },
    {
        "name": "google",
        "auth_endpoint_link": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_endpoint_link": "https://oauth2.googleapis.com/token",
        "userinfo_link": "https://openidconnect.googleapis.com/v1/userinfo",
        "internal_redirect_uri": "http://127.0.0.1:8000/authorize/oidc/google",
        "provider_icon": "fa-google",
    },
    {
        "name": "gitlab",
        "auth_endpoint_link": "https://gitlab.com/oauth/authorize",
        "token_endpoint_link": "https://gitlab.com/oauth/token",
        "userinfo_link": "https://gitlab.com/oauth/userinfo",
        "internal_redirect_uri": "http://127.0.0.1:8000/authorize/oidc/gitlab",
        "provider_icon": "fa-gitlab",
    },
    {
        "name": "microsoft",
        "auth_endpoint_link": "https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize",
        "token_endpoint_link": "https://login.microsoftonline.com/consumers/oauth2/v2.0/token",
        "userinfo_link": "https://graph.microsoft.com/oidc/userinfo",
        "internal_redirect_uri": "http://localhost:8000/authorize/oidc/microsoft",
        "provider_icon": "fa-microsoft",
    },
]

# <<<<<<< one_branch_user_client_registration
# POST_LOGOUT_REDIRECT_URL = [
#     "http://thompson-chung.com/",
#     "http://welch-miller.com/",
#     "https://www.cole.com/",
#     "https://www.mccarthy-ruiz.info/",
#     "http://chen-smith.com/",
#     "http://www.ross-zamora.biz/",
#     "https://www.king.com/",
#     "http://www.sparks.net/",
#     "https://www.villarreal.com/",
#     "https://meyer-berry.com/",
# ]

RESPONSE_TYPES = ['code', 'id_token', 'token', 'code id_token']

# POST_LOGOUT_REDIRECT_URL = {
#     "test_client": "http://thompson-chung.com/",
#     "double_test": "http://welch-miller.com/",
#     "santa": "https://www.cole.com/",
#     "krampus": "https://www.mccarthy-ruiz.info/",
#     "frodo": "http://chen-smith.com/",
#     "aragorn": "http://www.ross-zamora.biz/",
#     "iron_man": "https://www.king.com/",
#     "spider_man": "http://www.sparks.net/",
#     "thor": "https://www.villarreal.com/",
#     "samuel": "https://meyer-berry.com/",
# }

POST_LOGOUT_REDIRECT_URL = {
    1: "http://thompson-chung.com/",
    2: "http://welch-miller.com/",
    3: "https://www.cole.com/",
    4: "https://www.mccarthy-ruiz.info/",
    5: "http://chen-smith.com/",
    6: "http://www.ross-zamora.biz/",
    7: "https://www.king.com/",
    8: "http://www.sparks.net/",
    9: "https://www.villarreal.com/",
    10: "https://meyer-berry.com/",
}
