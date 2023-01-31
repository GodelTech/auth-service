-- auto-generated definition
create table users_groups
(
    group_id integer not null
        references groups,
    user_id  integer not null
        references users,
    primary key (group_id, user_id)
);

alter table users_groups
    owner to postgres;
