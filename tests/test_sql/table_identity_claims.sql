-- auto-generated definition
create table identity_claims
(
    id                   serial
        primary key,
    created_at           timestamp default now(),
    updated_at           timestamp default now(),
    identity_resource_id integer
        references identity_resources,
    type                 varchar
);

alter table identity_claims
    owner to postgres;
