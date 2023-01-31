-- auto-generated definition
create table api_secrets
(
    id               serial
        primary key,
    created_at       timestamp default now(),
    updated_at       timestamp default now(),
    description      varchar,
    expiration       timestamp not null,
    type             varchar,
    value            varchar,
    api_resources_id integer
        references api_resources
);

alter table api_secrets
    owner to postgres;
