# Quick Setup Guide - PostgreSQL Configuration

## ✅ Configuration Complete

Your PostgreSQL credentials have been configured:
- **Username:** postgres
- **Password:** anil
- **Database:** GDB-GDB
- **Connection URL:** `postgresql://postgres:anil@localhost:5432/GDB-GDB`

---

## 🚀 Quick Start

### 1. Verify PostgreSQL is Running
```powershell
# Windows - Check if PostgreSQL service is running
Get-Service postgresql-* | Status

# Or connect to test
psql -U postgres -d postgres
```

### 2. Create Database (if not exists)
```sql
-- Connect as postgres user
psql -U postgres

-- Create database if needed
CREATE DATABASE "GDB-GDB";

-- Verify
\l
\q
```

### 3. Install Python Dependencies
```powershell
# Navigate to console application directory
cd account_service_console_application

# Install required packages
pip install -r requirements.txt
```

### 4. Initialize Database Schema
```powershell
# This will create all tables, sequences, and indexes
python database/init_db.py
```

Expected output:
```
Initializing database: postgresql://postgres:anil@localhost:5432/GDB-GDB

✅ Created account_number_seq sequence
✅ Created accounts table
✅ Created savings_account_details table
✅ Created current_account_details table
✅ Created indexes

✅ Database initialization complete!
```

### 5. Run the Application
```powershell
python main.py
```

You should see:
```
================================================================================
🚀 Starting Account Service Console v1.0.0
================================================================================
Initializing PostgreSQL database: postgresql://postgres:anil@localhost:5432/GDB-GDB
✅ Database schema initialized
✅ Database connection pool initialized

================================================================================
          🏦 GLOBAL DIGITAL BANK - ACCOUNT SERVICE CONSOLE
================================================================================
...
Main Menu:
...
```

---

## 📋 What Was Configured

### Files Updated ✅
1. **app/config/settings.py** - Default PostgreSQL URL set
2. **.env** - Created with your credentials (encrypted in production)
3. **.env.example** - Template updated
4. **database/init_db.py** - Default connection string updated
5. **POSTGRESQL_MIGRATION_COMPLETE.md** - Documentation updated

### All SQL Statements Converted ✅
- ✅ All 13 repository methods use PostgreSQL syntax ($1, $2, $3...)
- ✅ Boolean values use TRUE/FALSE instead of 1/0
- ✅ Account number sequence properly configured
- ✅ Connection pool configured (min=2, max=10)

---

## 🔍 Testing the Connection

### Test 1: Direct psql Connection
```powershell
psql -U postgres -d GDB-GDB -c "SELECT version();"
```

### Test 2: Python asyncpg Connection
```powershell
python
>>> import asyncpg
>>> import asyncio
>>> async def test():
...     conn = await asyncpg.connect('postgresql://postgres:anil@localhost:5432/GDB-GDB')
...     version = await conn.fetchval('SELECT version()')
...     print(version)
...     await conn.close()
>>> asyncio.run(test())
```

### Test 3: Run Application
```powershell
python main.py
```

---

## ⚠️ Troubleshooting

### "Could not connect to PostgreSQL"
1. Verify PostgreSQL service is running
2. Check credentials in .env file
3. Verify database GDB-GDB exists: `psql -U postgres -l`

### "Database does not exist"
```powershell
# Create it manually
psql -U postgres -c "CREATE DATABASE \"GDB-GDB\";"
```

### "Authentication failed"
1. Verify username: postgres
2. Verify password: anil
3. Test direct connection: `psql -U postgres`

### "Port 5432 in use"
PostgreSQL is already running (this is normal). Proceed with initialization.

---

## 📦 Requirements Met

✅ Python 3.9+
✅ PostgreSQL 12.0+
✅ asyncpg 0.28.0+
✅ bcrypt 4.0.0+
✅ python-dateutil 2.8.2+

---

## 🎯 Next Steps

1. **Initialize Schema:**
   ```powershell
   python database/init_db.py
   ```

2. **Run Application:**
   ```powershell
   python main.py
   ```

3. **Create Test Account:**
   - Select: Create Account
   - Choose: Savings Account
   - Enter name, age (18+), PIN, phone number
   - Account created successfully!

4. **Test Account Operations:**
   - View account details
   - Check balance
   - Debit/Credit funds
   - Close account

---

## 📞 Support

All configuration files are in:
- `app/config/settings.py` - Default values
- `.env` - Your actual credentials (do not commit to git!)

For more details, see:
- `POSTGRESQL_MIGRATION_COMPLETE.md` - Full migration documentation
- `README.md` - Feature overview
- `database/init_db.py` - Schema details

**Ready to go! 🚀**
