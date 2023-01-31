-- auto-generated definition
create table permissions_groups
(
    group_id      integer not null
        references groups,
    permission_id integer not null
        references permissions,
    primary key (group_id, permission_id)
);

alter table permissions_groups
    owner to postgres;
