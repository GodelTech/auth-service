-- auto-generated definition
create table api_resources
(
    id           serial
        primary key,
    created_at   timestamp default now(),
    updated_at   timestamp default now(),
    description  varchar,
    display_name varchar,
    enabled      boolean,
    name         varchar not null
);

alter table api_resources
    owner to postgres;
