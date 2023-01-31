-- auto-generated definition
create table client_grant_types
(
    id         serial
        primary key,
    grant_type varchar not null,
    client_id  varchar
        references clients (client_id),
    updated_at timestamp,
    created_at timestamp default now()
);

alter table client_grant_types
    owner to postgres;
