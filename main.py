import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

import tkinter as tk
from gui import TranslatorGUI
from translator import Translator

def main():
    MODEL_ID = "facebook/nllb-200-3.3B"
    SRC_LANG = "kor_Latn"
    TGT_LANG = "eng_Latn"
    MAX_LENGTH = 250 # 입력받을수 있는 토큰 최대 길이

    translator = Translator(model_id=MODEL_ID, src_lang=SRC_LANG, tgt_lang=TGT_LANG, max_length=MAX_LENGTH)

    root = tk.Tk()
    app = TranslatorGUI(root, translator)
    root.mainloop()

if __name__ == "__main__":
    main()
