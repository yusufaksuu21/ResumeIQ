[README (1).md](https://github.com/user-attachments/files/25774274/README.1.md)

# 🚀 ResumeIQ – AI Powered Resume Analyzer

**ResumeIQ**, iş başvurularında özgeçmişinizi daha güçlü hale getirmenize yardımcı olan yapay zeka destekli bir CV analiz aracıdır.  
Google Gemini API kullanarak CV'nizi analiz eder, eksik noktaları belirler ve kariyerinizi geliştirmek için öneriler sunar.

Uygulama, CV analizi, ATS uyumluluğu değerlendirmesi ve kişiselleştirilmiş kariyer önerileri üretmek için geliştirilmiştir.

---

# ✨ Features

### Resume Analysis
CV'nizi analiz ederek güçlü ve zayıf yönlerini belirler.

### ATS Compatibility Score
Özgeçmişinizin Applicant Tracking System (ATS) uyumluluğunu değerlendirir.

### Cover Letter Generator
Başvuracağınız pozisyona uygun ön yazı oluşturur.

### Career Development Roadmap
Eksik becerilerinizi geliştirmek için öneriler sunar.

### Resume Comparison
İki farklı CV’yi karşılaştırarak avantaj ve eksiklerini analiz eder.

---

# 🛠 Tech Stack

- Python 3.10+
- Streamlit – Web arayüzü
- Google Gemini API – Yapay zeka analizi
- pdfplumber – PDF CV okuma
- python-docx – DOCX CV işleme
- Matplotlib & WordCloud – Veri görselleştirme

---

# ⚙️ Installation

Projeyi yerel ortamınızda çalıştırmak için:

### 1. Repository'i klonlayın

```bash
git clone https://github.com/yusufaksu21/ResumeIQ.git
cd ResumeIQ
```

### 2. Bağımlılıkları yükleyin

```bash
pip install -r requirements.txt
```

### 3. Environment variables oluşturun

Proje klasöründe `.env` dosyası oluşturun:

```
GEMINI_API_KEY=your_api_key_here
```

### 4. Uygulamayı çalıştırın

```bash
streamlit run app.py
```

---

# 🔐 Security

- API anahtarları **kod içerisinde saklanmaz**
- `.env` ve `.gitignore` ile hassas bilgiler korunur
- Yüklenen CV dosyaları **kalıcı olarak depolanmaz**

---

# 👨‍💻 Developer

**Yusuf Aksu**  
Software Engineering Student  

GitHub:  
https://github.com/yusufaksuu21
Canlı Demo:
https://kariyer-planla.streamlit.app/
