-- auto-generated definition
create table api_claims
(
    id               serial
        primary key,
    created_at       timestamp default now(),
    updated_at       timestamp default now(),
    type             varchar,
    api_resources_id integer
        references api_resources
);

alter table api_claims
    owner to postgres;
