GitHub aktarımı tamamlandı: https://github.com/tncyypttvk-1/prom-student-assistant

Canlı üniversite demosu: https://tncyypttvk-1.github.io/prom-student-assistant/

Aşağıdaki adımlar projeyi başka bir depoda tekrar kurmak içindir.

# GitHub’a yükleme

1. GitHub hesabında New repository seç. İsim önerisi: `prom-student-assistant`.
2. LinkedIn’de kodu paylaşmak istiyorsan Public seç.
3. Create repository ardından uploading an existing file bağlantısını aç.
4. Bu paketin ZIP’ini aç. İçindeki **prometheus-university klasörünün içeriğini** yükle; ZIP’i tek dosya olarak yükleme.
5. `.github/workflows/pages.yml` gizli klasörünü de eklemek için Git kullanabilir veya GitHub arayüzünde bu yolu açıp dosya içeriğini yapıştırabilirsin.
6. Settings → Pages → Source: GitHub Actions. Pages iş akışı `site/dist` klasörünü yayımlar.
7. Actions çalışması başarılı olunca Pages adresini kontrol et; ardından README ve LinkedIn metnine gerçek bağlantıları ekle.

Hugging Face token’ını yükleme. Bu paket model ağırlıklarını ve Colab’daki güncel çalıştırma çıktılarını içermez. Teslim için Colab’daki çıktı içeren son defterini ayrıca kaydet ve bu depodaki çalıştırılmamış defterin yerine koy.
