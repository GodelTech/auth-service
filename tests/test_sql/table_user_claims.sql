-- auto-generated definition
create table user_claims
(
    id          serial
        primary key,
    created_at  timestamp default now(),
    updated_at  timestamp default now(),
    claim_type  varchar,
    claim_value varchar not null,
    "User"      integer
        references users
);

alter table user_claims
    owner to postgres;


INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (1, '2023-01-30 22:01:15.528002', '2023-01-30 22:01:15.528002', 'name', 'Daniil', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (2, '2023-01-30 22:01:15.533011', '2023-01-30 22:01:15.533011', 'given_name', 'Ibragim', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (3, '2023-01-30 22:01:15.537743', '2023-01-30 22:01:15.537743', 'family_name', 'Krats', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (4, '2023-01-30 22:01:15.543657', '2023-01-30 22:01:15.543657', 'middle_name', '-el-', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (5, '2023-01-30 22:01:15.549499', '2023-01-30 22:01:15.549499', 'nickname', 'Nagibator2000', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (6, '2023-01-30 22:01:15.561035', '2023-01-30 22:01:15.561035', 'preferred_username', 'Graf', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (7, '2023-01-30 22:01:15.568366', '2023-01-30 22:01:15.568366', 'profile', 'werni_stenu', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (8, '2023-01-30 22:01:15.574633', '2023-01-30 22:01:15.574633', 'picture', 'https://i1.sndcdn.com/artworks-000094489636-qzznk3-t500x500.jpg', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (9, '2023-01-30 22:01:15.582276', '2023-01-30 22:01:15.582276', 'website', 'https://www.instagram.com/daniilkrats/', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (10, '2023-01-30 22:01:15.588532', '2023-01-30 22:01:15.588532', 'email', 'danya.krats87@gmail.com', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (11, '2023-01-30 22:01:15.635170', '2023-01-30 22:01:15.635170', 'email_verified', 'true', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (12, '2023-01-30 22:01:15.642961', '2023-01-30 22:01:15.642961', 'gender', 'Attack Helicopter', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (13, '2023-01-30 22:01:15.651264', '2023-01-30 22:01:15.651264', 'birthdate', '02/01/2000', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (14, '2023-01-30 22:01:15.667388', '2023-01-30 22:01:15.667388', 'zoneinfo', 'GMT+1', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (15, '2023-01-30 22:01:15.675862', '2023-01-30 22:01:15.675862', 'locale', 'Warsaw', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (16, '2023-01-30 22:01:15.683335', '2023-01-30 22:01:15.683335', 'phone_number', '+48510143314', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (17, '2023-01-30 22:01:15.698752', '2023-01-30 22:01:15.698752', 'phone_number_verified', 'false', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (18, '2023-01-30 22:01:15.706505', '2023-01-30 22:01:15.706505', 'address', '5 Snowdon View, Ffordd Caergybi, Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch LL61 5SX, Wielka Brytania', 1);
INSERT INTO public.user_claims (id, created_at, updated_at, claim_type, claim_value, "User") VALUES (19, '2023-01-30 22:01:15.724632', '2023-01-30 22:01:15.724632', 'updated_at', '1234567890', 1);
