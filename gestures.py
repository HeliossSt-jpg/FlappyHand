# gestures.py
# Kaynak: MediaPipe Hand Landmarks — https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker
# El landmark noktalarından jest (hareket) tespiti yapan modül

# ──────────────────────────────────────────────
# SABITLER — MediaPipe'ın her parmağa atadığı
# landmark (nokta) numaraları
# ──────────────────────────────────────────────

# Her parmağın en uç noktası (tırnak hizası)
PARMAK_UCLARI = [8, 12, 16, 20]   # işaret, orta, yüzük, serçe (baş parmak hariç)

# Her parmağın orta eklemi
PARMAK_EKLEMLERI = [6, 10, 14, 18]


def jest_tespit_et(el_landmarks):
    """
    Baş parmak hariç 4 parmağa bakarak jest tespit eder.
    Baş parmak sağ/sol el farkından dolayı sorunlu olduğu için devre dışı.

    Dönüş değerleri:
        'yumruk'     → ✊ 4 parmak kapalı
        'acik'       → 🖐 4 parmak açık
        'isaret'     → ☝️ sadece işaret parmağı açık
        'bilinmiyor' → diğer durumlar
    """

    nokta = el_landmarks
    parmaklar = []

    # 4 parmak — Y ekseni yukarıdan aşağıya artar
    # Uç eklemden küçükse (yukarıdaysa) parmak açık demektir
    for uc, eklem in zip(PARMAK_UCLARI, PARMAK_EKLEMLERI):
        if nokta[uc].y < nokta[eklem].y:
            parmaklar.append(1)  # açık
        else:
            parmaklar.append(0)  # kapalı

    acik_parmak_sayisi = sum(parmaklar)

    # ──────────────────────────────────────────────
    # HAREKET TANIMA
    # ──────────────────────────────────────────────

    if acik_parmak_sayisi == 0:
        return 'yumruk'        # ✊ hiçbir parmak açık değil

    elif acik_parmak_sayisi >= 3:
        return 'acik'          # 🖐 çoğu parmak açık

    elif parmaklar[0] == 1 and acik_parmak_sayisi == 1:
        return 'isaret'        # ☝️ sadece işaret parmağı açık

    else:
        return 'bilinmiyor'