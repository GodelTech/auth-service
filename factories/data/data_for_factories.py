from src.main import app
from src.business_logic.services.password import PasswordHash


CLIENT_IDS = [
    "test_client",
    "double_test",
    "santa",
    "krampus",
    "frodo",
    "aragorn",
    "iron_man",
    "spider_man",
    "thor",
    "samuel",
]

CLIENT_HASH_PASSWORDS = {
    "test_client": PasswordHash.hash_password("test_password"),
    "double_test": PasswordHash.hash_password("double_password"),
    "santa": PasswordHash.hash_password("christmas_forever"),
    "krampus": PasswordHash.hash_password("no_to_christmas"),
    "frodo": PasswordHash.hash_password("one_ring_to_rule_them_all"),
    "aragorn": PasswordHash.hash_password("son_of_aratorn"),
    "iron_man": PasswordHash.hash_password("best_avenger"),
    "spider_man": PasswordHash.hash_password("the_beginner"),
    "thor": PasswordHash.hash_password("god_of_thunder"),
    "samuel": PasswordHash.hash_password("just_a_guy"),
}

CLIENT_PASSWORDS = {
    "test_client": "test_password",
    "double_test": "double_password",
    "santa": "christmas_forever",
    "krampus": "no_to_christmas",
    "frodo": "one_ring_to_rule_them_all",
    "aragorn": "son_of_aratorn",
    "iron_man": "best_avenger",
    "spider_man": "the_beginner",
    "thor": "god_of_thunder",
    "samuel": "just_a_guy",
}

CLIENT_USERNAMES = {
    "test_client": "TestClient",
    "double_test": "Doubl",
    "santa": "SantaClaus",
    "krampus": "Krampus",
    "frodo": "FrodoBaggins",
    "aragorn": "Aragorn",
    "iron_man": "TonyStark",
    "spider_man": "PeterParker",
    "thor": "Thor",
    "samuel": "SamuelGamgy",
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
]

TYPES_OF_GRANTS = [
    "code",
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
    "name": "Daniil",
    "given_name": "Ibragim",
    "family_name": "Krats",
    "middle_name": "-el-",
    "nickname": "Nagibator2000",
    "preferred_username": "Graf",
    "profile": "werni_stenu",
    "picture": "https://i1.sndcdn.com/artworks-000094489636-qzznk3-t500x500.jpg",
    "website": "https://www.instagram.com/daniilkrats/",
    "email": "danya.krats87@gmail.com",
    "email_verified": True,
    "gender": "Attack Helicopter",
    "birthdate": "02/01/2000",
    "zoneinfo": "GMT+1",
    "locale": "Warsaw",
    "phone_number": "+48510143314",
    "phone_number_verified": False,
    "address": "5 Snowdon View, Ffordd Caergybi, Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch LL61 5SX, Wielka Brytania",
    "updated_at": 1234567890,
}
