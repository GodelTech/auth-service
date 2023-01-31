-- auto-generated definition
create table client_id_restrictions
(
    id         serial
        primary key,
    provider   varchar not null,
    client_id  varchar
        references clients (client_id),
    updated_at timestamp,
    created_at timestamp default now()
);

alter table client_id_restrictions
    owner to postgres;
