import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
import platform
import winsound
import requests
from bs4 import BeautifulSoup
import threading
import webbrowser
from docx import Document  # Для .docx
import pyth  # Для .rtf

root = tk.Tk()
root.title("Ридли")
root.state('zoomed')  # Разворачивание на весь экран

# Глобальные переменные
original_text = ""
stage = 1
case_sensitive = True
punctuation_sensitive = True
delay_time = 6
font_size = 18
auto_clear = True
bg_color = "#F5F5F4"
text_bg_color = "#FFFFFF"
button_color = "#D9E7F4"
text_color = "#333333"

# Переменные для режима "По строкам"
lines = []
current_line = 0
line_stage = 1

# Переменные для режима "По абзацам" (бывшие "Четверостишья")
quatrains = []
current_quatrain = 0

# Пастельные цвета для фона
pastel_colors = {
    "Светло-серый": "#F5F5F5",
    "Светло-голубой": "#D9E7F4",
    "Светло-зелёный": "#E0F4E0",
    "Светло-розовый": "#F4E0E7",
    "Светло-бежевый": "#F5E9D9",
    "Светло-фиолетовый": "#E9E0F4"
}

# Спокойные цвета для текста
text_colors = {
    "Тёмно-серый": "#333333",
    "Тёмно-синий": "#2F4858",
    "Тёмно-зелёный": "#3A5F3A",
    "Коричневый": "#5C4033",
    "Тёмно-фиолетовый": "#4B3A5F",
    "Чёрный": "#000000"
}

def load_text_from_file():
    global original_text, lines, current_line, line_stage, quatrains, current_quatrain
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = None
        supported_extensions = ['.txt', '.docx', '.rtf', '.md', '.text']
        for ext in supported_extensions:
            potential_path = os.path.join(script_dir, f"stih{ext}")
            if os.path.exists(potential_path):
                file_path = potential_path
                break
        
        if not file_path:
            raise FileNotFoundError("Файл stih с поддерживаемым расширением не найден")

        # Чтение текста в зависимости от формата
        if file_path.endswith('.txt') or file_path.endswith('.text') or file_path.endswith('.md'):
            with open(file_path, "r", encoding="utf-8") as file:
                original_text = file.read().strip()
        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            original_text = "\n".join([para.text for para in doc.paragraphs]).strip()
        elif file_path.endswith('.rtf'):
            with open(file_path, "r", encoding="utf-8") as file:
                rtf_content = file.read()
                original_text = pyth.rtf_to_text(rtf_content).strip()

        # Деление на строки
        lines = [line.strip() for line in original_text.split('\n') if line.strip()]
        current_line = 0
        line_stage = 1

        # Деление на абзацы (от красной строки до красной строки или по 4 строки)
        if "\n\n" in original_text:
            quatrains = [block.strip() for block in original_text.split("\n\n") if block.strip()]
        else:
            temp_lines = original_text.split('\n')
            quatrains = ['\n'.join(temp_lines[i:i+4]) for i in range(0, len(temp_lines), 4)]
        current_quatrain = 0

        # Обновление интерфейса
        sample_text.config(state="normal")
        sample_text.delete("1.0", tk.END)
        sample_text.insert(tk.END, original_text)
        sample_text.config(state="disabled")
        
        if lines:
            line_sample_text.config(state="normal")
            line_sample_text.delete("1.0", tk.END)
            line_sample_text.insert(tk.END, lines[current_line])
            line_sample_text.config(state="disabled")
        else:
            line_sample_text.config(state="normal")
            line_sample_text.delete("1.0", tk.END)
            line_sample_text.insert(tk.END, "Текст пуст")
            line_sample_text.config(state="disabled")
        
        if quatrains:
            quatrain_sample_text.config(state="normal")
            quatrain_sample_text.delete("1.0", tk.END)
            quatrain_sample_text.insert(tk.END, quatrains[current_quatrain])
            quatrain_sample_text.config(state="disabled")
        else:
            quatrain_sample_text.config(state="normal")
            quatrain_sample_text.delete("1.0", tk.END)
            quatrain_sample_text.insert(tk.END, "Текст пуст")
            quatrain_sample_text.config(state="disabled")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")
        original_text = ""
        lines = []
        quatrains = []
        sample_text.config(state="normal")
        sample_text.delete("1.0", tk.END)
        sample_text.insert(tk.END, "Ошибка загрузки текста")
        sample_text.config(state="disabled")
        line_sample_text.config(state="normal")
        line_sample_text.delete("1.0", tk.END)
        line_sample_text.insert(tk.END, "Ошибка загрузки текста")
        line_sample_text.config(state="disabled")
        quatrain_sample_text.config(state="normal")
        quatrain_sample_text.delete("1.0", tk.END)
        quatrain_sample_text.insert(tk.END, "Ошибка загрузки текста")
        quatrain_sample_text.config(state="disabled")

def play_sound():
    try:
        winsound.Beep(37, 100)
        winsound.PlaySound("click.wav", winsound.SND_ASYNC | winsound.SND_FILENAME)
    except Exception:
        pass

def play_sound1():
    try:
        winsound.Beep(37, 100)
        winsound.PlaySound("click1.wav", winsound.SND_ASYNC | winsound.SND_FILENAME)
    except Exception:
        pass

def play_click_sound():
    try:
        winsound.PlaySound("click2.wav", winsound.SND_ASYNC | winsound.SND_FILENAME)
    except Exception:
        pass

def check_input():
    global stage
    user_input = text_widget.get("1.0", tk.END).strip()
    text_to_compare = original_text

    if not case_sensitive:
        user_input = user_input.lower()
        text_to_compare = text_to_compare.lower()
    if not punctuation_sensitive:
        for punct in ".,!?;:-—\"'()[]{}":
            user_input = user_input.replace(punct, "")
            text_to_compare = text_to_compare.replace(punct, "")

    if user_input == text_to_compare:
        play_sound()
        if stage == 1:
            style.configure("TButton", background="green")
            check_button.config(text="Правильно!")
            root.after(delay_time * 1000, proceed_to_stage_2)
        elif stage == 2:
            style.configure("TButton", background="green")
            check_button.config(text="Успех!")
            root.after(delay_time * 1000, finish_task)
    else:
        play_sound1()
        style.configure("TButton", background="red")
        check_button.config(text="Ошибка!")
        root.after(delay_time * 1000, reset_after_error)

def proceed_to_stage_2():
    global stage
    stage = 2
    sample_text.config(state="normal")
    sample_text.delete("1.0", tk.END)
    sample_text.config(state="disabled")
    text_widget.delete("1.0", tk.END)
    status_label.config(text="Введи текст по памяти")
    style.configure("TButton", background=button_color)
    check_button.config(text="Проверить память")

def finish_task():
    status_label.config(text="Правильно! Можешь начать заново")
    text_widget.delete("1.0", tk.END)
    style.configure("TButton", background=button_color)
    check_button.config(text="Проверить", state=tk.DISABLED)
    reset_button.config(state=tk.NORMAL)

def reset_after_error():
    global stage
    if stage == 1:
        status_label.config(text="Нет, неправильно. Попробуй ещё")
        if auto_clear:
            text_widget.delete("1.0", tk.END)
    elif stage == 2:
        stage = 1
        sample_text.config(state="normal")
        sample_text.delete("1.0", tk.END)
        sample_text.insert(tk.END, original_text)
        sample_text.config(state="disabled")
        text_widget.delete("1.0", tk.END)
        status_label.config(text="Ошибка! Спиши текст заново")
    style.configure("TButton", background=button_color)
    check_button.config(text="Проверить")

def reset():
    global stage
    stage = 1
    sample_text.config(state="normal")
    sample_text.delete("1.0", tk.END)
    sample_text.insert(tk.END, original_text)
    sample_text.config(state="disabled")
    text_widget.delete("1.0", tk.END)
    status_label.config(text="Спиши текст в поле ниже")
    check_button.config(state=tk.NORMAL, text="Проверить")
    reset_button.config(state=tk.DISABLED)
    style.configure("TButton", background=button_color)

def check_line():
    global current_line, line_stage
    user_input = line_text_widget.get("1.0", tk.END).strip()
    text_to_compare = lines[current_line].strip()

    if not case_sensitive:
        user_input = user_input.lower()
        text_to_compare = text_to_compare.lower()
    if not punctuation_sensitive:
        for punct in ".,!?;:-—\"'()[]{}":
            user_input = user_input.replace(punct, "")
            text_to_compare = text_to_compare.replace(punct, "")

    if user_input == text_to_compare:
        play_sound()
        style.configure("TButton", background="green")
        line_check_button.config(text="Правильно!")
        if line_stage == 1:
            root.after(delay_time * 1000, proceed_to_memory_stage)
        elif line_stage == 2:
            root.after(delay_time * 1000, next_line)
    else:
        play_sound1()
        style.configure("TButton", background="red")
        line_check_button.config(text="Ошибка!")
        root.after(delay_time * 1000, reset_line_error)

def proceed_to_memory_stage():
    global line_stage
    line_stage = 2
    line_sample_text.config(state="normal")
    line_sample_text.delete("1.0", tk.END)
    line_sample_text.config(state="disabled")
    line_text_widget.delete("1.0", tk.END)
    line_status_label.config(text=f"Строка {current_line + 1} из {len(lines)}: Введи по памяти")
    style.configure("TButton", background=button_color)
    line_check_button.config(text="Проверить память")

def next_line():
    global current_line, line_stage
    current_line += 1
    line_stage = 1
    if current_line < len(lines):
        line_sample_text.config(state="normal")
        line_sample_text.delete("1.0", tk.END)
        line_sample_text.insert(tk.END, lines[current_line])
        line_sample_text.config(state="disabled")
        line_text_widget.delete("1.0", tk.END)
        line_status_label.config(text=f"Строка {current_line + 1} из {len(lines)}: Спиши строку")
        style.configure("TButton", background=button_color)
        line_check_button.config(text="Проверить")
    else:
        line_status_label.config(text="Все строки пройдены!")
        line_check_button.config(state=tk.DISABLED, text="Завершено")
        line_reset_button.config(state=tk.NORMAL)

def reset_line_error():
    global line_stage
    if line_stage == 1:
        line_status_label.config(text=f"Строка {current_line + 1} из {len(lines)}: Ошибка! Спиши заново")
    elif line_stage == 2:
        line_stage = 1
        line_sample_text.config(state="normal")
        line_sample_text.delete("1.0", tk.END)
        line_sample_text.insert(tk.END, lines[current_line])
        line_sample_text.config(state="disabled")
        line_status_label.config(text=f"Строка {current_line + 1} из {len(lines)}: Ошибка! Спиши заново")
    if auto_clear:
        line_text_widget.delete("1.0", tk.END)
    style.configure("TButton", background=button_color)
    line_check_button.config(text="Проверить")

def reset_lines():
    global current_line, line_stage
    current_line = 0
    line_stage = 1
    if lines:
        line_sample_text.config(state="normal")
        line_sample_text.delete("1.0", tk.END)
        line_sample_text.insert(tk.END, lines[current_line])
        line_sample_text.config(state="disabled")
    else:
        line_sample_text.config(state="normal")
        line_sample_text.delete("1.0", tk.END)
        line_sample_text.insert(tk.END, "Текст пуст")
        line_sample_text.config(state="disabled")
    line_text_widget.delete("1.0", tk.END)
    line_status_label.config(text=f"Строка 1 из {len(lines)}: Спиши строку")
    line_check_button.config(state=tk.NORMAL, text="Проверить")
    line_reset_button.config(state=tk.DISABLED)
    style.configure("TButton", background=button_color)

def check_quatrain():
    global current_quatrain
    user_input = quatrain_text_widget.get("1.0", tk.END).strip()
    text_to_compare = quatrains[current_quatrain].strip()

    if not case_sensitive:
        user_input = user_input.lower()
        text_to_compare = text_to_compare.lower()
    if not punctuation_sensitive:
        for punct in ".,!?;:-—\"'()[]{}":
            user_input = user_input.replace(punct, "")
            text_to_compare = text_to_compare.replace(punct, "")

    if user_input == text_to_compare:
        play_sound()
        style.configure("TButton", background="green")
        quatrain_check_button.config(text="Правильно!")
        root.after(delay_time * 1000, next_quatrain)
    else:
        play_sound1()
        style.configure("TButton", background="red")
        quatrain_check_button.config(text="Ошибка!")
        root.after(delay_time * 1000, reset_quatrain_error)

def next_quatrain():
    global current_quatrain
    current_quatrain += 1
    if current_quatrain < len(quatrains):
        quatrain_sample_text.config(state="normal")
        quatrain_sample_text.delete("1.0", tk.END)
        quatrain_sample_text.insert(tk.END, quatrains[current_quatrain])
        quatrain_sample_text.config(state="disabled")
        quatrain_text_widget.delete("1.0", tk.END)
        quatrain_status_label.config(text=f"Абзац {current_quatrain + 1} из {len(quatrains)}")
        style.configure("TButton", background=button_color)
        quatrain_check_button.config(text="Проверить")
    else:
        quatrain_status_label.config(text="Все абзацы пройдены!")
        quatrain_check_button.config(state=tk.DISABLED, text="Завершено")
        quatrain_reset_button.config(state=tk.NORMAL)

def reset_quatrain_error():
    quatrain_status_label.config(text="Ошибка! Попробуй ещё раз")
    if auto_clear:
        quatrain_text_widget.delete("1.0", tk.END)
    style.configure("TButton", background=button_color)
    quatrain_check_button.config(text="Проверить")

def reset_quatrains():
    global current_quatrain
    current_quatrain = 0
    if quatrains:
        quatrain_sample_text.config(state="normal")
        quatrain_sample_text.delete("1.0", tk.END)
        quatrain_sample_text.insert(tk.END, quatrains[current_quatrain])
        quatrain_sample_text.config(state="disabled")
    else:
        quatrain_sample_text.config(state="normal")
        quatrain_sample_text.delete("1.0", tk.END)
        quatrain_sample_text.insert(tk.END, "Текст пуст")
        quatrain_sample_text.config(state="disabled")
    quatrain_text_widget.delete("1.0", tk.END)
    quatrain_status_label.config(text=f"Абзац 1 из {len(quatrains)}")
    quatrain_check_button.config(state=tk.NORMAL, text="Проверить")
    quatrain_reset_button.config(state=tk.DISABLED)
    style.configure("TButton", background=button_color)

def update_case_sensitivity():
    global case_sensitive
    case_sensitive = case_var.get()

def update_punctuation_sensitivity():
    global punctuation_sensitive
    punctuation_sensitive = punct_var.get()

def update_delay_time():
    global delay_time
    try:
        delay_time = int(delay_entry.get())
        if delay_time < 1:
            delay_time = 1
            delay_entry.delete(0, tk.END)
            delay_entry.insert(0, "1")
    except ValueError:
        delay_time = 6
        delay_entry.delete(0, tk.END)
        delay_entry.insert(0, "6")

def update_font_size():
    global font_size
    try:
        font_size = int(font_entry.get())
        if font_size < 8:
            font_size = 8
            font_entry.delete(0, tk.END)
            font_entry.insert(0, "8")
        sample_text.config(font=("Courier New", font_size))
        text_widget.config(font=("Courier New", font_size))
        line_sample_text.config(font=("Courier New", font_size))
        line_text_widget.config(font=("Courier New", font_size))
        quatrain_sample_text.config(font=("Courier New", font_size))
        quatrain_text_widget.config(font=("Courier New", font_size))
    except ValueError:
        font_size = 18
        font_entry.delete(0, tk.END)
        font_entry.insert(0, "18")

def update_auto_clear():
    global auto_clear
    auto_clear = auto_clear_var.get()

def update_colors(*args):
    global bg_color, button_color, text_bg_color, text_color
    bg_color = pastel_colors[bg_var.get()]
    text_bg_color = pastel_colors[text_bg_var.get()]
    button_color = pastel_colors[button_var.get()]
    text_color = text_colors[text_color_var.get()]
    
    style.configure("Custom.TFrame", background=bg_color)
    style.configure("TButton", background=button_color, foreground=text_color)
    root.config(bg=bg_color)
    settings_canvas.config(bg=bg_color)
    settings_frame.config(bg=bg_color)
    title_label.config(bg=bg_color, fg=text_color)
    sample_text.config(bg=text_bg_color, fg=text_color)
    text_widget.config(bg=text_bg_color, fg=text_color)
    status_label.config(bg=bg_color, fg=text_color)
    font_label.config(bg=bg_color, fg=text_color)
    case_check.config(bg=bg_color, fg=text_color)
    punct_check.config(bg=bg_color, fg=text_color)
    auto_clear_check.config(bg=bg_color, fg=text_color)
    bg_label.config(bg=bg_color, fg=text_color)
    text_bg_label.config(bg=bg_color, fg=text_color)
    button_label.config(bg=bg_color, fg=text_color)
    text_color_label.config(bg=bg_color, fg=text_color)
    line_sample_text.config(bg=text_bg_color, fg=text_color)
    line_text_widget.config(bg=text_bg_color, fg=text_color)
    line_status_label.config(bg=bg_color, fg=text_color)
    quatrain_sample_text.config(bg=text_bg_color, fg=text_color)
    quatrain_text_widget.config(bg=text_bg_color, fg=text_color)
    quatrain_status_label.config(bg=bg_color, fg=text_color)

def save_settings():
    settings = {
        "case_sensitive": case_sensitive,
        "punctuation_sensitive": punctuation_sensitive,
        "delay_time": delay_time,
        "font_size": font_size,
        "auto_clear": auto_clear,
        "bg_color": bg_var.get(),
        "text_bg_color": text_bg_var.get(),
        "button_color": button_var.get(),
        "text_color": text_color_var.get()
    }
    script_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(script_dir, "settings.json")
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f)

def load_settings():
    global case_sensitive, punctuation_sensitive, delay_time, font_size, auto_clear
    script_dir = os.path.dirname(os.path.abspath(__file__))
    settings_path = os.path.join(script_dir, "settings.json")
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
            case_sensitive = settings.get("case_sensitive", True)
            punctuation_sensitive = settings.get("punctuation_sensitive", True)
            delay_time = settings.get("delay_time", 6)
            font_size = settings.get("font_size", 18)
            auto_clear = settings.get("auto_clear", True)
            bg_var.set(settings.get("bg_color", "Светло-серый"))
            text_bg_var.set(settings.get("text_bg_color", "Светло-серый"))
            button_var.set(settings.get("button_color", "Светло-голубой"))
            text_color_var.set(settings.get("text_color", "Тёмно-серый"))
            case_var.set(case_sensitive)
            punct_var.set(punctuation_sensitive)
            auto_clear_var.set(auto_clear)
            delay_entry.delete(0, tk.END)
            delay_entry.insert(0, str(delay_time))
            font_entry.delete(0, tk.END)
            font_entry.insert(0, str(font_size))
            update_colors()

def open_folder():
    folder_path = os.path.dirname(os.path.abspath(__file__))
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(folder_path)
        elif system == "Darwin":
            subprocess.run(["open", folder_path])
        elif system == "Linux":
            subprocess.run(["xdg-open", folder_path])
        else:
            messagebox.showerror("Ошибка", "Неподдерживаемая ОС!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось открыть папку: {e}")

def on_mouse_wheel(event, canvas=None):
    if canvas:
        canvas.yview_scroll(-1 * int(event.delta / 120), "units")

def show_instructions():
    instr_window = tk.Toplevel(root)
    instr_window.title("Инструкция")
    instr_window.geometry("600x600")
    instr_window.transient(root)
    instr_window.grab_set()

    instr_notebook = ttk.Notebook(instr_window)
    instr_notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Вкладка "Описание программы"
    desc_frame = ttk.Frame(instr_notebook, style="Custom.TFrame")
    instr_notebook.add(desc_frame, text="Описание программы")

    desc_canvas = tk.Canvas(desc_frame, bg=bg_color)
    desc_scrollbar = ttk.Scrollbar(desc_frame, orient="vertical", command=desc_canvas.yview)
    desc_canvas.configure(yscrollcommand=desc_scrollbar.set)

    desc_inner_frame = tk.Frame(desc_canvas, bg=bg_color)
    desc_canvas.create_window((0, 0), window=desc_inner_frame, anchor="nw")

    desc_text = tk.Label(desc_inner_frame, text=(
        "Описание программы 'Ридли':\n\n"
        "'Ридли' — это приложение для тренировки памяти и навыков письма. Оно помогает пользователям запоминать тексты, переписывая их вручную. Программа включает:\n"
        "- Режим 'Главная': Списывание текста с образца, затем ввод по памяти.\n"
        "- Режим 'По строкам': Списывание и запоминание текста построчно.\n"
        "- Режим 'По абзацам': Работа с текстом по абзацам (от красной строки или по 4 строки).\n"
        "- Загрузка стихов с сайта stihi.ru для разнообразия текстов.\n"
        "- Поддержка форматов: .txt, .docx, .rtf, .md, .text.\n"
        "- Настраиваемый интерфейс: цвета, шрифт, задержки и другие параметры.\n"
        "- Звуковые эффекты для обратной связи.\n\n"
        "Цель: Улучшить концентрацию, память и навыки ручного ввода."
    ), font=("Courier New", 16), justify="left", wraplength=560, bg=bg_color, fg=text_color)
    desc_text.pack(pady=10)
    desc_text.bind("<Button-1>", lambda e: play_click_sound())

    desc_canvas.pack(side="left", fill="both", expand=True)
    desc_scrollbar.pack(side="right", fill="y")

    def update_desc_scroll(event):
        desc_canvas.configure(scrollregion=desc_canvas.bbox("all"))
        desc_canvas.yview_moveto(0)

    desc_inner_frame.bind("<Configure>", update_desc_scroll)
    desc_canvas.bind("<MouseWheel>", lambda e: on_mouse_wheel(e, desc_canvas))

    # Вкладка "Инструкция"
    instr_frame = ttk.Frame(instr_notebook, style="Custom.TFrame")
    instr_notebook.add(instr_frame, text="Инструкция")

    instr_canvas = tk.Canvas(instr_frame, bg=bg_color)
    instr_scrollbar = ttk.Scrollbar(instr_frame, orient="vertical", command=instr_canvas.yview)
    instr_canvas.configure(yscrollcommand=instr_scrollbar.set)

    instr_inner_frame = tk.Frame(instr_canvas, bg=bg_color)
    instr_canvas.create_window((0, 0), window=instr_inner_frame, anchor="nw")

    instr_text = tk.Label(instr_inner_frame, text=(
        "Как пользоваться 'Ридли':\n\n"
        "1. Вкладка 'Главная':\n"
        "   - Спиши текст из левого поля в правое и нажми 'Проверить'.\n"
        "   - После успеха текст исчезнет — введи его по памяти.\n"
        "   - Ошибка? Начни заново с кнопки 'Начать заново'.\n\n"
        "2. Вкладка 'По строкам':\n"
        "   - Спиши строку, проверь, затем введи по памяти.\n"
        "   - Переходи к следующей строке после успеха.\n\n"
        "3. Вкладка 'По абзацам':\n"
        "   - Спиши абзац (от красной строки или 4 строки), проверь.\n"
        "   - Переходи к следующему абзацу.\n\n"
        "4. Вкладка 'Параметры':\n"
        "   - Настрой шрифт, цвета, задержку и другие опции.\n"
        "   - Открой 'Выбор стихотворения stihi.ru' для поиска стихов."
    ), font=("Courier New", 16), justify="left", wraplength=560, bg=bg_color, fg=text_color)
    instr_text.pack(pady=10)
    instr_text.bind("<Button-1>", lambda e: play_click_sound())

    instr_canvas.pack(side="left", fill="both", expand=True)
    instr_scrollbar.pack(side="right", fill="y")

    def update_instr_scroll(event):
        instr_canvas.configure(scrollregion=instr_canvas.bbox("all"))
        instr_canvas.yview_moveto(0)

    instr_inner_frame.bind("<Configure>", update_instr_scroll)
    instr_canvas.bind("<MouseWheel>", lambda e: on_mouse_wheel(e, instr_canvas))

    # Вкладка "Для учителя"
    teacher_frame = ttk.Frame(instr_notebook, style="Custom.TFrame")
    instr_notebook.add(teacher_frame, text="Для учителя")

    teacher_canvas = tk.Canvas(teacher_frame, bg=bg_color)
    teacher_scrollbar = ttk.Scrollbar(teacher_frame, orient="vertical", command=teacher_canvas.yview)
    teacher_canvas.configure(yscrollcommand=teacher_scrollbar.set)

    teacher_inner_frame = tk.Frame(teacher_canvas, bg=bg_color)
    teacher_canvas.create_window((0, 0), window=teacher_inner_frame, anchor="nw")

    teacher_text = tk.Label(teacher_inner_frame, text=(
        "Инструкция для учителя:\n\n"
        "1. Работа с текстом:\n"
        "   - Открой папку программы через 'Параметры'.\n"
        "   - Создай файл 'stih' с расширением .txt, .docx, .rtf, .md или .text.\n"
        "   - Перезапусти программу для обновления текста.\n\n"
        "2. Советы:\n"
        "   - Используй разные тексты для тренировки.\n"
        "   - Настрой параметры под свои нужды."
    ), font=("Courier New", 16), justify="left", wraplength=560, bg=bg_color, fg=text_color)
    teacher_text.pack(pady=10)
    teacher_text.bind("<Button-1>", lambda e: play_click_sound())

    teacher_canvas.pack(side="left", fill="both", expand=True)
    teacher_scrollbar.pack(side="right", fill="y")

    def update_teacher_scroll(event):
        teacher_canvas.configure(scrollregion=teacher_canvas.bbox("all"))
        teacher_canvas.yview_moveto(0)

    teacher_inner_frame.bind("<Configure>", update_teacher_scroll)
    teacher_canvas.bind("<MouseWheel>", lambda e: on_mouse_wheel(e, teacher_canvas))

    # Вкладка "Решение проблем"
    problem_frame = ttk.Frame(instr_notebook, style="Custom.TFrame")
    instr_notebook.add(problem_frame, text="Решение проблем")

    problem_canvas = tk.Canvas(problem_frame, bg=bg_color)
    problem_scrollbar = ttk.Scrollbar(problem_frame, orient="vertical", command=problem_canvas.yview)
    problem_canvas.configure(yscrollcommand=problem_scrollbar.set)

    problem_inner_frame = tk.Frame(problem_canvas, bg=bg_color)
    problem_canvas.create_window((0, 0), window=problem_inner_frame, anchor="nw")

    problem_text = tk.Label(problem_inner_frame, text=(
        "Решение возможных проблем:\n\n"
        "1. Текст не загружается:\n"
        "   - Проверь, есть ли файл 'stih' (.txt, .docx, .rtf, .md, .text) в папке.\n"
        "   - Убедись, что файл не пустой и в кодировке UTF-8 (для .txt).\n\n"
        "2. Программа не запускается:\n"
        "   - Убедись, что установлены Python 3.x, python-docx и pyth.\n"
        "   - Проверь наличие зависимостей (tkinter).\n\n"
        "3. Ошибки при проверке:\n"
        "   - Проверь настройки 'Учитывать размер букв' и 'Знаки препинания'.\n"
        "   - Убедись, что текст введён полностью.\n\n"
        "4. Цвета не меняются:\n"
        "   - Перезапусти программу после изменения настроек.\n"
        "   - Проверь файл 'settings.json'.\n\n"
        "5. Ошибка в 'Выбор стихотворения stihi.ru':\n"
        "   - Проверь интернет и доступность stihi.ru."
    ), font=("Courier New", 16), justify="left", wraplength=560, bg=bg_color, fg=text_color)
    problem_text.pack(pady=10)
    problem_text.bind("<Button-1>", lambda e: play_click_sound())

    problem_canvas.pack(side="left", fill="both", expand=True)
    problem_scrollbar.pack(side="right", fill="y")

    def update_problem_scroll(event):
        problem_canvas.configure(scrollregion=problem_canvas.bbox("all"))
        problem_canvas.yview_moveto(0)

    problem_inner_frame.bind("<Configure>", update_problem_scroll)
    problem_canvas.bind("<MouseWheel>", lambda e: on_mouse_wheel(e, problem_canvas))

    close_button = ttk.Button(instr_window, text="Закрыть", command=instr_window.destroy, style="TButton")
    close_button.pack(pady=10)
    close_button.bind("<Button-1>", lambda e: play_click_sound())

    def on_notebook_mouse_wheel(event):
        current_tab = instr_notebook.tab(instr_notebook.select(), "text")
        if current_tab == "Описание программы":
            on_mouse_wheel(event, desc_canvas)
        elif current_tab == "Инструкция":
            on_mouse_wheel(event, instr_canvas)
        elif current_tab == "Для учителя":
            on_mouse_wheel(event, teacher_canvas)
        elif current_tab == "Решение проблем":
            on_mouse_wheel(event, problem_canvas)

    instr_window.bind("<MouseWheel>", on_notebook_mouse_wheel)

def fetch_stihi_ru_data():
    try:
        url = "https://stihi.ru"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        poem_links = soup.select('.poemlink')
        poems = []
        for link in poem_links[:10]:
            title = link.text.strip()
            poem_url = "https://stihi.ru" + link['href']
            poem_response = requests.get(poem_url, headers=headers, timeout=10)
            poem_soup = BeautifulSoup(poem_response.text, 'html.parser')
            poem_text_elem = poem_soup.select_one('div.text')
            poem_text = poem_text_elem.text.strip() if poem_text_elem else "Текст не найден"
            poems.append({'title': title, 'text': poem_text})

        author_links = soup.select('.authorlink')
        authors = []
        for link in author_links[:10]:
            author_name = link.text.strip()
            author_url = "https://stihi.ru" + link['href']
            author_response = requests.get(author_url, headers=headers, timeout=10)
            author_soup = BeautifulSoup(author_response.text, 'html.parser')
            author_poem_elem = author_soup.select_one('div.text')
            author_poem = author_poem_elem.text.strip() if author_poem_elem else "Стих не найден"
            authors.append({'name': author_name, 'poem': author_poem})

        return poems, authors
    except Exception:
        return None, None

def open_poem_selector():
    selector_window = tk.Toplevel(root)
    selector_window.title("Выбор стихотворения stihi.ru")
    selector_window.geometry("800x600")
    selector_window.transient(root)
    selector_window.grab_set()

    notebook = ttk.Notebook(selector_window)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    notebook.bind("<Button-1>", lambda e: play_click_sound())

    poem_frame = ttk.Frame(notebook, style="Custom.TFrame")
    notebook.add(poem_frame, text="Стихи")

    poem_left_frame = tk.Frame(poem_frame)
    poem_left_frame.grid(row=0, column=0, sticky="nsew")

    poem_listbox = tk.Listbox(poem_left_frame, width=40, font=("Courier New", 16))
    poem_listbox.pack(side="left", fill="y")
    poem_listbox.bind("<Button-1>", lambda e: play_click_sound())

    poem_scrollbar = tk.Scrollbar(poem_left_frame, orient="vertical")
    poem_scrollbar.config(command=poem_listbox.yview)
    poem_scrollbar.pack(side="right", fill="y")
    poem_listbox.config(yscrollcommand=poem_scrollbar.set)
    poem_scrollbar.bind("<Button-1>", lambda e: play_click_sound())

    poem_preview_frame = tk.Frame(poem_frame, bg=bg_color)
    poem_preview_frame.grid(row=0, column=1, sticky="nsew")

    poem_preview_title = tk.Label(poem_preview_frame, text="", font=("Courier New", 16), bg=bg_color, fg=text_color, wraplength=600, justify="center")
    poem_preview_title.pack(fill="x", padx=10, pady=5)
    poem_preview_title.bind("<Button-1>", lambda e: play_click_sound())

    poem_preview_text = tk.Text(poem_preview_frame, wrap="word", state="disabled", font=("Courier New", 16))
    poem_preview_text.pack(fill="both", expand=True, padx=10, pady=5)
    poem_preview_text.bind("<Button-1>", lambda e: play_click_sound())

    poem_add_button = ttk.Button(poem_frame, text="Добавить в stih.txt", command=lambda: add_to_stih(poem_listbox, poem_frame), state="disabled")
    poem_add_button.grid(row=1, column=0, pady=10, sticky="ew")
    poem_add_button.bind("<Button-1>", lambda e: play_click_sound())

    poem_site_button = ttk.Button(poem_frame, text="Перейти на stihi.ru", command=lambda: webbrowser.open("https://stihi.ru"), style="TButton")
    poem_site_button.grid(row=1, column=1, pady=10, sticky="ew")
    poem_site_button.bind("<Button-1>", lambda e: play_click_sound())

    poem_error_label = tk.Label(poem_frame, text="", font=("Courier New", 16), fg="red", bg=bg_color)
    poem_error_label.grid(row=2, column=0, columnspan=2)
    poem_error_label.bind("<Button-1>", lambda e: play_click_sound())

    poem_frame.grid_rowconfigure(0, weight=1)
    poem_frame.grid_rowconfigure(1, weight=0)
    poem_frame.grid_rowconfigure(2, weight=0)
    poem_frame.grid_columnconfigure(0, weight=1)
    poem_frame.grid_columnconfigure(1, weight=3)

    author_frame = ttk.Frame(notebook, style="Custom.TFrame")
    notebook.add(author_frame, text="Авторы")

    author_left_frame = tk.Frame(author_frame)
    author_left_frame.grid(row=0, column=0, sticky="nsew")

    author_listbox = tk.Listbox(author_left_frame, width=40, font=("Courier New", 16))
    author_listbox.pack(side="left", fill="y")
    author_listbox.bind("<Button-1>", lambda e: play_click_sound())

    author_scrollbar = tk.Scrollbar(author_left_frame, orient="vertical")
    author_scrollbar.config(command=author_listbox.yview)
    author_scrollbar.pack(side="right", fill="y")
    author_listbox.config(yscrollcommand=author_scrollbar.set)
    author_scrollbar.bind("<Button-1>", lambda e: play_click_sound())

    author_preview_frame = tk.Frame(author_frame, bg=bg_color)
    author_preview_frame.grid(row=0, column=1, sticky="nsew")

    author_preview_title = tk.Label(author_preview_frame, text="", font=("Courier New", 16), bg=bg_color, fg=text_color, wraplength=600, justify="center")
    author_preview_title.pack(fill="x", padx=10, pady=5)
    author_preview_title.bind("<Button-1>", lambda e: play_click_sound())

    author_preview_text = tk.Text(author_preview_frame, wrap="word", state="disabled", font=("Courier New", 16))
    author_preview_text.pack(fill="both", expand=True, padx=10, pady=5)
    author_preview_text.bind("<Button-1>", lambda e: play_click_sound())

    author_add_button = ttk.Button(author_frame, text="Добавить в stih.txt", command=lambda: add_to_stih(author_listbox, author_frame), state="disabled")
    author_add_button.grid(row=1, column=0, pady=10, sticky="ew")
    author_add_button.bind("<Button-1>", lambda e: play_click_sound())

    author_site_button = ttk.Button(author_frame, text="Перейти на stihi.ru", command=lambda: webbrowser.open("https://stihi.ru"), style="TButton")
    author_site_button.grid(row=1, column=1, pady=10, sticky="ew")
    author_site_button.bind("<Button-1>", lambda e: play_click_sound())

    author_error_label = tk.Label(author_frame, text="", font=("Courier New", 16), fg="red", bg=bg_color)
    author_error_label.grid(row=2, column=0, columnspan=2)
    author_error_label.bind("<Button-1>", lambda e: play_click_sound())

    author_frame.grid_rowconfigure(0, weight=1)
    author_frame.grid_rowconfigure(1, weight=0)
    author_frame.grid_rowconfigure(2, weight=0)
    author_frame.grid_columnconfigure(0, weight=1)
    author_frame.grid_columnconfigure(1, weight=3)

    def update_poem_list(poems):
        poem_listbox.delete(0, tk.END)
        for poem in poems:
            poem_listbox.insert(tk.END, poem['title'])
        poem_frame.poems = poems
        if poems:
            poem_add_button.config(state="normal")

    def update_author_list(authors):
        author_listbox.delete(0, tk.END)
        for author in authors:
            author_listbox.insert(tk.END, author['name'])
        author_frame.authors = authors
        if authors:
            author_add_button.config(state="normal")

    def show_error(label):
        label.config(text="Ошибка. Решение в инструкции")

    def on_poem_select(event):
        selection = poem_listbox.curselection()
        if selection:
            index = selection[0]
            poem = poem_frame.poems[index]
            poem_preview_title.config(text=poem['title'])
            poem_preview_text.config(state="normal")
            poem_preview_text.delete("1.0", tk.END)
            poem_preview_text.insert(tk.END, poem['text'])
            poem_preview_text.config(state="disabled")
            poem_add_button.config(state="normal")
        else:
            poem_preview_title.config(text="")
            poem_add_button.config(state="disabled")

    def on_author_select(event):
        selection = author_listbox.curselection()
        if selection:
            index = selection[0]
            author = author_frame.authors[index]
            author_preview_title.config(text=author['name'])
            author_preview_text.config(state="normal")
            author_preview_text.delete("1.0", tk.END)
            author_preview_text.insert(tk.END, author['poem'])
            author_preview_text.config(state="disabled")
            author_add_button.config(state="normal")
        else:
            author_preview_title.config(text="")
            author_add_button.config(state="disabled")

    def add_to_stih(listbox, frame):
        selection = listbox.curselection()
        if selection:
            index = selection[0]
            item = frame.poems[index] if hasattr(frame, 'poems') else frame.authors[index]
            text = item['text'] if 'text' in item else item['poem']
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, "stih.txt")
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text + "\n\n")
                messagebox.showinfo("Успех", "Стих добавлен в stih.txt")
                load_text_from_file()
            except PermissionError:
                messagebox.showerror("Ошибка", "Нет прав для записи в stih.txt. Проверь права доступа.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить стих: {e}")

    poem_listbox.bind("<<ListboxSelect>>", on_poem_select)
    author_listbox.bind("<<ListboxSelect>>", on_author_select)

    def load_data():
        poems, authors = fetch_stihi_ru_data()
        if poems is None or authors is None:
            show_error(poem_error_label)
            show_error(author_error_label)
        else:
            update_poem_list(poems)
            update_author_list(authors)

    threading.Thread(target=load_data, daemon=True).start()

# Инициализация стилей
style = ttk.Style()
style.theme_use("clam")
style.configure("Custom.TFrame", background=bg_color, relief="flat")
style.configure("TButton", background=button_color, foreground=text_color, font=("Courier New", 24), borderwidth=1, relief="raised", padding=10)
style.map("TButton",
          background=[("active", "#B0C4DE"), ("disabled", "#D3D3D3")],
          foreground=[("active", text_color), ("disabled", "#A9A9A9")])

# Виджеты основного окна
title_label = tk.Label(root, text="Ридли", font=("Courier New", 40), bg=bg_color, fg=text_color)
title_label.grid(row=0, column=0, padx=20, pady=20, sticky="n")
title_label.bind("<Button-1>", lambda e: play_click_sound())

notebook = ttk.Notebook(root)
notebook.grid(row=1, column=0, pady=20, sticky="nsew")
notebook.bind("<Button-1>", lambda e: play_click_sound())

# Вкладка "Главная"
frame_main = ttk.Frame(notebook, style="Custom.TFrame")
notebook.add(frame_main, text="Главная")

sample_text_frame = tk.Frame(frame_main)
sample_text_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
sample_text = tk.Text(sample_text_frame, wrap="word", height=20, width=40, font=("Courier New", font_size), 
                      bg=text_bg_color, fg=text_color, exportselection=0)
sample_text.pack(side="left", fill="both", expand=True)
sample_text.config(state="disabled")
sample_scrollbar = tk.Scrollbar(sample_text_frame, orient="vertical", command=sample_text.yview)
sample_scrollbar.pack(side="right", fill="y")
sample_text.config(yscrollcommand=sample_scrollbar.set)
sample_text.bind("<Control-c>", lambda e: "break")
sample_text.bind("<Button-3>", lambda e: "break")
sample_text.bind("<Button-1>", lambda e: play_click_sound())
sample_scrollbar.bind("<Button-1>", lambda e: play_click_sound())

right_frame = tk.Frame(frame_main, bg=bg_color)
right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

text_widget = tk.Text(right_frame, width=40, height=20, font=("Courier New", font_size), bg=text_bg_color, fg=text_color)
text_widget.grid(row=0, column=0, padx=0, pady=10, sticky="nsew")
text_widget.bind("<Button-1>", lambda e: play_click_sound())

status_label = tk.Label(right_frame, text=" ", font=("Courier New", 20), bg=bg_color, fg=text_color)
status_label.grid(row=1, column=0, padx=0, pady=10, sticky="nsew")
status_label.bind("<Button-1>", lambda e: play_click_sound())

check_button = ttk.Button(right_frame, text="Проверить", command=check_input, style="TButton")
check_button.grid(row=2, column=0, pady=10, sticky="ew")

reset_button = ttk.Button(right_frame, text="Начать заново", command=reset, state=tk.DISABLED, style="TButton")
reset_button.grid(row=3, column=0, pady=10, sticky="ew")
reset_button.bind("<Button-1>", lambda e: play_click_sound())

frame_main.grid_rowconfigure(0, weight=1)
frame_main.grid_columnconfigure(0, weight=1)
frame_main.grid_columnconfigure(1, weight=1)
right_frame.grid_rowconfigure(0, weight=3)
right_frame.grid_rowconfigure(1, weight=1)
right_frame.grid_rowconfigure(2, weight=0)
right_frame.grid_rowconfigure(3, weight=0)
right_frame.grid_columnconfigure(0, weight=1)

# Вкладка "По строкам"
line_frame = ttk.Frame(notebook, style="Custom.TFrame")
notebook.add(line_frame, text="По строкам")

line_sample_text_frame = tk.Frame(line_frame)
line_sample_text_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
line_sample_text = tk.Text(line_sample_text_frame, wrap="word", height=20, width=40, font=("Courier New", font_size), 
                           bg=text_bg_color, fg=text_color, exportselection=0)
line_sample_text.pack(side="left", fill="both", expand=True)
line_sample_text.config(state="disabled")
line_sample_scrollbar = tk.Scrollbar(line_sample_text_frame, orient="vertical", command=line_sample_text.yview)
line_sample_scrollbar.pack(side="right", fill="y")
line_sample_text.config(yscrollcommand=line_sample_scrollbar.set)
line_sample_text.bind("<Control-c>", lambda e: "break")
line_sample_text.bind("<Button-3>", lambda e: "break")
line_sample_text.bind("<Button-1>", lambda e: play_click_sound())
line_sample_scrollbar.bind("<Button-1>", lambda e: play_click_sound())

line_right_frame = tk.Frame(line_frame, bg=bg_color)
line_right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

line_text_widget = tk.Text(line_right_frame, width=40, height=20, font=("Courier New", font_size), bg=text_bg_color, fg=text_color)
line_text_widget.grid(row=0, column=0, padx=0, pady=10, sticky="nsew")
line_text_widget.bind("<Button-1>", lambda e: play_click_sound())

line_status_label = tk.Label(line_right_frame, text=" ", font=("Courier New", 20), bg=bg_color, fg=text_color)
line_status_label.grid(row=1, column=0, padx=0, pady=10, sticky="nsew")
line_status_label.bind("<Button-1>", lambda e: play_click_sound())

line_check_button = ttk.Button(line_right_frame, text="Проверить", command=check_line, style="TButton")
line_check_button.grid(row=2, column=0, pady=10, sticky="ew")

line_reset_button = ttk.Button(line_right_frame, text="Начать заново", command=reset_lines, state=tk.DISABLED, style="TButton")
line_reset_button.grid(row=3, column=0, pady=10, sticky="ew")
line_reset_button.bind("<Button-1>", lambda e: play_click_sound())

line_frame.grid_rowconfigure(0, weight=1)
line_frame.grid_columnconfigure(0, weight=1)
line_frame.grid_columnconfigure(1, weight=1)
line_right_frame.grid_rowconfigure(0, weight=3)
line_right_frame.grid_rowconfigure(1, weight=1)
line_right_frame.grid_rowconfigure(2, weight=0)
line_right_frame.grid_rowconfigure(3, weight=0)
line_right_frame.grid_columnconfigure(0, weight=1)

# Вкладка "По абзацам" (бывшая "Четверостишья")
quatrain_frame = ttk.Frame(notebook, style="Custom.TFrame")
notebook.add(quatrain_frame, text="По абзацам")

quatrain_sample_text_frame = tk.Frame(quatrain_frame)
quatrain_sample_text_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
quatrain_sample_text = tk.Text(quatrain_sample_text_frame, wrap="word", height=20, width=40, font=("Courier New", font_size), 
                               bg=text_bg_color, fg=text_color, exportselection=0)
quatrain_sample_text.pack(side="left", fill="both", expand=True)
quatrain_sample_text.config(state="disabled")
quatrain_sample_scrollbar = tk.Scrollbar(quatrain_sample_text_frame, orient="vertical", command=quatrain_sample_text.yview)
quatrain_sample_scrollbar.pack(side="right", fill="y")
quatrain_sample_text.config(yscrollcommand=quatrain_sample_scrollbar.set)
quatrain_sample_text.bind("<Control-c>", lambda e: "break")
quatrain_sample_text.bind("<Button-3>", lambda e: "break")
quatrain_sample_text.bind("<Button-1>", lambda e: play_click_sound())
quatrain_sample_scrollbar.bind("<Button-1>", lambda e: play_click_sound())

quatrain_right_frame = tk.Frame(quatrain_frame, bg=bg_color)
quatrain_right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

quatrain_text_widget = tk.Text(quatrain_right_frame, width=40, height=20, font=("Courier New", font_size), bg=text_bg_color, fg=text_color)
quatrain_text_widget.grid(row=0, column=0, padx=0, pady=10, sticky="nsew")
quatrain_text_widget.bind("<Button-1>", lambda e: play_click_sound())

quatrain_status_label = tk.Label(quatrain_right_frame, text=" ", font=("Courier New", 20), bg=bg_color, fg=text_color)
quatrain_status_label.grid(row=1, column=0, padx=0, pady=10, sticky="nsew")
quatrain_status_label.bind("<Button-1>", lambda e: play_click_sound())

quatrain_check_button = ttk.Button(quatrain_right_frame, text="Проверить", command=check_quatrain, style="TButton")
quatrain_check_button.grid(row=2, column=0, pady=10, sticky="ew")

quatrain_reset_button = ttk.Button(quatrain_right_frame, text="Начать заново", command=reset_quatrains, state=tk.DISABLED, style="TButton")
quatrain_reset_button.grid(row=3, column=0, pady=10, sticky="ew")
quatrain_reset_button.bind("<Button-1>", lambda e: play_click_sound())

quatrain_frame.grid_rowconfigure(0, weight=1)
quatrain_frame.grid_columnconfigure(0, weight=1)
quatrain_frame.grid_columnconfigure(1, weight=1)
quatrain_right_frame.grid_rowconfigure(0, weight=3)
quatrain_right_frame.grid_rowconfigure(1, weight=1)
quatrain_right_frame.grid_rowconfigure(2, weight=0)
quatrain_right_frame.grid_rowconfigure(3, weight=0)
quatrain_right_frame.grid_columnconfigure(0, weight=1)

# Вкладка "Параметры"
frame_settings = ttk.Frame(notebook, style="Custom.TFrame")
notebook.add(frame_settings, text="Параметры")

settings_canvas = tk.Canvas(frame_settings, bg=bg_color)
settings_scrollbar = ttk.Scrollbar(frame_settings, orient="vertical", command=settings_canvas.yview)
settings_canvas.configure(yscrollcommand=settings_scrollbar.set)
settings_canvas.bind("<Button-1>", lambda e: play_click_sound())
settings_scrollbar.bind("<Button-1>", lambda e: play_click_sound())

settings_frame = tk.Frame(settings_canvas, bg=bg_color)
settings_canvas.create_window((0, 0), window=settings_frame, anchor="nw")

case_var = tk.BooleanVar(value=True)
punct_var = tk.BooleanVar(value=True)
auto_clear_var = tk.BooleanVar(value=True)

case_check = tk.Checkbutton(settings_frame, text="Учитывать размер букв", font=("Courier New", 16), 
                            variable=case_var, command=update_case_sensitivity, bg=bg_color, fg=text_color)
case_check.grid(row=0, column=0, pady=10, sticky="w")
case_check.bind("<Button-1>", lambda e: play_click_sound())

punct_check = tk.Checkbutton(settings_frame, text="Учитывать знаки препинания", font=("Courier New", 16), 
                             variable=punct_var, command=update_punctuation_sensitivity, bg=bg_color, fg=text_color)
punct_check.grid(row=1, column=0, pady=10, sticky="w")
punct_check.bind("<Button-1>", lambda e: play_click_sound())

delay_entry = tk.Entry(settings_frame, width=5, font=("Courier New", 16))
delay_entry.grid(row=2, column=0, padx=(250, 0), pady=10, sticky="w")
delay_entry.insert(0, "6")
delay_entry.bind("<FocusOut>", lambda e: update_delay_time())
delay_entry.bind("<Button-1>", lambda e: play_click_sound())

font_label = tk.Label(settings_frame, text="Размер шрифта текста:", font=("Courier New", 16), bg=bg_color, fg=text_color)
font_label.grid(row=3, column=0, pady=10, sticky="w")
font_label.bind("<Button-1>", lambda e: play_click_sound())

font_entry = tk.Entry(settings_frame, width=5, font=("Courier New", 16))
font_entry.grid(row=3, column=0, padx=(250, 0), pady=10, sticky="w")
font_entry.insert(0, "18")
font_entry.bind("<FocusOut>", lambda e: update_font_size())
font_entry.bind("<Button-1>", lambda e: play_click_sound())

auto_clear_check = tk.Checkbutton(settings_frame, text="Автоматически очищать поле", font=("Courier New", 16), 
                                  variable=auto_clear_var, command=update_auto_clear, bg=bg_color, fg=text_color)
auto_clear_check.grid(row=4, column=0, pady=10, sticky="w")
auto_clear_check.bind("<Button-1>", lambda e: play_click_sound())

bg_label = tk.Label(settings_frame, text="Цвет фона:", font=("Courier New", 16), bg=bg_color, fg=text_color)
bg_label.grid(row=5, column=0, pady=10, sticky="w")
bg_label.bind("<Button-1>", lambda e: play_click_sound())

bg_var = tk.StringVar(value="Светло-серый")
bg_menu = ttk.OptionMenu(settings_frame, bg_var, "Светло-серый", *pastel_colors.keys(), command=update_colors)
bg_menu.grid(row=5, column=0, padx=(200, 0), pady=10, sticky="w")
bg_menu.bind("<Button-1>", lambda e: play_click_sound())

text_bg_label = tk.Label(settings_frame, text="Цвет фона текста:", font=("Courier New", 16), bg=bg_color, fg=text_color)
text_bg_label.grid(row=6, column=0, pady=10, sticky="w")
text_bg_label.bind("<Button-1>", lambda e: play_click_sound())

text_bg_var = tk.StringVar(value="Светло-серый")
text_bg_menu = ttk.OptionMenu(settings_frame, text_bg_var, "Светло-серый", *pastel_colors.keys(), command=update_colors)
text_bg_menu.grid(row=6, column=0, padx=(250, 0), pady=10, sticky="w")
text_bg_menu.bind("<Button-1>", lambda e: play_click_sound())

button_label = tk.Label(settings_frame, text="Цвет кнопок:", font=("Courier New", 16), bg=bg_color, fg=text_color)
button_label.grid(row=7, column=0, pady=10, sticky="w")
button_label.bind("<Button-1>", lambda e: play_click_sound())

button_var = tk.StringVar(value="Светло-голубой")
button_menu = ttk.OptionMenu(settings_frame, button_var, "Светло-голубой", *pastel_colors.keys(), command=update_colors)
button_menu.grid(row=7, column=0, padx=(200, 0), pady=10, sticky="w")
button_menu.bind("<Button-1>", lambda e: play_click_sound())

text_color_label = tk.Label(settings_frame, text="Цвет текста:", font=("Courier New", 16), bg=bg_color, fg=text_color)
text_color_label.grid(row=8, column=0, pady=10, sticky="w")
text_color_label.bind("<Button-1>", lambda e: play_click_sound())

text_color_var = tk.StringVar(value="Тёмно-серый")
text_color_menu = ttk.OptionMenu(settings_frame, text_color_var, "Тёмно-серый", *text_colors.keys(), command=update_colors)
text_color_menu.grid(row=8, column=0, padx=(200, 0), pady=10, sticky="w")
text_color_menu.bind("<Button-1>", lambda e: play_click_sound())

open_folder_button = ttk.Button(settings_frame, text="Открыть папку", command=open_folder, style="TButton")
open_folder_button.grid(row=9, column=0, pady=10, sticky="ew")
open_folder_button.bind("<Button-1>", lambda e: play_click_sound())

poem_selector_button = ttk.Button(settings_frame, text="Выбор стихотворения stihi.ru", command=open_poem_selector, style="TButton")
poem_selector_button.grid(row=10, column=0, pady=10, sticky="ew")
poem_selector_button.bind("<Button-1>", lambda e: play_click_sound())

settings_canvas.pack(side="left", fill="both", expand=True)
settings_scrollbar.pack(side="right", fill="y")

def configure_settings_scroll(event):
    settings_canvas.configure(scrollregion=settings_canvas.bbox("all"))
    settings_canvas.yview_moveto(0)

settings_frame.bind("<Configure>", configure_settings_scroll)
settings_canvas.bind("<MouseWheel>", lambda e: on_mouse_wheel(e, settings_canvas))

# Настройка основного окна
def on_closing():
    save_settings()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.config(bg=bg_color)
root.grid_rowconfigure(0, weight=0)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Загрузка настроек и текста после создания интерфейса
load_settings()
load_text_from_file()
show_instructions()

root.mainloop()
