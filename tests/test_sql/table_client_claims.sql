-- auto-generated definition
create table client_claims
(
    id         serial
        primary key,
    type       varchar not null,
    value      varchar not null,
    client_id  varchar
        references clients (client_id),
    updated_at timestamp,
    created_at timestamp default now()
);

alter table client_claims
    owner to postgres;
