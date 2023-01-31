-- auto-generated definition
create table permissions_roles
(
    role_id       integer not null
        references roles,
    permission_id integer not null
        references permissions,
    primary key (role_id, permission_id)
);

alter table permissions_roles
    owner to postgres;
