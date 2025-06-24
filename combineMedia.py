import os
import subprocess
import json # Import json to parse ffprobe output

from moviepy import VideoFileClip, TextClip, CompositeVideoClip, ImageClip, AudioFileClip, ColorClip, concatenate_videoclips
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
    titleFont = "fonts/NotoSansJP-SemiBold.ttf",
    titlePosition = ("center", 300),
    captionColor ='white',
    captionSize = 80,
    captionMargin = (0,40),
    captionFont = "fonts/NotoSansJP-SemiBold.ttf",
    captionPosition = ("center", 1400)
):
    audio = AudioFileClip(audioPath)
    addedImage = ImageClip(videoPath)
    video_width, video_height = addedImage.size
    target_text_width = int(video_width * 0.8)
    #https://fonts.google.com/
    #https://fonts.google.com/noto/specimen/Noto+Sans+JP

    
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
    imWidth,imHeight = addedImage.size
    addedImage = addedImage.resized(width=canvas_width)
    imWidth,imHeight = addedImage.size
    maxHeight= 800
    if imHeight>maxHeight:
        addedImage = addedImage.resized(height= maxHeight)

    addedImage = addedImage.with_duration(audio.duration).with_position('center')


    final_clip = CompositeVideoClip([background, addedImage, titleClip, captionClip])
    final_clip = final_clip.with_audio(audio)
    return final_clip

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


    allClips = []
    for i,x in enumerate(statements):
        basePath = f'media/'
        input_video = f"img-{i}.png"
        input_audio = f'audio-{i}.wav'
        output_path = f"temp_segment_{i}.mp4"
        text_to_add = x

        allClips.append(addTextBlock(
            title = title,
            caption =text_to_add,
            videoPath=basePath+input_video,
            audioPath=basePath+input_audio,
            outputPath=output_path

        ))

    final_video=concatenate_videoclips(allClips)
    final_video.write_videofile(output_filename, codec="libx264", fps=30, audio_codec="aac")

    print(f"\nSuccessfully created '{output_filename}'")





if __name__ == '__main__':
    import os
    if os.path.exists('output_shorts.mp4'):
        os.remove('output_shorts.mp4')
    combineMedia("世界を動かす巨大企業、知ってる？",['その影響力、私たちの想像を超えるかも！']*1, )