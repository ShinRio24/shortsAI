import json
import asyncio
import aiohttp
import base64
import os
from dotenv import load_dotenv
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, ColorClip
from moviepy.editor import vfx # For visual effects like pan

# Load environment variables from .env file for local development
load_dotenv()

async def generate_youtube_shorts_script(topic: str) -> list[str]:
    """
    Generates a YouTube Shorts video script in Japanese for a given topic
    using the Gemini API. The script is returned as a list of sentences/statements.

    Args:
        topic (str): The topic for the YouTube Shorts video.

    Returns:
        list[str]: A list of strings, where each string is a sentence,
                   statement, or fact in Japanese for the video script.
                   Returns an empty list if generation fails.
    """
    prompt = (
        f"YouTubeショート動画の台本を作成してください。テーマは「{topic}」です。 "
        "日本の視聴者が楽しめるように、面白くてエンターテイメント性のある内容にしてください。 "
        "各文がリストの項目になるように、箇条書き形式で提供してください。 "
        "例：\n"
        "1. こんにちは皆さん！\n"
        "2. 今日はすごいことを紹介します。\n"
        "3. これは本当に驚きです！\n"
        "4. 最後に、ぜひチャンネル登録を！"
    )

    chat_history = []
    chat_history.append({"role": "user", "parts": [{"text": prompt}]})

    payload = {
        "contents": chat_history,
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "ARRAY",
                "items": {
                    "type": "STRING"
                }
            }
        }
    }

    api_key = os.getenv("gemeniKey", "")
    if not api_key:
        print("Warning: 'gemeniKey' not found in environment variables. API calls might fail.")

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(api_url, headers={'Content-Type': 'application/json'}, json=payload) as response:
                response.raise_for_status()
                result = await response.json()

                if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
                    script_json_string = result["candidates"][0]["content"].get("parts")[0].get("text", "")
                    if script_json_string:
                        script_list = json.loads(script_json_string)
                        return script_list
                    else:
                        print("Error: Empty text part in script generation response.")
                        return []
                else:
                    print("Error: Unexpected API response structure or no content from script generation.")
                    return []
        except aiohttp.ClientError as e:
            print(f"Error calling Gemini API for script generation: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response from script generation API: {e}")
            return []
        except Exception as e:
            print(f"An unexpected error occurred during script generation: {e}")
            return []

async def generate_image_from_text(prompt: str) -> str:
    """
    Generates an image using the Google Imagen API (imagen-3.0-generate-002).

    Args:
        prompt (str): The text description for the image to be generated.

    Returns:
        str: A base64 encoded data URL for the generated image (e.g., "data:image/png;base64,...").
             Returns an empty string if image generation fails.
    """
    payload = {
        "instances": {"prompt": prompt},
        "parameters": {"sampleCount": 1}
    }

    api_key = os.getenv("gemeniKey", "")
    if not api_key:
        print("Warning: 'gemeniKey' not found in environment variables. API calls might fail.")

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"

    async with aiohttp.ClientSession() as session:
        try:
            print(f"Generating image for prompt: '{prompt[:50]}...'")
            async with session.post(api_url, headers={'Content-Type': 'application/json'}, json=payload) as response:
                response.raise_for_status()
                result = await response.json()

                if result.get("predictions") and len(result["predictions"]) > 0 and result["predictions"][0].get("bytesBase64Encoded"):
                    base64_image_data = result["predictions"][0]["bytesBase64Encoded"]
                    image_url = f"data:image/png;base64,{base64_image_data}"
                    print("Image generated successfully!")
                    return image_url
                else:
                    print("Error: Unexpected API response structure or no image content from image generation.")
                    return ""
        except aiohttp.ClientError as e:
            print(f"Error calling Imagen API for image generation: {e}")
            return ""
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response from image generation API: {e}")
            return ""
        except Exception as e:
            print(f"An unexpected error occurred during image generation: {e}")
            return ""

async def generate_audio_from_text(text: str) -> str:
    """
    Generates audio for a given Japanese text using the Gemini Text-to-Speech API.

    Args:
        text (str): The Japanese text to convert to speech.

    Returns:
        str: A base64 encoded data URL for the generated audio (e.g., "data:audio/mp3;base64,...").
             Returns an empty string if audio generation fails.
    """
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": text}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "audio/mpeg",
            "audioConfig": {
                "sampleRateHertz": 24000,
                "speakingRate": 1.0,
                "pitch": 0.0,
                "volumeGainDb": 0.0,
                "effectsProfileId": [],
                "enableTimePointing": [],
                "languageCode": "ja-JP",
                "ssmlGender": "FEMALE"
            }
        }
    }

    api_key = os.getenv("gemeniKey", "")
    if not api_key:
        print("Warning: 'gemeniKey' not found in environment variables. API calls might fail.")

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={api_key}"

    async with aiohttp.ClientSession() as session:
        try:
            print(f"Generating audio for text: '{text[:30]}...'")
            async with session.post(api_url, headers={'Content-Type': 'application/json'}, json=payload) as response:
                response.raise_for_status()
                result = await response.json()

                if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
                    audio_data_base64 = result["candidates"][0]["content"]["parts"][0]["text"]
                    audio_url = f"data:audio/mp3;base64,{audio_data_base64}"
                    print("Audio generated successfully!")
                    return audio_url
                else:
                    print("Error: Unexpected API response structure or no audio content from TTS generation.")
                    return ""
        except aiohttp.ClientError as e:
            print(f"Error calling TTS API for audio generation: {e}")
            return ""
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response from TTS generation API: {e}")
            return ""
        except Exception as e:
            print(f"An unexpected error occurred during audio generation: {e}")
            return ""

# Example usage (run this in an async context, e.g., in a Jupyter notebook or with asyncio.run())
async def main():
    topic_input = "日本の伝統的な祭り" # Example topic in Japanese
    script = await generate_youtube_shorts_script(topic_input)

    if script:
        print(f"\n--- YouTube Shorts Script for '{topic_input}' ---")
        
        # Store paths to saved image and audio files
        video_segments_data = []

        # Create a directory to save generated files
        output_dir = "youtube_shorts_assets"
        os.makedirs(output_dir, exist_ok=True)
        print(f"Assets will be saved in: {os.path.abspath(output_dir)}")

        for i, sentence in enumerate(script):
            print(f"\nProcessing line {i+1}: {sentence}")

            # Generate an image for each sentence
            # Note: For better quality or specific styles, you might refine the image_prompt
            # based on the overall video theme or even the specific sentence's content.
            image_prompt = f"YouTubeショート動画の背景画像：日本の伝統的な祭り、{topic}に関連する情景、鮮やかで魅力的な縦型アートスタイル。具体的に示す：{sentence}"
            image_data_url = await generate_image_from_text(image_prompt)
            image_file_path = ""
            if image_data_url:
                image_filename = f"{output_dir}/image_line_{i+1}.png"
                try:
                    with open(image_filename, "wb") as f:
                        f.write(base64.b64decode(image_data_url.split(',')[1]))
                    image_file_path = image_filename
                    print(f"Image saved to: {image_file_path}")
                except Exception as e:
                    print(f"Error saving image file: {e}")
            else:
                print(f"Failed to generate image for line {i+1}.")

            # Generate audio for each sentence
            audio_data_url = await generate_audio_from_text(sentence)
            audio_file_path = ""
            if audio_data_url:
                audio_filename = f"{output_dir}/audio_line_{i+1}.mp3"
                try:
                    with open(audio_filename, "wb") as f:
                        f.write(base64.b64decode(audio_data_url.split(',')[1]))
                    audio_file_path = audio_filename
                    print(f"Audio saved to: {audio_file_path}")
                except Exception as e:
                    print(f"Error saving audio file: {e}")
            else:
                print(f"Failed to generate audio for line {i+1}.")
            
            # Store information for video generation
            if image_file_path and audio_file_path:
                video_segments_data.append({
                    "line_text": sentence,
                    "image_path": image_file_path,
                    "audio_path": audio_file_path
                })
            else:
                print(f"Skipping video segment for line {i+1} due to missing assets.")

        print("\n--- Script and Asset Generation Complete ---")

        if video_segments_data:
            print("\n--- Generating YouTube Shorts Video (using moviepy) ---")
            
            final_clips = []
            shorts_width, shorts_height = 1080, 1920 # Standard YouTube Shorts resolution (9:16)

            for i, segment in enumerate(video_segments_data):
                try:
                    audio_clip = AudioFileClip(segment['audio_path'])
                    segment_duration = audio_clip.duration

                    # Load image and resize/crop for vertical shorts
                    img_clip = ImageClip(segment['image_path']).set_duration(segment_duration)
                    
                    # Ensure image fits vertically and is centered, allowing for horizontal panning
                    # If image is wider than 9:16, it will be cropped horizontally.
                    # If image is taller than 9:16, it will be resized to fit height.
                    # For a pan effect, we'll start zoomed in slightly and move across.
                    
                    # Calculate aspect ratio of the generated image
                    img_aspect_ratio = img_clip.w / img_clip.h

                    if img_aspect_ratio > (shorts_width / shorts_height): # Image is wider than Shorts aspect ratio
                        # Resize image so its height matches shorts_height, then pan across its width
                        scaled_height = shorts_height
                        scaled_width = int(img_clip.w * (scaled_height / img_clip.h))
                        resized_img_clip = img_clip.resize(height=scaled_height)

                        # Define pan start/end positions
                        # Pan from left to right (e.g., start at x=0, end at x=max_pan_distance)
                        pan_start_x = 0
                        pan_end_x = max(0, scaled_width - shorts_width) # Max pan distance without going out of bounds
                        
                        # Use a custom function for horizontal pan
                        def horizontal_pan(t):
                            x_pos = pan_start_x - (pan_end_x * (t / segment_duration))
                            return (x_pos, 0) # (x, y)
                        
                        # Create a composite video clip with the background and the panning image
                        background_clip = ColorClip((shorts_width, shorts_height), color=(0,0,0)).set_duration(segment_duration)
                        final_img_clip = CompositeVideoClip([
                            background_clip,
                            resized_img_clip.set_position(horizontal_pan)
                        ], size=(shorts_width, shorts_height))

                    else: # Image is taller or same aspect ratio as Shorts, pan vertically
                        # Resize image so its width matches shorts_width, then pan across its height
                        scaled_width = shorts_width
                        scaled_height = int(img_clip.h * (scaled_width / img_clip.w))
                        resized_img_clip = img_clip.resize(width=scaled_width)

                        # Define pan start/end positions
                        # Pan from top to bottom (e.g., start at y=0, end at y=max_pan_distance)
                        pan_start_y = 0
                        pan_end_y = max(0, scaled_height - shorts_height)
                        
                        # Use a custom function for vertical pan
                        def vertical_pan(t):
                            y_pos = pan_start_y - (pan_end_y * (t / segment_duration))
                            return (0, y_pos) # (x, y)
                        
                        # Create a composite video clip with the background and the panning image
                        background_clip = ColorClip((shorts_width, shorts_height), color=(0,0,0)).set_duration(segment_duration)
                        final_img_clip = CompositeVideoClip([
                            background_clip,
                            resized_img_clip.set_position(vertical_pan)
                        ], size=(shorts_width, shorts_height))


                    # Set the audio for the image clip
                    final_clip = final_img_clip.set_audio(audio_clip)
                    final_clips.append(final_clip)
                    print(f"Segment {i+1} prepared for video.")

                except Exception as e:
                    print(f"Error processing video segment for line {i+1}: {e}")
                    # Clean up partial clips if an error occurs
                    if 'audio_clip' in locals():
                        audio_clip.close()
                    if 'img_clip' in locals():
                        img_clip.close()
                    # Continue to next segment even if one fails
                    continue

            if final_clips:
                print("\nConcatenating all video clips...")
                try:
                    final_video = concatenate_videoclips(final_clips, method='compose')
                    output_video_filename = f"{output_dir}/youtube_shorts_output.mp4"
                    print(f"Writing final video to: {output_video_filename}")
                    final_video.write_videofile(
                        output_video_filename,
                        fps=24, # Frames per second
                        codec='libx264', # H.264 codec
                        audio_codec='aac', # AAC audio codec
                        temp_audiofile=f"{output_dir}/temp_audio.m4a", # Temporary file for audio
                        remove_temp=True # Remove temporary files after completion
                    )
                    print("\n--- Video Generation Complete! ---")
                    print(f"Your YouTube Shorts video is saved as: {os.path.abspath(output_video_filename)}")
                    print("You can now upload this file to YouTube Shorts.")
                except Exception as e:
                    print(f"Error during final video concatenation or writing: {e}")
            else:
                print("No valid video clips to concatenate. Video generation aborted.")

    else:
        print("Failed to generate script.")

# --- How to run this code ---
# 1. Save the code: Save this entire block as a Python file (e.g., `generate_shorts.py`).
# 2. Create a .env file: In the same directory, create a file named `.env` and add your API key:
#    `gemeniKey="YOUR_GEMINI_API_KEY_HERE"`
# 3. Install dependencies: Open your terminal or command prompt and run:
#    `pip install python-dotenv aiohttp moviepy`
#    You also need `ffmpeg` installed on your system, which `moviepy` uses for video processing.
#    - For Windows: Download from https://ffmpeg.org/download.html and add to PATH.
#    - For macOS: `brew install ffmpeg` (if you have Homebrew)
#    - For Linux: `sudo apt update && sudo apt install ffmpeg` (for Debian/Ubuntu)
# 4. Run the script:
#    `python generate_shorts.py`
#
# This will create a `youtube_shorts_assets` folder containing images, audio, and the final MP4 video.
if __name__ == "__main__":
    asyncio.run(main())
