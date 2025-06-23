import os
import subprocess
import json # Import json to parse ffprobe output

from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip, AudioFileClip, ColorClip
from moviepy.video.tools.subtitles import SubtitlesClip

def addTextBlock(
    videoPath,
    audioPath,
    title,
    caption,
    outputPath,
    titleColor ='white',
    titleSize = 100,
    titleMargin = (0,40),
    titleFont = "fonts/Oswald-VariableFont_wght.ttf",
    titlePosition = ("center", 350),
    captionColor ='white',
    captionSize = 80,
    captionMargin = (0,40),
    captionFont = "fonts/Oswald-VariableFont_wght.ttf",
    captionPosition = ("center", 1400)
):
    addedImage = ImageClip(videoPath)
    audio = AudioFileClip(audioPath)
    video_width, video_height = addedImage.size
    target_text_width = int(video_width * 0.8)
    addedImage = addedImage.with_duration(audio.duration)
    #https://fonts.google.com/

    titleClip = TextClip(
        text = title,
        color= titleColor,
        size=(target_text_width, None), 
        method='caption',
        text_align='center',
        font_size = titleSize,
        margin = titleMargin,
        font = titleFont,
        duration = audio.duration
    ).with_position(titlePosition).with_start(0)

    captionClip = TextClip(
        text = caption,
        color= captionColor,
        size=(target_text_width, None), 
        method='caption',
        text_align='center',
        font_size = captionSize,
        margin = captionMargin,
        font = captionFont,
        duration = audio.duration
    ).with_position(captionPosition).with_start(0)

    canvas_width = 1080 
    canvas_height = 1920
    background = ColorClip(size=(canvas_width, canvas_height), color=(0, 0, 0), duration=audio.duration)
    addedImage.with_position('center')

    final_clip = CompositeVideoClip([background, addedImage, titleClip, captionClip])

    final_clip = final_clip.with_audio(audio)
    final_clip.write_videofile(outputPath, codec="libx264", fps= 30)

def combineMedia(title, statements,output_filename="output_shorts.mp4"):
    n_pairs = len(statements)

    image_files = []
    audio_files = []
    audio_durations = []


    segment_commands = []
    segment_files = []
    for i in range(n_pairs):
        segment_output = f"temp_segment_{i}.mp4"
        segment_files.append(segment_output)


    # Step 2: Create a concatenation list file
    concat_list_file = "concat_list.txt"
    with open(concat_list_file, "w") as f:
        for seg_file in segment_files:
            f.write(f"file '{seg_file}'\n")
    print(f"\nCreated concatenation list file: '{concat_list_file}'")
    print("Content:")
    with open(concat_list_file, "r") as f:
        print(f.read())

    # Step 3: Concatenate all segments
    final_concat_cmd = (
        f"ffmpeg -f concat -safe 0 -i \"{concat_list_file}\" "
        f"-c copy \"{output_filename}\""
    )
    print(f"\nCommand to concatenate all segments:")
    print(final_concat_cmd)
    print(f"\nAfter running this script, '{output_filename}' will be your YouTube Shorts video.")



    for i,x in enumerate(statements):
        basePath = f'media/'
        input_video = f"img-{i}.png"
        input_audio = f'audio-{i}.wav'
        output_path = f"temp_segment_{i}.mp4"
        text_to_add = x

        addTextBlock(
            title = title,
            caption =text_to_add,
            videoPath=basePath+input_video,
            audioPath=basePath+input_audio,
            outputPath=output_path

        )

    # Execute the final concatenation command
    print(f"\nExecuting: {final_concat_cmd}")
    subprocess.run(final_concat_cmd, shell=True, check=True)

    print(f"\nSuccessfully created '{output_filename}'")

    # Clean up (uncomment these lines if you want the script to remove temp files)
    for seg_file in segment_files:
        os.remove(seg_file)
    os.remove(concat_list_file)
    print("Cleaned up temporary files.")




if __name__ == '__main__':
    import os
    if os.path.exists('output_shorts.mp4'):
        os.remove('output_shorts.mp4')
    combineMedia("whats up bro",['Hello my name is rio shintani how are you doing']*1, )