"""Run after section 7 in the current Colab session. Does not train the model."""
import json
import math
import re
import unicodedata
from pathlib import Path

ALIASES = {
    1: 'kayıt yenileme kayıt ücreti registration renewal late enrollment tuition',
    2: 'ders ekle bırak ders seçimi course selection add drop semester credits',
    3: 'yoklama devamsızlık devam katılım attendance absence missing classes',
    4: 'sınav ara sınav final exam midterm assessment',
    5: 'mazeret rapor kaçırılan sınav excused exam missed final medical report',
    6: 'harf notu katsayı not ortalaması letter grade coefficient GPA grading',
    7: 'bütünleme telafi resit retake exam',
    8: 'yazın yaz yaz okulu yaz dersi ücret fiyat para summer school summer course ECTS tuition fee cost',
    9: 'burs başarı ihtiyaç destek scholarship merit need financial aid',
    10: 'okula ara izin kayıt dondurma freeze registration leave of absence suspend studies',
    11: 'yatay geçiş üniversite değiştirme transfer university eligibility',
    12: 'kitap kütüphane ödünç iade gecikme library book loan overdue fine',
    13: 'yurt oda konaklama dormitory housing room accommodation',
    14: 'mezuniyet diploma staj graduation degree internship requirements',
    15: 'kopya intihal akademik dürüstlük plagiarism cheating academic integrity AI assignments',
}
STOP = set('bir bu ne nedir kaç kadar hangi için ile ve mi mı mu mü bana benim olur olursa var the a an is are i my how much many what when where for of to in do does can me'.split())

def normalize(text):
    text = text.replace('ı', 'i').replace('İ', 'i').casefold()
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))

STOP = {normalize(w) for w in STOP}

def tokens(text):
    return set(w for w in re.findall(r'[a-z0-9]+', normalize(text)) if len(w) > 1 and w not in STOP)

def matches(word, vocabulary):
    if word in vocabulary:
        return True
    # Handle common Turkish word endings, without matching very short roots.
    return any(len(root) >= 5 and word.startswith(root) and len(word)-len(root) <= 5 for root in vocabulary)

sections = json.loads(Path('rehber_bolumleri.json').read_text(encoding='utf-8'))
assert len(sections) >= 10
lookup = {}
for section in sections:
    for language in ('tr', 'en'):
        sid = int(section['id'])
        text = section[language].strip()
        lookup[(sid, language)] = {
            'text': text,
            'words': tokens(text + ' ' + ALIASES.get(sid, '')),
            'aliases': tokens(ALIASES.get(sid, '')),
        }

def lexical_scores(question):
    terms = tokens(question)
    if not terms:
        return {key: 0.0 for key in lookup}
    weights = {}
    for word in terms:
        frequency = sum(matches(word, row['words']) for row in lookup.values())
        weights[word] = math.log(1 + len(lookup) / (1 + frequency))
    denominator = sum(weights.values())
    return {
        key: (0.8 * sum(weight for word, weight in weights.items() if matches(word, row['aliases']))
              + 0.2 * sum(weight for word, weight in weights.items() if matches(word, row['words']))) / denominator
        for key, row in lookup.items()
    }

def chroma_ara(soru, k=2):
    """Combine keyword coverage and Chroma ranking; return original guide text."""
    if not isinstance(soru, str) or not soru.strip() or k < 1:
        return []
    lexical = lexical_scores(soru)
    semantic = {}
    vector_index = globals().get('vs_temiz')
    if vector_index is not None:
        candidates = vector_index.similarity_search(soru, k=min(30, len(lookup)))
        for rank, doc in enumerate(candidates):
            sid = doc.metadata.get('bolum_id')
            language = doc.metadata.get('dil')
            if sid is not None and language in ('tr', 'en'):
                semantic[(int(sid), language)] = 1 / (rank + 1)
    ranked = sorted(lookup, key=lambda key: 0.90 * lexical[key] + 0.10 * semantic.get(key, 0), reverse=True)
    chosen, seen = [], set()
    for key in ranked:
        if key[0] in seen:
            continue
        seen.add(key[0])
        chosen.append(lookup[key]['text'])
        if len(chosen) >= k:
            break
    return chosen

