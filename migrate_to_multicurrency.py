#!/usr/bin/env python3
"""
Database migration script to update from Bitcoin-only to multi-currency schema.

This script will:
1. Add currency columns to wallets and transactions tables
2. Set all existing wallets and transactions to BTC
3. Rename btc_amount columns to amount
4. Update the transaction stats table

Usage: python migrate_to_multicurrency.py [database_path]
"""

import sqlite3
import sys
import os
from datetime import datetime


def backup_database(db_path):
    """Create a backup of the database before migration"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"Creating backup at: {backup_path}")
    
    with sqlite3.connect(db_path) as source:
        with sqlite3.connect(backup_path) as backup:
            source.backup(backup)
    
    return backup_path


def migrate_wallets_table(conn):
    """Migrate the wallets table to support multiple currencies"""
    cursor = conn.cursor()
    
    print("Migrating wallets table...")
    
    # Check if migration is needed
    cursor.execute("PRAGMA table_info(wallets)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'currency' in columns and 'amount' in columns:
        print("Wallets table already migrated, skipping...")
        return
    
    # Create new wallets table with updated schema
    cursor.execute("""
        CREATE TABLE wallets_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            public_key VARCHAR NOT NULL,
            amount FLOAT NOT NULL,
            currency VARCHAR NOT NULL,
            create_date_utc DATE NOT NULL,
            api_key VARCHAR NOT NULL,
            FOREIGN KEY(api_key) REFERENCES users (api_key)
        )
    """)
    
    # Copy data from old table, setting currency to BTC
    if 'btc_amount' in columns:
        cursor.execute("""
            INSERT INTO wallets_new (id, public_key, amount, currency, create_date_utc, api_key)
            SELECT id, public_key, btc_amount, 'BTC', create_date_utc, api_key
            FROM wallets
        """)
    else:
        cursor.execute("""
            INSERT INTO wallets_new (id, public_key, amount, currency, create_date_utc, api_key)
            SELECT id, public_key, amount, 'BTC', create_date_utc, api_key
            FROM wallets
        """)
    
    # Drop old table and rename new one
    cursor.execute("DROP TABLE wallets")
    cursor.execute("ALTER TABLE wallets_new RENAME TO wallets")
    
    print("Wallets table migrated successfully!")


def migrate_transactions_table(conn):
    """Migrate the transactions table to support multiple currencies"""
    cursor = conn.cursor()
    
    print("Migrating transactions table...")
    
    # Check if migration is needed
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'currency' in columns and 'amount' in columns:
        print("Transactions table already migrated, skipping...")
        return
    
    # Create new transactions table with updated schema
    cursor.execute("""
        CREATE TABLE transactions_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            src_api_key VARCHAR NOT NULL,
            src_public_key VARCHAR NOT NULL,
            dst_public_key VARCHAR NOT NULL,
            amount FLOAT NOT NULL,
            currency VARCHAR NOT NULL,
            commission FLOAT NOT NULL,
            create_date_utc DATE NOT NULL,
            FOREIGN KEY(src_api_key) REFERENCES users (api_key),
            FOREIGN KEY(src_public_key) REFERENCES wallets (public_key),
            FOREIGN KEY(dst_public_key) REFERENCES wallets (public_key)
        )
    """)
    
    # Copy data from old table, setting currency to BTC
    if 'btc_amount' in columns:
        cursor.execute("""
            INSERT INTO transactions_new (id, src_api_key, src_public_key, dst_public_key, amount, currency, commission, create_date_utc)
            SELECT id, src_api_key, src_public_key, dst_public_key, btc_amount, 'BTC', commission, create_date_utc
            FROM transactions
        """)
    else:
        cursor.execute("""
            INSERT INTO transactions_new (id, src_api_key, src_public_key, dst_public_key, amount, currency, commission, create_date_utc)
            SELECT id, src_api_key, src_public_key, dst_public_key, amount, 'BTC', commission, create_date_utc
            FROM transactions
        """)
    
    # Drop old table and rename new one
    cursor.execute("DROP TABLE transactions")
    cursor.execute("ALTER TABLE transactions_new RENAME TO transactions")
    
    print("Transactions table migrated successfully!")


def migrate_transaction_stats_table(conn):
    """Migrate the transaction_stats table to support multiple currencies"""
    cursor = conn.cursor()
    
    print("Migrating transaction_stats table...")
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transaction_stats'")
    if not cursor.fetchone():
        print("Transaction_stats table doesn't exist, creating new one...")
        cursor.execute("""
            CREATE TABLE transaction_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                commission_sum FLOAT NOT NULL,
                currency VARCHAR NOT NULL,
                total_transactions INTEGER NOT NULL,
                stat_date_utc DATE NOT NULL
            )
        """)
        return
    
    # Check if migration is needed
    cursor.execute("PRAGMA table_info(transaction_stats)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'currency' in columns and 'commission_sum' in columns:
        print("Transaction_stats table already migrated, skipping...")
        return
    
    # Create new transaction_stats table with updated schema
    cursor.execute("""
        CREATE TABLE transaction_stats_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            commission_sum FLOAT NOT NULL,
            currency VARCHAR NOT NULL,
            total_transactions INTEGER NOT NULL,
            stat_date_utc DATE NOT NULL
        )
    """)
    
    # Copy data from old table, setting currency to BTC
    if 'commission_sum_btc' in columns:
        cursor.execute("""
            INSERT INTO transaction_stats_new (id, commission_sum, currency, total_transactions, stat_date_utc)
            SELECT id, commission_sum_btc, 'BTC', total_transactions, stat_date_utc
            FROM transaction_stats
        """)
    else:
        cursor.execute("""
            INSERT INTO transaction_stats_new (id, commission_sum, currency, total_transactions, stat_date_utc)
            SELECT id, commission_sum, 'BTC', total_transactions, stat_date_utc
            FROM transaction_stats
        """)
    
    # Drop old table and rename new one
    cursor.execute("DROP TABLE transaction_stats")
    cursor.execute("ALTER TABLE transaction_stats_new RENAME TO transaction_stats")
    
    print("Transaction_stats table migrated successfully!")


def main():
    if len(sys.argv) < 2:
        db_path = "identifier.sqlite"
        if not os.path.exists(db_path):
            print(f"Error: Database file '{db_path}' not found!")
            print("Usage: python migrate_to_multicurrency.py [database_path]")
            sys.exit(1)
    else:
        db_path = sys.argv[1]
        if not os.path.exists(db_path):
            print(f"Error: Database file '{db_path}' not found!")
            sys.exit(1)
    
    print(f"Starting migration of database: {db_path}")
    
    # Create backup
    backup_path = backup_database(db_path)
    print(f"Backup created successfully!")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        
        # Run migrations
        migrate_wallets_table(conn)
        migrate_transactions_table(conn)
        migrate_transaction_stats_table(conn)
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("\nMigration completed successfully!")
        print(f"Original database backed up to: {backup_path}")
        
    except Exception as e:
        print(f"\nError during migration: {str(e)}")
        print(f"Database backup available at: {backup_path}")
        print("Please restore from backup if needed.")
        sys.exit(1)


if __name__ == "__main__":
    main()