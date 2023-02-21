CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS cube;


CREATE TABLE Admins
(
	admin_id uuid DEFAULT uuid_generate_v4(), 
	username VARCHAR(100) UNIQUE, 
	password VARCHAR(100), 
	permissions VARCHAR(100)[100],
	PRIMARY KEY (admin_id)
);


CREATE OR REPLACE FUNCTION static_gen_ref_code()
RETURNS varchar AS $$
DECLARE
    var_code varchar(5);
    var_counter integer;
BEGIN
    var_counter = 1;
    WHILE var_counter > 0 loop
        SELECT array_to_string(array((
        SELECT SUBSTRING('abcdefghjklmnpqrstuvwxyz23456789'
                         FROM mod((random()*32)::int, 32)+1 FOR 1)
        FROM generate_series(1,5))),'') INTO var_code;
        SELECT count(*) INTO var_counter FROM Users WHERE invite_code=var_code;
    END loop;
    RETURN var_code;
END;
$$ LANGUAGE plpgsql;

INSERT INTO Admins (username, password, permissions) VALUES ('Admin', '123456', ARRAY['Self', 'Admin', 'User', 'Table', 'category', 'Category', 'Setting', 'Food', 'OfflineOrder']);

CREATE TABLE Users
(
	user_id uuid default uuid_generate_v4(),
	phone_number varchar(20) unique,
	username varchar(200),
	password varchar(200),
	sms_code varchar(10),
	is_active int,
	wallet_amount double precision,
	create_date timestamp default now(),
	primary key (user_id)

);

CREATE TABLE Tables
(
	table_id uuid default uuid_generate_v4(),
	table_name varchar(100),
	table_information json,
	create_date timestamp default now(),
	primary key (table_id)

);

CREATE TABLE Categories
(
	category_id uuid default uuid_generate_v4(),
	category_name varchar(100),
	category_information json,
	create_date timestamp default now(),
	primary key (category_id)

);

CREATE TABLE Settings
(
	setting_id uuid default uuid_generate_v4(),
	setting_title varchar(2000),
	setting_information json,
	create_date timestamp default now(),
	primary key (setting_id)

);

CREATE TABLE Foods
(
	food_id uuid default uuid_generate_v4(),
	category_id uuid REFERENCES Categories(category_id) on delete cascade,
	food_name varchar(100),
	food_price bigint,
	food_information json,
	is_active int,
	create_date timestamp default now(),
	primary key (food_id)

);

CREATE TABLE Addresses
(
	address_id uuid default uuid_generate_v4(),
	user_id uuid REFERENCES Users (user_id),
	address_name varchar(100),
	address_description json,
	create_date timestamp default now(),
	primary key (address_id)

);

CREATE TABLE OfflineOrders
(
	order_id uuid default uuid_generate_v4(),
	table_id uuid REFERENCES Tables(table_id) on delete cascade,
	foods_list json,
	order_price bigint,
	order_information json,
	create_date timestamp default now(),
	primary key (order_id)

);

