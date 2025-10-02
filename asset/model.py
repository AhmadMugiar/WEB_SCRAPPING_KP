# model.py
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import streamlit as st
MODEL_NAME = "./models/models-indobert" 


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, local_files_only=True)
    model.to(device)
    model.eval()
    return model, tokenizer
model, tokenizer = load_model()
ID2LABEL = {0: "Negatif", 1: "Netral", 2: "Positif"}
def _sanitize_batch_texts(batch):
    return [x if isinstance(x, str) and x.strip() else "" for x in batch]
@torch.no_grad()
def predict_sentiment(texts, batch_size=64, max_length=96): # HAPUS parameter return_proba
    if isinstance(texts, str):
        texts = [texts]
    all_preds, all_confidences = [], [] 
    for i in range(0, len(texts), batch_size):
        batch = _sanitize_batch_texts(texts[i:i+batch_size])
        enc = tokenizer(batch, padding=True, truncation=True,
                        max_length=max_length, return_tensors="pt")
        enc = {k: v.to(device) for k, v in enc.items()}
        if device.type == "cuda":
            with torch.autocast("cuda", dtype=torch.float16):
                logits = model(**enc).logits
        else:
            logits = model(**enc).logits
        probs = F.softmax(logits, dim=-1)
        pred_ids = probs.argmax(dim=1) 
        confidences, _ = probs.max(dim=1)         
        all_preds.extend(pred_ids.cpu().numpy().tolist())
        all_confidences.extend(confidences.detach().cpu().numpy().tolist()) # <--- SIMPAN CONFIDENCE

    labels = [ID2LABEL[int(i)] for i in all_preds]
    return labels, all_confidences 