# 🎓 Okul Yönetim Sistemi - Flask + Firebase

Bu proje, öğrenci-öğretmen-müdür etkileşimini kolaylaştırmak amacıyla geliştirilen bir **Okul Yönetim Sistemi**dir. Öğrencilerin notları, devamsızlıkları ve öğretmen geri bildirimleri sistem üzerinden takip edilebilir. Aynı zamanda müdür, öğrenci başarı analizlerini grafik ve yapay zeka destekli analizlerle görüntüleyebilir.

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
-https://console.firebase.google.com/ adresine gidip Google hesabınızla giriş yapın.
-Var olan projenizi seçin veya sağ üstten “Proje ekle” diyerek yeni proje oluşturun.
-Soldaki menüden "Proje Ayarları"na tıklayın.
-Üst sekmelerden “Hizmet hesapları” (Service Accounts) kısmına geçin.
-Python platformunu seçerek “Yeni özel anahtar oluştur” (Generate New Private Key) butonuna tıklayın.
-Açılan uyarıda “Oluştur” diyerek .json dosyasını indirin. Dosya adını firebase_config.json olarak değiştirin.
-İndirilen dosyayı proje klasörünüzün içine taşıyın.
