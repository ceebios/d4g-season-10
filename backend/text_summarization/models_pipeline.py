from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch
from time import time


class model_summerisation:
    name:str
    def __init__(self, name_model_gz:str) -> None:
        self.name_model_gz = name_model_gz
    def load_model(self):
        pass
    def make_outputs(self):
        pass

class model_pegasus(model_summerisation):
    def __init__(self, name_model_gz:str="google/pegasus-xsum") -> None:
        self.name_model_gz = name_model_gz
        self.load_model()

    def load_model(self):
        t = time()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = PegasusTokenizer.from_pretrained(self.name_model_gz)
        self.model = PegasusForConditionalGeneration.from_pretrained(self.name_model_gz).to(self.device)
        print(f"Temps mis pour le chargement:{time() - t} seconds")
        

    def make_outputs(self, batch):
        size = len(batch)
        t = time()
        batch = self.tokenizer(batch, truncation=True, padding="longest", return_tensors="pt").to(self.device)
        translated = self.model.generate(**batch)
        tgt_text = self.tokenizer.batch_decode(translated, skip_special_tokens=True)
        print(f"Temps mis pour {size} summerisations:{time() - t} seconds")
        return tgt_text
    