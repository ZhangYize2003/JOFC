import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="JOFC", page_icon="🕶️", layout="centered", initial_sidebar_state="auto")

# Dark mode styling
st.markdown("""
    <style>
    body { background-color: #181818; color: #f1f1f1; }
    .stApp { background-color: #181818; }

    /* Make metric label (above the number) bigger */
    [data-testid="stMetricLabel"] {
        font-size: 1.3em !important;
        font-weight: 600 !important;
        color: #f1f1f1 !important;
    }

    /* Make metric number stand out */
    [data-testid="stMetricValue"] {
        font-size: 1.6em !important;
        font-weight: bold !important;
    }

    /* Description style */
    .category-card { text-align: center; padding: 6px; }
    .category-desc { font-size: 0.95em; color: #bbb; }
    </style>
""", unsafe_allow_html=True)

st.title("JOFC")
st.subheader("Joel Ong Fan Club")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Simple AI labelling: assign random category 0-3
    df['category'] = [random.randint(0, 3) for _ in range(len(df))]
    counts = df['category'].value_counts().sort_index().to_dict()

    st.write("### Category Counts:")

    # Category headers + descriptions
    category_info = {
        0: ("0: Valid", "A genuine review about the location, describing food, service, atmosphere, or experience."),
        1: ("1: Spam/Advertisement", "Contains promotional content, links, phone numbers, or marketing language like 'visit', 'discount', 'special offer'. / Talks about unrelated topics (phones, politics, news)."),
        2: ("2: Low Quality", "Nonsense, repetitive, very short, or generic ('Good', 'Nice', 'Ok!!!')."),
        3: ("3: Rant Without Visit", "Reviewer complains or gives opinion but admits they never visited (e.g., 'Never been here but...').")
    }

    # Display counts in 4 separate columns
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]

    for i, col in enumerate(cols):
        with col:
            st.metric(category_info[i][0], counts.get(i, 0))  # only label + number
            st.markdown(
                f"<div class='category-card'>"
                f"<div class='category-desc'>{category_info[i][1]}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

    # Download labelled CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download labelled CSV",
        data=csv,
        file_name="labelled_jofc.csv",
        mime="text/csv"
    )
else:
    st.info("Please upload a CSV file to begin.")
