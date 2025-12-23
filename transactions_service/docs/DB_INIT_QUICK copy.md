# 📊 Database Initialization - Quick Reference

## 🚀 Quick Start

### Option 1: Automatic (Python)
```bash
cd transactions_service
python init_database.py
```

### Option 2: Manual (SQL)
```bash
psql -U gdb_user -d gdb_transactions_db -f transactions_init.sql
```

---

## 📋 What Gets Created

### 4 Tables:
1. **transactions** - All withdrawal, deposit, transfer records
2. **daily_transfer_limits** - Daily tracking per account
3. **transaction_logs** - Complete audit trail
4. **transfer_rules** - Privilege-based limits

### 3 Default Rules:
| Privilege | Daily Limit | Daily Transactions |
|-----------|------------|-------------------|
| PREMIUM   | ₹100,000   | 50                |
| GOLD      | ₹50,000    | 30                |
| SILVER    | ₹25,000    | 20                |

### Multiple Indexes:
- Optimized for account lookups
- Fast date-based queries
- Efficient filtering by status

---

## 📁 Files Created

### `init_database.py`
- Python script for database initialization
- Usage: `python init_database.py`
- Reset: `python init_database.py reset`

### `transactions_init.sql`
- SQL script for manual setup
- Usage: `psql ... -f transactions_init.sql`
- Can be run multiple times safely

### `DATABASE_SETUP.md`
- Complete setup guide
- Troubleshooting section
- Sample SQL queries

---

## ✅ Verification

### Check tables exist:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name LIKE '%transaction%' OR table_name LIKE '%daily%' OR table_name LIKE '%transfer%';
```

### Check rules inserted:
```sql
SELECT * FROM transfer_rules;
```

### Check indexes created:
```sql
SELECT indexname FROM pg_indexes WHERE schemaname = 'public';
```

---

## 🔧 Environment Setup

Make sure `.env` has:
```env
DATABASE_URL=postgresql://gdb_user:gdb_password@localhost:5432/gdb_transactions_db
```

---

## ⚡ Performance

All tables have:
- ✅ Primary keys
- ✅ Foreign key constraints
- ✅ Check constraints
- ✅ Unique constraints
- ✅ Optimized indexes
- ✅ Automatic timestamps

---

## 🛡️ Safety Features

- **Idempotent**: Safe to run multiple times
- **Cascade deletes**: Logs auto-delete with transactions
- **Constraints**: Prevent invalid data entry
- **Unique keys**: Prevent duplicate transactions

---

## 📞 Quick Commands

| Task | Command |
|------|---------|
| Initialize | `python init_database.py` |
| Reset DB | `python init_database.py reset` |
| Run SQL script | `psql ... -f transactions_init.sql` |
| List tables | `psql ... -c "\dt"` |
| Check rules | `psql ... -c "SELECT * FROM transfer_rules;"` |

---

**Ready to use!** 🎉

For detailed information, see `DATABASE_SETUP.md`
