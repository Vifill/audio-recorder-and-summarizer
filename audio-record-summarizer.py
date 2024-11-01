import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import openai
import threading
import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise EnvironmentError("Please set the OPENAI_API_KEY environment variable in your .env file.")

# Create an OpenAI client instance
client = openai.Client(api_key=api_key)

# Recording parameters
SAMPLE_RATE = 44100  # Hertz
DURATION = 30  # Seconds per chunk

# Global variables to store transcripts and manage threads
transcripts = []
transcription_threads = []
is_recording = True
session_name = ""

def get_device_id(device_name):
    """
    Retrieves the device ID for the specified audio device name.
    """
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if device_name in device['name']:
            return idx
    raise ValueError(f"Device '{device_name}' not found.")

# Set the device name to 'BlackHole 2ch' for capturing system audio
DEVICE_NAME = 'BlackHole 2ch'
try:
    DEVICE_ID = get_device_id(DEVICE_NAME)
except ValueError as e:
    print(e)
    print("Please ensure BlackHole is installed and configured correctly.")
    exit(1)

def record_audio(filename, duration, sample_rate):
    """
    Records audio from the specified device and saves it to a WAV file.
    """
    print(f"Recording started: {filename}")
    try:
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=2,  # BlackHole 2ch supports 2 channels
            dtype='int16',
            device=DEVICE_ID
        )
        sd.wait()  # Wait until recording is finished
        write(filename, sample_rate, audio_data)
        print(f"Recording finished: {filename}")
    except Exception as e:
        print(f"An error occurred during recording: {e}")

def transcribe_audio(filename):
    """
    Transcribes audio using OpenAI's Whisper API.
    """
    print(f"Transcribing audio: {filename}")
    try:
        with open(filename, 'rb') as audio_file:
            # Updated method call using the new API
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
        text = transcript_response.text
        print(f"Transcription completed for {filename}.")
        return text
    except openai.error.OpenAIError as e:
        print(f"An error occurred during transcription: {e}")
        return ""

def process_audio_chunk(filename):
    """
    Processes an audio chunk: transcribes and appends it to the global transcripts list.
    """
    text = transcribe_audio(filename)
    if text:
        transcripts.append(text)

def continuous_recording():
    """
    Continuously records audio in chunks and processes them.
    """
    global transcription_threads
    chunk_count = 0
    print("Starting continuous recording. Press Enter to summarize and stop.")
    while is_recording:
        filename = f'audio_chunk_{chunk_count}.wav'
        record_audio(filename, DURATION, SAMPLE_RATE)

        # Process the audio chunk in a separate thread
        transcription_thread = threading.Thread(target=process_audio_chunk, args=(filename,))
        transcription_thread.start()
        transcription_threads.append(transcription_thread)

        chunk_count += 1

def wait_for_summarize():
    """
    Waits for the user to press Enter to trigger summarization.
    """
    global is_recording, session_name
    input()
    is_recording = False
    session_name = input("Enter a name for this session: ")
    print("\nSummarizing collected transcripts...")

def summarize_transcripts():
    """
    Summarizes all collected transcripts with a custom prompt.
    """
    full_transcript = "\n".join(transcripts)
    if not full_transcript.strip():
        print("No transcripts available to summarize.")
        return

    # Create a directory for the session
    session_dir = os.path.join(os.getcwd(), session_name)
    os.makedirs(session_dir, exist_ok=True)

    # Save the full transcript to a file
    transcript_file = os.path.join(session_dir, 'transcript.txt')
    with open(transcript_file, 'w', encoding='utf-8') as f:
        f.write(full_transcript)
    print(f"Full transcript saved to {transcript_file}")

    print("Summarizing text...")
    try:
        # Custom prompt tailored for F1 fantasy decisions
        custom_prompt = (
            "Based on the following transcript, provide a detailed analysis of the performance of the mentioned "
            "Formula 1 drivers, their teams/constructors, and their cars. Focus on driver performance, team strategies, "
            "and any insights that could help in making informed decisions for F1 fantasy selections."
            "\n\nTranscript:\n" + full_transcript
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": custom_prompt}
            ],
            max_tokens=500,
            temperature=0.2,
        )
        summary = response.choices[0].message.content.strip()

        # Save the summary to a file
        summary_file = os.path.join(session_dir, 'summary.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary saved to {summary_file}")

        print("\nFinal Summary:\n")
        print(summary)
    except openai.error.OpenAIError as e:
        print(f"An error occurred during summarization: {e}")

if __name__ == "__main__":
    try:
        # Start the recording in a separate thread
        recording_thread = threading.Thread(target=continuous_recording)
        recording_thread.start()

        # Wait for user input to trigger summarization
        wait_for_summarize()

        # Wait for the recording thread to finish
        recording_thread.join()

        # Wait for any remaining transcription threads to finish
        print("Waiting for all transcription threads to finish...")
        for t in transcription_threads:
            t.join()
        print("All transcription threads have finished.")

        # Summarize the collected transcripts
        summarize_transcripts()

    except KeyboardInterrupt:
        print("\nRecording stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
