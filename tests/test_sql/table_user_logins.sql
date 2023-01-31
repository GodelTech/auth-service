-- auto-generated definition
create table user_logins
(
    id             integer not null,
    created_at     timestamp default now(),
    updated_at     timestamp default now(),
    "User"         integer
        references users,
    login_provider varchar not null
        unique,
    provider_key   varchar not null
        unique,
    primary key (id, login_provider, provider_key)
);

alter table user_logins
    owner to postgres;
