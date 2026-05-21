# Flappy Hand oyununun kuş, engel ve skor mantığını içeren modül

import cv2
import numpy as np
import random

# EKRAN BOYUTU

GENISLIK = 640
YUKSEKLIK = 480

# KUŞ SINIFI

class Kus:
    # Oyuncunun eli ile kontrol edilen kuşu temsil eder.
    # Yumruk yapıldığında elin üstünde belirir.
    
    YARI_CAP = 20  # Kuşun yarıçapı 

    def __init__(self):
        self.x = GENISLIK // 4      # Kuşun sabit X konumu (ekranın sol çeyreği)
        self.y = YUKSEKLIK // 2     # Başlangıç Y konumu (ekran ortası)
        self.renk = (0, 200, 255)   # Turuncu-sarı renk

    def guncelle(self, el_konumu):
        # El konumuna göre kuşun Y pozisyonunu günceller.
        # Kuş elin biraz üstünde durur.

        if el_konumu:
            # Kuş bileğin 40 piksel üstünde konumlanır
            self.y = el_konumu[1] - 40

            # Ekran sınırları içinde kal
            self.y = max(self.YARI_CAP, min(YUKSEKLIK - self.YARI_CAP, self.y))

    def ciz(self, kare):
        # Kuşu ekrana çizer.
        cv2.circle(kare, (self.x, self.y), self.YARI_CAP, self.renk, -1)

        # Göz detayı
        cv2.circle(kare, (self.x + 8, self.y - 6), 5, (0, 0, 0), -1)
        cv2.circle(kare, (self.x + 10, self.y - 6), 2, (255, 255, 255), -1)

    def carpisti_mi(self, engel):
        # Kuş ile engel arasında çarpışma kontrolü yapar.

        # Kuş engelin X aralığındaysa Y kontrolü yap
        if self.x + self.YARI_CAP > engel.x and self.x - self.YARI_CAP < engel.x + engel.GENISLIK:
            # Üst boşluk dışında mı?
            if self.y - self.YARI_CAP < engel.ust_yukseklik:
                return True
            # Alt boşluk dışında mı?
            if self.y + self.YARI_CAP > engel.ust_yukseklik + engel.BOSLUK:
                return True
        return False

# ENGEL SINIFI

class Engel:
    # Ekranın sağından sola doğru hareket eden boru engelini temsil eder.

    GENISLIK = 60       # Borunun genişliği (piksel)
    BOSLUK = 160        # Üst ve alt boru arasındaki geçiş boşluğu
    HIZ = 4             # Her karede sola hareket miktarı (piksel)

    def __init__(self):
        self.x = GENISLIK  # Ekranın sağ kenarından başla
        # Boşluğun rastgele Y konumu , ekranın ortasına yakın tutulur
        self.ust_yukseklik = random.randint(80, YUKSEKLIK - self.BOSLUK - 80)
        self.gecildi = False    # Skor sayımı için: kuş geçti mi?
        self.renk = (34, 139, 34)   # Koyu yeşil

    def guncelle(self):
        # Engeli sola doğru hareket ettirir.
        self.x -= self.HIZ

    def ekran_disi_mi(self):
        # Engel ekranın solundan çıktı mı?
        return self.x + self.GENISLIK < 0

    def ciz(self, kare):
        # Üst ve alt boruyu ekrana çizer.

        # Üst boru
        cv2.rectangle(
            kare,
            (self.x, 0),
            (self.x + self.GENISLIK, self.ust_yukseklik),
            self.renk, -1
        )
        # Üst boru başlık şeridi
        cv2.rectangle(
            kare,
            (self.x - 5, self.ust_yukseklik - 20),
            (self.x + self.GENISLIK + 5, self.ust_yukseklik),
            self.renk, -1
        )

        # Alt boru
        alt_baslangic = self.ust_yukseklik + self.BOSLUK
        cv2.rectangle(
            kare,
            (self.x, alt_baslangic),
            (self.x + self.GENISLIK, YUKSEKLIK),
            self.renk, -1
        )
        # Alt boru başlık şeridi
        cv2.rectangle(
            kare,
            (self.x - 5, alt_baslangic),
            (self.x + self.GENISLIK + 5, alt_baslangic + 20),
            self.renk, -1
        )
        
# OYUN SINIFI

class Oyun:
    # Oyunun ana mantığını yönetir.
    # Kuş, engeller ve skoru bir arada tutar.

    ENGEL_ARALIK = 90   # Yeni engel üretmek için gereken kare sayısı

    def __init__(self):
        self.kus = Kus()
        self.engeller = []          # Aktif engellerin listesi
        self.skor = 0
        self.kare_sayaci = 0        # Engel üretim zamanlaması için
        self.oyun_bitti = False

    def sifirla(self):
        # Oyunu baştan başlatır.
        self.kus = Kus()
        self.engeller = []
        self.skor = 0
        self.kare_sayaci = 0
        self.oyun_bitti = False

    def guncelle(self, el_konumu):
        # Her karede oyun durumunu günceller.

        if self.oyun_bitti:
            return

        # Kuşu güncelle
        self.kus.guncelle(el_konumu)

        # Belirli aralıklarla yeni engel üret
        self.kare_sayaci += 1
        if self.kare_sayaci % self.ENGEL_ARALIK == 0:
            self.engeller.append(Engel())

        # Engelleri güncelle
        for engel in self.engeller:
            engel.guncelle()

            # Kuş engeli geçtiyse skor artır
            if not engel.gecildi and engel.x + engel.GENISLIK < self.kus.x:
                engel.gecildi = True
                self.skor += 1

            # Çarpışma kontrolü
            if self.kus.carpisti_mi(engel):
                self.oyun_bitti = True

        # Ekran dışına çıkan engelleri listeden sil
        self.engeller = [e for e in self.engeller if not e.ekran_disi_mi()]

        # Kuş ekran üstüne veya altına çıktıysa oyun bitti
        if self.kus.y <= 0 or self.kus.y >= YUKSEKLIK:
            self.oyun_bitti = True

    def ciz(self, kare):
        # Tüm oyun nesnelerini ekrana çizer.

        # Engelleri çiz
        for engel in self.engeller:
            engel.ciz(kare)

        # Kuşu çiz
        self.kus.ciz(kare)

        # Skoru ekrana yaz
        cv2.putText(
            kare,
            f'Skor: {self.skor}',
            (GENISLIK // 2 - 50, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )