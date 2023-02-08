text = """ACCESS_TOKEN_TYPES
Table
public
PROTOCOL_TYPES
Table
public
REFRESH_TOKEN_EXPIRATION
Table
public
REFRESH_TOKEN_USAGE
Table
public
USER_CLAIM_TYPE
Table
public
alembic_version
Table
public
api_claims
Table
public
api_resources
Table
public
api_scope_claims
Table
public
api_scopes
Table
public
api_secrets

public
client_claims"""

text = text.replace("Table", "")
text = text.replace("public", "")
text = text.replace("\n"*2, "\n")
text = text.replace("\n"*2, "\n")
text = text.split("\n")
for t in text:
    print(f'sess.session.execute(text("DROP TABLE {t} CASCADE"))')