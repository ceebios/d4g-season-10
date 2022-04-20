from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch


src_text = [
    """Endogenous retroviruses (ERVs) are abundant in mammalian genomes and contain sequences modulating transcription.The impact of ERV propagation on the evolution of gene regulation remains poorly understood. We found that ERVs have shaped the evolution of a transcriptional network underlying the interferon (IFN) response, a major branch of innate immunity, and that lineage-specific ERVs have dispersed numerous IFN-inducible enhancers independently in diverse mammalian genomes. CRISPR-Cas9 deletion of a subset of these ERV elements in the human genome impaired expression of adjacent IFN-induced genes and revealed their involvement in the regulation of essential immune functions, including activation of the AIM2 inflammasome. Although these regulatory sequences likely arose in ancient viruses, they now constitute a dynamic reservoir of IFN-inducible enhancers fueling genetic innovation in mammalian immune defenses."""
]

model_name = "google/pegasus-pubmed"
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name).to(device)
batch = tokenizer(src_text, truncation=True, padding="longest", return_tensors="pt").to(device)
translated = model.generate(**batch)
tgt_text = tokenizer.batch_decode(translated, skip_special_tokens=True)

print(tgt_text)
