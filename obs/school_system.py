from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, firestore
import io
from io import BytesIO
import base64
import matplotlib.pyplot as plt
from datetime import datetime
from transformers import pipeline
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM, pipeline

######MODELLERİ BURAYA EKLEDİM.
# Duygu analizi modeli (BERT)
sentiment_tokenizer = AutoTokenizer.from_pretrained("savasy/bert-base-turkish-sentiment-cased")
sentiment_model = AutoModelForSequenceClassification.from_pretrained("savasy/bert-base-turkish-sentiment-cased")
sentiment_analyzer = pipeline("sentiment-analysis", model=sentiment_model, tokenizer=sentiment_tokenizer)

# Özetleme modeli (BART)
summarizer_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
summarizer_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")

# Tkinter hatası verdiği için..
import matplotlib
matplotlib.use('Agg')  

# Firebase uygulamasını başlatmaa yeri
cred = credentials.Certificate("firebase_config.json")     
firebase_admin.initialize_app(cred)                            
db = firestore.client()

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'

def generate_custom_id(role):               ###kaydolma kısmında id verme. eğer öğretmense T ile başlayacak müdürse M ile. öğrenciyse direkt id numarası alıyor
    users_ref = db.collection('users')
    if role == 'ogrenci':
        prefix = ''
    elif role == 'ogretmen':
        prefix = 'T'
    elif role == 'mudur':
        prefix = 'M'
    else:
        prefix = 'X'

    existing_ids = [
        doc.id for doc in users_ref.stream()
        if doc.to_dict().get('role') == role and doc.id.startswith(prefix)
    ]

    numbers = []
    for eid in existing_ids:
        try:
            num = int(eid[len(prefix):])
            numbers.append(num)
        except:
            continue

    next_number = max(numbers, default=0) + 1
    return f"{prefix}{next_number}"

@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email')
    password = request.form.get('password')

    users_ref = db.collection('users')
    query = users_ref.where('email', '==', email).stream()
    user = next(query, None)

    if user:
        user_data = user.to_dict()

    if user and check_password_hash(user.to_dict()['password_hash'], password):               ##firebasete parolayı hash şeklinde tuttum.
        session['user_id'] = user.id
        session['user_name'] = user_data['name']
        session['user_role'] = user_data['role']

        if user_data['role'] == 'ogrenci':                                    ##eğer başlangıçta rol olarak öğrenci seçildiyse öğrenci paneline gitsin...
            return redirect(url_for('ogrenci_panel'))
        elif user_data['role'] == 'ogretmen':
            return redirect(url_for('ogretmen_panel'))
        elif user_data['role'] == 'mudur':
            return redirect(url_for('mudur_panel'))
        else:
            return "Tanımsız rol", 403
    else:
        return "Geçersiz giriş bilgileri", 401

###kayıt kısmı
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        branch = request.form.get('branch')

        hashed_pw = generate_password_hash(password)

        users_ref = db.collection('users')
        query = users_ref.where('email', '==', email).stream()     ##aynı mail hesabını kullanamasın diye oluşturdum

        if any(query):
            return "Bu e-posta zaten kayıtlı.", 400

        custom_id = generate_custom_id(role)

        user_data = {
            'name': name,
            'email': email,
            'password_hash': hashed_pw,
            'role': role
        }

        # Eğer öğretmense branşını da alıp kaydet
        if role == 'ogretmen':
            user_data['branch'] = branch

        db.collection('users').document(custom_id).set(user_data)

        return redirect(url_for('login'))

    return render_template('register.html')

##öğgrenci paneli
@app.route('/ogrenci_panel')
def ogrenci_panel():
    if 'user_role' not in session or session['user_role'] != 'ogrenci':
        return redirect('/')

    student_id = session['user_id']
    student_name = session['user_name']

    # Firebase'ten notları al
    grades = {}
    student_ref = db.collection('grades').document(student_id)
    for subject_doc in student_ref.collection('dersler').stream():
        subject_data = subject_doc.to_dict()
        grades[subject_doc.id] = subject_data

    # Devamsızlıkları al
    attendance_ref = db.collection('attendance').document(student_id).collection('Tarih')
    attendance_docs = attendance_ref.stream()

    attendance_data_list = []
    total_absences = 0

    for doc in attendance_docs:
        data = doc.to_dict()
        reason = data.get('reason')
        date = doc.id  # Belge adı tarih ise bunu al
        if reason:
            total_absences += 1
            attendance_data_list.append((date, reason))

    # Toplam ders sayısını 80 belirledim
    total_classes = 80
    absence_rate = (total_absences / total_classes) * 100 if total_classes else 0

    graph_url = create_pie_chart(total_absences, total_classes)        ##devamsızlık verisini pie chartta gösterir.

    return render_template('ogrenci_panel.html', 
        grades=grades, 
        attendance=attendance_data_list,
        graph_url=graph_url
    )


##ogretmen paneli
@app.route('/ogretmen_panel', methods=['GET'])
def ogretmen_panel():
    if 'user_role' not in session or session['user_role'] != 'ogretmen':
        return redirect('/')

    per_page = 5  # Sayfa başına gösterilecek not sayısı
    page = request.args.get('page', 1, type=int)  # URL'den gelen sayfa numarasını al

    grades = []
    students_ref = db.collection('users').where('role', '==', 'ogrenci').stream()
    students = [{'id': doc.id, 'name': doc.to_dict().get('name')} for doc in students_ref]

    # Sayfa başına verileri almak için limit ve offset kullanıyoruz
    start_index = (page - 1) * per_page  # Offset hesaplama
    end_index = start_index + per_page  # Limit

    for student in students:
        student_id = student['id']
        student_name = student['name']
        
        student_grades_ref = db.collection('grades').document(student_id).collection('dersler').stream()      ##not koleksiyonuu

        for subject_doc in student_grades_ref:
            subject_data = subject_doc.to_dict()
            grade = {                                                  #koleksiyona bu verilerle birlikte eklenyior. 
                'student_name': student_name,
                'subject': subject_doc.id,
                'Vize': subject_data.get('Vize', 'Not yok'),
                'Final': subject_data.get('Final', 'Not yok'),
                'Quiz': subject_data.get('Quiz', 'Not yok'),
                'student_id': student_id
            }
            grades.append(grade)

    #1 sayfada belirli sayıda not göstermesi için ekleidm.
    paged_grades = grades[start_index:end_index]
    
    # Sonraki sayfa var mı kontrolü yapılıyor
    next_page = None
    if len(grades) > end_index:
        next_page = page + 1

    return render_template('ogretmen_panel.html', grades=paged_grades, students=students, page=page, next_page=next_page)

##not güncelleme fonksiyonu
@app.route('/ogretmen/guncelle/<student_id>/<subject>', methods=['POST'])
def update_grade(student_id, subject):
    if 'user_role' not in session or session['user_role'] != 'ogretmen':
        return redirect('/')

    new_grade = request.form['new_grade']
    grade_type = request.form['grade_type']  # Vize, Final, Quiz

    # Öğrencinin dersindeki notu güncelleme (koleksiyon)
    subject_ref = db.collection('grades').document(student_id).collection('Dersler').document(subject)

    # Notu güncelleme 
    subject_ref.update({
        grade_type: new_grade
    })

    return redirect(url_for('ogretmen_panel'))

from datetime import datetime, timedelta



###öğrenciye not ekleme fonksiyonu id, ders,not ve hangi sınav olduğu verisini alacak. 
@app.route('/add_grade', methods=['POST'])
def add_grade():
    if 'user_role' not in session or session['user_role'] != 'ogretmen':
        return redirect('/')

    student_id = request.form['student_id']
    subject = request.form['subject']
    score = request.form['score']
    grade_type = request.form['grade_type']  # Vize, Final, Quiz

    # Öğrenci adına göre koleksiyon açılıyorr
    student_ref = db.collection('grades').document(student_id)
    subject_ref = student_ref.collection('dersler').document(subject)

    # Not ekle veya güncelle kısmı.
    subject_ref.set({
        grade_type: score 
    }, merge=True)  

    return redirect(url_for('ogretmen_panel'))


###devamsızlık eklemek için fonksiyon  id, sebep ve tarih alıyoruz
@app.route('/add_attendance', methods=['POST'])
def add_attendance():
    if 'user_role' not in session or session['user_role'] != 'ogretmen':          
        return redirect('/')

    student_id = request.form['student_id']
    date = request.form['date']
    reason = request.form['reason']

    student_doc = db.collection('users').document(student_id).get()
    student_data = student_doc.to_dict() if student_doc.exists else {}
    student_name = student_data.get('name', 'Bilinmiyor')

    attendance_ref = db.collection('attendance').document(student_id).collection('Tarih').document(date)     ##açılan firebase koleksiyonu

    attendance_ref.set({                             ##firebase'e bu şekilde kaydedilecek. tarih verisini de alıcak.
        'student_id': student_id,
        'student_name': student_name,
        'reason': reason,
        'date' : date
    })

    return redirect(url_for('ogretmen_panel'))


#geri bildirim eklemek için
@app.route('/ogretmen/gorus', methods=['POST'])
def ogretmen_gorus():
    if 'user_role' not in session or session['user_role'] != 'ogretmen':
        return redirect('/')

    student_id = request.form['ogrenci']
    subject = request.form['ders']
    message = request.form['mesaj']
    teacher_id = session.get('user_id', 'Unknown')  # Öğretmen ID
    teacher_name = session.get('user_name')

    # Duygu analizi yap
    sentiment = sentiment_analysis_bert(message)  # BERT ile duygu analizi

    # Öğrenci verisini al
    student_doc = db.collection('users').document(student_id).get()
    student_data = student_doc.to_dict() if student_doc.exists else {}
    student_name = student_data.get('name', 'Bilinmiyor')

    # Firebase'e geri bildirim kaydet
    feedback_ref = db.collection('feedbacks').document(student_id).collection('Dersler').document(subject)    ##geri bildirim koleksiyonu
    feedback_ref.set({                                                #geri bildirim ile birlikte eklenen bilgiler
        'message': message,
        'sentiment': sentiment,  # BERT ile analiz edilen duygu
        'student_id': student_id,
        'subject': subject,
        'teacher_id': teacher_id,
        'teacher_name': teacher_name,
        'date': datetime.now().strftime('%Y-%m-%d')
    })

    return redirect(url_for('ogretmen_panel'))

 ##üdür panelii
@app.route('/mudur_panel', methods=['GET', 'POST'])
def mudur_panel():
    if 'user_role' not in session or session['user_role'] != 'mudur':
        return redirect(url_for('login'))

    students_ref = db.collection('users').where('role', '==', 'ogrenci').stream()
    students = [{'id': doc.id, **doc.to_dict()} for doc in students_ref]

    grades = []
    attendance = []
    feedbacks = []

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        data_type = request.form.get('data_type')

        if data_type == 'grades':
            dersler_ref = db.collection('grades').document(student_id).collection('dersler').stream()
            for doc in dersler_ref:
                data = doc.to_dict()
                grades.append([
                    student_id,
                    doc.id,
                    data.get('Vize', '-'),
                    data.get('Final', '-'),
                    data.get('Quiz', '-')
                ])

        elif data_type == 'attendance':
            tarih_ref = db.collection('attendance').document(student_id).collection('Tarih').stream()
            for doc in tarih_ref:
                data = doc.to_dict()
                attendance.append([
                    student_id,
                    data.get('date', '-'),
                    data.get('reason', '-')
                ])
        
        elif data_type == 'feedback':
            ders_ref = db.collection('feedbacks').document(student_id).collection('Dersler').stream()
            for doc in ders_ref:
                data = doc.to_dict()
                feedbacks.append([
                    student_id,
                    data.get('message', '-'),
                    data.get('subject', '-'),
                    data.get('teacher_id', '-')
                ])

    return render_template('mudur_panel.html', 
                           students=students, 
                           grades=grades, 
                           attendance=attendance, 
                           feedbacks=feedbacks)



###müdür panrlinde öğrencinin analizini istedikten sonra açılacak sayfa fonksiyonu
@app.route('/ogrenci_analiz', methods=['GET'])
def ogrenci_analiz():
    student_id = request.args.get('student_id')
    student_name = request.args.get('student_name')
    
    student_ref = db.collection('users').document(student_id)
    student = student_ref.get()

    if not student.exists:
        return "Öğrenci bulunamadı", 404

    student_data = student.to_dict()
    student_name = student_data['name']

    # Ders notları...koleksiyonu
    grades_ref = db.collection('grades').document(student_id).collection('dersler')
    grades_data = {grade.id: grade.to_dict() for grade in grades_ref.stream()}

    # Devamsızlıklar...koleksiyonu
    attendance_ref = db.collection('attendance').document(student_id).collection('Tarih')
    attendance_data = [absence.to_dict() for absence in attendance_ref.stream()]

    # Feedback ve duygu analizi
    feedbacks_ref = db.collection('feedbacks').document(student_id).collection('Dersler').stream()            ##geri bildirim koleksioynu
    feedbacks = [] 
    sentiments = {'olumlu': 0, 'olumsuz': 0}

    last_month = datetime.now() - timedelta(days=30)
    total_last_month = 0  # Son 1 aydaki toplam yorum sayısı

    for doc in feedbacks_ref:
        data = doc.to_dict()
        message = data.get('message', '')
        sentiment = data.get('sentiment')

        # Tarih kontrolü (formatı kendimiz de ayarlayabiliriz)
        tarih_str = data.get('date')
        if tarih_str:
            try:
                tarih_dt = datetime.strptime(tarih_str, "%Y-%m-%d")
                if tarih_dt >= last_month:
                    total_last_month += 1
                    if sentiment == 'olumlu':
                        sentiments['olumlu'] += 1
                    elif sentiment == 'olumsuz':
                        sentiments['olumsuz'] += 1
            except:
                pass

        feedbacks.append({
            'subject': data.get('subject', doc.id),
            'message': message,
            'teacher_id': data.get('teacher_id', ''),
            'teacher_name': data.get('teacher_name', ''),
            'sentiment': sentiment,
            'date': tarih_str
        })

    # Özet mesaj oluşturma kısmııı
    sentiment_summary = f"Bu öğrenci için son 1 ayda yapılan {total_last_month} yorumdan " \
                        f"{sentiments['olumlu']}’i olumlu, {sentiments['olumsuz']}’i olumsuzdur "

    fig, ax = plt.subplots()
    duygular = ['Olumlu', 'Olumsuz']
    yorum_sayilari = [sentiments['olumlu'], sentiments['olumsuz']]
    ax.bar(duygular, yorum_sayilari, color=['green', 'red'])

    ax.set_title("Duygu Analizi Özeti")
    ax.set_xlabel("Duygu Türü")
    ax.set_ylabel("Yorum Sayısı")

    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()

    # Sadece son 1 ayın geri bildirim mesajlarını toplayacak
    feedback_messages = []
    for fb in feedbacks:
        tarih_str = fb.get('date')
        try:
            if tarih_str and datetime.strptime(tarih_str, "%Y-%m-%d") >= last_month:
                feedback_messages.append(fb['message'])
        except:
            pass

    # Özetleme fonksiyonunu çağır
    feedback_summary = summarize_feedbacks(feedback_messages)

    return render_template('ogrenci_analiz.html',
                           student_id=student_id,
                           student_name=student_name,
                           grades=grades_data,
                           attendance=attendance_data,
                           sentiment_data=sentiments,
                           sentiment_summary=sentiment_summary,
                           feedback_summary=feedback_summary,
                           sentiment_image=img_base64,
                           feedbacks=feedbacks)


def sentiment_analysis_bert(message):
    result = sentiment_analyzer(message)
    label = result[0]['label'].lower()  
    
    if 'positive' in label:
        return 'olumlu'
    elif 'negative' in label: 
        return 'olumsuz'
    else:
        return 'Bilinmeyen'  # Diğer durumlar için


##özetleme kısmı için. 
def summarize_feedbacks(feedback_messages):
    full_text = " ".join(feedback_messages)
    if len(full_text) > 1024:
        full_text = full_text[:1024]

    try:
        inputs = summarizer_tokenizer.encode(full_text, return_tensors="pt", max_length=1024, truncation=True)

        summary_ids = summarizer_model.generate(                        ##buradaki değerleri değiştirerek daha uzun veya daha kısa özetleme yapılabilir.
            inputs,
            max_length=200,
            min_length=50,
            length_penalty=1.0,
            num_beams=6,
            early_stopping=True
        )

        summary = summarizer_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

    except Exception as e:
        return f"Özetleme başarısız: {str(e)}"

#grafik fonksiyonu. devamsızlık için
def create_pie_chart(total_absences, total_classes):
    import matplotlib.pyplot as plt
    import io
    import base64

    labels = ['Devamsızlık', 'Katılım']
    sizes = [total_absences, total_classes - total_absences]
    colors = ['#ff9999', '#66b3ff']

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return graph_url

#duygu grafiği
def create_sentiment_pie_chart(sentiment_data):
    import matplotlib.pyplot as plt
    import io
    import base64

    # duygu verilerini al
    labels = ['Olumlu', 'Olumsuz']
    sizes = [sentiment_data['olumlu'], sentiment_data['olumsuz']]
    colors = ['#2ecc71', '#e74c3c']  # Olumlu = Yeşil, Olumsuz = Kırmızı olacak

    # Grafik oluşturma
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    sentiment_graph_url = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()

    return sentiment_graph_url

##çıkış
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
    