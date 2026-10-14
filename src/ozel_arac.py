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
