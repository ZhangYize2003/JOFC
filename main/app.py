import streamlit as st
import pandas as pd
import io
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# Use conda install pytorch torchvision torchaudio cpuonly -c pytorch if no GPU
# use conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia if u have Nvidia GPU

st.set_page_config(page_title="JOFC", page_icon="🕶️", layout="centered", initial_sidebar_state="auto")

# Dark mode styling
st.markdown("""
    <style>
    body { background-color: #181818; color: #f1f1f1; }
    .stApp { background-color: #181818; }

    [data-testid="stMetricLabel"] {
        font-size: 1.3em !important;
        font-weight: 600 !important;
        color: #f1f1f1 !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.6em !important;
        font-weight: bold !important;
    }

    .category-card { text-align: center; padding: 6px; }
    .category-desc { font-size: 0.95em; color: #bbb; }
    </style>
""", unsafe_allow_html=True)

st.title("JOFC")
st.subheader("Google Reviews Noise Filter")

# Load model once (cached so it doesn’t reload every time)
@st.cache_resource
def load_model():
    model_path = "../debert-v12"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    return pipeline("text-classification", model=model, tokenizer=tokenizer)

classifier = load_model()

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding="latin-1")


    if "text" not in df.columns:
        st.error("CSV must contain a 'text' column")
    else:
        # Run classification
        predictions = classifier(df["text"].tolist(), truncation=True)
        df["category"] = [pred["label"] for pred in predictions]

        # Count categories
        counts = df["category"].value_counts().to_dict()

        st.write("### Category Counts:")

        # Map Hugging Face labels to human-friendly names
        category_info = {
            "LABEL_0": ("0: Valid", "A genuine review about the location, describing food, service, atmosphere, or experience."),
            "LABEL_1": ("1: Spam/Advertisement", "Contains promotional content, links, phone numbers, or marketing language like 'visit', 'discount', 'special offer'. / Talks about unrelated topics (phones, politics, news)."),
            "LABEL_2": ("2: Low Quality", "Nonsense, repetitive, very short, or generic ('Good', 'Nice', 'Ok!!!')."),
            "LABEL_3": ("3: Rant Without Visit", "Reviewer complains or gives opinion but admits they never visited (e.g., 'Never been here but...').")
        }

        # Show metrics
        col1, col2, col3, col4 = st.columns(4)
        for i, col in enumerate([col1, col2, col3, col4]):
            label_key = f"LABEL_{i}"
            with col:
                st.metric(category_info[label_key][0], counts.get(label_key, 0))
                st.markdown(
                    f"<div class='category-card'>"
                    f"<div class='category-desc'>{category_info[label_key][1]}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        # Get original filename without extension
        base_name = os.path.splitext(uploaded_file.name)[0]
        output_filename = f"{base_name}_labelled.csv"

        # Download classified CSV
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"Download {output_filename}",
            data=csv_bytes,
            file_name=output_filename,
            mime="text/csv"
        )
else:
    st.info("Please upload a CSV file to begin.")
