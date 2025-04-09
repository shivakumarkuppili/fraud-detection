import os
import logging
import pickle
import numpy as np
import speech_recognition as sr
from pydub import AudioSegment
from keras.models import load_model
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)

# Load tokenizer
with open("models/tokenizer.pickle", 'rb') as handle:
    tokenizer = pickle.load(handle)

# Load pre-trained model
model = load_model("models/improved_fraud_detection_model_with_glove.h5")

MAX_SEQUENCE_LENGTH = 150

def convert_to_wav(input_file):
    """Converts any audio file format to WAV."""
    output_file = input_file.rsplit('.', 1)[0] + ".wav"
    try:
        audio = AudioSegment.from_file(input_file)
        audio.export(output_file, format="wav")
        return output_file
    except Exception as e:
        logging.error(f"Error converting {input_file} to WAV: {e}")
        return None

def transcribe_audio(file_path):
    """Transcribes speech from an audio file to text."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        logging.error(f"Google Speech Recognition error: {e}")
        return None

def classify_text(text):
    """Classifies the transcribed text using the trained model."""
    sequences = tokenizer.texts_to_sequences([text])
    padded_sequence = pad_sequences(sequences, maxlen=MAX_SEQUENCE_LENGTH)
    prediction = model.predict(padded_sequence)
    return "Fraudulent" if prediction[0][0] > 0.5 else "Legitimate"

def process_sentence_audio(file_path):
    """Processes the audio for sentence-level classification."""
    wav_file = convert_to_wav(file_path)
    if not wav_file:
        return None, None

    transcription = transcribe_audio(wav_file)
    if not transcription:
        return None, None

    classification = classify_text(transcription)
    return transcription, classification
