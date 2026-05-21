# Oyunun menü ekranını ve buton mantığını yöneten modül
# El işaretiyle buton seçimi bu dosyada gerçekleşir

import cv2

# EKRAN BOYUTU (game.py ile aynı olmalı)

GENISLIK = 640
YUKSEKLIK = 480

# BUTON SINIFI

class Buton:
    # Ekranda dikdörtgen şeklinde görünen, el işaretiyle tıklanabilen buton nesnesi.

    def __init__(self, x, y, genislik, yukseklik, yazi):
        self.x = x
        self.y = y
        self.genislik = genislik
        self.yukseklik = yukseklik
        self.yazi = yazi
        self.uzerinde = False       # İşaret parmağı butonun üzerinde mi?

    def nokta_icinde_mi(self, px, py):
        # Verilen (px, py) koordinatı butonun içinde mi?
        
        return (self.x < px < self.x + self.genislik and
                self.y < py < self.y + self.yukseklik)

    def ciz(self, kare):
    
        #Butonu ekrana çizer, işaret parmağı üzerine gelince renk değişir (hover efekti).
        
        # Hover durumuna göre renk seç
        renk = (0, 200, 100) if self.uzerinde else (50, 50, 50)

        # Buton arka planı
        cv2.rectangle(kare,
                      (self.x, self.y),
                      (self.x + self.genislik, self.y + self.yukseklik),
                      renk, -1)

        # Buton çerçevesi
        cv2.rectangle(kare,
                      (self.x, self.y),
                      (self.x + self.genislik, self.y + self.yukseklik),
                      (255, 255, 255), 2)

        # Buton yazısı — ortalanmış
        (metin_gen, metin_yuk), _ = cv2.getTextSize(
            self.yazi, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)

        metin_x = self.x + (self.genislik - metin_gen) // 2
        metin_y = self.y + (self.yukseklik + metin_yuk) // 2

        cv2.putText(kare, self.yazi,
                    (metin_x, metin_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (255, 255, 255), 2)

# MENU SINIFI

class Menu:
    #Oyun duraklatıldığında ekrana gelen STOP menüsü, iki buton içerir: Devam Et ve Çıkış.

    def __init__(self):
        self.el_bulunamadi_sayaci = 0
        self.el_bulunamadi_suresi = 60   # 60 kare ≈ 2 saniye
        # Butonları ekranın ortasına hizala
        buton_gen = 200
        buton_yuk = 60
        merkez_x = GENISLIK // 2 - buton_gen // 2

        self.devam_butonu = Buton(merkez_x, 180, buton_gen, buton_yuk, 'Devam Et')
        self.cikis_butonu = Buton(merkez_x, 280, buton_gen, buton_yuk, 'Cikis')

        # İşaret parmağının butona ne kadar süredir üzerinde olduğunu sayar
        # Yanlışlıkla seçimi önlemek için 1 saniye bekler
        self.secim_sayaci = 0
        self.secim_suresi = 30   # 30 kare ≈ 1 saniye (30 fps varsayımıyla)

    def guncelle(self, isaret_konumu, jest):
        #İşaret parmağının konumunu alır, butonların hover durumunu günceller ve seçim yapılıp yapılmadığını döndürür.
    
        # Varsayılan olarak hover kapalı
        self.devam_butonu.uzerinde = False
        self.cikis_butonu.uzerinde = False

        if isaret_konumu is None:
            self.secim_sayaci = 0
            return None

        # Sadece işaret jesti aktifse buton kontrolü yap
        if jest != 'isaret':
            self.secim_sayaci = 0
            self.devam_butonu.uzerinde = False
            self.cikis_butonu.uzerinde = False
            return None

        px, py = isaret_konumu

        # Hangi butonun üzerinde?
        devam_uzerinde = self.devam_butonu.nokta_icinde_mi(px, py)
        cikis_uzerinde = self.cikis_butonu.nokta_icinde_mi(px, py)

        self.devam_butonu.uzerinde = devam_uzerinde
        self.cikis_butonu.uzerinde = cikis_uzerinde

        # Herhangi bir butonun üzerindeyse sayacı artır
        if devam_uzerinde or cikis_uzerinde:
            self.secim_sayaci += 1
        else:
            self.secim_sayaci = 0       # Buton dışına çıkınca sıfırla

        # Yeterince beklendi mi?
        if self.secim_sayaci >= self.secim_suresi:
            self.secim_sayaci = 0       # Sayacı sıfırla, tekrar seçim yapılabilsin
            if devam_uzerinde:
                return 'devam'
            if cikis_uzerinde:
                return 'cikis'

        return None

    def ciz(self, kare):
        # Yarı saydam koyu arka plan ve iki butonu ekrana çizer.

        # Yarı saydam koyu katman
        katman = kare.copy()
        cv2.rectangle(katman, (0, 0), (GENISLIK, YUKSEKLIK), (0, 0, 0), -1)
        cv2.addWeighted(katman, 0.5, kare, 0.5, 0, kare)
        
# El bulunamadı uyarısı (2 saniye görünür)
        if self.el_bulunamadi_sayaci > 0:
            cv2.putText(kare, 'El bulunamadi!',
                        (GENISLIK // 2 - 110, 80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 100, 255), 2)
            self.el_bulunamadi_sayaci -= 1
        # Başlık yazısı
        cv2.putText(kare, 'DURAKLATILDI',
                    (GENISLIK // 2 - 120, 130),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (255, 255, 255), 3)

        # Butonları çiz
        self.devam_butonu.ciz(kare)
        self.cikis_butonu.ciz(kare)

        # Seçim ilerleme çubuğu (işaret parmağı butonda ne kadar bekledi)
        if self.secim_sayaci > 0:
            ilerleme = int((self.secim_sayaci / self.secim_suresi) * (GENISLIK - 40))
            cv2.rectangle(kare, (20, YUKSEKLIK - 20),
                          (20 + ilerleme, YUKSEKLIK - 10),
                          (0, 255, 150), -1)