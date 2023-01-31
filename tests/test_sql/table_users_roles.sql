-- auto-generated definition
create table users_roles
(
    role_id integer not null
        references roles,
    user_id integer not null
        references users,
    primary key (role_id, user_id)
);

alter table users_roles
    owner to postgres;
