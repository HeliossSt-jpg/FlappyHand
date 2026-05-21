# Projenin ana döngüsü — tüm modülleri bir araya getirir

import cv2
from hand_tracker import ElTakipci
from game import Oyun
from ui import Menu

# EKRAN BOYUTU

GENISLIK = 640
YUKSEKLIK = 480

# OYUN DURUMLARI

DURUM_BEKLIYOR = 'bekliyor'
DURUM_OYNUYOR  = 'oynuyor'
DURUM_MENU     = 'menu'
DURUM_BITTI    = 'bitti'

def main():
    # Nesneleri oluştur 
    takipci = ElTakipci()
    oyun    = Oyun()
    menu    = Menu()

    durum = DURUM_BEKLIYOR      # Oyun başlangıç durumu
    bitti_yumruk_bekleniyor = False  # Bitti ekranında yeniden başlatmak için yumruk bekleniyor mu?

    print('Başlatılıyor... Çıkmak için Q tuşuna bas.')

    while True:

        # Kameradan kare al ve el tespiti yap 
        kare, basari = takipci.kareyi_isle()

        if not basari:
            # Kare gelmezse döngüye devam et
            continue

        # El bilgilerini al 
        jest        = takipci.guncel_jest          # 'yumruk', 'acik', 'isaret', 'bilinmiyor'
        el_konumu   = takipci.guncel_el_konumu     # (x, y) piksel veya None
        isaret_konum = takipci.guncel_isaret_konumu  # işaret parmağı ucu (x, y) veya None

        # DURUM BELİRTECİ

        if durum == DURUM_BEKLIYOR:
            # Başlangıç ekranı 
            _baslik_ciz(kare, 'Yumruk yap, baslat!')

            # Yumruk yapılınca oyunu başlat
            if jest == 'yumruk':
                durum = DURUM_OYNUYOR

        elif durum == DURUM_OYNUYOR:
            # Oyun aktif 

            # Açık el: duraklatma menüsü
            if jest == 'acik':
                durum = DURUM_MENU

            else:
                if el_konumu is None:
                    oyun.ciz(kare)
                    menu.el_bulunamadi_sayaci = menu.el_bulunamadi_suresi
                    durum = DURUM_MENU
                else:
                    oyun.guncelle(el_konumu)
                    oyun.ciz(kare)

                # Çarpışma olduysa bitti ekranına geç
                if oyun.oyun_bitti:
                    durum = DURUM_BITTI

        elif durum == DURUM_MENU:
            # Duraklatma menüsü 

            # Oyun görüntüsü arka planda kalsın
            oyun.ciz(kare)

            # Menüyü güncelle ve çiz
            secim = menu.guncelle(isaret_konum, jest)
            menu.ciz(kare)

            if secim == 'devam':
                durum = DURUM_OYNUYOR
            elif secim == 'cikis':
                break

        elif durum == DURUM_BITTI:
            oyun.ciz(kare)
            _bitti_ekrani_ciz(kare, oyun.skor)

            # Yumrukla başlatmak için önce eli çekip tekrar yumruk yapması lazım
            if jest != 'yumruk':
                bitti_yumruk_bekleniyor = True

            if jest == 'yumruk' and bitti_yumruk_bekleniyor:
                bitti_yumruk_bekleniyor = False
                oyun.sifirla()
                durum = DURUM_OYNUYOR

        # Jest bilgisini ekrana yaz (debug) 
        cv2.putText(kare, f'Jest: {jest}',
                    (10, YUKSEKLIK - 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (200, 200, 200), 1)

        # Kareyi göster
        cv2.imshow('Flappy Hand', kare)

        # Q tuşu → çık
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Temizlik
    takipci.kapat()
    cv2.destroyAllWindows()

# YARDIMCI FONKSİYONLAR


def _baslik_ciz(kare, mesaj):
    """Başlangıç ekranında yönlendirme mesajı gösterir."""
    cv2.putText(kare, mesaj,
                (GENISLIK // 2 - 160, YUKSEKLIK // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9, (0, 255, 200), 2)


def _bitti_ekrani_ciz(kare, skor):
    # Oyun bitti ekranında skoru ve yeniden başlatma mesajını gösterir.

    # Yarı saydam katman
    katman = kare.copy()
    cv2.rectangle(katman, (0, 0), (GENISLIK, YUKSEKLIK), (0, 0, 0), -1)
    cv2.addWeighted(katman, 0.45, kare, 0.55, 0, kare)

    cv2.putText(kare, 'OYUN BITTI',
                (GENISLIK // 2 - 110, 180),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.3, (0, 80, 255), 3)

    cv2.putText(kare, f'Skor: {skor}',
                (GENISLIK // 2 - 55, 250),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0, (255, 255, 255), 2)

    cv2.putText(kare, 'Yumruk yap: yeniden baslat',
                (GENISLIK // 2 - 170, 320),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, (200, 200, 200), 2)


if __name__ == '__main__':
    main()