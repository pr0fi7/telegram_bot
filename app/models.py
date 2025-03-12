import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
import time 

load_dotenv()

class telegram_db:
    def __init__(self, conn_params):
        attempts = 5
        while attempts:
            try:
                self.conn = psycopg2.connect(**conn_params)
                break
            except psycopg2.OperationalError as e:
                attempts -= 1
                print("Postgres not ready, retrying in 5 seconds...")
                time.sleep(5)
        else:
            raise Exception("Could not connect to Postgres after multiple attempts")
        self._create_tables()
        
    def _create_tables(self):
        with self.conn.cursor() as cursor:
            # Run as a single transaction to avoid multiple workers executing it simultaneously
            self.conn.autocommit = True  
            try:
                cursor.execute('''
                    DO $$ 
                    BEGIN 
                        IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto') THEN
                            CREATE EXTENSION pgcrypto;
                        END IF;
                    END $$;
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS public.cvs (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        "createdAt" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        "person" TEXT,
                        "raw_text" TEXT,
                        "formatted_text" TEXT
                    );
                    CREATE TABLE IF NOT EXISTS public.predefined_questions (
                        question_order INTEGER NOT NULL PRIMARY KEY,
                        question_text TEXT NOT NULL
                    );
                ''')
            except Exception as e:
                print("Error creating tables:", e)
            finally:
                self.conn.autocommit = False  # Reset autocommit

    def get_predefined_questions(self):
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT question_text FROM public.predefined_questions ORDER BY question_order")
            rows = cursor.fetchall()
            return [row["question_text"] for row in rows]
        
    def insert_predefined_question(self, question_text, question_order):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO public.predefined_questions (question_text, question_order)
                VALUES (%s, %s)
            ''', (question_text, question_order))
        self.conn.commit()
    
    def get_predefined_question(self, order):
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT question_text FROM public.predefined_questions WHERE question_order = %s", (order,))
            row = cursor.fetchone()
            return row["question_text"] if row else None
    

    def update_predefined_question(self, question_text, question_order):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                UPDATE public.predefined_questions
                SET question_text = %s
                WHERE question_order = %s
            ''', (question_text, question_order))

    def delete_predefined_question(self, question_order):
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM public.predefined_questions WHERE question_order = %s", (question_order,))
        self.conn.commit()
        return cursor.rowcount > 0  # Return True if delete was successful

    def get_all(self):
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM public.cvs")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]  # Convert to JSON format
        
    def insert(self, person_name, raw_text=None, formatted_text=None):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO public.cvs (person, raw_text, formatted_text)
                VALUES (%s, %s, %s)
                RETURNING id;
            ''', (person_name, raw_text, formatted_text))
            new_id = cursor.fetchone()[0]
        self.conn.commit()
        return new_id

    def update(self, id, person_name, raw_text=None, formatted_text=None):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                UPDATE public.cvs
                SET person = %s, raw_text = %s, formatted_text = %s
                WHERE id = %s
            ''', (person_name, raw_text, formatted_text, id))
        self.conn.commit()
        return cursor.rowcount > 0  # Return True if update was successful

    def delete(self, id):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                DELETE FROM public.cvs WHERE id = %s
            ''', (id,))
        self.conn.commit()
        return cursor.rowcount > 0  # Return True if delete was successful
    
    def get_by_id(self, id):
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT * FROM public.cvs WHERE id = %s", (id,))
            row = cursor.fetchone()
            return dict(row) if row else None  # Convert to JSON format

db_params = {
    "dbname": os.getenv("POSTGRES_DB"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT")
}

print(db_params)

cvs_db = telegram_db(db_params)
