# Import các thư viện cần thiết
import speech_recognition as sr  # Nhận diện giọng nói
from gtts import gTTS  # Chuyển văn bản thành giọng nói
import os  # Các thao tác với hệ điều hành
import json  # Làm việc với JSON để lưu trữ và đọc dữ liệu
from playsound import playsound  # Phát âm thanh
from datetime import datetime  # Làm việc với thời gian và ngày tháng
import matplotlib.pyplot as plt  # Thư viện vẽ biểu đồ

# Đường dẫn đến tệp lưu trữ tiến trình học
PROGRESS_FILE = 'progress.json'

# Hàm chuyển văn bản thành giọng nói và phát âm thanh
def speak(text):
    tts = gTTS(text=text, lang='en')  # Chuyển văn bản thành giọng nói
    filename = "voice.mp3"  # Tên tệp âm thanh
    tts.save(filename)  # Lưu giọng nói vào tệp âm thanh
    playsound(filename)  # Phát âm thanh
    os.remove(filename)  # Xóa tệp sau khi phát xong để dọn dẹp

# Hàm nhận diện giọng nói từ micro
def recognize_speech_from_mic():
    recognizer = sr.Recognizer()  # Tạo đối tượng nhận diện
    mic = sr.Microphone()  # Tạo đối tượng micro

    with mic as source:  # Sử dụng micro làm nguồn âm thanh
        recognizer.adjust_for_ambient_noise(source)  # Điều chỉnh theo tiếng ồn xung quanh
        print("Listening...")  # In thông báo đang nghe
        audio = recognizer.listen(source)  # Nghe và lưu âm thanh

    try:
        # Sử dụng API của Google để nhận diện giọng nói
        response = recognizer.recognize_google(audio)
        return response.lower()  # Trả về kết quả nhận diện đã chuyển thành chữ thường
    except sr.RequestError:
        return "API unavailable"  # Lỗi khi API không có sẵn
    except sr.UnknownValueError:
        return "Unable to recognize speech"  # Lỗi khi không thể nhận diện giọng nói

# Hàm tải tiến trình từ tệp JSON
def load_progress():
    if os.path.exists(PROGRESS_FILE):  # Kiểm tra nếu tệp tồn tại
        with open(PROGRESS_FILE, 'r') as file:  # Mở tệp để đọc
            return json.load(file)  # Đọc dữ liệu từ tệp và trả về
    return {"sessions": [], "words": {}}  # Trả về tiến trình mặc định nếu tệp không tồn tại

# Hàm lưu tiến trình vào tệp JSON
def save_progress(progress):
    with open(PROGRESS_FILE, 'w') as file:  # Mở tệp để ghi
        json.dump(progress, file, indent=4)  # Lưu dữ liệu vào tệp với định dạng đẹp

# Hàm thực hành một từ cụ thể
def practice_word(word, progress):
    print(f"Please say the word: {word}")  # Yêu cầu người dùng nói từ cần học
    speak(f"Please say the word: {word}")  # Phát âm từ cần học

    user_response = recognize_speech_from_mic()  # Nhận diện giọng nói của người dùng
    print(f"You said: {user_response}")  # In ra kết quả nhận diện

    if user_response == word:  # Kiểm tra nếu người dùng nói đúng từ
        print("Correct!")  # Thông báo đúng
        speak("Correct!")  # Phát âm thông báo đúng
        result = "Correct"  # Ghi nhận kết quả là đúng
    else:
        print(f"Incorrect, the correct word was {word}")  # Thông báo sai và từ đúng
        speak(f"Incorrect, the correct word was {word}")  # Phát âm thông báo sai
        result = "Incorrect"  # Ghi nhận kết quả là sai

    # Cập nhật tiến trình học từ
    if word not in progress:
        progress[word] = {"attempts": 0, "correct": 0}
    
    progress[word]["attempts"] += 1  # Tăng số lần thử
    if result == "Correct":
        progress[word]["correct"] += 1  # Tăng số lần đúng

    return result  # Trả về kết quả

# Hàm thực hành danh sách các từ
def practice_words(words, progress):
    session = {"start_time": datetime.now().isoformat(), "words": []}  # Tạo phiên học mới
    for word in words:  # Duyệt qua từng từ trong danh sách
        result = practice_word(word, progress)  # Thực hành từ và lấy kết quả
        session["words"].append({"word": word, "result": result})  # Ghi lại kết quả của từ trong phiên học
    session["end_time"] = datetime.now().isoformat()  # Ghi lại thời gian kết thúc phiên học
    progress["sessions"].append(session)  # Lưu phiên học vào tiến trình
    save_progress(progress)  # Lưu tiến trình vào tệp

# Hàm hiển thị tiến trình học
def display_progress(progress):
    print("\nYour progress:")  # In tiêu đề
    for word, stats in progress["words"].items():  # Duyệt qua từng từ và thống kê của từ
        print(f"{word}: {stats['correct']} correct out of {stats['attempts']} attempts")  # In kết quả

    print("\nSession Details:")  # In tiêu đề chi tiết phiên học
    for session in progress["sessions"]:  # Duyệt qua từng phiên học
        start_time = datetime.fromisoformat(session["start_time"]).strftime('%H:%M:%S %d/%m/%Y')
        end_time = datetime.fromisoformat(session["end_time"]).strftime('%H:%M:%S %d/%m/%Y')
        print(f"Session from {start_time} to {end_time}:")  # In thời gian của phiên học
        for word in session["words"]:  # Duyệt qua từng từ trong phiên học
            print(f"  {word['word']}: {word['result']}")  # In kết quả của từng từ

# Hàm vẽ biểu đồ tiến trình học
def plot_progress(progress):
    session_dates = []  # Danh sách ngày của các phiên học
    accuracy_rates = []  # Danh sách tỷ lệ chính xác của các phiên học

    for session in progress["sessions"]:  # Duyệt qua từng phiên học
        session_dates.append(datetime.fromisoformat(session["start_time"]))  # Thêm ngày bắt đầu của phiên học
        correct = sum(1 for word in session["words"] if word["result"] == "Correct")  # Đếm số từ đúng
        total = len(session["words"])  # Tổng số từ
        accuracy_rate = (correct / total) * 100 if total > 0 else 0  # Tính tỷ lệ chính xác
        accuracy_rates.append(accuracy_rate)  # Thêm tỷ lệ chính xác vào danh sách

    plt.figure(figsize=(10, 5))  # Thiết lập kích thước biểu đồ
    plt.plot(session_dates, accuracy_rates, marker='o', linestyle='-')  # Vẽ đường biểu diễn tỷ lệ chính xác
    plt.xlabel('Date')  # Nhãn trục X
    plt.ylabel('Accuracy Rate (%)')  # Nhãn trục Y
    plt.title('Learning Progress Over Time')  # Tiêu đề biểu đồ
    plt.grid(True)  # Hiển thị lưới
    plt.xticks(rotation=45)  # Xoay nhãn trục X
    plt.tight_layout()  # Điều chỉnh bố cục
    plt.show()  # Hiển thị biểu đồ

# Hàm chính của ứng dụng học ngôn ngữ
def language_learning_app():
    progress = load_progress()  # Tải tiến trình học từ tệp
    # Danh sách các từ để học theo chủ đề
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

    # Lựa chọn mức độ học
    print("Choose a difficulty level: basic, advanced, animals, fruits, colors, jobs, weather, food or freestyle.")
    level = input("Enter your choice: ").strip().lower()

    if level == "freestyle":  # Nếu người dùng chọn freestyle
        session = {"start_time": datetime.now().isoformat(), "words": []}  # Tạo phiên học mới
        while True:
            word = input("Enter the word you want to learn: ").strip().lower()  # Yêu cầu nhập từ cần học
            result = practice_word(word, progress)  # Thực hành từ và lấy kết quả
            session["words"].append({"word": word, "result": result})  # Ghi lại kết quả
            if input("Continue? (y/n): ").strip().lower() == 'n':  # Hỏi người dùng có tiếp tục không
                break
        session["end_time"] = datetime.now().isoformat()  # Ghi lại thời gian kết thúc phiên học
        progress["sessions"].append(session)  # Lưu phiên học vào tiến trình
        save_progress(progress)  # Lưu tiến trình vào tệp
    else:  # Nếu người dùng chọn mức độ cố định
        if level not in words:  # Kiểm tra mức độ hợp lệ
            print("Invalid choice. Defaulting to basic level.")  # Thông báo nếu chọn sai mức độ
            level = "basic"
        practice_words(words[level], progress)  # Thực hành các từ theo mức độ

    display_progress(progress)  # Hiển thị tiến trình học
    plot_progress(progress)  # Vẽ biểu đồ tiến trình học

# Chạy ứng dụng nếu là chương trình chính
if __name__ == "__main__":
    language_learning_app()