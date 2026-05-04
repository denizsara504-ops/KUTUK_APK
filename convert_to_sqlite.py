"""
MySQL → SQLite Dönüştürücü
PC'de çalıştırın, oluşan kutuk.db dosyasını tablete USB ile kopyalayın.

Kullanım:
    python convert_to_sqlite.py

Çıktı:
    kutuk.db  (SQLite veritabanı - tablete kopyalayın)
"""

import sqlite3
import sys
import time
from pathlib import Path

# ── MySQL bağlantı ayarları (avg_full.py ile aynı) ───────────────────────────
MYSQL_HOST   = "127.0.0.1"
MYSQL_PORT   = 3366        # avg_full.py'deki DB_PORT
MYSQL_USER   = "root"
MYSQL_PASS   = ""
MYSQL_DB     = "kutuk"
MYSQL_TABLE  = "secmen"

# Çıktı dosyası
OUTPUT_DB    = Path(__file__).parent / "kutuk.db"

# Kaç satırda bir commit (bellek için)
BATCH_SIZE   = 50_000

def format_sure(sn):
    if sn < 60:    return f"{sn:.0f} saniye"
    elif sn < 3600: return f"{sn/60:.0f} dakika"
    else:           return f"{sn/3600:.1f} saat"

def format_boyut(path):
    b = Path(path).stat().st_size
    if b < 1024**2:  return f"{b/1024:.0f} KB"
    elif b < 1024**3: return f"{b/1024**2:.0f} MB"
    return f"{b/1024**3:.2f} GB"

def main():
    print("=" * 55)
    print("  MySQL → SQLite Dönüştürücü")
    print("  Kütük Sorgulama - Android için")
    print("=" * 55)
    print()

    # PyMySQL var mı?
    try:
        import pymysql
    except ImportError:
        print("HATA: pymysql yüklü değil!")
        print("  pip install pymysql")
        sys.exit(1)

    # MySQL bağlan
    print(f"MySQL'e bağlanılıyor ({MYSQL_HOST}:{MYSQL_PORT})...")
    try:
        mysql_conn = pymysql.connect(
            host=MYSQL_HOST, port=MYSQL_PORT,
            user=MYSQL_USER, password=MYSQL_PASS,
            database=MYSQL_DB, charset='utf8',
            connect_timeout=5
        )
        print("✅ MySQL bağlantısı başarılı")
    except Exception as e:
        print(f"❌ MySQL bağlantı hatası: {e}")
        print()
        print("Not: Bu scripti çalıştırmadan önce")
        print("     Kütük Sorgulama programını AÇIN")
        print("     (MySQL servisi o programa bağlı)")
        sys.exit(1)

    # Toplam kayıt sayısı
    with mysql_conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) FROM {MYSQL_TABLE}")
        toplam = cur.fetchone()[0]
    print(f"📊 Toplam kayıt: {toplam:,}")
    print()

    # SQLite oluştur
    if OUTPUT_DB.exists():
        print(f"⚠️  {OUTPUT_DB} zaten var — üzerine yazılacak!")
        cevap = input("Devam? (E/H): ").strip().upper()
        if cevap != 'E':
            print("İptal.")
            sys.exit(0)
        OUTPUT_DB.unlink()

    print(f"SQLite oluşturuluyor: {OUTPUT_DB}")
    sqlite_conn = sqlite3.connect(str(OUTPUT_DB))
    sqlite_conn.execute("PRAGMA journal_mode=WAL")
    sqlite_conn.execute("PRAGMA synchronous=OFF")   # Dönüşüm hızı için
    sqlite_conn.execute("PRAGMA cache_size=200000")
    sqlite_conn.execute("PRAGMA temp_store=memory")
    sqlite_conn.execute("PRAGMA page_size=4096")

    # Tablo oluştur
    sqlite_conn.execute("""
        CREATE TABLE secmen (
            tc          TEXT PRIMARY KEY,
            ad          TEXT,
            soyad       TEXT,
            anaadi      TEXT,
            babaadi     TEXT,
            dogumyeri   TEXT,
            dogumtarihi TEXT,
            cinsiyet    TEXT,
            nufusil     TEXT,
            nufusilce   TEXT,
            adresil     TEXT,
            adresilce   TEXT,
            mahalle     TEXT,
            cadde       TEXT,
            kapino      TEXT,
            daireno     TEXT
        )
    """)
    sqlite_conn.execute("""
        CREATE TABLE notlar (
            tc    TEXT PRIMARY KEY,
            metin TEXT,
            tarih TEXT DEFAULT (datetime('now'))
        )
    """)
    sqlite_conn.commit()

    # Veri aktar
    print()
    print("Veri aktarımı başlıyor...")
    print("-" * 55)

    # MySQL kolon mapping - gerçek tablo kolonlarını al
    with mysql_conn.cursor() as cur:
        cur.execute(f"DESCRIBE {MYSQL_TABLE}")
        kolonlar = [row[0].lower() for row in cur.fetchall()]
    print(f"MySQL kolonları: {', '.join(kolonlar[:6])}...")

    # Kolon eşleşmesi
    KOLON_MAP = {
        'tc': 'tc', 'no': 'tc', 'tcno': 'tc', 'kimlikno': 'tc',
        'ad': 'ad', 'isim': 'ad', 'adi': 'ad',
        'soyad': 'soyad', 'soyisim': 'soyad', 'soyadi': 'soyad',
        'anaadi': 'anaadi', 'anneadi': 'anaadi', 'anne': 'anaadi',
        'babaadi': 'babaadi', 'baba': 'babaadi',
        'dogumyeri': 'dogumyeri', 'dogumyeri': 'dogumyeri',
        'dogumtarihi': 'dogumtarihi', 'dt': 'dogumtarihi',
        'cinsiyet': 'cinsiyet', 'cns': 'cinsiyet',
        'nufusil': 'nufusil', 'nufusili': 'nufusil',
        'nufusilce': 'nufusilce', 'nufusilcesi': 'nufusilce',
        'adresil': 'adresil', 'adresili': 'adresil',
        'adresilce': 'adresilce', 'adresilcesi': 'adresilce',
        'mahalle': 'mahalle',
        'cadde': 'cadde', 'sokak': 'cadde', 'caddesokak': 'cadde',
        'kapino': 'kapino', 'kapinumarasi': 'kapino',
        'daireno': 'daireno', 'daire': 'daireno',
    }

    # Hedef kolonların MySQL'deki karşılıkları
    hedef_kolonlar = ['tc','ad','soyad','anaadi','babaadi','dogumyeri',
                      'dogumtarihi','cinsiyet','nufusil','nufusilce',
                      'adresil','adresilce','mahalle','cadde','kapino','daireno']

    # MySQL kolon indeksleri
    kolon_indeksleri = {}
    for hedef in hedef_kolonlar:
        for i, k in enumerate(kolonlar):
            if KOLON_MAP.get(k,'') == hedef or k == hedef:
                kolon_indeksleri[hedef] = i
                break

    print(f"Eşleşen kolonlar: {list(kolon_indeksleri.keys())}")
    print()

    offset = 0
    toplam_eklenen = 0
    t_baslangic = time.time()
    t_son = t_baslangic

    while True:
        with mysql_conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {MYSQL_TABLE} LIMIT {BATCH_SIZE} OFFSET {offset}"
            )
            satirlar = cur.fetchall()

        if not satirlar:
            break

        # SQLite'a yaz
        sqlite_conn.execute("BEGIN")
        for satir in satirlar:
            deger = tuple(
                str(satir[kolon_indeksleri.get(k, -1)] or '').strip()
                if kolon_indeksleri.get(k, -1) >= 0 and kolon_indeksleri.get(k, -1) < len(satir)
                else ''
                for k in hedef_kolonlar
            )
            try:
                sqlite_conn.execute(
                    "INSERT OR IGNORE INTO secmen VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    deger
                )
                toplam_eklenen += 1
            except Exception:
                pass
        sqlite_conn.execute("COMMIT")

        offset += BATCH_SIZE
        simdi = time.time()
        gecen = simdi - t_baslangic
        hiz = toplam_eklenen / max(gecen, 0.1)
        kalan = max(0, toplam - toplam_eklenen)
        kalan_sure = kalan / max(hiz, 1)
        yuzde = min(100, toplam_eklenen / max(toplam, 1) * 100)

        print(f"  {toplam_eklenen:>12,} / {toplam:>12,}  "
              f"({yuzde:5.1f}%)  "
              f"⚡ {hiz/1000:.0f}K/sn  "
              f"⏱ Kalan: {format_sure(kalan_sure)}", end='\r')

    print()
    print()

    # İndeksleri oluştur (en son - dönüşüm hızlı olsun)
    print("İndeksler oluşturuluyor...")
    sqlite_conn.execute("PRAGMA synchronous=NORMAL")
    sqlite_conn.execute("CREATE INDEX IF NOT EXISTS idx_ad_soyad ON secmen(ad, soyad)")
    sqlite_conn.execute("CREATE INDEX IF NOT EXISTS idx_soyad    ON secmen(soyad)")
    sqlite_conn.execute("CREATE INDEX IF NOT EXISTS idx_nufusil  ON secmen(nufusil, nufusilce)")
    sqlite_conn.execute("CREATE INDEX IF NOT EXISTS idx_adresil  ON secmen(adresil, adresilce)")
    sqlite_conn.commit()
    print("✅ İndeksler hazır")

    # VACUUM - dosyayı optimize et
    print("Veritabanı optimize ediliyor...")
    sqlite_conn.execute("VACUUM")
    sqlite_conn.commit()

    sqlite_conn.close()
    mysql_conn.close()

    toplam_sure = time.time() - t_baslangic
    print()
    print("=" * 55)
    print(f"  ✅ DÖNÜŞÜM TAMAMLANDI!")
    print(f"  📊 Aktarılan kayıt : {toplam_eklenen:,}")
    print(f"  ⏱  Geçen süre      : {format_sure(toplam_sure)}")
    print(f"  📦 Dosya boyutu    : {format_boyut(OUTPUT_DB)}")
    print(f"  📁 Konum           : {OUTPUT_DB}")
    print("=" * 55)
    print()
    print("SONRAKİ ADIM:")
    print(f"  kutuk.db dosyasını USB ile tabletteki")
    print(f"  'KutukSorgulama' klasörüne kopyalayın.")
    print()


if __name__ == '__main__':
    main()
