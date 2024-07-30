import mysql.connector
from tkinter import Tk, Label, Entry, Button, Text, Scrollbar, Toplevel, messagebox, StringVar, OptionMenu

class MorseCodeTranslator:
    def __init__(self, language='en'):
        self.language = language
        self.morse_code_dicts = {
            'en': {
                'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
                'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
                'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
                'Y': '-.--', 'Z': '--..', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
                '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----', ' ': '/'
            },
            'hi': {
                'अ': '.-', 'आ': '.-', 'इ': '..', 'ई': '..', 'उ': '..-', 'ऊ': '..-', 'ए': '.', 'ऐ': '.-.',
                'ओ': '---', 'औ': '---', 'क': '-.-', 'ख': '-.-', 'ग': '--.', 'घ': '--.', 'च': '-.-.', 'छ': '-.-.',
                'ज': '.---', 'झ': '.---', 'ट': '-..-', 'ठ': '-..-', 'ड': '-..-', 'ढ': '-..-', 'ण': '-..-.',
                'त': '-', 'थ': '-', 'द': '-', 'ध': '-', 'न': '-.', 'प': '.--.', 'फ': '.--.', 'ब': '-...',
                'भ': '-...', 'म': '--', 'य': '-.--', 'र': '.-.', 'ल': '.-..', 'व': '.--', 'श': '----', 'ष': '----',
                'स': '...', 'ह': '....', 'ळ': '...', 'क्ष': '-.-', 'ज्ञ': '.---'
            },
            'te': {
                'అ': '.-', 'ఆ': '.-', 'ఇ': '..', 'ఈ': '..', 'ఉ': '..-', 'ఊ': '..-', 'ఎ': '.', 'ఏ': '.-.',
                'ఒ': '---', 'ఓ': '---', 'క': '-.-', 'ఖ': '-.-', 'గ': '--.', 'ఘ': '--.', 'చ': '-.-.', 'ఛ': '-.-.',
                'జ': '.---', 'ఝ': '.---', 'ట': '-..-', 'ఠ': '-..-', 'డ': '-..-', 'ఢ': '-..-', 'ణ': '-..-.',
                'త': '-', 'థ': '-', 'ద': '-', 'ధ': '-', 'న': '-.', 'ప': '.--.', 'ఫ': '.--.', 'బ': '-...',
                'భ': '-...', 'మ': '--', 'య': '-.--', 'ర': '.-.', 'ల': '.-..', 'వ': '.--', 'శ': '----', 'ష': '----',
                'స': '...', 'హ': '....', 'ళ': '...', 'క్ష': '-.-', 'జ్ఞ': '.---'
            }
        }

        self.reverse_morse_code_dicts = {}
        for lang, morse_code_dict in self.morse_code_dicts.items():
            self.reverse_morse_code_dicts[lang] = {v: k for k, v in morse_code_dict.items()}

        try:
            self.db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="aasif",
                database="morse_code_db"
            )
            self.db_cursor = self.db_connection.cursor()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

    def __del__(self):
        if hasattr(self, 'db_cursor') and hasattr(self, 'db_connection'):
            self.db_cursor.close()
            self.db_connection.close()

    def translate_to_morse(self, text):
        morse_dict = self.morse_code_dicts.get(self.language, {})
        morse_code = ''
        for char in text.upper():
            if char in morse_dict:
                morse_code += morse_dict[char] + ' '
        return morse_code.strip()

    def translate_to_text(self, morse_code):
        reverse_morse_dict = self.reverse_morse_code_dicts.get(self.language, {})
        text = ''
        for code in morse_code.split(' '):
            if code in reverse_morse_dict:
                text += reverse_morse_dict[code]
        return text

    def save_to_database(self, input_text, output_text):
        try:
            if hasattr(self, 'db_cursor'):
                sql = "INSERT INTO translation_history (input_text, output_text) VALUES (%s, %s)"
                val = (input_text, output_text)
                self.db_cursor.execute(sql, val)
                self.db_connection.commit()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")

class MorseCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Morse Code Translator")
        self.root.geometry("600x400")

        self.translator = MorseCodeTranslator()

        self.create_widgets()

    def create_widgets(self):
        Label(self.root, text="Enter text or Morse code:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.input_entry = Entry(self.root, width=50, font=("Arial", 12))
        self.input_entry.grid(row=0, column=1, padx=10, pady=10)

        Button(self.root, text="Translate", command=self.translate, font=("Arial", 12)).grid(row=0, column=2, padx=10, pady=10)
        Button(self.root, text="Clear", command=self.clear, font=("Arial", 12)).grid(row=0, column=3, padx=10, pady=10)
        Button(self.root, text="History", command=self.show_history, font=("Arial", 12)).grid(row=0, column=4, padx=10, pady=10)

        Label(self.root, text="Translation:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        self.output_text = Text(self.root, width=50, height=8, font=("Arial", 12))
        self.output_text.grid(row=1, column=1, columnspan=3, padx=10, pady=10, sticky='ew')

        self.scrollbar = Scrollbar(self.root, command=self.output_text.yview)
        self.scrollbar.grid(row=1, column=4, sticky='ns')

        languages = ['English', 'Hindi', 'Telugu']
        self.selected_language = StringVar()
        self.selected_language.set('English')
        OptionMenu(self.root, self.selected_language, *languages, command=self.update_language).grid(row=2, column=0, padx=10, pady=10, sticky='w')

    def translate(self):
        input_text = self.input_entry.get().strip()
        if input_text:
            if input_text[0] in '-.':
                translated_text = self.translator.translate_to_text(input_text)
            else:
                translated_text = self.translator.translate_to_morse(input_text)
            self.output_text.delete('1.0', 'end')
            self.output_text.insert('end', translated_text)
            self.translator.save_to_database(input_text, translated_text)
        else:
            messagebox.showwarning("Warning", "Please enter text or Morse code.")

    def clear(self):
        self.input_entry.delete(0, 'end')
        self.output_text.delete('1.0', 'end')

    def show_history(self):
        history_window = Toplevel(self.root)
        history_window.title("Translation History")
        history_window.geometry("600x400")

        history_text = Text(history_window, width=80, height=20, font=("Arial", 12))
        history_text.pack(padx=10, pady=10)

        scrollbar = Scrollbar(history_window, command=history_text.yview)
        scrollbar.pack(side="right", fill="y")

        history_text.config(yscrollcommand=scrollbar.set)

        if hasattr(self.translator, 'db_cursor'):
            self.translator.db_cursor.execute("SELECT * FROM translation_history")
            records = self.translator.db_cursor.fetchall()
            for record in records:
                history_text.insert('end', f"{record[0]} - Input: {record[1]}, Output: {record[2]}\n")

    def update_language(self, selected_language):
        if selected_language == 'English':
            self.translator.language = 'en'
        elif selected_language == 'Hindi':
            self.translator.language = 'hi'
        elif selected_language == 'Telugu':
            self.translator.language = 'te'

if __name__ == "__main__":
    root = Tk()
    app = MorseCodeApp(root)
    root.mainloop()
