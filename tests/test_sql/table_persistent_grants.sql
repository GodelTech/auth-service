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
