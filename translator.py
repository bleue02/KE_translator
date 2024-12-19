import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

class Translator:
    def __init__(self, model_id: str, src_lang: str, tgt_lang: str, max_length: int = 250):
        """
        Args:
            model_id (str): Hugging Face 모델 ID.
            src_lang (str): 소스 언어 코드.
            tgt_lang (str): 타겟 언어 코드.
            max_length (int, optional): 최대 토큰 길이. Defaults 250.
        """
        self.model_id = model_id
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        self.max_length = max_length
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        self.model, self.tokenizer = self.load_model_and_tokenizer()

    def load_model_and_tokenizer(self):
        try:
            print(f"{self.model_id} 다운로드 소요 시간 약 2분")
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_id).to(self.device).eval()

        except Exception as e:
            print(f"Error loading model: {e}")
            raise e

        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        except Exception as e:
            print(f"Error loading tokenizer: {e}")
            raise e

        return model, tokenizer

    def translate(self, text: str) -> str:
        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.max_length
            ).to(self.device)
        except Exception as e:
            print(f"Error during tokenization: {e}")
            return "Tokenization failed."

        try:
            translated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.lang_code_to_id.get(
                    self.tgt_lang, self.tokenizer.lang_code_to_id["eng_Latn"]
                ),
                max_length=self.max_length,
                num_beams=4,
                early_stopping=True
            )
            translated_text = self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
        except Exception as e:
            print(f"Error during translation: {e}")
            return "Translation failed."

        return translated_text
