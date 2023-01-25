CREATE TABLE clients (
	id SERIAL NOT NULL,
	client_id VARCHAR NOT NULL,
	absolute_refresh_token_lifetime INTEGER NOT NULL,
	access_token_lifetime INTEGER NOT NULL,
	access_token_type VARCHAR NOT NULL,
	allow_access_token_via_browser BOOLEAN NOT NULL,
	allow_offline_access BOOLEAN NOT NULL,
	allow_plain_text_pkce BOOLEAN NOT NULL,
	allow_remember_consent BOOLEAN NOT NULL,
	always_include_user_claims_id_token BOOLEAN NOT NULL,
	always_send_client_claims BOOLEAN NOT NULL,
	authorisation_code_lifetime INTEGER NOT NULL,
	client_name VARCHAR NOT NULL,
	client_uri VARCHAR NOT NULL,
	enable_local_login BOOLEAN,
	enabled BOOLEAN,
	identity_token_lifetime INTEGER NOT NULL,
	include_jwt_id BOOLEAN NOT NULL,
	logo_uri VARCHAR NOT NULL,
	logout_session_required BOOLEAN NOT NULL,
	logout_uri VARCHAR NOT NULL,
	prefix_client_claims VARCHAR,
	protocol_type VARCHAR NOT NULL,
	refresh_token_expiration VARCHAR NOT NULL,
	refresh_token_usage VARCHAR NOT NULL,
	require_client_secret BOOLEAN NOT NULL,
	require_consent BOOLEAN NOT NULL,
	require_pkce BOOLEAN NOT NULL,
	sliding_refresh_token_lifetime INTEGER NOT NULL,
	update_access_token_claims_on_refresh BOOLEAN NOT NULL,
	created TIMESTAMP WITHOUT TIME ZONE,
	updated_at TIMESTAMP WITHOUT TIME ZONE,
	PRIMARY KEY (id),
	UNIQUE (client_id),
	UNIQUE (id)
);



CREATE TABLE persistent_grants (
	id SERIAL NOT NULL,
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
	key VARCHAR(512) NOT NULL,
	data JSON NOT NULL,
	expiration TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	subject_id INTEGER NOT NULL,
	type VARCHAR NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (key)
);
ALTER TABLE persistent_grants ADD COLUMN client_id VARCHAR(80);
ALTER TABLE persistent_grants ADD FOREIGN KEY(client_id) REFERENCES clients (client_id);
