-- auto-generated definition
create table client_cors_origins
(
    id         serial
        primary key,
    origin     varchar not null,
    client_id  varchar
        references clients (client_id),
    updated_at timestamp,
    created_at timestamp default now()
);

alter table client_cors_origins
    owner to postgres;
