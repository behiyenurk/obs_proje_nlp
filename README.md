# 🎓 Okul Yönetim Sistemi - Flask + Firebase

## Proje Tanımı

Bu proje, öğrenci-öğretmen-müdür etkileşimini kolaylaştırmak amacıyla geliştirilen bir **Okul Yönetim Sistemi**dir. Sistem, öğrencilerin akademik notların ve devamsızlıkların takibini kolaylaştırır. Müdür panelinde yer alan grafikler ve yapay zeka destekli doğal dil işleme modülü sayesinde, öğrenci performansı çok boyutlu olarak analiz edilir ve eğitim yönetimine veri odaklı katkı sağlanır.

## Kullanılan Teknolojiler

- **Python** (Flask framework)
- **Firebase Firestore** (Veritabanı olarak)
- **HTML / CSS / JavaScript** (Frontend)
- **Doğal Dil İşleme** (Geri bildirimlerde duygu analizi, geri bildirim özetleme)

## Roller

- **Öğrenci:**  
  - Kendi notlarını ve devamsızlıklarını görüntüleyebilir  

- **Öğretmen:**  
  - Öğrencilerin notlarını (vize, final, quiz) girebilir ve güncelleyebilir. 
  - Devamsızlık bilgisi ekleyebilir.
  - Öğrenci hakkında geri bildirim yazabilir.

- **Müdür:**  
  - Tüm öğrenci verilerini görebilir. (Notlar, devamsızlıklar, geri bildirimler)  
  - Geri bildirimlerde duygu analizi ve genel başarı değerlendirmesi yapabilir.   
  - Grafiklerle analiz ekranı üzerinden öğrencileri takip edebilir.

## Özellikler

- 🔐 Giriş ve Kayıt Sistemi (Rollere özel arayüzler)
- 📝 Not ve Devamsızlık Yönetimi
- 💬 Öğretmen Geri Bildirimleri
- 📈 Öğrenci Başarı Analizi (Not ortalaması, devamsızlık yüzdesi, duygu analizi)
- 📊 Dinamik Grafikler
- 🧠 NLP Tabanlı Geri Bildirim Analizi (Duygu analizi)
- 🔍 Müdür Paneli ile detaylı öğrenci analizi

## Firebase Yapısı

- `users`: Tüm kullanıcılar (öğrenci, öğretmen, müdür)
- `grades`: Öğrencilerin not bilgileri
- `attendance`: Devamsızlık kayıtları
- `feedbacks`: Öğretmen geri bildirimleri

## firebase_config.json dosyası için;

- https://console.firebase.google.com/ adresine gidip Google hesabınızla giriş yapın.
- Var olan projenizi seçin veya sağ üstten “Proje ekle” diyerek yeni proje oluşturun.
- Soldaki menüden "Proje Ayarları"na tıklayın.
- Üst sekmelerden “Hizmet hesapları” (Service Accounts) kısmına geçin.
- Python platformunu seçerek “Yeni özel anahtar oluştur” (Generate New Private Key) butonuna tıklayın.
- Açılan uyarıda “Oluştur” diyerek .json dosyasını indirin. Dosya adını firebase_config.json olarak değiştirin.
- İndirilen dosyayı proje klasörünüzün içine taşıyın.

## Gelecek Planları (Roadmap)

Projeyi daha kullanışlı ve kapsamlı hale getirmek için aşağıdaki özelliklerin eklenmesi planlanmaktadır:
- **Haftalık Ders Programı Modülü**  
  Öğrenciler ve öğretmenler için haftalık ders programlarının görüntülenebileceği, kişisel ders takibine olanak tanıyan modül.
- **Öğrenci ve Öğretmen için Bildirim Sistemi**  
  Not güncellemeleri, devamsızlık bildirimleri ve geri bildirimler için gerçek zamanlı bildirim mekanizması.
- **Doğal Dil İşleme Modülünün Genişletilmesi**  
  Geri bildirim özetleme, öneri sistemi ve gelişmiş duygu analizi ile yapay zeka destekli eğitim rehberliği.

## 📸 Ekran Görüntüleri

### Giriş ve Kayıt Sayfası
<img src="screenshots/giris.png" alt="Giriş Sayfası" width="300"/>
<br>
<img src="screenshots/kaydol.png" alt="Kayıt Sayfası" width="300"/>

### Öğrenci Paneli  
<img src="screenshots/ogrenci_panel.png" alt="Öğrenci Paneli" width="600"/>

### Öğretmen Paneli  
<img src="screenshots/ogretmen_panel.png" alt="Öğretmen Paneli" width="600"/>

### Müdür Paneli  
<img src="screenshots/mudur_panel.png" alt="Müdür Paneli" width="600"/>

### Öğrenci Analiz Sayfası
<img src="screenshots/ogrenci_analiz1.png" alt="Öğrenci Analiz 1" width="600"/>
<br>
<img src="screenshots/ogrenci_analiz2.png" alt="Öğrenci Analiz 2" width="600"/>
