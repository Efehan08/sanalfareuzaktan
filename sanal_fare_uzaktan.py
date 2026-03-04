import cv2
import mediapipe as mp
import math
import pyautogui
import time

# ==========================================
# --- KULLANICI AYARLARI VE BAĞLANTI ---
# ==========================================

# TELEFONUNUN IP ADRESİNİ BURAYA YAZ (Sonuna /video ekle)
# Eğer tekrar bilgisayar kamerasına dönmek istersen bu satırı silip '0' yazabilirsin.
url = "http://.../video" 

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0     # Wi-Fi gecikmesini önlemek için zorunlu beklemeyi sıfırladık

screen_w, screen_h = pyautogui.size()

margin = 180          # Telefondan daha rahat kontrol için alanı biraz genişlettik
click_ratio = 0.15    # DİNAMİK TIKLAMA (Eski click_dist yerine)
freeze_ratio = 0.30   # DİNAMİK DONDURMA (Eski freeze_dist yerine)

plocX, plocY = 0, 0 
clocX, clocY = 0, 0 
drag_active = False   
# ==========================================

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1, 
    model_complexity=1,           # 0 daha hızlıdır ama çok titrer. 1 daha zeki ve stabildir.
    min_detection_confidence=0.7, # Eli bulma konusunda daha seçici ol
    min_tracking_confidence=0.8   # Takip ederken tahminde bulunma, emin ol (Titremeyi keser)
)
mp_draw = mp.solutions.drawing_utils

# Kamera bağlantısını kur
print(f"Bağlanılıyor: {url}")
cap = cv2.VideoCapture(url)

if not cap.isOpened():
    print("HATA: Telefondaki kameraya bağlanılamadı! IP adresini ve Wi-Fi ağını kontrol et.")
else:
    print("Bağlantı Başarılı! Telefon artık bir uzaktan kumanda. Çıkış için 'q'.")

while cap.isOpened():
    success, img = cap.read()
    if not success: 
        print("Görüntü akışı koptu...")
        break

    # --- YÖN DÜZELTME YAMASI ---
    # Görüntüyü saat yönünün tersine 90 derece döndürerek düzeltir:
    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # --- PERFORMANS YAMASI ---
    # Telefon kameraları çok yüksek çözünürlüklü (1080p) veri gönderir.
    # Bunu Wi-Fi üzerinden kasmadan işlemek için 640x480'e küçültüyoruz.
    img = cv2.resize(img, (640, 480))
    img = cv2.flip(img, 1) 
    h, w, c = img.shape
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            landmarks = handLms.landmark
            
            # --- REFERANS (Elin Büyüklüğünü Ölçüyoruz) ---
            x0, y0 = int(landmarks[0].x * w), int(landmarks[0].y * h) # Bilek
            x9, y9 = int(landmarks[9].x * w), int(landmarks[9].y * h) # Orta parmak kökü
            ref_mesafe = math.hypot(x9 - x0, y9 - y0)
            if ref_mesafe == 0: ref_mesafe = 1

            # --- PARMAK UÇLARI ---
            x4, y4 = int(landmarks[4].x * w), int(landmarks[4].y * h)     # Baş
            x8, y8 = int(landmarks[8].x * w), int(landmarks[8].y * h)     # İşaret
            x12, y12 = int(landmarks[12].x * w), int(landmarks[12].y * h) # Orta

            # Piksel mesafeleri
            dist_left = math.hypot(x8 - x4, y8 - y4)
            dist_right = math.hypot(x12 - x4, y12 - y4)

            # --- DİNAMİK ORAN (Uzaklık / Yakınlık Körlüğü Çözüldü) ---
            oran_sol = dist_left / ref_mesafe
            oran_sag = dist_right / ref_mesafe

            # --- MERKEZ NOKTASI HEDEFİ ---
            cx, cy = (x8 + x4) / 2, (y8 + y4) / 2
            tx = (cx - margin) * screen_w / (w - 2 * margin)
            ty = (cy - margin) * screen_h / (h - 2 * margin)

            # --- KESKİN NİŞANCI (SNIPER) VE DONDURMA ---
            if (freeze_ratio > oran_sol > click_ratio) or (freeze_ratio > oran_sag > click_ratio):
                pass # Tıklamaya hazırlanıyor, imleci dondur (Asılı Kalır)
            else:
                # Elin anlık hızını ölç (Hedef nokta ile mevcut nokta arasındaki fark)
                el_hizi = math.hypot(tx - plocX, ty - plocY)
                
                # Dinamik İvme (Hızlıysan hızlı, yavaşsan ağır ve tutarlı)
                if el_hizi < 40: 
                    dinamik_smooth = 18 # Yavaş hareket, yüksek stabilite (Sniper)
                else:
                    dinamik_smooth = 6  # Hızlı hareket, ekranı çabuk geç

                clocX = plocX + (tx - plocX) / dinamik_smooth
                clocY = plocY + (ty - plocY) / dinamik_smooth

            mouse_x = max(0, min(screen_w, int(clocX)))
            mouse_y = max(0, min(screen_h, int(clocY)))

            pyautogui.moveTo(mouse_x, mouse_y, _pause=False)
            plocX, plocY = clocX, clocY

            # --- SÜRÜKLE VE BIRAK (SOL TIK) ---
            if oran_sol < click_ratio:
                if not drag_active:
                    pyautogui.mouseDown(button='left')
                    drag_active = True
                cv2.circle(img, (int(cx), int(cy)), 12, (0, 255, 0), cv2.FILLED) 
            else:
                if drag_active:
                    pyautogui.mouseUp(button='left')
                    drag_active = False

            # --- SAĞ TIKLAMA ---
            if oran_sag < click_ratio:
                cv2.circle(img, (int(x12), int(y12)), 10, (0, 0, 255), cv2.FILLED)
                pyautogui.rightClick()
                time.sleep(0.2) # Wi-Fi'da kasmayı önlemek için time.sleep kullanıyoruz
            
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Sanal Fare - Mobil Kumanda", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()