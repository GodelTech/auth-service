-- auto-generated definition
create table users
(
    id                     serial
        primary key,
    created_at             timestamp default now(),
    updated_at             timestamp default now(),
    email                  varchar
        unique,
    email_confirmed        boolean,
    password_hash          varchar not null,
    security_stamp         varchar,
    phone_number           varchar not null
        unique,
    phone_number_confirmed boolean,
    two_factors_enabled    boolean,
    lockout_end_date_utc   date,
    lockout_enabled        boolean,
    access_failed_count    integer not null,
    username               varchar not null
        unique
);

alter table users
    owner to postgres;


INSERT INTO public.users (id, created_at, updated_at, email, email_confirmed, password_hash, security_stamp, phone_number, phone_number_confirmed, two_factors_enabled, lockout_end_date_utc, lockout_enabled, access_failed_count, username) VALUES (1, '2023-01-30 22:01:15.448874', '2023-01-30 22:01:15.448874', 'amanda96@bruce-compton.org', false, '$2b$12$Hh5flmg7R82gZDhpBBQd3ehkKItIc/XLG5iXuxAj/iYIrIupA5CoC', 'today', '0248945174', true, true, '1996-02-22', true, 1020, 'TestClient');
INSERT INTO public.users (id, created_at, updated_at, email, email_confirmed, password_hash, security_stamp, phone_number, phone_number_confirmed, two_factors_enabled, lockout_end_date_utc, lockout_enabled, access_failed_count, username) VALUES (2, '2023-01-30 22:01:15.458794', '2023-01-30 22:01:15.458794', 'johnblair@brown-johnson.biz', false, '$2b$12$XAYxWAqiYAiyANw5fQ3f3uP0enBev67CU7DCkpoPiuoERHJ0tqFCq', 'million', '+1-125-609-7670x172', false, false, '2010-09-18', false, 5306, 'Doubl');
INSERT INTO public.users (id, created_at, updated_at, email, email_confirmed, password_hash, security_stamp, phone_number, phone_number_confirmed, two_factors_enabled, lockout_end_date_utc, lockout_enabled, access_failed_count, username) VALUES (3, '2023-01-30 22:01:15.466596', '2023-01-30 22:01:15.466596', 'james71@bishop.org', true, '$2b$12$zdWVz4XOtX54/SrRIqmdTeJvE.NaoKPlhC8J3RaDgn.47Qerc5RHm', 'rather', '942-641-8306', true, true, '2021-06-27', false, 7462, 'SantaClaus');
INSERT INTO public.users (id, created_at, updated_at, email, email_confirmed, password_hash, security_stamp, phone_number, phone_number_confirmed, two_factors_enabled, lockout_end_date_utc, lockout_enabled, access_failed_count, username) VALUES (4, '2023-01-30 22:01:15.474186', '2023-01-30 22:01:15.474186', 'huberrachel@gmail.com', true, '$2b$12$dKiV3.whFCXSuzD029OzheK/V1.s967i0ZxvE5RlY5Yp/gi795PRG', 'especially', '8993318868', true, false, '1979-12-01', true, 9273, 'Krampus');
INSERT INTO public.users (id, created_at, updated_at, email, email_confirmed, password_hash, security_stamp, phone_number, phone_number_confirmed, two_factors_enabled, lockout_end_date_utc, lockout_enabled, access_failed_count, username) VALUES (5, '2023-01-30 22:01:15.481233', '2023-01-30 22:01:15.481233', 'wallsrobert@gmail.com', true, '$2b$12$6SWxQ8lKhc/FQo1Y4WSS6.0FTD6r6h0SqJvbV1QUR15BsB3gxp/rS', 'staff', '(076)607-5415', false, false, '1994-06-13', false, 5659, 'FrodoBaggins');
INSERT INTO public.users (id, created_at, updated_at, email, email_confirmed, password_hash, security_stamp, phone_number, phone_number_confirmed, two_factors_enabled, lockout_end_date_utc, lockout_enabled, access_failed_count, username) VALUES (6, '2023-01-30 22:01:15.488547', '2023-01-30 22:01:15.488547', 'alejandromccann@yahoo.com', false, '$2b$12$VK2dOVKFFgGHo/OAsMk3.e4dYl02cS8Kme5ugNAsqoQjGbHF2cwBm', 'pick', '(303)104-5093', false, false, '2000-11-24', false, 7810, 'Aragorn');
INSERT INTO public.users (id, created_at, updated_at, email, email_confirmed, password_hash, security_stamp, phone_number, phone_number_confirmed, two_factors_enabled, lockout_end_date_utc, lockout_enabled, access_failed_count, username) VALUES (7, '2023-01-30 22:01:15.496194', '2023-01-30 22:01:15.496194', 'david35@yahoo.com', true, '$2b$12$e0Nu5Zo/3N9p6I7y.bX.KeEt4ToLcPQM0j1KGtx5kBZWHYE65sOza', 'final', '852-911-8942x6223', true, false, '1986-02-08', false, 4768, 'TonyStark');
INSERT INTO public.users (id, created_at, updated_at, email, email_confirmed, password_hash, security_stamp, phone_number, phone_number_confirmed, two_factors_enabled, lockout_end_date_utc, lockout_enabled, access_failed_count, username) VALUES (8, '2023-01-30 22:01:15.505376', '2023-01-30 22:01:15.505376', 'ialvarado@hotmail.com', false, '$2b$12$icIItrfeBNeHonHN7UwtvuAprmtr37dN2lNkOq31XJfWWkoQiB9Zu', 'indeed', '126-486-2964', true, false, '1986-11-18', true, 6049, 'PeterParker');
INSERT INTO public.users (id, created_at, updated_at, email, email_confirmed, password_hash, security_stamp, phone_number, phone_number_confirmed, two_factors_enabled, lockout_end_date_utc, lockout_enabled, access_failed_count, username) VALUES (9, '2023-01-30 22:01:15.513924', '2023-01-30 22:01:15.513924', 'aortiz@valenzuela.info', false, '$2b$12$1ae6TpnDlsS/Ma1vmlM5xugwmUDNj1nSs8lwkSCCVn/dCahlSk18q', 'crime', '418-927-6266', false, false, '2000-11-09', true, 8574, 'Thor');
INSERT INTO public.users (id, created_at, updated_at, email, email_confirmed, password_hash, security_stamp, phone_number, phone_number_confirmed, two_factors_enabled, lockout_end_date_utc, lockout_enabled, access_failed_count, username) VALUES (10, '2023-01-30 22:01:15.521103', '2023-01-30 22:01:15.521103', 'steven17@phillips.info', true, '$2b$12$IAzZEbF3fu5H3qSN42mJlOJmRw6/EO0OMQRE0JtYo4XLcuDJU3nPq', 'account', '414.892.6717', false, true, '1989-01-22', false, 1979, 'SamuelGamgy');
