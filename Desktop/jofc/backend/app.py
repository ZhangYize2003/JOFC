from flask import Flask, request, send_file, jsonify
import pandas as pd
import io
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/upload', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only CSV files allowed'}), 400
    df = pd.read_csv(file)
    # Simple AI labelling: assign random category 0-3
    df['category'] = [random.randint(0, 3) for _ in range(len(df))]
    counts = df['category'].value_counts().sort_index().to_dict()
    # Prepare CSV for download
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return jsonify({
        'csv': output.getvalue(),
        'counts': counts
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
