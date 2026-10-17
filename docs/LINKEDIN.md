# LinkedIn paylaşım taslağı

Antik çağın bilgeliği, geleceğin teknolojisi: Prom ile tanışın.

AI Engineering bitirme projemde, kurgusal Prometheus University için Türkçe ve İngilizce çalışan bir öğrenci işleri asistanı geliştirdim. Qwen2.5-1.5B-Instruct modelini QLoRA ile ince ayarlayıp kurum rehberinden bilgi getiren RAG ve araç kullanan bir ajan akışıyla birleştirdim.

Prom; rehberden kaynak getiriyor, ders tablosunda arama yapıyor ve kendi AKTS ağırlıklı not ortalaması aracımı kullanıyor. Modeli GGUF biçiminde CPU üzerinde de üç temel örnekle denedim. Projeyi sunmak için antik mimariyi ve yapay zekâ temasını buluşturan bir üniversite web sitesi tasarladım; sitedeki Prom panelinden geçici Colab demosu açılabiliyor.

30 soruluk son değerlendirmede Gemini hakem puanı 0,78 oldu: Türkçe 0,73, İngilizce 0,83. Bu sonuç arama ve ajan kodu düzeltmelerini de içeriyor; modelin tek başına doğruluk oranı değil. Bazı Türkçe rehber yanıtlarında ve dil tutarlılığında hatalar devam ediyor. Benim için en öğretici bölüm, bu hataların aramadan mı, araç çağrısından mı, yoksa modelin cevabından mı kaynaklandığını ayırmak oldu.

Web sitesi: https://tncyypttvk-1.github.io/prom-student-assistant/
GitHub: https://github.com/tncyypttvk-1/prom-student-assistant
Model ve rapor: https://huggingface.co/tncyypttvk/Prom-1.5B

Prometheus University eğitim amacıyla tasarlanmış kurgusal bir kurumdur. Sohbet demosu Colab oturumu açıkken kullanılabilir; kalıcı model yayını eğitmen vitrini için bekleniyor.

#AIEngineering #YapayZeka #RAG #QLoRA #LLM #HuggingFace
