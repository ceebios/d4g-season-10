import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
)
model = AutoModelForSeq2SeqLM.from_pretrained("sshleifer/distilbart-cnn-12-6")
tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
device = torch.device("cpu")
model = model.to(device)
import re

def decode(tokenizer, outputs):
    return [
        tokenizer.decode(o)
        .replace("<pad>", "")
        .replace("</s>", "")
        .replace("<s>", "")
        .strip()
        for o in outputs
    ]


def clean_text(text):
    return re.sub("\(.*?\) ","",text)


def summarize(paragraph):
    max_length=256
    min_length=64
    length_penalty=0.0
    num_beams=1
    early_stopping=False

    text = paragraph #clean_text(paragraph)
    if len(text)<128:
        return text

    inputs = tokenizer(
        ["summarize: " + text],
        return_tensors="pt",
        max_length=512 * 2,
        truncation=True,
        padding=True,
    )
    inputs["input_ids"] = inputs.input_ids.to(device)
    inputs["attention_mask"] = inputs.attention_mask.to(device)

    outputs = model.generate(
        inputs["input_ids"],
        max_length=max_length,
        min_length=min_length,
        length_penalty=length_penalty,
        num_beams=num_beams,
        early_stopping=early_stopping,
    )
    summ = decode(tokenizer, outputs)
    return summ