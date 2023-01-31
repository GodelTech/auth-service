-- auto-generated definition
create table identity_resources
(
    id                         serial
        primary key,
    created_at                 timestamp default now(),
    updated_at                 timestamp default now(),
    description                varchar(512),
    display_name               varchar(32) not null,
    emphasize                  boolean     not null,
    enabled                    boolean     not null,
    name                       varchar(32) not null,
    required                   boolean     not null,
    show_in_discovery_document boolean     not null
);

alter table identity_resources
    owner to postgres;
