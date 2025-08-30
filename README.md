# Review Classification System

## Project Overview
This project builds a machine learning system to automatically classify online reviews into four categories:

- 0 = Valid → genuine reviews about the location/service  
- 1 = Spam/Ads → promotional or irrelevant advertising content  
- 2 = LowQuality → very short or uninformative reviews  
- 3 = RantWithoutVisit → negative complaints where the user admits they never visited  

The system improves the reliability of review platforms by filtering out noise, spam, and misleading content.

We explored both **classical ML models (TF-IDF + Random Forest)** and **transformer models (DistilBERT, DeBERTa)**, with **DeBERTa-v3-small** selected as the final deployed model. A **Streamlit web app** provides an interactive interface for testing and visualizing predictions.

---

## Setup Instructions

1. **Clone this repository**
   ```bash
   git clone https://github.com/ZhangYize2003/JOFC.git
   ```

2. **Download the pretrained model**  
   Visit our Hugging Face model repository:  
   [DeBERTa-v12 Model](https://huggingface.co/ZhangYize2003/debert-v12)  

   Download the model folder (it contains `config.json`, `pytorch_model.bin`, `tokenizer.json`, etc.).

3. **Place the model folder**  
   Move the downloaded model folder into the same directory as this GitHub repo.  

   Your folder structure should look like this:
   ```
   <your-repo>/
   ├── main
   ├── debert-v12   <-- downloaded from Hugging Face
   ...
   └── README.md
   ```
  ### Important Note
  In `app.py`, go to **Line 39** and update the model path to point to your downloaded Hugging Face model folder. For example:

  ```python
  model_path = ".../"   # adjust this if your model folder is elsewhere
  ```

4. **Install dependencies**  
   Make sure you are using Python 3.8+ and have pip installed.  

   Run the following command to install required packages:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Streamlit app**  
   Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```

   The app will open automatically in your browser at [http://localhost:8501](http://localhost:8501).

---

## How to Reproduce Results

### Dataset
- We used the [masterList_relabelled_v2 dataset](https://huggingface.co/datasets/sizhao/tiktoktechjam/tree/main).  
- The dataset is **already labeled** into four categories:  
  - 0 = Valid  
  - 1 = Spam/Ads  
  - 2 = LowQuality  
  - 3 = RantWithoutVisit  

### Pretrained Model
- Final model: [DeBERTa-v12](https://huggingface.co/ZhangYize2003/debert-v12)  
- Already fine-tuned — no extra training required.  

### Evaluation
1. Place the pretrained model folder in the project root.  
2. Run the evaluation script on the labeled dataset:  
   ```bash
   python evaluation/evaluate.py --model_path debert-v12 --data_path data/masterList_relabelled_v2.csv

---

## Team Member Contributions
- Rishabh, Yize – Dataset creation, Streamlit deployment and visualization  
- Joel, Chuhao – Random Forest baseline and TF-IDF preprocessing  
- Si Zhao – Gemma-assisted labeling pipeline, DistilBERT & DeBERTa-v3-small fine-tuning and final model selection  
[Youtube Demo](https://www.youtube.com/watch?v=Q2uovyCQv_4)
