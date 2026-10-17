"""ARAÇLAR ve AJAN DÖNGÜSÜ. Defter, eğitim verisi üretimi ve site aynı dosyayı kullanır."""
import csv                                        # Tablo dosyasını okumak için.
import json                                       # Ajan protokolü JSON'dur.
import re                                         # Hesap ifadesini denetlemek için.
from proje import KIMLIK, KURUM, ISARET, TABLO, TABLO_ANAHTAR, TABLO_ARACI, TABLO_ACIKLAMA   # Kart.

# Rehber arama fonksiyonu: defter Chroma'yı, site TF-IDF'i buraya bağlar.
ARA = None


def kucuk(metin):                                 # Türkçe küçük harf: "İ" → "i", "I" → "ı".
    """Türkçe harflere uygun küçük harfe çevirir (karşılaştırma için)."""
    return str(metin).replace("İ", "i").replace("I", "ı").lower().strip()   # Sonra Python'un lower'ı.


def rehberde_ara(soru):                           # Araç 1: rehber araması (RAG'ın araç hâli).
    """Rehberde soruya en yakın 3 bölümü döndürür."""
    if ARA is None:                               # Arama henüz bağlanmadıysa
        return "Rehber araması hazır değil."      #   çökme yerine metin döndür.
    return "\n\n".join(ARA(soru, 3))              # 3 parça, aralarında boş satır.


with open(TABLO, encoding="utf-8") as f:          # Paketin tablosu:
    SATIRLAR = list(csv.DictReader(f))            #   her satır bir sözlük {sütun: değer}.


def tablo_ara(deger):                             # Araç 2: tablodan kesin bilgi (benzerlik değil).
    """Anahtar sütununda değeri içeren satırları (en fazla 5) 'sütun: değer' biçiminde döndürür."""
    aranan = str(deger).casefold().strip()
    exact = [r for r in SATIRLAR if any(aranan == str(r.get(k, '')).casefold() for k in ('ders_kodu','ders_adi','ders_adi_en'))]
    bulunan = exact or [r for r in SATIRLAR if aranan and any(aranan in str(r.get(k, '')).casefold() for k in ('ders_kodu','ders_adi','ders_adi_en'))]
    if not bulunan:                               # Hiç yoksa hata değil metin: model uydurmasın.
        return f"'{deger}' için kayıt bulunamadı."   # Bulunamadı mesajı.
    return "\n".join("; ".join(f"{k}: {v}" for k, v in s.items())   # Her satır: "sütun: değer; …",
                     for s in bulunan[:5])        #   en fazla 5 satır.


def hesapla(ifade):                               # Araç 3: hesap makinesi (model hesapta hata yapar).
    """Yalnızca rakam ve dört işlem içeren ifadeyi hesaplar."""
    if len(str(ifade)) > 200 or "**" in str(ifade) or "//" in str(ifade):
        return "Geçersiz ifade / Invalid expression."
    if not re.fullmatch(r"[\d\s+\-*/().]+", str(ifade)):   # eval tehlikelidir: yalnızca rakam ve işaret.
        return "Geçersiz ifade."                  # Reddet.
    try:                                          # Sıfıra bölme gibi hatalar:
        sonuc = eval(str(ifade), {"__builtins__": {}}, {})                  #   Python hesaplar,
    except Exception:                             #   olmazsa
        return "Hesaplanamadı."                   #   metin döndür.
    return str(int(sonuc)) if float(sonuc).is_integer() else str(round(sonuc, 2))   # 840.0 → "840".


"""One-parameter tool; all outcomes return a string."""
import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
KATSAYILAR = {'AA': '4', 'BA': '3.5', 'BB': '3', 'CB': '2.5', 'CC': '2', 'DC': '1.5', 'DD': '1', 'FD': '0.5', 'FF': '0'}
def not_ortalamasi(veri):
    """JSON: {"lang":"tr|en", "dersler":[{"not":"AA", "akts":6}, ...]}."""
    lang = 'tr'
    try:
        data = json.loads(veri) if isinstance(veri, str) else veri
        if not isinstance(data, dict): raise ValueError('object required')
        lang = data.get('lang', 'tr')
        if lang not in ('tr', 'en'): raise ValueError('language')
        courses = data['dersler']
        if not isinstance(courses, list) or not courses: raise ValueError('courses')
        total, weighted = Decimal(0), Decimal(0)
        for row in courses:
            grade = row['not'].strip().upper()
            if grade not in KATSAYILAR or isinstance(row['akts'], bool): raise ValueError('grade or credits')
            credits = Decimal(str(row['akts']))
            if not credits.is_finite() or credits <= 0: raise ValueError('credits')
            total += credits
            weighted += Decimal(KATSAYILAR[grade]) * credits
        result = (weighted / total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if lang == 'en':
            return f'ECTS-weighted average for the supplied courses: {result}/4.00. Total ECTS: {total}. This is not an official cumulative GPA.'
        return f'Girilen derslerin AKTS ağırlıklı ortalaması: {result}/4.00. Toplam AKTS: {total}. Bu sonuç resmî GNO değildir.'
    except (ValueError, TypeError, KeyError, AttributeError, InvalidOperation, OverflowError):
        return ('Invalid input: supply a nonempty course list, valid letter grades (AA–FF), and positive finite ECTS values.' if lang == 'en' else 'Geçersiz girdi: boş olmayan ders listesi, geçerli harf notları (AA–FF) ve pozitif sonlu AKTS değerleri girin.')
OZEL_ARAC = {
    'ad': 'not_ortalamasi', 'param': 'veri', 'fonk': not_ortalamasi,
    'aciklama': 'Verilen derslerin AKTS ağırlıklı 4 üzerinden ortalamasını hesaplar. Computes an ECTS-weighted average. Input is JSON with lang and dersler (not, akts).',
    'tema': 'Türkçe veya İngilizce harf notları ve AKTS değerleri vererek ağırlıklı ortalama hesaplamayı isteyen öğrenci mesajları / Turkish or English requests to calculate a weighted average from letter grades and ECTS.'
}


# Araç listesi: ad, parametre, açıklama (model görür), tema (veri üretimi), fonksiyon.
ARACLAR = [
    {"ad": "rehberde_ara", "param": "soru", "fonk": rehberde_ara,             # Araç 1.
     "aciklama": f"{KURUM} rehberinde arama yapar. Soruyu tam cümle olarak yaz.",
     "tema": "rehberdeki kurallar, ücretler, süreler ve prosedürler hakkında sorular"},
    {"ad": TABLO_ARACI, "param": TABLO_ANAHTAR, "fonk": tablo_ara,            # Araç 2 (adı karttan).
     "aciklama": TABLO_ACIKLAMA,
     "tema": (f"tablodaki belirli bir kayıt hakkında sorular; '{TABLO_ANAHTAR}' değerleri yalnızca "
              "şunlar: " + ", ".join(s[TABLO_ANAHTAR] for s in SATIRLAR))},  # Geçerli anahtarlar.
    {"ad": "hesapla", "param": "ifade", "fonk": hesapla,                      # Araç 3.
     "aciklama": 'Aritmetik ifadeyi hesaplar, örn. "22 - 9".',
     "tema": "hesap gerektiren sorular (toplam, fark, çarpım, indirim); argüman '22 - 9' gibi"},
    OZEL_ARAC,
]
FONK = {a["ad"]: a["fonk"] for a in ARACLAR}      # ad → fonksiyon (döngü için).
ARAC_LISTESI = "\n".join(f"- {a['ad']}({a['param']}: str): {a['aciklama']}" for a in ARACLAR)   # Metin.
# Ajan system mesajı: kimlik + araçlar + JSON protokolü + kurallar.
AJAN_SISTEM = f"""{KIMLIK}
Soruları araçlarla çözersin. Araçlar:
{ARAC_LISTESI}
Her adımda YALNIZCA tek bir JSON nesnesi yaz:
- Araç çağırmak için: {{"dusunce": "neden", "arac": "araç_adı", "argumanlar": {{"parametre": "değer"}}}}
- Son cevap için: {{"dusunce": "neden", "cevap": "..."}}
Kurallar: Rehberdeki kuralları ve tablodaki bilgileri bilmezsin; araçla öğren, uydurma.
Aritmetik için hesapla, ağırlıklı not ortalaması için not_ortalamasi kullan. For arithmetic use hesapla; for weighted grade averages use not_ortalamasi. User-facing final answers must follow the question language. Keep the JSON key names unchanged. Tek seferde tek araç çağır."""


# sor: mesaj listesi alıp metin döndüren model fonksiyonu (defterde transformers, sitede llama.cpp).
def ajan(soru, sor, maks_adim=4):
    """ReAct döngüsü: düşün → araç → gözlem → cevap. (cevap, araç izleri) döndürür."""
    mesajlar = [{"role": "system", "content": AJAN_SISTEM},   # Başlangıç: system (araçlar, protokol),
                {"role": "user", "content": soru}]            #   kullanıcının sorusu.
    izler = []                                    # Hangi araçlar çağrıldı (kullanıcıya gösterilecek).
    for _ in range(maks_adim):                    # Adım sınırı: sonsuz döngü olmasın.
        ham = sor(mesajlar)                       # 1) DÜŞÜN: modelden JSON karar.
        try:                                      # JSON'u ayrıştır:
            karar = json.loads(ham[ham.index("{"): ham.rindex("}") + 1])   #   ilk { … son },
            assert isinstance(karar, dict)        #   nesne olmalı (liste değil).
        except Exception:                         # Bozuk JSON:
            mesajlar += [{"role": "assistant", "content": ham},            #   olduğu gibi kaydet,
                         {"role": "user", "content": "Araç sonucu: geçersiz JSON."}]   # uyar,
            continue                              #   yeniden iste.
        mesajlar.append({"role": "assistant",     # Kararı geçmişe yaz (eğitimdeki biçimle):
                         "content": json.dumps(karar, ensure_ascii=False)})   # JSON metni.
        if isinstance(karar.get("cevap"), str) and karar["cevap"].strip():   # Son cevap ya da bilinmeyen araç:
            return (karar.get("cevap") or ham), izler   # bitir.
        if karar.get("arac") not in FONK:
            mesajlar.append({"role":"user","content":"Araç sonucu: bilinmeyen araç / unknown tool."})
            continue
        argumanlar = karar.get("argumanlar") or {}  # 2) EYLEM: argümanlar (yoksa boş).
        try:                                      # Aracı BİZ çalıştırıyoruz:
            spec = next(a for a in ARACLAR if a['ad'] == karar['arac'])
            if not isinstance(argumanlar, dict) or set(argumanlar) != {spec['param']}:
                raise ValueError('Expected exactly the named tool parameter')
            sonuc = FONK[karar["arac"]](argumanlar[spec['param']])   #   tek parametreli araçlar.
        except Exception as hata:                 # Yanlış argüman vb.:
            sonuc = f"Araç hatası: {hata}"        #   hatayı gözlem olarak ver.
        izler.append(f"{karar['arac']}({', '.join(map(str, argumanlar.values()))})")   # İz.
        mesajlar.append({"role": "user", "content": f"Araç sonucu: {sonuc}"})   # 3) GÖZLEM.
    return f"Adım sınırına ulaşıldı. {ISARET}", izler   # Güvenli çıkış.
