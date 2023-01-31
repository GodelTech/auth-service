-- auto-generated definition
create table api_scopes
(
    id                         serial
        primary key,
    created_at                 timestamp default now(),
    updated_at                 timestamp default now(),
    description                varchar,
    name                       varchar not null,
    display_name               varchar,
    emphasize                  boolean,
    required                   boolean,
    show_in_discovery_document boolean,
    api_resources_id           integer
        references api_resources
);

alter table api_scopes
    owner to postgres;
