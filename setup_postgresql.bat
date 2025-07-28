@echo off
echo ====================================
echo PostgreSQL Setup for Training Management System
echo ====================================

echo.
echo 1. Make sure PostgreSQL is installed and running
echo 2. You'll be prompted for the postgres user password
echo.

pause

echo Setting up database...
psql -U postgres -f setup_postgresql.sql

echo.
echo Database setup complete!
echo.

echo Running Django migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo Creating superuser (optional)...
python manage.py createsuperuser

echo.
echo Setup complete! You can now run:
echo python manage.py runserver
echo.
pause
