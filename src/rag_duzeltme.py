# Colab: run in a new cell in the current session, after section 7.
import json
import uuid
from pathlib import Path
from langchain_core.documents import Document
from langchain_chroma import Chroma

# Clean text comes from the same guide; page headers/footers are excluded.
bolumler = json.loads(Path('rehber_bolumleri.json').read_text(encoding='utf-8'))
ES_ANLAMLAR = {
    3: 'yoklama devamsızlık derse katılım attendance absence missing classes',
    8: 'yazın yaz dersi yaz okulu summer courses summer school tuition cost',
    10: 'okula ara verme izin kayıt dondurma leave of absence freeze registration',
}
parcalar = []
for b in bolumler:
    for dil in ('tr', 'en'):
        asil = b[dil]
        parcalar.append(Document(
            page_content=asil + '\nSearch keywords: ' + ES_ANLAMLAR.get(b['id'], ''),
            metadata={'bolum_id': b['id'], 'dil': dil, 'asil': asil}
        ))
# Reuse the existing embedding model without retraining the language model.
vs_temiz = Chroma.from_documents(
    parcalar, embedding,
    collection_name='prom_clean_' + uuid.uuid4().hex,
    collection_metadata={'hnsw:space': 'cosine'}
)

def chroma_ara(soru, k=2):
    bulunan = vs_temiz.similarity_search(soru, k=min(30, k * 4))
    secilen, gorulen = [], set()
    for belge in bulunan:
        bolum_id = belge.metadata['bolum_id']
        if bolum_id not in gorulen:
            secilen.append(belge.metadata['asil'])
            gorulen.add(bolum_id)
        if len(secilen) == k:
            break
    return secilen

araclar.ARA = chroma_ara
for soru in [
    'Bir derste kaç saat yoklamam olursa kalırım?',
    "Yazın bir AKTS'lik ders kaç para?"
]:
    print('\nSORU:', soru)
    for parca in chroma_ara(soru):
        print('BULUNAN:', parca)
    cevap, kaynaklar = asistan_rag(soru)
    print('YENİ CEVAP:', cevap)
    print('KAYNAKLAR:', kaynaklar)
