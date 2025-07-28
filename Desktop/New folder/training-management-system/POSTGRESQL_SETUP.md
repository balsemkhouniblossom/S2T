# PostgreSQL Setup Guide

This guide helps you configure PostgreSQL for the Training Management System.

## 🚀 Quick Setup

### Option 1: Local PostgreSQL Installation

1. **Download PostgreSQL**
   - Visit https://www.postgresql.org/download/
   - Download and install PostgreSQL for your operating system
   - Remember the password you set for the `postgres` user

2. **Create Database**
   ```sql
   -- Connect to PostgreSQL as postgres user
   psql -U postgres
   
   -- Create database
   CREATE DATABASE training_management_db;
   
   -- Create user (optional)
   CREATE USER training_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE training_management_db TO training_user;
   
   -- Exit
   \q
   ```

3. **Update Django Settings**
   Edit `training_management/settings.py`:
   
   ```python
   # Comment out SQLite configuration
   # DATABASES = {
   #     'default': {
   #         'ENGINE': 'django.db.backends.sqlite3',
   #         'NAME': BASE_DIR / 'db.sqlite3',
   #     }
   # }
   
   # Uncomment PostgreSQL configuration
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'training_management_db',
           'USER': 'postgres',  # or 'training_user'
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

4. **Run Migrations**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

### Option 2: Docker PostgreSQL

1. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   services:
     postgres:
       image: postgres:15
       environment:
         POSTGRES_DB: training_management_db
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: yourpassword
       ports:
         - "5432:5432"
       volumes:
         - postgres_data:/var/lib/postgresql/data
   
   volumes:
     postgres_data:
   ```

2. **Start PostgreSQL**
   ```bash
   docker-compose up -d
   ```

3. **Update Django settings** (same as Option 1, step 3)

4. **Run migrations** (same as Option 1, step 4)

### Option 3: Cloud PostgreSQL (Production)

Popular cloud providers:
- **AWS RDS**: Amazon Relational Database Service
- **Google Cloud SQL**: Google Cloud Platform
- **Azure Database**: Microsoft Azure
- **Heroku Postgres**: Heroku add-on
- **DigitalOcean Managed Databases**

For cloud setup:
1. Create PostgreSQL instance on your chosen provider
2. Get connection details (host, port, database name, username, password)
3. Update Django settings with cloud database credentials
4. Run migrations

## 🔧 Configuration Tips

### Security Best Practices
```python
# Use environment variables for sensitive data
import os
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='training_management_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
```

### Create .env file
```env
DB_NAME=training_management_db
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### Performance Settings
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'training_management_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'charset': 'utf8',
        },
        'CONN_MAX_AGE': 60,  # Connection pooling
    }
}
```

## ✅ Testing Connection

Create `test_connection.py`:
```python
import psycopg2
from psycopg2 import OperationalError

def test_connection():
    try:
        connection = psycopg2.connect(
            database="training_management_db",
            user="postgres",
            password="your_password",
            host="localhost",
            port="5432"
        )
        print("✅ PostgreSQL connection successful!")
        connection.close()
    except OperationalError as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
```

Run: `python test_connection.py`

## 🚨 Troubleshooting

### Common Issues

1. **Connection refused**
   - Check if PostgreSQL service is running
   - Verify host and port settings
   - Check firewall settings

2. **Authentication failed**
   - Verify username and password
   - Check pg_hba.conf configuration
   - Ensure user has database privileges

3. **Database does not exist**
   - Create the database using SQL commands above
   - Verify database name spelling

4. **psycopg2 installation issues**
   ```bash
   # Windows
   pip install psycopg2-binary
   
   # Linux/Mac
   pip install psycopg2
   ```

### Useful Commands

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Connect to PostgreSQL
psql -U postgres -h localhost

# List databases
\l

# Connect to specific database
\c training_management_db

# List tables
\dt

# Exit PostgreSQL
\q
```

## 📊 Migration Commands

```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Rollback migrations
python manage.py migrate app_name 0001

# Reset database (careful!)
python manage.py flush
```

## 🎯 Next Steps

After PostgreSQL setup:
1. ✅ Test database connection
2. ✅ Run all migrations
3. ✅ Create superuser account
4. ✅ Access admin panel
5. ✅ Start adding data through admin interface

Your training management system is now ready for production use with PostgreSQL! 🚀
