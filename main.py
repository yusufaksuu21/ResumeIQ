from google import genai
from config import API_KEY

client = genai.Client(api_key=API_KEY)

print("Chatbot başlatıldı. Çıkmak için q yaz.")

while True:
    user_input = input("Sen: ")

    if user_input.lower() == "q":
        break

    prompt = f"""
Sen yazılım mühendisliği öğrencilerine yardım eden bir asistansın.

Sadece şu konularda cevap ver:
- Python
- Yapay zeka
- NLP
- Staj önerileri
- Programlama öğrenme

Soru: {user_input}
"""

    response = client.models.generate_content(
      model="gemini-2.5-flash",
        contents=prompt
    )

    print("Bot:", response.text)