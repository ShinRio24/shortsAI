import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("gemeniKey", "")

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

def genIMG(content, num):
    client = genai.Client(api_key=GEMINI_API_KEY)

    script_prompt = (f"""
    Generate a prompt to create a visual for the following line which will be given in japanese: {content}
    Output the prompt in english. You do no need to include everything in the line, the image simply needs to add context and visual
    example:
    input: University of kyoto conducts top research globaly
    output: Generate an image of the university of kyoto""")
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=script_prompt
    )

    print(response.text)
    contents = (response.text)
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=contents,
        config=types.GenerateContentConfig(
        response_modalities=['TEXT','IMAGE']
        )
    )
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO((part.inline_data.data)))
            image.save('media/img-{}.png'.format(num))
            #image.show()

if __name__ == '__main__':
    genIMG('Visualizing: a student wakes up',-1)