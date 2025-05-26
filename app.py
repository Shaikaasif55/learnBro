from flask import Flask, render_template, request, jsonify
from transformers import DistilBertTokenizer, DistilBertForMaskedLM
import torch
import pymysql
from datetime import datetime
import pyaudio
from vosk import Model, KaldiRecognizer

app = Flask(__name__)

# Load DistilBERT model and tokenizer
model = DistilBertForMaskedLM.from_pretrained('distilbert-base-uncased')
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

# Connect to MySQL
db = pymysql.connect(host='localhost',
                     user='root',
                     password='aasif',
                     database='bert_predictions',
                     cursorclass=pymysql.cursors.DictCursor)

# Load the Vosk model for speech-to-text (offline)
model_path = "C:/Users/ASUS/Desktop/advancedmask/vosk-model-small-en-in-0.4"  # Path to your Vosk model directory
vosk_model = Model(model_path)

def predict_masked_word(sentence):
    """Predict masked words in a sentence, returning top 5 predictions."""
    try:
        input_ids = tokenizer.encode(sentence, return_tensors='pt', clean_up_tokenization_spaces=True)
        masked_indices = torch.where(input_ids == tokenizer.mask_token_id)[1].tolist()
        all_predicted_tokens = []

        for masked_index in masked_indices:
            with torch.no_grad():
                outputs = model(input_ids)
                predictions = outputs.logits[0, masked_index].topk(20)  # Top 10 predictions
                predicted_tokens = tokenizer.convert_ids_to_tokens(predictions.indices.tolist())
                all_predicted_tokens.append(predicted_tokens)

        return all_predicted_tokens
    except Exception as e:
        return str(e)

def voice_to_text():
    """Capture voice input and convert it to text with [MASK] handling and punctuation."""
    recognizer = KaldiRecognizer(vosk_model, 16000)
    p = pyaudio.PyAudio()

    # Open microphone stream
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=8000)
    print("Listening for voice input...")
    stream.start_stream()

    full_text = ""  # Initialize an empty string to capture full input

    while True:
        data = stream.read(4000)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            result_json = eval(result)
            text = result_json.get("text", "")

            # Append recognized text to full_text
            if text:
                full_text += " " + text  # Keep appending recognized words
                print(f"Captured text so far: {full_text}")

                # Check for question mark based on common question words
                if text.lower().endswith(("what", "how", "where", "why", "who")):
                    full_text += "?"  # Add question mark for typical question words
                else:
                    full_text += "."  # Add period for statements

                # Replace "mask" or "blank" with [MASK]
                text_with_mask = full_text.replace("mask", "[MASK]").replace("blank", "[MASK]")
                print(f"Processed Text with [MASK] and Punctuation: {text_with_mask}")
                return text_with_mask
        else:
            continue


@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction requests."""
    data = request.get_json()
    sentence = data.get('sentence')

    if not sentence:
        return jsonify({'error': 'No sentence provided.'}), 400

    predicted_tokens = predict_masked_word(sentence)
    return jsonify(predicted_tokens)

@app.route('/voice-to-text', methods=['POST'])
def voice_to_text_route():
    """Handle voice-to-text conversion requests."""
    text = voice_to_text()
    return jsonify({'text': text})

@app.route('/save', methods=['POST'])
def save():
    """Save predictions to the database."""
    data = request.get_json()
    sentence = data.get('sentence')
    predictions = data.get('predictions')

    if not sentence or not predictions:
        return jsonify({'error': 'Invalid data.'}), 400

    try:
        with db.cursor() as cursor:
            query = "INSERT INTO predictions (sentence, predictions, created_at) VALUES (%s, %s, %s)"
            cursor.execute(query, (sentence, str(predictions), datetime.now()))
            db.commit()

        return jsonify({'status': 'Saved'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
def history():
    """Retrieve saved predictions from the database."""
    try:
        with db.cursor() as cursor:
            query = "SELECT sentence, predictions, created_at FROM predictions ORDER BY created_at DESC"
            cursor.execute(query)
            results = cursor.fetchall()

        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
