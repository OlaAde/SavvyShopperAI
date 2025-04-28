import psycopg2
import sqlite3
from typing import Dict, Any
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=30)


def get_all_listings(table_name):
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        port=int(os.getenv('POSTGRES_PORT'))
    )

    cur = conn.cursor()

    # Execute a query
    cur.execute(f"""SELECT * FROM {table_name};""")

    colnames = [desc[0] for desc in cur.description]

    # Fetch all the rows
    rows = cur.fetchall()
    result = [dict(zip(colnames, row)) for row in rows]

    # Close the cursor and connection
    cur.close()
    conn.close()

    return result

def get_listing(table_name, listing_id):
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        port=int(os.getenv('POSTGRES_PORT'))
    )

    cur = conn.cursor()

    # Execute a query
    cur.execute(f"""SELECT * FROM {table_name} WHERE id = {listing_id};""")

    colnames = [desc[0] for desc in cur.description]

    # Fetch all the rows
    rows = cur.fetchall()
    result = [dict(zip(colnames, row)) for row in rows]

    # Close the cursor and connection
    cur.close()
    conn.close()

    return result[0]

def get_cheapest_10_listings(table_name):
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        port=int(os.getenv('POSTGRES_PORT'))
    )

    cur = conn.cursor()

    # Execute a query
    cur.execute(f"""SELECT * FROM {table_name} order by CAST(fiyat AS INTEGER) ASC LIMIT 10;""")

    colnames = [desc[0] for desc in cur.description]

    # Fetch all the rows
    rows = cur.fetchall()
    result = [dict(zip(colnames, row)) for row in rows]

    # Close the cursor and connection
    cur.close()
    conn.close()

    return result

def get_top_10_listings_with_the_newest_years(table_name):
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        port=int(os.getenv('POSTGRES_PORT'))
    )

    cur = conn.cursor()

    # Execute a query
    cur.execute(f"""SELECT * FROM {table_name} order by CAST(yil AS INTEGER) DESC, CAST(fiyat AS INTEGER) ASC LIMIT 10;""")

    colnames = [desc[0] for desc in cur.description]

    # Fetch all the rows
    rows = cur.fetchall()
    result = [dict(zip(colnames, row)) for row in rows]

    # Close the cursor and connection
    cur.close()
    conn.close()

    return result


def get_least_used_10_listings(table_name):
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        port=int(os.getenv('POSTGRES_PORT'))
    )

    cur = conn.cursor()

    # Execute a query
    cur.execute(f"""SELECT * FROM {table_name} order by CAST(kilometre AS INTEGER) ASC, CAST(fiyat AS INTEGER) ASC LIMIT 10;""")

    colnames = [desc[0] for desc in cur.description]

    # Fetch all the rows
    rows = cur.fetchall()
    result = [dict(zip(colnames, row)) for row in rows]

    # Close the cursor and connection
    cur.close()
    conn.close()

    return result

# Veritabanı yöneticisi.
class DatabaseHandler:
    def __init__(self, db_type: str = "sqlite", table_name: str = None):
        """
        db_type: "sqlite" veya "postgres" olabilir.
        """
        
        self.db_type = db_type
        self.table_name = table_name
        self.conn = None
        self.cursor = None

        try:
            if db_type == "sqlite":
                db_path = os.getenv('SQLITE_DB_PATH')
                if not db_path:
                    raise ValueError("SQLITE_DB_PATH environment variable is not set")
                self.conn = sqlite3.connect(db_path)
            elif db_type == "postgres":
                self.conn = psycopg2.connect(
                    host=os.getenv('POSTGRES_HOST'),
                    dbname=os.getenv('POSTGRES_DB'),
                    user=os.getenv('POSTGRES_USER'),
                    password=os.getenv('POSTGRES_PASSWORD'),
                    port=int(os.getenv('POSTGRES_PORT'))
                )
            else:
                raise ValueError(f"Desteklenmeyen veri tabanı tipi: {db_type}")

            self.cursor = self.conn.cursor()
            self._create_table()
        except Exception as e:
            print(f"Database connection error: {e}")
            raise

    def _create_table(self):
        """
        Veritabanı için tablo oluşturur, eğer yeni bir veri eklenicekse buradan ekleyip yeniden tablo oluşturabilirsiniz.
        """
        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {self.table_name}(
            id SERIAL PRIMARY KEY,
            baslik VARCHAR(150),
            marka VARCHAR(30),
            model VARCHAR(100),
            motor VARCHAR(75),
            renk VARCHAR(20),
            yil VARCHAR(100),
            kilometre VARCHAR(100),
            fiyat VARCHAR(100),
            tarih VARCHAR(100),
            adres VARCHAR(100),
            resim_url VARCHAR(300),
            ilan_url VARCHAR(500)
        )
        """)

    def add_data(self, data: Dict[str, Any]):
        """
        Verileri veri tabanına kayıt eder, eğer eşleşen araç varsa o araç atlanır.
        """
        try:
            # Veri mevcut mu diye kontrol eder.
            query = f"""
                SELECT 1 FROM {self.table_name} 
                WHERE baslik=%s AND motor=%s AND adres=%s
            """ if self.db_type == "postgres" else f"""
                SELECT 1 FROM {self.table_name} 
                WHERE baslik=? AND motor=? AND adres=?
            """
            self.cursor.execute(query, (data['başlık'], data['motor'], data['adres']))

            if not self.cursor.fetchone():
                insert_query = f"""
                    INSERT INTO {self.table_name} 
                    (baslik, marka, model, motor, renk, yil, kilometre, fiyat, tarih, adres, resim_url, ilan_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """ if self.db_type == "postgres" else f"""
                    INSERT INTO {self.table_name} 
                    (baslik, marka, model, motor, renk, yil, kilometre, fiyat, tarih, adres, resim_url, ilan_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                self.cursor.execute(insert_query, (
                    data['başlık'], data['marka'], data['model'],
                    data['motor'], data['renk'], data['yil'],
                    data['kilometre'], data['fiyat'],
                    data['tarih'], data['adres'], data['resim_url'], data['ilan_url']
                ))
                self.conn.commit()
            else:
                print(f"Araç halihazırda kayıtlı: {data['başlık']}, {data['fiyat']}")
        except Exception as e:
                print(f"Hata: {e}")
                self.conn.rollback()

    def __del__(self):
        """
        Bağlantılar kapatılır.
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

## Veri tabanına veri eklemek için kullanılacak fonksiyon. Yapacağınız değişikleri DatabaseHandler içinde "add_data" fonksiyonu içinde yapmalısınız.
def veri_ekle(table_name, marka, motor, renk, ilan_model, yil, ilan_basligi,
             ilan_kilometre, ilan_fiyati, ilan_tarihi, ilan_sehir, resim_url, ilan_url):
    """
    Spesifik olarak dokunulmamasını tavsiye ederim fakat test için basit bir veri gönderebilirsiniz.
    """

    print("Veri ekleniyor...")

    db_type = os.getenv('DB_TYPE')
    db = DatabaseHandler(table_name=table_name, db_type=db_type)
    
    data = {
        'başlık': ilan_basligi,
        'marka': marka,
        'model': ilan_model,
        'motor': motor,
        'renk': renk,
        'yil': yil,
        'kilometre': ilan_kilometre,
        'fiyat': ilan_fiyati,
        'tarih': ilan_tarihi,
        'adres': ilan_sehir,
        'resim_url': resim_url,
        'ilan_url': ilan_url
    }
    
    db.add_data(data)

if __name__ == "__main__":
    print("Fonksiyonlar başarıyla içeri aktarıldı.")