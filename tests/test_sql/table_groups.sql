-- auto-generated definition
create table groups
(
    id           serial
        primary key,
    created_at   timestamp default now(),
    updated_at   timestamp default now(),
    name         varchar,
    parent_group integer
        references groups
            on delete cascade
);

alter table groups
    owner to postgres;


INSERT INTO public.groups (id, created_at, updated_at, name, parent_group) VALUES (1, '2023-01-30 22:08:20.546738', '2023-01-30 22:08:20.546738', 'Jorno', null);
INSERT INTO public.groups (id, created_at, updated_at, name, parent_group) VALUES (11, '2023-01-30 22:08:20.571570', '2023-01-30 22:08:20.571570', 'gold', 1);
INSERT INTO public.groups (id, created_at, updated_at, name, parent_group) VALUES (12, '2023-01-30 22:08:20.597873', '2023-01-30 22:08:20.597873', 'experience', 1);
INSERT INTO public.groups (id, created_at, updated_at, name, parent_group) VALUES (13, '2023-01-30 22:08:20.621189', '2023-01-30 22:08:20.621189', 'requiem', 1);
INSERT INTO public.groups (id, created_at, updated_at, name, parent_group) VALUES (2, '2023-01-30 22:08:20.645050', '2023-01-30 22:08:20.645050', 'Polnareff', null);
INSERT INTO public.groups (id, created_at, updated_at, name, parent_group) VALUES (21, '2023-01-30 22:08:20.668011', '2023-01-30 22:08:20.668011', 'silver', 2);
INSERT INTO public.groups (id, created_at, updated_at, name, parent_group) VALUES (201, '2023-01-30 22:08:20.719474', '2023-01-30 22:08:20.719474', 'chariot', 21);
INSERT INTO public.groups (id, created_at, updated_at, name, parent_group) VALUES (202, '2023-01-30 22:08:20.748626', '2023-01-30 22:08:20.748626', 'requiem', 21);
INSERT INTO public.groups (id, created_at, updated_at, name, parent_group) VALUES (3, '2023-01-30 22:08:20.772810', '2023-01-30 22:08:20.772810', 'Kakyoin', null);
INSERT INTO public.groups (id, created_at, updated_at, name, parent_group) VALUES (31, '2023-01-30 22:08:20.796654', '2023-01-30 22:08:20.796654', 'hierophant', 3);
INSERT INTO public.groups (id, created_at, updated_at, name, parent_group) VALUES (32, '2023-01-30 22:08:20.820861', '2023-01-30 22:08:20.820861', 'green', 3);
