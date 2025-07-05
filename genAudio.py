import requests
import json
import os
from dotenv import load_dotenv
import base64

load_dotenv()
TTS_API_KEY = os.getenv("gemeniKey", "")

from google import genai
from google.genai import types
import wave


import contextlib
import wave
from IPython.display import Audio


def genAUDIO(context,num):
    google= False
    if google:
        genWGoogle(context,num)
    else:
        genLib(context,num)

def genLib(context,num):
    from melo.api import TTS

    # Speed is adjustable
    speed = 1.2
    device = 'cpu' # or cuda:0

    text = context

    client = genai.Client(api_key=TTS_API_KEY)
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"""For the following script convert all of the english words into katagana. Do not change anything else, output exactly what is given to you with english words swapped: Here is the script: {text}
    example:
    input: こんにちわgoogle
    output: こんにちわグーグル
    """
    )
    text= response.text
    model = TTS(language='JP', device=device)
    speaker_ids = model.hps.data.spk2id

    output_path = f'media/audio-{num}.wav'
    print(text)
    model.tts_to_file(text, speaker_ids['JP'], output_path, speed=speed)

def genWGoogle(context,num):

    @contextlib.contextmanager
    def wave_file(filename, channels=1, rate=24000, sample_width=2):
        with wave.open(filename, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(rate)
            yield wf

    def play_audio_blob(blob):
        fname = f'media/audio-{num}.wav'
        with wave_file(fname) as wav:
            wav.writeframes(blob.data)

        return Audio(fname, autoplay=True)

    def play_audio(response):
        return play_audio_blob(response.candidates[0].content.parts[0].inline_data)

    client = genai.Client(api_key=TTS_API_KEY)

    MODEL_ID="gemini-2.5-flash-preview-tts"
    voice_name = "kore" # @param ["Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda", "Orus", "Aoede", "Callirhoe", "Autonoe", "Enceladus", "Iapetus", "Umbriel", "Algieba", "Despina", "Erinome", "Algenib", "Rasalgethi", "Laomedeia", "Achernar", "Alnilam", "Schedar", "Gacrux", "Pulcherrima", "Achird", "Zubenelgenubi", "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafar"]
    #https://ai.google.dev/gemini-api/docs/speech-generation#voices

    response = client.models.generate_content(
    model=MODEL_ID,
    contents=context,
    config={
        "response_modalities": ['Audio'],
        "speech_config": {
            "voice_config": {
                "prebuilt_voice_config": {
                    "voice_name": voice_name
                }
            }
        }
    },
    )

    play_audio(response)
        
        
    data = response
    #print(data)
    blob = response.candidates[0].content.parts[0].inline_data
    play_audio_blob(blob)


if __name__ == '__main__':
    genAUDIO("彼は毎朝ジョギングgoogleをして体を健康に保っています。",-1)