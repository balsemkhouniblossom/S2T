-- PostgreSQL Database Setup Script
-- Run this script after installing PostgreSQL

-- Connect to PostgreSQL as postgres user:
-- psql -U postgres

-- Create the database
CREATE DATABASE training_management_db;

-- Create a specific user for the application (optional but recommended)
CREATE USER training_user WITH PASSWORD 'training123';

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON DATABASE training_management_db TO training_user;

-- Grant additional privileges for the user to create tables, etc.
ALTER USER training_user CREATEDB;

-- Connect to the new database
\c training_management_db;

-- Grant schema permissions
GRANT ALL ON SCHEMA public TO training_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO training_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO training_user;

-- Show database info
\l

-- Exit
\q
