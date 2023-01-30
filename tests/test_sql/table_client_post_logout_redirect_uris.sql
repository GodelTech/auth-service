-- auto-generated definition
create table client_post_logout_redirect_uris
(
    id                       serial
        primary key,
    post_logout_redirect_uri varchar not null,
    client_id                varchar
        references clients (client_id),
    updated_at               timestamp,
    created_at               timestamp default now()
);

alter table client_post_logout_redirect_uris
    owner to postgres;


INSERT INTO public.client_post_logout_redirect_uris (id, post_logout_redirect_uri, client_id, updated_at, created_at) VALUES (1, 'https://www.scott.org/', 'test_client', null, '2023-01-30 22:01:15.733330');
INSERT INTO public.client_post_logout_redirect_uris (id, post_logout_redirect_uri, client_id, updated_at, created_at) VALUES (2, 'https://francis.com/', 'double_test', null, '2023-01-30 22:01:15.739594');
INSERT INTO public.client_post_logout_redirect_uris (id, post_logout_redirect_uri, client_id, updated_at, created_at) VALUES (3, 'http://www.jones.com/', 'santa', null, '2023-01-30 22:01:15.746310');
INSERT INTO public.client_post_logout_redirect_uris (id, post_logout_redirect_uri, client_id, updated_at, created_at) VALUES (4, 'https://www.villarreal.com/', 'krampus', null, '2023-01-30 22:01:15.767372');
INSERT INTO public.client_post_logout_redirect_uris (id, post_logout_redirect_uri, client_id, updated_at, created_at) VALUES (5, 'https://meyer-berry.com/', 'frodo', null, '2023-01-30 22:01:15.775052');
INSERT INTO public.client_post_logout_redirect_uris (id, post_logout_redirect_uri, client_id, updated_at, created_at) VALUES (6, 'http://stephens.com/', 'aragorn', null, '2023-01-30 22:01:15.782408');
INSERT INTO public.client_post_logout_redirect_uris (id, post_logout_redirect_uri, client_id, updated_at, created_at) VALUES (7, 'https://carroll-taylor.com/', 'iron_man', null, '2023-01-30 22:01:15.792354');
INSERT INTO public.client_post_logout_redirect_uris (id, post_logout_redirect_uri, client_id, updated_at, created_at) VALUES (8, 'http://garza-taylor.com/', 'spider_man', null, '2023-01-30 22:01:15.799505');
INSERT INTO public.client_post_logout_redirect_uris (id, post_logout_redirect_uri, client_id, updated_at, created_at) VALUES (9, 'https://perry.com/', 'thor', null, '2023-01-30 22:01:15.805980');
INSERT INTO public.client_post_logout_redirect_uris (id, post_logout_redirect_uri, client_id, updated_at, created_at) VALUES (10, 'https://www.evans-mcgee.com/', 'samuel', null, '2023-01-30 22:01:15.812598');
