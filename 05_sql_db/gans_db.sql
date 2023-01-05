drop database gans_db;
create database gans_db;
use gans_db;

create table city(
	city_id int auto_increment,
	city 		varchar(50),
	country		varchar(50),
    population 	int, 
	lat 		float(6),
    lon 		float(6),
    primary key (city_id)
);

drop table weather;
create table weather(
	city_id 		int ,
	forcast_time 	datetime,
	outlook			varchar(100),
    temperature 	float(3),
	feels_like 		float(3),
    wind_speed 		float(3),
    rain_prob 		float(3),
    foreign key (city_id) references city(city_id)
);

drop table airport;
create table airport(
	city_id 	int,
	icao		varchar(10),
    primary key (icao),
    foreign key (city_id) references city(city_id)
);

drop table flight;
create table flight(
	flight_data_id  		int auto_increment,
	arrival_icao 			varchar(10),
	arrival_time_local 		datetime,
	arrival_terminal		varchar(10),
    departure_city 			varchar(50),
	departure_icao 			varchar(10),
    departure_time_local 	datetime,
    airline 				varchar(50),
    flight_number 			varchar(15),
    data_retrieved_on 		date,
    primary key (flight_data_id),
    foreign key (arrival_icao) references airport(icao)
);