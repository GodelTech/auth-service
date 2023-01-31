-- auto-generated definition
create table roles
(
    id         serial
        primary key,
    created_at timestamp default now(),
    updated_at timestamp default now(),
    name       varchar not null
        unique
);

alter table roles
    owner to postgres;
