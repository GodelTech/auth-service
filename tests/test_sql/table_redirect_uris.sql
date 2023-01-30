-- auto-generated definition
create table client_redirect_uris
(
    id           serial
        primary key,
    redirect_uri varchar not null,
    client_id    varchar
        references clients (client_id),
    updated_at   timestamp,
    created_at   timestamp default now()
);

alter table client_redirect_uris
    owner to postgres;


INSERT INTO public.client_redirect_uris (id, redirect_uri, client_id, updated_at, created_at) VALUES (1, 'https://www.google.com/', 'test_client', null, '2023-01-30 22:01:15.882867');
INSERT INTO public.client_redirect_uris (id, redirect_uri, client_id, updated_at, created_at) VALUES (2, 'https://www.google.com/', 'double_test', null, '2023-01-30 22:01:15.894605');
INSERT INTO public.client_redirect_uris (id, redirect_uri, client_id, updated_at, created_at) VALUES (3, 'https://www.google.com/', 'santa', null, '2023-01-30 22:01:15.900715');
INSERT INTO public.client_redirect_uris (id, redirect_uri, client_id, updated_at, created_at) VALUES (4, 'https://www.google.com/', 'krampus', null, '2023-01-30 22:01:15.907073');
INSERT INTO public.client_redirect_uris (id, redirect_uri, client_id, updated_at, created_at) VALUES (5, 'https://www.google.com/', 'frodo', null, '2023-01-30 22:01:15.912749');
INSERT INTO public.client_redirect_uris (id, redirect_uri, client_id, updated_at, created_at) VALUES (6, 'https://www.google.com/', 'aragorn', null, '2023-01-30 22:01:15.918695');
INSERT INTO public.client_redirect_uris (id, redirect_uri, client_id, updated_at, created_at) VALUES (7, 'https://www.google.com/', 'iron_man', null, '2023-01-30 22:01:15.926779');
INSERT INTO public.client_redirect_uris (id, redirect_uri, client_id, updated_at, created_at) VALUES (8, 'https://www.google.com/', 'spider_man', null, '2023-01-30 22:01:15.934062');
INSERT INTO public.client_redirect_uris (id, redirect_uri, client_id, updated_at, created_at) VALUES (9, 'https://www.google.com/', 'thor', null, '2023-01-30 22:01:15.938870');
INSERT INTO public.client_redirect_uris (id, redirect_uri, client_id, updated_at, created_at) VALUES (10, 'https://www.google.com/', 'samuel', null, '2023-01-30 22:01:15.943724');
