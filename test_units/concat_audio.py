from moviepy.audio.AudioClip import concatenate_audioclips
from moviepy import AudioFileClip

audio_number = 6
clips = [AudioFileClip(f"{i}.mp3") for i in range(6)]
final_clip = concatenate_audioclips(clips)
final_clip.write_audiofile("audio.mp3")

