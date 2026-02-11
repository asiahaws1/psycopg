import psycopg2
import os

def get_connection():
    db = os.environ.get("DATABASE_NAME")
    return psycopg2.connect(f"dbname={db}")

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Companies (
      company_id SERIAL PRIMARY KEY,
      company_name VARCHAR UNIQUE NOT NULL,
      active BOOLEAN
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Categories (
      category_id SERIAL PRIMARY KEY,
      category_name VARCHAR UNIQUE NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products (
      product_id SERIAL PRIMARY KEY,
      product_name VARCHAR UNIQUE NOT NULL,
      company_id INTEGER,
      description VARCHAR,
      price FLOAT,
      active BOOLEAN,
      FOREIGN KEY (company_id)
        REFERENCES Companies (company_id)
        ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Warranties (
      warranty_id SERIAL PRIMARY KEY,
      warranty_months INTEGER NOT NULL,
      product_id INTEGER,
      FOREIGN KEY (product_id)
        REFERENCES Products (product_id)
        ON DELETE CASCADE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ProductsCategoriesXref (
        product_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        PRIMARY KEY (product_id, category_id),
        FOREIGN KEY (product_id) 
            REFERENCES Products(product_id) 
            ON DELETE CASCADE,
        FOREIGN KEY (category_id) 
            REFERENCES Categories(category_id) 
            ON DELETE CASCADE
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()
    

