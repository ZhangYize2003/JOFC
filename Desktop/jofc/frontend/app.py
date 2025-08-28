import streamlit as st
import pandas as pd
import io
import random

st.set_page_config(page_title="JOFC", page_icon="🕶️", layout="centered", initial_sidebar_state="auto")

# Dark mode styling
st.markdown("""
    <style>
    body { background-color: #181818; color: #f1f1f1; }
    .stApp { background-color: #181818; }
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
    st.write(counts)
    # Download labelled CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download labelled CSV",
        data=csv,
        file_name="labelled_jofc.csv",
        mime="text/csv"
    )
    st.write("### Preview:")
    st.dataframe(df)
else:
    st.info("Please upload a CSV file to begin.")
