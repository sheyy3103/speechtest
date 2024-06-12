# Import các thư viện cần thiết
import speech_recognition as sr
from gtts import gTTS
import os
import json
from playsound import playsound
from datetime import datetime
import matplotlib.pyplot as plt

# Đường dẫn tệp lưu trữ tiến trình học
PROGRESS_FILE = 'progress.json'

# Hàm chuyển văn bản thành giọng nói và phát âm thanh
def speak(text):
    tts = gTTS(text=text, lang='en')
    filename = "voice.mp3"
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

# Hàm nhận diện giọng nói từ micro
def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)

    try:
        response = recognizer.recognize_google(audio)
        return response.lower()
    except sr.RequestError:
        return "API unavailable"
    except sr.UnknownValueError:
        return "Unable to recognize speech"

# Hàm tải tiến trình từ tệp JSON
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as file:
            return json.load(file)
    return {"sessions": [], "words": {}}

# Hàm lưu tiến trình vào tệp JSON
def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as file:
        json.dump(progress, file, indent=4)

# Hàm thực hành một từ cụ thể
def practice_word(word, progress):
    print(f"Please say the word: {word}")
    speak(f"Please say the word: {word}")

    user_response = recognize_speech_from_mic()
    print(f"You said: {user_response}")

    if user_response == word:
        print("Correct!")
        speak("Correct!")
        result = "Correct"
    else:
        print(f"Incorrect, the correct word was {word}")
        speak(f"Incorrect, the correct word was {word}")
        result = "Incorrect"

    if word not in progress:
        progress[word] = {"attempts": 0, "correct": 0}
    
    progress[word]["attempts"] += 1
    if result == "Correct":
        progress[word]["correct"] += 1

    return result

# Hàm thực hành danh sách các từ
def practice_words(words, progress):
    session = {"start_time": datetime.now().isoformat(), "words": []}
    for word in words:
        result = practice_word(word, progress)
        session["words"].append({"word": word, "result": result})
    session["end_time"] = datetime.now().isoformat()
    progress["sessions"].append(session)
    save_progress(progress)

# Hàm hiển thị tiến trình học
def display_progress(progress):
    print("\nYour progress:")
    for word, stats in progress["words"].items():
        print(f"{word}: {stats['correct']} correct out of {stats['attempts']} attempts")

    print("\nSession Details:")
    for session in progress["sessions"]:
        start_time = datetime.fromisoformat(session["start_time"]).strftime('%H:%M:%S %d/%m/%Y')
        end_time = datetime.fromisoformat(session["end_time"]).strftime('%H:%M:%S %d/%m/%Y')
        print(f"Session from {start_time} to {end_time}:")
        for word in session["words"]:
            print(f"  {word['word']}: {word['result']}")

# Hàm vẽ biểu đồ tiến trình học
def plot_progress(progress):
    session_dates = []
    accuracy_rates = []

    for session in progress["sessions"]:
        session_dates.append(datetime.fromisoformat(session["start_time"]))
        correct = sum(1 for word in session["words"] if word["result"] == "Correct")
        total = len(session["words"])
        accuracy_rate = (correct / total) * 100 if total > 0 else 0
        accuracy_rates.append(accuracy_rate)

    plt.figure(figsize=(10, 5))
    plt.plot(session_dates, accuracy_rates, marker='o', linestyle='-')
    plt.xlabel('Date')
    plt.ylabel('Accuracy Rate (%)')
    plt.title('Learning Progress Over Time')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Hàm chính của ứng dụng học ngôn ngữ
def language_learning_app():
    progress = load_progress()
    words = {
        "basic": ["hello", "world", "computer", "science", "language"],
        "advanced": ["algorithm", "database", "infrastructure", "optimization", "artificial intelligence"],
        "animals": ["cat", "dog", "elephant", "tiger", "lion", "giraffe", "zebra", "kangaroo", "panda", "dolphin"],
        "fruits": ["apple", "banana", "cherry", "date", "grape", "kiwi", "lemon", "mango", "orange", "strawberry"],
        "colors": ["red", "blue", "green", "yellow", "purple", "orange", "black", "white", "pink", "brown"],
        "jobs": ["doctor", "engineer", "teacher", "nurse", "pilot", "chef", "artist", "lawyer", "farmer", "firefighter"],
        "weather": ["sunny", "rainy", "cloudy", "stormy", "windy", "snowy", "foggy", "hot", "cold", "warm"],
        "food": ["bread", "rice", "chicken", "fish", "beef", "pasta", "salad", "soup", "cake", "cookie"]
    }

    print("Choose a difficulty level: basic, advanced, animals, fruits, colors, jobs, weather, food or freestyle.")
    level = input("Enter your choice: ").strip().lower()

    if level == "freestyle":
        session = {"start_time": datetime.now().isoformat(), "words": []}
        while True:
            word = input("Enter the word you want to learn: ").strip().lower()
            result = practice_word(word, progress)
            session["words"].append({"word": word, "result": result})
            if input("Continue? (y/n): ").strip().lower() == 'n':
                break
        session["end_time"] = datetime.now().isoformat()
        progress["sessions"].append(session)
        save_progress(progress)
    else:
        if level not in words:
            print("Invalid choice. Defaulting to basic level.")
            level = "basic"
        practice_words(words[level], progress)

    display_progress(progress)
    plot_progress(progress)

# Chạy ứng dụng nếu là chương trình chính
if __name__ == "__main__":
    language_learning_app()