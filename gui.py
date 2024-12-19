import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinter import ttk
import threading
from translator import Translator

class TranslatorGUI:
    def __init__(self, root, translator: Translator):
        self.root = root
        self.translator = translator
        self.root.geometry("1000x800")
        self.root.resizable(True, True)


        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 12))
        self.style.configure('TButton', font=('Helvetica', 12), padding=6)
        self.style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'))

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=10)

        header_label = ttk.Label(header_frame, text="한영 번역 프로그램", style='Header.TLabel')
        header_label.pack()

        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        input_frame = ttk.Frame(middle_frame)
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        input_label = ttk.Label(input_frame, text="한국어")
        input_label.pack(anchor='w')

        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, font=('Helvetica', 12))
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.input_text.bind("<KeyRelease>", self.update_token_count)

        # 토큰 수 레이블
        self.token_count_label = ttk.Label(input_frame, text="토큰 최대길이: 0/250", style='TLabel')
        self.token_count_label.pack(anchor='e', pady=5)

        # 출력 섹션 (우측)
        output_frame = ttk.Frame(middle_frame)
        output_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        output_label = ttk.Label(output_frame, text="영어")
        output_label.pack(anchor='w')

        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=('Helvetica', 12), state='disabled', bg='#e6ffe6')
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # 하단 프레임
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=10)

        self.translate_button = ttk.Button(bottom_frame, text="번역", command=self.handle_translate)
        self.translate_button.pack(side=tk.LEFT, padx=10)

        self.clear_button = ttk.Button(bottom_frame, text="지우기", command=self.clear_text)
        self.clear_button.pack(side=tk.LEFT, padx=10)

    def handle_translate(self):
        """
        번역 버튼 클릭 시 호출되는 함수.
        """
        input_text = self.input_text.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showwarning("Input Required", "Please enter some Korean text to translate.")
            return

        # 토큰 수 계산
        tokens = self.translator.tokenizer.tokenize(input_text)
        token_count = len(tokens)
        self.token_count_label.config(text=f"Token Count: {token_count}/{self.translator.max_length}")
        if token_count > self.translator.max_length:
            messagebox.showwarning("Input Too Long", f"입력 길이는 {self.translator.max_length} 넘어서는 안됩니다.")

        # 번역 버튼 비활성화
        self.translate_button.config(state='disabled')
        self.clear_button.config(state='disabled')
        self.translate_button.config(text='번역중..')
        self.root.update_idletasks()

        # 번역을 별도의 스레드에서 수행
        threading.Thread(target=self.perform_translation, args=(input_text,)).start()

    def perform_translation(self, input_text):
        """
        번역을 수행하고 결과를 업데이트하는 함수.
        """
        translated = self.translator.translate(input_text)
        self.root.after(0, self.update_translation, translated)

    def update_translation(self, translated):
        """
        번역 결과를 GUI에 업데이트하는 함수.
        """
        # 번역 버튼 활성화
        self.translate_button.config(state='normal')
        self.clear_button.config(state='normal')
        self.translate_button.config(text='번역')

        if translated:
            self.output_text.config(state='normal')
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, translated)
            self.output_text.config(state='disabled')
        else:
            self.output_text.config(state='normal')
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, "Translation failed.")
            self.output_text.config(state='disabled')

    def clear_text(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.config(state='normal')
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state='disabled')
        self.token_count_label.config(text="Token Count: 0/250")

    def update_token_count(self, event=None):
        """
        입력 텍스트의 토큰 수를 실시간으로 업데이트하는 함수.
        """
        input_text = self.input_text.get("1.0", tk.END).strip()
        tokens = self.translator.tokenizer.tokenize(input_text)
        token_count = len(tokens)
        self.token_count_label.config(text=f"Token Count: {token_count}/{self.translator.max_length}")
        if token_count > self.translator.max_length:
            self.token_count_label.config(foreground="red")
        else:
            self.token_count_label.config(foreground="black")

def main():
    root = tk.Tk()
    MODEL_ID = "facebook/nllb-200-3.3B"
    SRC_LANG = "kor_Latn"
    TGT_LANG = "eng_Latn"
    MAX_LENGTH = 250

    translator = Translator(model_id=MODEL_ID, src_lang=SRC_LANG, tgt_lang=TGT_LANG, max_length=MAX_LENGTH)

    app = TranslatorGUI(root, translator)
    root.mainloop()

if __name__ == "__main__":
    main()
