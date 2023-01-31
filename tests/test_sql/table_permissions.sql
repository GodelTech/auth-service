-- auto-generated definition
create table permissions
(
    id         serial
        primary key,
    created_at timestamp default now(),
    updated_at timestamp default now(),
    name       varchar
        unique
);

alter table permissions
    owner to postgres;
