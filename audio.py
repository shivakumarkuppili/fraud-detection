import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from PIL import Image
import os

MODEL_PATH = "C:\\Users\\SAI MAHESH\\Desktop\\files\\semisters\\sem7\\prj\\audiomodel\\spectrogram_cnn_model.h5"

def audio_to_spectrogram(audio_file, output_folder):
    """
    Converts an audio file into a spectrogram and saves it in the specified folder.
    Returns the saved spectrogram's file path.
    """
    y, sr = librosa.load(audio_file)
    D = np.abs(librosa.stft(y))
    S = librosa.amplitude_to_db(D, ref=np.max)

    plt.figure(figsize=(10, 4))
    librosa.display.specshow(S, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.tight_layout()

    output_path = os.path.join(output_folder, "spectrogram.png")
    plt.savefig(output_path)
    plt.close()

    return output_path

def predict_spectrogram(image_path):
    """
    Uses a trained CNN model to predict if the spectrogram belongs to a fraud or real call.
    """
    model = keras.models.load_model(MODEL_PATH)
    img = Image.open(image_path).convert("RGB").resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)[0][0]
    return "Fraud FedEx Call" if prediction > 0.5 else "Real Call"
