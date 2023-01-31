-- auto-generated definition
create table api_scope_claims
(
    id            serial
        primary key,
    created_at    timestamp default now(),
    updated_at    timestamp default now(),
    type          varchar,
    api_scopes_id integer
        references api_scopes
);

alter table api_scope_claims
    owner to postgres;
