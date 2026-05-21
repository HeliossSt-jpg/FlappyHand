# Kamerayı açan, eli tespit eden ve jest sonucunu döndüren modül

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.components import containers
import urllib.request
import os
from gestures import jest_tespit_et

# MODEL DOSYASINI İNDİR (yoksa)

MODEL_DOSYASI = 'hand_landmarker.task'

if not os.path.exists(MODEL_DOSYASI):
    print('Model indiriliyor...')
    urllib.request.urlretrieve(
        'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task',
        MODEL_DOSYASI
    )
    print('Model indirildi.')


# EL TAKİP SINIFI

class ElTakipci:
    """
    Kameradan görüntü alır, MediaPipe ile eli tespit eder,
    jest adını ve el konumunu döndürür.
    """

    def __init__(self):
        # Kamerayı başlat
        self.kamera = cv2.VideoCapture(0)

        # Son tespit edilen jest ve el konumu
        self.guncel_jest = 'bilinmiyor'
        self.guncel_el_konumu = None        # bilek merkezi (x, y)
        self.guncel_isaret_konumu = None    # işaret parmağı ucu (x, y)
        self.son_sonuc = None

        # MediaPipe yeni API ayarları
        temel_secenekler = python.BaseOptions(model_asset_path=MODEL_DOSYASI)
        secenekler = vision.HandLandmarkerOptions(
            base_options=temel_secenekler,
            num_hands=1,                        # Aynı anda en fazla 1 el
            min_hand_detection_confidence=0.7,  # Tespit güven eşiği
            min_hand_presence_confidence=0.7,   # Varlık güven eşiği
            min_tracking_confidence=0.7         # Takip güven eşiği
        )

        self.dedektör = vision.HandLandmarker.create_from_options(secenekler)

    def kareyi_isle(self):
        #Kameradan bir kare okur, eli işler ve sonuçları günceller.

        basari, kare = self.kamera.read()
        if not basari:
            return None, False

        # Görüntüyü yatay aynalar
        kare = cv2.flip(kare, 1)

        # MediaPipe RGB formatında görüntü ister
        rgb_kare = cv2.cvtColor(kare, cv2.COLOR_BGR2RGB)

        # MediaPipe Image nesnesine çevir
        mp_goruntu = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_kare)

        # El tespiti yap
        sonuc = self.dedektör.detect(mp_goruntu)
        self.son_sonuc = sonuc

        yukseklik, genislik, _ = kare.shape

        # EL BULUNDUYSA İŞLE

        if sonuc.hand_landmarks:
            el = sonuc.hand_landmarks[0]  # İlk eli al

            # Landmark noktalarını ekrana çiz
            for nokta in el:
                x = int(nokta.x * genislik)
                y = int(nokta.y * yukseklik)
                cv2.circle(kare, (x, y), 5, (0, 255, 0), -1)

            # Jest tespiti
            self.guncel_jest = jest_tespit_et(el)

            # Elin bilek noktasını merkez olarak al (landmark 0)
            bilek = el[0]
            self.guncel_el_konumu = (
                int(bilek.x * genislik),
                int(bilek.y * yukseklik)
            )

            # İşaret parmağı ucu 
            isaret = el[8]
            self.guncel_isaret_konumu = (
                int(isaret.x * genislik),
                int(isaret.y * yukseklik)
            )
            

        else:
            self.guncel_jest = 'bilinmiyor'
            self.guncel_el_konumu = None
            self.guncel_isaret_konumu = None

        return kare, True

    def kapat(self):
        # Kamerayı ve OpenCV pencerelerini düzgünce kapat.
        self.kamera.release()
        cv2.destroyAllWindows()


# TEST 

if __name__ == '__main__':
    takipci = ElTakipci()

    while True:
        kare, basari = takipci.kareyi_isle()
        if not basari:
            break

        cv2.putText(
            kare,
            f'Jest: {takipci.guncel_jest}',
            (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )
        cv2.imshow('El Takip Testi', kare)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    takipci.kapat()