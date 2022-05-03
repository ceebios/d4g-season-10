import torch
from time import time


class TransformersSummarizationModel:

    def __init__(self, name_model_gz:str, tokenizer_instance, model_instance) -> None:
        t = time()
        self.name_model_gz = name_model_gz
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = tokenizer_instance.from_pretrained(self.name_model_gz)
        self.model = model_instance.from_pretrained(self.name_model_gz).to(self.device)
        print(f"LOG: Temps mis pour le chargement : {round(time() - t)} seconds")

    def make_outputs(self, batch):
        size = len(batch)
        t = time()
        batch = self.tokenizer(batch, truncation=True, padding="longest", return_tensors="pt").to(self.device)
        translated = self.model.generate(**batch)
        tgt_text = self.tokenizer.batch_decode(translated, skip_special_tokens=True)
        print(f"LOG: Temps mis pour {size} summerisations : {round(time() - t)} seconds")
        return tgt_text


