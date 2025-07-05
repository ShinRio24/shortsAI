import os
import json
import base64
import requests
from io import BytesIO
from dotenv import load_dotenv
from PIL import Image
import wave
import contextlib
from IPython.display import Audio

from google import genai
from google.genai import types

from genAudio import genAUDIO
from genImg import genIMG
from combineMedia import combineMedia
from imgSearch import imgSearch
load_dotenv()
GEMINI_API_KEY = os.getenv("gemeniKey", "")



def generate_video_script(theme):
    """
    Generates a YouTube short video script based on a given theme.
    Returns a list of parsed statements from the script.
    """
    print(f"--- Generating script for theme: '{theme}'... ---")
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)

    script_prompt = (f"""
    Create a highly engaging and dynamic YouTube Short video script about {theme}.

The script should be in Japanese and structured for a fast-paced video, designed to maximize viewer retention and interaction. Ensure the content is concise and impactful. Add meaningful punctuation to make the script read naturally. DO NOT ADD EMOJIS

Please format the output as a list. before each statement, add a 1 or 0. If the statement is about a real, existing place, human or thing, add a 1. (this means the image going with it will be a real photo) if the image is talking about an act, concept, make it 0. (this mean the image going with it will be ai generated). split the number and statement with a period

Here's the required structure for the script:
If the theme is asking for a ranking, (such as top 3 companies) make sure to clearly rank the choices
Hook: Start with a captivating statement or quick visual idea that immediately grabs attention. This should be a very short, impactful phrase.
Introduction: Briefly set the scene or introduce the topic, drawing the viewer further in.
Main Points/Narrative: Develop the core content through a series of distinct, action-oriented sentences or short phrases. Each point should suggest a quick visual cut and contribute to the overall story or message. Focus on clear, impactful imagery.
Concluding Question/Call to Action: End with a thought-provoking question, a challenge, or a simple call to action (e.g., "What do you think?", "Share your experiences!").
Example of how your desired output will be formatted:

0. 世界トップ3の大学ってどこ？！
0. 誰もが憧れる、世界の最高峰の学び舎をご紹介！
1. 第3位！イギリスのオックスフォード大学。800年以上の歴史を誇る、知の殿堂です。
0. 数々の著名人を輩出し、リベラルアーツ教育で世界をリードしています。
1. 第2位！イギリスのインペリアル・カレッジ・ロンドン。科学、工学、医学分野で世界をリードする研究機関です。
0. 最先端のイノベーションと技術開発で知られています。
1. そして第1位は...アメリカのMIT。革新的な技術と研究で未来を創造しています。
0. 世界を動かす画期的な発見が日々生まれる場所です。
0. あなたが行ってみたい大学はどこですか？コメントで教えてね！
    """)
    
    response = gemini_client.models.generate_content(
    model="gemini-2.5-flash",
    contents=script_prompt
    )
    print(response.text)

    # Parse the generated script into individual statements
    script_lines = [line.strip() for line in response.text.split('\n') if line.strip() and line.strip()[0].isdigit()]
    imgFormat = [x[0] for x in script_lines]
    statements = [line[line.find('.') + 1:].strip() for line in script_lines if line.find('.') != -1]
    
    return statements,imgFormat


# Example usage (this part won't execute video creation here):
# If you run this Python script on your local machine,
# it will print the FFmpeg commands for you to use.
# n_images_audios = 3 # Replace with your actual number of pairs
# create_youtube_shorts_video(n_images_audios)


def generate_youtube_short_video(theme):
    """
    Generates a YouTube short video script based on a theme, then
    generates an image and narrates each statement of the script.
    The generated images and audio files are saved locally.
    """
    #print(f"Starting YouTube Short Video component generation for theme: '{theme}'")

    # Step 1: Generate Script for the YouTube Short Video using the new method
    statements,imgFormat = generate_video_script(theme)
    if not statements:
        print("Script generation failed or no statements were parsed. Aborting video component generation.")
        return
    print(statements,imgFormat,'aaaaaaa')
    #print("\n--- Step 2: Processing each statement (generating image and audio)... ---")
    for i, statement in enumerate(statements):
        print(f"\n--- Processing Statement {i+1} of {len(statements)}: \"{statement}\" ---")

        # Generate Image for the current statement
        #print("  Generating image...")
        if imgFormat[i]=='0':
            genIMG(statement,i)
        else:

            print(statement, 'bbbbb')
            imgSearch(statement,i)
            

        # Generate Audio for the current statement
        audio_generation_contents = statement
        #print("  Generating audio...")
        genAUDIO(audio_generation_contents,i)

    #print(statements)

    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    response = gemini_client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"""convert the following theme: {theme} into a short, interesting japanese title. Do not add any additional text except the new title.
    example:
    input: Top 3 companies in the world
    output: 世界のトップ3企業
    """
    )
    print(response.text, "this is the title ")
    combineMedia(response.text, statements)

if __name__ =='__main__':
    # The user's original line is commented out to avoid immediate image generation on load,
    # as the new method will handle the full workflow.
    # tt = genIMG("generate an image of YouTubeショート動画の台本を作成してください。テーマは「college」です。")
    #combineMedia(5)

    # Call the main video generation method. You can change the theme.
    generate_youtube_short_video("世界のトップ3大企業")