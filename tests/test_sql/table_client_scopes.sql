-- auto-generated definition
create table client_scopes
(
    id         serial
        primary key,
    scope      varchar not null,
    client_id  varchar
        references clients (client_id),
    updated_at timestamp,
    created_at timestamp default now()
);

alter table client_scopes
    owner to postgres;
