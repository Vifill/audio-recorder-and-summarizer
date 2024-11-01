# Audio Recorder and Summarizer

This project is a Python script that records system audio on macOS using BlackHole, transcribes the audio using OpenAI's Whisper API, and summarizes the transcription using OpenAI's GPT models. The script allows you to:

- Continuously record system audio in chunks.
- Transcribe each audio chunk.
- Wait for a user-triggered event (pressing Enter) to stop recording.
- Summarize all collected transcripts with a custom prompt tailored for Formula 1 (F1) fantasy decision-making.
- Save the full transcript and summary in a user-named session folder.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
- [Configuration](#configuration)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)
- [Legal and Ethical Considerations](#legal-and-ethical-considerations)
- [License](#license)

---

## Prerequisites

- **macOS**: The script uses BlackHole, which is a macOS virtual audio driver.
- **Python 3.7 or higher**
- **Homebrew**: For installing dependencies on macOS.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/audio-recorder-summarizer.git
cd audio-recorder-summarizer
```

### 2. Set Up a Python Virtual Environment (Optional but Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### 3. Install Required Python Packages

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, install the packages manually:

```bash
pip install sounddevice numpy scipy openai python-dotenv
```

### 4. Install BlackHole

Install BlackHole via Homebrew:

```bash
brew install blackhole-2ch
```

### 5. Install FFmpeg (Required by `pydub` if you use it)

```bash
brew install ffmpeg
```

---

## Setup

### 1. Configure BlackHole to Capture System Audio

#### Create a Multi-Output Device

1. Open **Audio MIDI Setup** (`/Applications/Utilities/Audio MIDI Setup.app`).
2. Click the **`+`** button at the bottom-left corner and select **"Create Multi-Output Device"**.
3. In the right pane, check both **"BlackHole 2ch"** and your built-in output device (e.g., "MacBook Pro Speakers").
4. Right-click on the **Multi-Output Device** and select **"Use This Device For Sound Output"**.

#### Set Input Device

- In **System Preferences > Sound > Input**, select **"BlackHole 2ch"** as the input device.

### 2. Set Up OpenAI API Key

#### Create a `.env` File

In the project directory, create a file named `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

**Important**:

- Keep your API key secure and do not share it publicly.
- Add `.env` to your `.gitignore` file to prevent it from being committed to version control.

---

## Usage

1. **Activate the Virtual Environment** (if you created one):

   ```bash
   source venv/bin/activate  # On macOS/Linux
   ```

2. **Run the Script**:

   ```bash
   python audio_recorder_summarizer.py
   ```

3. **Start Playing the Audio Content**:

   - Play the video or audio stream you wish to capture.

4. **Trigger Summarization**:

   - When you're ready to summarize, switch back to the terminal and press **Enter**.
   - Enter a name for the session when prompted.

5. **View Outputs**:

   - The full transcript and summary will be saved in a folder named after your session.
   - The final summary will also be printed in the terminal.

6. **Deactivate the Virtual Environment** (when you're done):

   ```bash
   deactivate
   ```

---

## Configuration

### Adjusting Recording Parameters

- **Chunk Duration**:

  Modify the `DURATION` variable to change the length of each audio recording chunk (in seconds):

  ```python
  DURATION = 30  # Seconds per chunk
  ```

- **Sample Rate**:

  Modify the `SAMPLE_RATE` if necessary:

  ```python
  SAMPLE_RATE = 44100  # Hertz
  ```

### Customizing the Summarization Prompt

- The prompt is tailored for F1 fantasy decision-making. You can modify it in the `summarize_transcripts()` function:

  ```python
  custom_prompt = (
      "Based on the following transcript, provide a detailed analysis of the performance of the mentioned "
      "Formula 1 drivers, their teams/constructors, and their cars. Focus on driver performance, team strategies, "
      "and any insights that could help in making informed decisions for F1 fantasy selections."
      "\n\nTranscript:\n" + full_transcript
  )
  ```

### Changing the OpenAI Model

- The script uses the `gpt-4o` model. Ensure that you have access to this model or change it to another model you have access to:

  ```python
  response = client.chat.completions.create(
      model="gpt-4o",
      ...
  )
  ```

### Adjusting OpenAI API Parameters

- **Max Tokens**:

  Adjust `max_tokens` to control the length of the summary:

  ```python
  max_tokens=500,
  ```

- **Temperature**:

  Adjust `temperature` to control the creativity of the summary (range: 0.0 to 1.0):

  ```python
  temperature=0.2,
  ```

---

## How It Works

1. **Recording Audio**:

   - The script records system audio in chunks using the `sounddevice` library.
   - Audio chunks are saved as WAV files (e.g., `audio_chunk_0.wav`).

2. **Transcribing Audio**:

   - Each audio chunk is transcribed using OpenAI's Whisper API.
   - Transcriptions are collected in a list.

3. **Waiting for User Input**:

   - The script waits for the user to press **Enter** to stop recording.

4. **Processing Transcriptions**:

   - Ensures all transcription threads are completed before proceeding.

5. **Summarizing Transcripts**:

   - Compiles all collected transcripts into one text.
   - Uses OpenAI's GPT model to generate a summary based on a custom prompt.

6. **Saving Outputs**:

   - Saves the full transcript and the summary in a session folder named by the user.

---

## Troubleshooting

### No Audio Captured

- **Check Audio Settings**:

  - Ensure the **Multi-Output Device** is set as the output device.
  - Ensure **BlackHole 2ch** is selected as the input device.

- **Volume Levels**:

  - Adjust the volume levels in the **Audio MIDI Setup** application.

### Permissions

- **Microphone Access**:

  - macOS may prompt you to grant microphone access to the Terminal or Python interpreter.
  - Go to **System Preferences > Security & Privacy > Privacy > Microphone** and ensure the necessary permissions are granted.

### Device Not Found Error

- **Device Name Mismatch**:

  - Verify the exact name of the **BlackHole** device in `Audio MIDI Setup`.
  - Update the `DEVICE_NAME` variable in the script if necessary.

  ```python
  DEVICE_NAME = 'BlackHole 2ch'
  ```

- **List Available Devices**:

  - Use the following code snippet to list available devices and their indices:

    ```python
    import sounddevice as sd
    print(sd.query_devices())
    ```

### API Errors

- **Invalid API Key**:

  - Ensure your OpenAI API key is correct and has the necessary permissions.

- **Rate Limits**:

  - Be mindful of API rate limits and usage policies.

### Recording Stops Unexpectedly

- **Exceptions**:

  - Check the terminal output for any exception messages.
  - Ensure that the script handles exceptions gracefully.

---

## Legal and Ethical Considerations

- **Permission to Record**:

  - Ensure you have the legal right to record and process the audio content.
  - Recording copyrighted material without permission may violate laws and regulations.

- **Privacy**:

  - Be mindful of privacy concerns when recording system audio.
  - Avoid recording sensitive or confidential information.

- **Compliance with OpenAI Policies**:

  - Adhere to OpenAI's usage policies regarding content and data handling.
  - Do not use the APIs for prohibited content as defined in the policies.

---

## License

This project is licensed under the [MIT License](LICENSE).

---