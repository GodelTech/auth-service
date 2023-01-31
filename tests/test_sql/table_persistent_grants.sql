-- auto-generated definition
create table persistent_grants
(
    id         serial
        primary key,
    created_at timestamp default now(),
    updated_at timestamp default now(),
    key        varchar(512)  not null
        unique
        constraint persistent_grants_key_key1
            unique,
    data       varchar(2048) not null,
    subject_id integer
        references users
        constraint persistent_grants_subject_id_fkey1
            references users,
    type       varchar       not null,
    expiration integer       not null,
    client_id  varchar(80)
        references clients (client_id)
);

alter table persistent_grants
    owner to postgres;


INSERT INTO public.persistent_grants (id, created_at, updated_at, key, data, subject_id, type, expiration, client_id) VALUES (9, '2023-01-30 22:01:29.436772', '2023-01-30 22:01:29.436772', '913bc2b7-849c-4d10-a974-8b5f07eac358', 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwMDAiLCJjbGllbnRfaWQiOiJkb3VibGVfdGVzdCIsImlhdCI6MTY3NTEwNTI4OSwiZXhwIjoxNjc1MTA4ODg5LCJzdWIiOjEsInNjb3BlcyI6InRlc3QifQ.P2LokMFksh71PymsSYZPLCLujPkhE7qcU9G-9Xd1QKeoF7YtikAIWqWpll3asFpUAgqnndzSeIkaDRi9HAavLt2npgTp7X2Taw-v7lZlxNpZZmxUGhx40NAEQsobGYHXhov_7IfCcVtqqH9mYY4DycNnqADS8GaHFIzh6Rhh9eej8eb5acFVynW_SPiWLsYM9Pp2GNAZ3rZlbrTinvwuMeIvkdVzIoVY8bkvRRmXx7XENDF_RiEjXt5ZGtz9h13mL7Inx3LduwZXxCQtRlgdkPNyaf6htCqo3CUXWFJapl6XQCOYRRpen8Dnfn2DYHQFivbdcN3ZBHKgmpbDiubUqQ', 1, 'refresh_token', 600, 'double_test');
INSERT INTO public.persistent_grants (id, created_at, updated_at, key, data, subject_id, type, expiration, client_id) VALUES (33, '2023-01-30 22:08:16.548736', '2023-01-30 22:08:16.548736', 'ba59a8b2-7afd-4fb9-9b6e-25f3ef2ab935', 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwMDAiLCJjbGllbnRfaWQiOiJkb3VibGVfdGVzdCIsImlhdCI6MTY3NTEwNTY5NiwiZXhwIjoxNjc1MTA5Mjk2LCJzdWIiOjEsInNjb3BlcyI6InRlc3QifQ.kzCJqHJ2JP0Qo0-jABNPQ4j1L4TcpV_6EcDrqG9N_H9Nrb5icJHn2bBL_tEEIUtcj9laZPO_IVqJPbhJB-clMRIfoPC-paCr4XYX4lXjkVJLz4W3xu2FC8Ot_xKV_OY-iAJL0-bqVo30M7g7CcVO82rlPjVAC6Kss-fwnoNBIWxir0oP9ASrxypHwaC_9bM4sdTQcjWac2sqvWjm9wVchnvCYCJEhh1zI5X395z44HiYGXCnjDfGfOXAQPeAzGKqYmyvkCnZP8qlzcGz-ID90qIG4vah_NgfX5ODmcVaMemi-4jbOvFU5jIT8KCJGgxZzHGj97-XWZ0H5zv5UliyXQ', 1, 'refresh_token', 600, 'double_test');
INSERT INTO public.persistent_grants (id, created_at, updated_at, key, data, subject_id, type, expiration, client_id) VALUES (34, '2023-01-30 22:08:16.786116', '2023-01-30 22:08:16.786116', 'b80c2c66-722b-41ff-bfc3-af75d207a2f0', 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTY3NTEwOTI5Ni42NjI2MDJ9.e4CCOW9xu3n8ClpPc40nFXjgzyKtmmtoKKQjXmV1KRTMMExCqzkF2a9_QfmSTVvjSwO5PbvJJfWZuBc51W78XX-xQtc1SMUsv6diJPk_BWl6oakmHPIYQVgecbT8HnQJBxGITXirJI8GZ0RW84C7-Q-NvCKlARwgwHUISMtFeMW71P1KhUVgNU2kpVyuXtSMDAFe3Lm0IcydGWxGJtSRmuGYN80fcFu3mM5VpVIPQPtNh6YnUsilHtUdX4rDz9lMCYzLYObh16hHYXwqmbsP8gJoscz9MWEm-2tE2IQU7sG-f5GTsY8g-6SU5e3XxGK50Wha0y6cs6oo-5-s8_ukJg', 1, 'refresh_token', 600, 'test_client');
INSERT INTO public.persistent_grants (id, created_at, updated_at, key, data, subject_id, type, expiration, client_id) VALUES (44, '2023-01-30 22:08:24.047028', '2023-01-30 22:08:24.047028', 'aea13d7f-cd60-4312-a98f-a0af202b6718', 'aphWlXXq5Gys18d1PmEPDt_cMTjmvZpV_blyH6xDKRs', 1, 'code', 600, 'test_client');
