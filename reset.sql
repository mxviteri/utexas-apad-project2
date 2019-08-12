# CLOUD SQL SCRIPT

DROP TABLE IF EXISTS usersEvents;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS venues;

CREATE TABLE IF NOT EXISTS roles (
	id integer not null auto_increment,
	name varchar(25),
    primary key (id)
);

CREATE TABLE IF NOT EXISTS venues (
	id integer not null auto_increment,
	name varchar(50),
	open time,
	close time,
    primary key (id)
);

CREATE TABLE IF NOT EXISTS events (
	id integer not null auto_increment,
	name varchar(50),
    	description blob,
	venue integer,
	datetime datetime,
	capacity integer,
    	primary key (id),
	foreign key (venue) references venues (id)
);

CREATE TABLE IF NOT EXISTS users (
	id integer not null auto_increment,
	username varchar(50),
    	password varchar(255),
	role integer,
	primary key (id),
	foreign key (role) references roles (id),
	unique key user_pass (username, password)
);

CREATE TABLE IF NOT EXISTS usersEvents (
	id integer not null auto_increment,
	userId integer,
    	eventId integer,
    	primary key (id),
	foreign key (userId) references users (id)
		on delete cascade,
    	foreign key (eventId) references events (id),
	unique key user_event (userId, eventId)
);

INSERT INTO roles
	(name)
VALUES
	('admin'),
	('user');
	
INSERT INTO users
	(username, password, role)
VALUES
	('super', 'master', 1),
	('john', 'password1', 2),
	('Susan', 'password2', 2);

INSERT INTO venues
	(name, open, close)
VALUES
	('atrium', '08:00:00', '17:00:00'),
	('Intramural Fields', '09:00:00', '21:00:00');
	
INSERT INTO events
	(name, description, venue, datetime, capacity)
VALUES
	('soccer', 'an event',  1, '2019-08-01 13:00:00', 10),
	('basketball', 'an event', 1, '2019-08-01 15:00:00', 5),
	('tennis', 'an event', 2, '2019-08-01 10:00:00', 2);