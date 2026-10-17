"""Bitirme projesi sitesi: GGUF model (CPU) + TF-IDF RAG + araçlı ajan + Gradio."""
import csv                                        # Örnek soruları okumak için.
import re                                         # Rehberi başlıklardan bölmek için.
import gradio as gr                               # Arayüz.
from llama_cpp import Llama                       # GGUF modelini CPU'da çalıştırır.
from pypdf import PdfReader                       # Rehber PDF'i.
from sklearn.feature_extraction.text import TfidfVectorizer   # Harf n-gram sıklığına dayalı arama.
from sklearn.metrics.pairwise import cosine_similarity         # Benzerlik ölçüsü.
import araclar                                    # Araçlar ve ajan döngüsü (defterle aynı dosya).
from proje import KIMLIK, PROJE_ADI, KURUM, ISARET, REHBER, TEST, rag_sistem   # Proje kartı.

from prom_runtime import install
install(araclar)

GGUF_DEPO = "tncyypttvk/Prom-1.5B-GGUF"                       # Yer tutucu: defter deponuzun adını yazar.
GGUF_DOSYA = "prom-1.5b-q8_0.gguf"                     # Yer tutucu: GGUF dosyasının adı.
llm = Llama.from_pretrained(repo_id=GGUF_DEPO, filename=GGUF_DOSYA,   # Hub'dan indir ve yükle:
                            n_ctx=2048, n_threads=2, verbose=False)   # 2048 token bağlam, 2 çekirdek.


def sor(mesajlar, maks=200):                      # Ajan ve RAG bu fonksiyonla modele sorar.
    """Mesaj listesini modele verir, cevabı döndürür (sıcaklık 0: kararlı)."""
    c = llm.create_chat_completion(messages=mesajlar, max_tokens=maks, temperature=0)   # Üret.
    return c["choices"][0]["message"]["content"].strip()   # Metni al.


import json
from pathlib import Path
rehber_bolumleri = json.loads(Path("rehber_bolumleri.json").read_text(encoding="utf-8"))
PARCALAR = [bolum[dil].strip() for bolum in rehber_bolumleri for dil in ("tr", "en")]
tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5)).fit(PARCALAR)   # Harf 3-5'lileri.
MATRIS = tfidf.transform(PARCALAR)                # Her bölümün vektörü.


def ara(soru, k=2):                               # soru → en benzer k bölüm.
    """TF-IDF kosinüs benzerliğiyle en yakın k bölümü döndürür."""
    puan = cosine_similarity(tfidf.transform([soru]), MATRIS)[0]   # Soru ile her bölümün benzerliği.
    return [PARCALAR[i] for i in puan.argsort()[::-1][:k]]          # En yüksek k.


araclar.ARA = ara                                 # Ajanın rehberde_ara aracı da TF-IDF kullansın.


def asistan_rag(soru):                            # RAG: ara → bağlam → sor (defterle aynı).
    """(cevap, kaynak başlıkları) döndürür."""
    bulunan = ara(soru)                           # 2 bölüm.
    cevap = sor([{"role": "system", "content": rag_sistem("\n\n".join(bulunan))},   # System,
                 {"role": "user", "content": soru}], 160)                            # soru.
    return cevap, [p.split("\n")[0] for p in bulunan]   # Cevap + başlıklar.


def cevapla(mesaj, gecmis, mod):                  # Gradio'nun çağırdığı fonksiyon.
    """Moda göre sohbet / RAG / ajan."""
    try:                                          # Hata arayüzü çökertmesin.
        if mod == "Sohbet":                       # Düz sohbet:
            return sor([{"role": "system", "content": KIMLIK}, {"role": "user", "content": mesaj}], 120)   #   tek mesaj.
        if mod == "Rehber (RAG)":                 # RAG:
            cevap, kaynaklar = asistan_rag(mesaj) #   cevap + kaynaklar,
            return f"{cevap}\n\n_Kaynak / Source: {', '.join(kaynaklar)}_"   #   kaynakları altına yaz.
        cevap, izler = araclar.ajan(mesaj, sor)   # Ajan: cevap + araç izleri,
        return cevap + (f"\n\n_🔧 {' · '.join(izler)}_" if izler else "")   #   izleri altına yaz.
    except Exception as hata:                     # Beklenmedik hata:
        return f"Bir sorun oldu: {type(hata).__name__}. Tekrar dener misiniz? {ISARET}"   # Kibar mesaj.


with open(TEST, encoding="utf-8") as f:           # Örnek sorular:
    ORNEKLER = [[r["soru"]] for r in list(csv.DictReader(f))[:3]]   #   paketin ilk 3 test sorusu.
demo = gr.ChatInterface(                          # Arayüz (defterdekiyle aynı):
    cevapla,                                      #   cevaplayan fonksiyon,
    additional_inputs=[gr.Radio(["Sohbet", "Rehber (RAG)", "Ajan"],   #   mod seçimi,
                                value="Rehber (RAG)", label="Mod / Mode")],  #   varsayılan RAG,
    title=f"{PROJE_ADI} {ISARET}",                #   başlık,
    description=f"{KURUM} asistanı / assistant · Fictional university / Kurgusal üniversite · CPU'da çalışır, cevaplar 10-60 sn sürebilir",   # açıklama,
    examples=ORNEKLER,                            #   örnek sorular,
    cache_examples=False)                         #   açılışta modelle çalıştırma (CPU'da çöker).
if __name__ == "__main__":                        # Space bu dosyayı doğrudan çalıştırır:
    demo.launch()                                 #   sunucuyu başlat.
