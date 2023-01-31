-- auto-generated definition
create table client_secrets
(
    id          serial
        primary key,
    description varchar not null,
    expiration  integer not null,
    type        varchar not null,
    value       varchar not null,
    client_id   varchar
        references clients (client_id),
    updated_at  timestamp,
    created_at  timestamp default now()
);

alter table client_secrets
    owner to postgres;


INSERT INTO public.client_secrets (id, description, expiration, type, value, client_id, updated_at, created_at) VALUES (1, 'Democratic green hospital year suffer without rather bank.', 107767, 'herself', 'past', 'test_client', null, '2023-01-30 22:01:15.819353');
INSERT INTO public.client_secrets (id, description, expiration, type, value, client_id, updated_at, created_at) VALUES (2, 'Break about establish.', 95302, 'wear', 'play', 'double_test', null, '2023-01-30 22:01:15.829060');
INSERT INTO public.client_secrets (id, description, expiration, type, value, client_id, updated_at, created_at) VALUES (3, 'Cell of course its respond.', 2822857, 'give', 'health', 'santa', null, '2023-01-30 22:01:15.836041');
INSERT INTO public.client_secrets (id, description, expiration, type, value, client_id, updated_at, created_at) VALUES (4, 'Possible reach challenge value challenge firm.', 3060, 'life', 'address', 'krampus', null, '2023-01-30 22:01:15.842227');
INSERT INTO public.client_secrets (id, description, expiration, type, value, client_id, updated_at, created_at) VALUES (5, 'Smile home southern hope detail cultural.', 9609, 'see', 'their', 'frodo', null, '2023-01-30 22:01:15.848073');
INSERT INTO public.client_secrets (id, description, expiration, type, value, client_id, updated_at, created_at) VALUES (6, 'Town almost plan.', 372, 'art', 'line', 'aragorn', null, '2023-01-30 22:01:15.853865');
INSERT INTO public.client_secrets (id, description, expiration, type, value, client_id, updated_at, created_at) VALUES (7, 'Do father beautiful than.', 46277, 'its', 'film', 'iron_man', null, '2023-01-30 22:01:15.859231');
INSERT INTO public.client_secrets (id, description, expiration, type, value, client_id, updated_at, created_at) VALUES (8, 'Approach recent program possible natural same issue.', 65793807, 'environmental', 'light', 'spider_man', null, '2023-01-30 22:01:15.864446');
INSERT INTO public.client_secrets (id, description, expiration, type, value, client_id, updated_at, created_at) VALUES (9, 'Democratic entire analysis clear about pressure cell.', 3727335, 'politics', 'position', 'thor', null, '2023-01-30 22:01:15.870062');
INSERT INTO public.client_secrets (id, description, expiration, type, value, client_id, updated_at, created_at) VALUES (10, 'Newspaper determine cover part paper beat.', 338615, 'north', 'themselves', 'samuel', null, '2023-01-30 22:01:15.877024');
