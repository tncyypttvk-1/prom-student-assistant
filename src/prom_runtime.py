"""Measured application patches; model weights and training identity are unchanged.
Source: user's executed notebook, test score 23/30 on 2026-10-16.
GPA routing supports the explicit grade (ECTS) notation only.
"""
import json
import re

def install(araclar):
    if getattr(araclar, '_prom_runtime_installed', False):
        return
    import re

    # Hücre tekrar çalıştırılırsa önceki fonksiyonu koru.
    if not hasattr(araclar, "_tekli_tablo_ara"):
        araclar._tekli_tablo_ara = araclar.tablo_ara

    def coklu_ders_ara(deger):
        metin = str(deger)
        kodlar = list(dict.fromkeys(
            re.findall(r"\b[A-Za-z]{2,10}\d{3,4}\b", metin.upper())
        ))

        if len(kodlar) < 2:
            return araclar._tekli_tablo_ara(metin)

        return "\n".join(
            araclar._tekli_tablo_ara(kod) for kod in kodlar
        )

    araclar.tablo_ara = coklu_ders_ara

    for arac in araclar.ARACLAR:
        if arac["ad"] == "ders_bilgisi":
            arac["fonk"] = coklu_ders_ara

    araclar.FONK["ders_bilgisi"] = coklu_ders_ara

    import json

    # Önceki ajanı karşılaştırma için koru.
    if not hasattr(araclar, "_ajan_onceki"):
        araclar._ajan_onceki = araclar.ajan

    def ajan_duzeltilmis(soru, sor, maks_adim=6):
        mesajlar = [
            {"role": "system", "content": araclar.AJAN_SISTEM},
            {"role": "user", "content": soru},
        ]
        izler = []
        arac_basarili = False
        tanimlar = {a["ad"]: a for a in araclar.ARACLAR}

        def geri_bildir(metin):
            mesajlar.append({
                "role": "user",
                "content": "Araç sonucu: " + metin
            })

        for _ in range(maks_adim):
            ham = sor(mesajlar)

            try:
                # JSON sonuna eklenmiş ★ gibi metinleri dışarıda bırakır.
                baslangic = ham.index("{")
                karar, _ = json.JSONDecoder().raw_decode(ham[baslangic:])
                if not isinstance(karar, dict):
                    raise ValueError()
            except (ValueError, TypeError):
                geri_bildir("Geçersiz JSON. Yalnızca bir JSON nesnesi yaz.")
                continue

            mesajlar.append({
                "role": "assistant",
                "content": json.dumps(karar, ensure_ascii=False)
            })

            cevap = karar.get("cevap")
            if isinstance(cevap, str) and cevap.strip():
                if not arac_basarili:
                    geri_bildir(
                        "Henüz başarılı araç sonucu yok. "
                        "Önce uygun aracı geçerli parametreyle çağır."
                    )
                    continue
                return cevap, izler

            ad = karar.get("arac")

            # Eksik karar, bilinmeyen araçla aynı hata değildir.
            if ad is None:
                geri_bildir(
                    'Eksik karar. Sonuç yeterliyse '
                    '{"dusunce":"...","cevap":"..."} yaz. '
                    "Cevabı sorunun dilinde ve araç sonucuna dayanarak ver. "
                    "Başka işlem gerekiyorsa geçerli araç çağrısı yaz."
                )
                continue

            if ad not in tanimlar:
                geri_bildir(
                    "Geçersiz araç adı. İzin verilenler: "
                    + ", ".join(tanimlar)
                )
                continue

            spec = tanimlar[ad]
            param = spec["param"]
            arg = karar.get("argumanlar")

            if (
                not isinstance(arg, dict)
                or set(arg) != {param}
                or not isinstance(arg[param], str)
            ):
                ornek = {param: "değer"}
                aciklama = ""
                if ad == "ders_bilgisi":
                    aciklama = (
                        " Birden fazla ders kodunu tek ders_adi metninde "
                        "virgülle ayır; ikinci parametre ekleme."
                    )
                geri_bildir(
                    f"Çağrı reddedildi. Tam olarak tek metin parametresi "
                    f"gerekli: {json.dumps(ornek, ensure_ascii=False)}."
                    + aciklama
                )
                continue

            try:
                sonuc = spec["fonk"](arg[param])
                if not isinstance(sonuc, str):
                    raise TypeError("Araç metin döndürmeli.")
            except Exception as hata:
                geri_bildir(f"Araç çalıştırılamadı: {hata}")
                continue

            arac_basarili = True
            izler.append(f"{ad}({arg[param]})")
            geri_bildir(sonuc)

        return f"İşlem adım sınırında tamamlanamadı. {araclar.ISARET}", izler

    araclar.ajan = ajan_duzeltilmis

    import json
    import re

    # Mevcut ajan döngüsünü koru.
    ajan_dongusu = ajan_duzeltilmis

    def ajan_uyumlu(soru, sor, maks_adim=6):
        def karar_duzelt(mesajlar):
            ham = sor(mesajlar)

            try:
                karar, _ = json.JSONDecoder().raw_decode(
                    ham[ham.index("{"):]
                )

                if karar.get("arac") != "ders_bilgisi":
                    return ham

                arg = karar.get("argumanlar")
                if not isinstance(arg, dict) or not arg:
                    return ham

                # Yalnızca ders_adi ve numaralı devam alanlarını kabul et.
                uygun = all(
                    re.fullmatch(r"ders_adi(?:_\d+)?", ad)
                    and isinstance(deger, str)
                    and deger.strip()
                    for ad, deger in arg.items()
                )

                if uygun and set(arg) != {"ders_adi"}:
                    karar["argumanlar"] = {
                        "ders_adi": ", ".join(arg.values())
                    }
                    print("ÇAĞRI DÜZELTİLDİ:", karar["argumanlar"])
                    return json.dumps(karar, ensure_ascii=False)

            except (ValueError, TypeError, AttributeError):
                pass

            return ham

        return ajan_dongusu(soru, karar_duzelt, maks_adim)

    araclar.ajan = ajan_uyumlu

    import json
    import re

    # Diğer sorularda mevcut ajan çalışmaya devam etsin.
    if not hasattr(araclar, "_ajan_ortalama_oncesi"):
        araclar._ajan_ortalama_oncesi = araclar.ajan

    def ajan_ortalama_destekli(soru, sor, maks_adim=6):
        metin = soru.casefold()
        ortalama_sorusu = any(
            kelime in metin
            for kelime in ("ortalama", "average", "gpa")
        )

        # Örnek giriş biçimi: BA (5 AKTS) veya CC (5 ECTS)
        eslesmeler = re.findall(
            r"\b(AA|BA|BB|CB|CC|DC|DD|FD|FF)\s*"
            r"\(\s*(\d+(?:[.,]\d+)?)\s*(?:AKTS|ECTS)\s*\)",
            soru,
            flags=re.IGNORECASE
        )

        if ortalama_sorusu and eslesmeler:
            dil = "en" if re.search(
                r"\b(average|gpa)\b", metin
            ) else "tr"

            veri = json.dumps({
                "lang": dil,
                "dersler": [
                    {"not": notu.upper(), "akts": akts.replace(",", ".")}
                    for notu, akts in eslesmeler
                ]
            }, ensure_ascii=False)

            cevap = araclar.FONK["not_ortalamasi"](veri)
            return (
                cevap.rstrip() + " " + araclar.ISARET,
                [f"kural yönlendirmesi → not_ortalamasi({veri})"]
            )

        return araclar._ajan_ortalama_oncesi(soru, sor, maks_adim)

    araclar.ajan = ajan_ortalama_destekli
    araclar._prom_runtime_installed = True
