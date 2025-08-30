import argparse
import pandas as pd
import torch
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

from transformers import AutoTokenizer, AutoModelForSequenceClassification

# ------------------------------------------------------------
# Parse arguments
# ------------------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--model_path", type=str, required=True, help="Path to pretrained model folder")
parser.add_argument("--data_path", type=str, required=True, help="Path to CSV dataset with 'text' and 'label' columns")
parser.add_argument("--text_col", type=str, default="text", help="Name of the text column in dataset")
parser.add_argument("--label_col", type=str, default="label", help="Name of the label column in dataset")
args = parser.parse_args()

# ------------------------------------------------------------
# Load dataset
# ------------------------------------------------------------
df = pd.read_csv(args.data_path)
df = df.dropna(subset=[args.text_col, args.label_col])

texts = df[args.text_col].astype(str).tolist()
labels = df[args.label_col].astype(int).tolist()

# ------------------------------------------------------------
# Load pretrained model + tokenizer
# ------------------------------------------------------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = AutoTokenizer.from_pretrained(args.model_path)
model = AutoModelForSequenceClassification.from_pretrained(args.model_path)
model.to(device)
model.eval()

# ------------------------------------------------------------
# Run inference
# ------------------------------------------------------------
batch_size = 16
all_preds = []

with torch.no_grad():
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        encodings = tokenizer(batch_texts, padding=True, truncation=True, return_tensors="pt").to(device)
        outputs = model(**encodings)
        preds = torch.argmax(outputs.logits, dim=1)
        all_preds.extend(preds.cpu().numpy())

# ------------------------------------------------------------
# Evaluation metrics
# ------------------------------------------------------------
print("\n=== Classification Report ===")
print(classification_report(labels, all_preds, digits=4))

# Confusion Matrix
cm = confusion_matrix(labels, all_preds)
plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["Valid","Spam/Ads","LowQuality","RantWithoutVisit"],
            yticklabels=["Valid","Spam/Ads","LowQuality","RantWithoutVisit"])
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title("Confusion Matrix")
plt.show()