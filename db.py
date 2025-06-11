import psycopg2
from datetime import datetime, timedelta

DB_HOST = "localhost"
DB_NAME = "suhrob"
DB_USER = "suhrob"
DB_PASSWORD = "123"

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def get_user(tablename, user_id):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(f"SELECT user_id, last_sent FROM {tablename} WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            if row:
                return {"user_id": row[0], "last_sent": row[1]}
            return None
    finally:
        conn.close()


def update_sent(tablename, user_id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {tablename} SET sent = true WHERE user_id = {user_id}")
        conn.commit()
    conn.close()

def get_active_admin_task():
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT id, channel_id, message_id, counts, tablename
                    FROM admins
                    WHERE status = TRUE
                        LIMIT 1
                    """)
        row = cur.fetchone()
    conn.close()
    return row  # None if no task

def get_users_to_send(tablename, count):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(f"""
                    SELECT user_id
                    FROM {tablename} WHERE sent = FALSE
                    ORDER BY last_sent ASC NULLS FIRST
                        LIMIT {count}
                    """)
        rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]

def deactivate_admin_task(tablename):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(f"UPDATE admins SET status = FALSE WHERE tablename = '{tablename}'")
        conn.commit()
    conn.close()

def update_last_sent(tablename, user_id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {tablename} SET last_sent = NOW() WHERE user_id = {user_id}")
        conn.commit()
    conn.close()

def insert_user(tablename, user_id):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(f"INSERT INTO {tablename} (user_id, saved_at, last_sent) VALUES ({user_id}, NOW(), NOW())")
        conn.commit()
    conn.close()

def get_inactive_users(tablename, days, count):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cutoff_date = datetime.now() - timedelta(days=days)
            cur.execute(
                f"""
                SELECT user_id FROM {tablename}
                WHERE last_sent < '{cutoff_date}' AND reminder_count = {count}
                """
            )
            rows = cur.fetchall()
            return [row[0] for row in rows]
    finally:
        conn.close()

def get_layal_users(tablename, days, count):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cutoff_date = datetime.now() - timedelta(days=days)
            cur.execute(
                f"""
                SELECT user_id FROM {tablename}
                WHERE saved_at < '{cutoff_date}' AND reminder_count = {count}
                """
            )
            rows = cur.fetchall()
            return [row[0] for row in rows]
    finally:
        conn.close()

def update_reminder(tablename, user_id, count):
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {tablename} SET reminder_count = {count} WHERE user_id = {user_id}")
        conn.commit()
    conn.close()

