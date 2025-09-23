import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser as wb
import os
import random
import pyautogui
import pyjokes
import subprocess
import time as t
import openai
import sys
import threading
import re
import queue
from PyQt5 import QtWidgets, QtCore, QtGui
 
# Инициализация голосового движка
engine = pyttsx3.init()
voices = engine.getProperty('voices')
for voice in voices:
    if 'russian' in voice.languages or 'ru' in str(voice.id).lower():
        engine.setProperty('voice', voice.id)
        break

# Скорость речи
engine.setProperty('rate', 180)

speech_queue = queue.Queue()

def speech_worker():
    """Поток для озвучивания сообщений"""
    while True:
        text = speech_queue.get()
        if text is None:
            break
        print(text)
        engine.say(text)
        engine.runAndWait()
        speech_queue.task_done()

# Запуск потока озвучки
speech_thread = threading.Thread(target=speech_worker, daemon=True)
speech_thread.start()

def speak(audio) -> None:
    """Произносит текст (через очередь)"""
    speech_queue.put(audio)

def update_status(self, message):
    """Обновление статуса в главном окне"""
    self.status_label.setText(message)
    QtCore.QCoreApplication.processEvents()  # Принудительное обновление GUI

def time() -> None:
    """Скажи текущее время"""
    current_time = datetime.datetime.now().strftime("%H:%M")
    speak(f"Сейчас {current_time}")

def date() -> None:
    """Скажи текущую дату"""
    months = {
        1: "января", 2: "февраля", 3: "марта", 4: "апреля",
        5: "мая", 6: "июня", 7: "июля", 8: "августа",
        9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
    }
    now = datetime.datetime.now()
    speak(f"Сегодня {now.day} {months[now.month]} {now.year} года")

def wishme() -> None:
    """Приветствие пользователя"""
    hour = datetime.datetime.now().hour
    
    if 4 <= hour < 12:
        speak("Доброе утро!")
    elif 12 <= hour < 16:
        speak("Добрый день!")
    elif 16 <= hour < 24:
        speak("Добрый вечер!")
    else:
        speak("Доброй ночи!")
    
    speak("Я ваш голосовой помощник. Чем могу помочь?")

def takecommand() -> str:
    """Получение голосовой команды"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Слушаю...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return None

    try:
        print("Распознаю...")
        query = r.recognize_google(audio, language="ru-RU")
        print(f"Вы сказали: {query}")
        return query.lower()
    except sr.UnknownValueError:
        speak("Не удалось распознать речь")
        return None
    except sr.RequestError:
        speak("Ошибка сервиса распознавания")
        return None

openai.api_key = ""

def ask_ai(prompt: str) -> str:
    """Запрос к ИИ (ChatGPT)"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка обращения к ИИ: {e}"

def left_mouse_click() -> None:
    """Нажать левую кнопку мыши"""
    pyautogui.click()
    speak("Левый клик выполнен")

def right_mouse_click() -> None:
    """Нажать правую кнопку мыши"""
    pyautogui.rightClick()
    speak("Правый клик выполнен")

def create_text_file() -> None:
    """Создание текстового файла"""
    speak("Как назвать файл?")
    filename = takecommand()
    
    if filename:
        filename = filename.replace(" ", "_") + ".txt"
        speak("Что записать в файл?")
        content = takecommand()
        
        if content:
            try:
                with open(filename, "w", encoding="utf-8") as file:
                    file.write(content)
                speak(f"Файл {filename} успешно создан")
            except Exception as e:
                speak(f"Ошибка при создании файла: {e}")
        else:
            speak("Не удалось распознать содержимое файла")
    else:
        speak("Не удалось распознать название файла")

def open_website(url: str, name: str) -> None:
    """Открытие веб-страницы"""
    try:
        wb.open(url)
        speak(f"Открываю {name}")
    except Exception as e:
        speak(f"Не удалось открыть {name}")

def open_application(app_name: str) -> None:
    """Открытие приложения"""
    apps = {
        "блокнот": "notepad.exe",
        "калькулятор": "calc.exe",
        "пайнт": "mspaint.exe",
        "браузер": "chrome.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "powerpoint": "POWERPNT.EXE"
    }
    
    if app_name in apps:
        try:
            subprocess.Popen(apps[app_name])
            speak(f"Запускаю {app_name}")
        except Exception as e:
            speak(f"Не удалось запустить {app_name}")
    else:
        speak("Не знаю такое приложение")

def search_wikipedia(query: str) -> None:
    """Поиск в Википедии"""
    try:
        speak("Ищу в Википедии...")
        wikipedia.set_lang("ru")
        result = wikipedia.summary(query, sentences=3)
        speak(result)
    except wikipedia.exceptions.DisambiguationError:
        speak("Найдено несколько вариантов. Уточните запрос")
    except wikipedia.exceptions.PageError:
        speak("Ничего не найдено")
    except Exception:
        speak("Произошла ошибка при поиске")

def play_music() -> None:
    """Воспроизведение музыки"""
    music_dir = os.path.expanduser("~\\Music")
    
    if os.path.exists(music_dir):
        songs = [f for f in os.listdir(music_dir) if f.endswith(('.mp3', '.wav'))]
        if songs:
            song = random.choice(songs)
            os.startfile(os.path.join(music_dir, song))
            speak(f"Включаю {os.path.splitext(song)[0]}")
        else:
            speak("В папке Музыка нет музыкальных файлов")
    else:
        speak("Папка Музыка не найдена")

def move_mouse_by_voice_loop() -> None:
    """Многократное перемещение курсором мыши по голосу, пока не скажут 'стоп'"""
    speak("Режим управления курсором активирован. Говорите направление и расстояние, например: 'вверх на 200'. Для выхода скажите 'стоп'.")
    while True:
        direction = takecommand()
        if not direction:
            continue
        if any(word in direction for word in ["стоп", "выход", "закончить", "хватит"]):
            speak("Режим управления курсором завершён.")
            break

        x, y = pyautogui.position()
        screen_width, screen_height = pyautogui.size()
        step = 100  # значение по умолчанию

        match = re.search(r"(\d+)", direction)
        if match:
            step = int(match.group(1))

        if any(word in direction for word in ["вверх", "верх"]):
            pyautogui.moveTo(x, max(0, y - step))
        elif any(word in direction for word in ["вниз", "низ"]):
            pyautogui.moveTo(x, min(screen_height, y + step))
        elif any(word in direction for word in ["влево", "лево", "лева"]):
            pyautogui.moveTo(max(0, x - step), y)
        elif any(word in direction for word in ["вправо", "право", "права"]):
            pyautogui.moveTo(min(screen_width, x + step), y)
        elif any(word in direction for word in ["центр", "центр экрана", "середина", "середина экрана"]):
            pyautogui.moveTo(screen_width // 2, screen_height // 2)
        else:
            speak("Не удалось распознать направление")
            continue
        speak(f"Курсор перемещён на {step} пикселей")

def type_text_by_voice() -> None:
    """Ввод текста с клавиатуры по голосу"""
    speak("Что напечатать?")
    text = takecommand()
    if text:
        pyautogui.typewrite(text)
        speak("Текст напечатан")
    else:
        speak("Не удалось распознать текст")

def take_screenshot() -> None:
    """Сделать скриншот экрана"""
    screenshot_dir = os.path.expanduser("~\\Pictures")
    filename = os.path.join(screenshot_dir, f"screenshot_{int(t.time())}.png")
    try:
        image = pyautogui.screenshot()
        image.save(filename)
        speak(f"Скриншот сохранён как {filename}")
    except Exception as e:
        speak(f"Ошибка при создании скриншота: {e}")

def tell_joke() -> None:
    """Рассказать шутку"""
    try:
        joke = pyjokes.get_joke(language='ru')
        speak(joke)
    except:
        speak("Почему программисты путают Хэллоуин и Рождество? Потому что окт 31 равно дек 25!")

def system_command(command: str) -> None:
    """Системные команды"""
    if "выключи компьютер" in command:
        speak("Выключаю компьютер")
        os.system("shutdown /s /t 1")
    elif "перезагрузи компьютер" in command:
        speak("Перезагружаю компьютер")
        os.system("shutdown /r /t 1")
    elif "режим сна" in command:
        speak("Перевожу компьютер в режим сна")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

def process_command(query):
    """Обработка голосовых команд"""
    if not query:
        return "Не удалось распознать команду"

    # Используем match-case с условиями
    match query:
        case query if any(word in query for word in ["дата", "какое сегодня число", "напомни дату"]):
            date()
            return "Дата озвучена"

        case query if any(word in query for word in ["время", "час", "который час"]):
            time()
            return "Время озвучено"

        case query if any(word in query for word in ["левый клик", "нажми левую кнопку", "кликни мышью", "клик"]):
            left_mouse_click()
            return "Левый клик мыши"
        
        case query if any(word in query for word in ["правый клик", "нажми правую кнопку", "правой кнопкой", "правая кнопка"]):
            right_mouse_click()
            return "Правый клик мыши"
        
        case query if any(word in query for word in ["создай файл", "создать файл", "новый файл"]):
            create_text_file()
            return "Создание файла"

        # Веб-сайты
        case query if any(word in query for word in ["открой ютуб", "ютуб", "YouTube"]):
            open_website("https://youtube.com", "YouTube")
            return "YouTube открыт"
        
        case query if any(word in query for word in ["открой гугл", "google", "гугл"]):
            open_website("https://google.com", "Google")
            return "Google открыт"
        
        case query if any(word in query for word in ["открой вк", "вконтакте"]):
            open_website("https://vk.com", "ВКонтакте")
            return "ВКонтакте открыт"
        
        case query if any(word in query for word in ["открой почту", "почта"]):
            open_website("https://gmail.com", "Gmail")
            return "Gmail открыт"

        # Приложения
        case query if any(word in query for word in ["открой блокнот", "блокнот"]):
            open_application("блокнот")
            return "Блокнот запущен"
        
        case query if any(word in query for word in ["открой калькулятор", "калькулятор"]):
            open_application("калькулятор")
            return "Калькулятор запущен"
        
        case query if any(word in query for word in ["открой paint", "пайнт"]):
            open_application("пайнт")
            return "Paint запущен"

        # Ввод текста с клавиатуры
        case query if any(word in query for word in ["напечатай текст", "введи текст", "напиши текст"]):
            type_text_by_voice()
            return "Ввод текста"

        # Управление курсором мыши
        case query if any(word in query for word in ["перемести курсор", "курсор", "курс","мышь", "мыш"]):
            move_mouse_by_voice_loop()
            return "Управление курсором"

        # Искусственный интеллект
        case query if any(word in query for word in ["искусственный интеллект", "чат гпт", "чатгпт"]):
            speak("Задайте вопрос для искусственного интеллекта")
            ai_query = takecommand()
            if ai_query:
                answer = ask_ai(ai_query)
                speak(answer)
                return "Ответ ИИ получен"
            else:
                speak("Не удалось распознать вопрос")
                return "Не удалось распознать вопрос"
    
        # Поиск
        case query if "википедия" in query:
            search_query = query.replace("википедия", "").strip()
            if search_query:
                search_wikipedia(search_query)
                return "Поиск в Википедии выполнен"
            else:
                speak("Что искать в Википедии?")
                return "Не указан запрос для Википедии"

        # Музыка
        case query if any(word in query for word in ["включи музыку", "музыка", "песня"]):
            play_music()
            return "Музыка включена"

        # Шутки
        case query if any(word in query for word in ["шутка", "пошути", "расскажи шутку"]):
            tell_joke()
            return "Шутка рассказана"
        
        case query if any(word in query for word in ["сделай скриншот", "скриншот", "снимок экрана"]):
            take_screenshot()
            return "Скриншот сделан"
        
        # Word   
        case query if any(word in query for word in ["открой word", "ворд", "word"]):
            open_application("word")
            return "Word запущен"
        
        # PowerPoint
        case query if any(word in query for word in ["открой powerpoint", "powerpoint", "презентация"]):
            open_application("powerpoint")
            return "PowerPoint запущен"
        
        # Системные команды
        case query if any(word in query for word in ["выключи компьютер", "завершение работы"]):
            system_command("выключи компьютер")
            return "Выключение компьютера"
        
        case query if any(word in query for word in ["перезагрузи компьютер", "перезагрузка"]):
            system_command("перезагрузи компьютер")
            return "Перезагрузка компьютера"
        
        case query if any(word in query for word in ["режим сна", "сон", "спящий режим"]):
            system_command("режим сна")
            return "Режим сна активирован"

        # Прощание
        case query if any(word in query for word in ["стоп", "выход", "закройся", "пока", "отключись"]):
            speak("До свидания! Буду рад помочь снова")
            return "Выход из программы"

        case _:
            speak("Не понял команду. Повторите, пожалуйста")
            return "Неизвестная команда"

class VoiceAssistantWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Голосовой помощник")
        self.setGeometry(100, 100, 900, 700)
        
        # Create a central widget
        self.central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        # Layout
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        
        # Установка фонового изображения
        self.set_background()
        
        # Add a label for status
        self.status_label = QtWidgets.QLabel("Добро пожаловать в голосовой помощник!", self)
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 150);
                padding: 15px;
                border-radius: 15px;
                margin: 10px;
            }
        """)
        self.layout.addWidget(self.status_label)
        
        # Add text area for command history
        self.history_text = QtWidgets.QTextEdit(self)
        self.history_text.setReadOnly(True)
        self.history_text.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 200);
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
            }
        """)
        self.layout.addWidget(self.history_text)
        
        # Add buttons
        self.button_layout = QtWidgets.QHBoxLayout()
        
        self.start_button = QtWidgets.QPushButton("🎤 Начать прослушивание", self)
        self.start_button.clicked.connect(self.start_listening)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
        """)
        self.button_layout.addWidget(self.start_button)
        
        self.exit_button = QtWidgets.QPushButton("🚪 Выход", self)
        self.exit_button.clicked.connect(self.close)
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.button_layout.addWidget(self.exit_button)
        
        self.layout.addLayout(self.button_layout)
        
        # Initialize assistant
        self.assistant_thread = None
        wishme()
        self.update_history("Голосовой помощник инициализирован и готов к работе")

    def set_background(self):
        """Установка фонового изображения"""
        try:
            # Попробуйте различные пути к изображениям
            possible_paths = [
                "background.jpg",
                "background.png",
                "wallpaper.jpg",
                "wallpaper.png",
                "фон.jpg",
                "фон.png"
            ]
            
            background_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    background_path = path
                    break
            
            if background_path:
                self.setStyleSheet(f"""
                    VoiceAssistantWindow {{
                        background-image: url({background_path});
                        background-position: center;
                        background-repeat: no-repeat;
                        background-attachment: fixed;
                        background-size: cover;
                    }}
                """)
            else:
                # Градиентный фон если изображение не найдено
                self.setStyleSheet("""
                    VoiceAssistantWindow {
                        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                                  stop: 0 #667eea, stop: 1 #764ba2);
                    }
                """)
        except Exception as e:
            print(f"Ошибка установки фона: {e}")
            # Простой фон в случае ошибки
            self.setStyleSheet("""
                VoiceAssistantWindow {
                    background-color: #2c3e50;
                }
            """)

    def start_listening(self):
        """Запуск прослушивания в отдельном потоке"""
        self.status_label.setText("🎤 Слушаю...")
        self.start_button.setEnabled(False)
        self.update_history("Начато прослушивание...")
        
        # Запуск в отдельном потоке чтобы не блокировать GUI
        self.assistant_thread = threading.Thread(target=self.process_voice_command)
        self.assistant_thread.daemon = True
        self.assistant_thread.start()

    def process_voice_command(self):
        """Обработка голосовой команды"""
        query = takecommand()
        
        if query:
            self.update_history(f"🎤 Распознано: {query}")
            result = process_command(query)
            self.update_history(f"✅ {result}")
        else:
            self.update_history("❌ Не удалось распознать команду")
        
        # Включить кнопку обратно после завершения
        self.start_button.setEnabled(True)
        self.status_label.setText("✅ Готов к прослушиванию")

    def update_history(self, message):
        """Обновление истории команд"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.history_text.append(f"[{timestamp}] {message}")
        
        # Прокрутка к нижней части текстового поля
        cursor = self.history_text.textCursor()
        cursor.movePosition(cursor.End)
        self.history_text.setTextCursor(cursor)

def closeEvent(self, event):
    """Обработка закрытия окна"""
    speak("До свидания!")
    self.update_history("📴 Программа завершена")
    speech_queue.put(None)  # Завершить поток озвучки
    event.accept()

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Установка стиля приложения
    app.setStyle('Fusion')
    
    window = VoiceAssistantWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
