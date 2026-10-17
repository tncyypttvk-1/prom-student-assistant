# Prom uygulama kaynakları

Bu dosyalar `notebooks/Prom_Son.ipynb` içindeki gömülü paketten aktarılmıştır. `app.py` içindeki GGUF depo ve dosya yer tutucuları mevcut yayımlanmış modele ayarlanmıştır. Model sürümünün birleşik GPU modeliyle hash eşitliği kanıtlanmamıştır.

- `proje.py`: kurum kimliği ve sistem mesajları.
- `araclar.py`: dört araç ve temel ajan döngüsü.
- `prom_runtime.py`: çoklu ders argümanlarını birleştirme ve not ortalaması yönlendirmesi; `app.py` tarafından kurulur.
- `prom_retrieval.py`: defterin hibrit arama desteği.
- `app.py`: CPU GGUF modeli, TF-IDF arama ve Gradio arayüzü.
- `ozel_arac.py`, `rag_duzeltme.py`: önceki kaynak yardımcıları; güncel uygulamanın başlangıç dosyası değildir.

## CPU uygulamasını çalıştırma

Depo kökünden, Python sanal ortamında:

```sh
python3 -m pip install -r src/requirements.txt
mkdir -p .prom-run
cp src/*.py data/rehber.pdf data/rehber_bolumleri.json data/dersler.csv data/test_sorulari.csv .prom-run/
cd .prom-run
python3 app.py
```

İlk açılışta yaklaşık 1,65 GB GGUF indirilir. Bu komut GPU eğitimi başlatmaz. Bağımlılık sürümleri son Colab kaydını izler; temiz yerel ortamda uçtan uca kurulum bu güncellemede denenmedi. Önerilen tekrar üretim yolu, çıktıları korunmuş son Colab defteridir.
