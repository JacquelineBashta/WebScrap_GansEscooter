drop database gans_db;
create database gans_db;
use gans_db;

create table city(
	city_id int auto_increment,
	city VARCHAR(50),
	country	VARCHAR(50),
    population int, 
	lat float(6),
    lon float(6),
    PRIMARY KEY (city_id)
);


drop table weather;
create table weather(
	city_id int ,
	forcast_time datetime,
	outlook	VARCHAR(100),
    temperature float(3),
	feels_like float(3),
    wind_speed float(3),
    rain_prob float(3),
    FOREIGN KEY (city_id) REFERENCES city(city_id)
);

drop table airport;
create table airport(
	city_id int ,
	icao	VARCHAR(10),
    primary key (icao),
    FOREIGN KEY (city_id) REFERENCES city(city_id)
);