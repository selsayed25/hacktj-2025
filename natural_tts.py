from kokoro import KPipeline
import soundfile as sf
from moviepy.audio.AudioClip import concatenate_audioclips
from moviepy import AudioFileClip

class Natural_TTS:
    # # pip install misaki[en]
    # a='American English',
    # b='British English',

    # # espeak-ng
    # e='es',
    # f='fr-fr',
    # h='hi',
    # i='it',
    # p='pt-br',

    # # pip install misaki[ja]
    # j='Japanese',

    # # pip install misaki[zh]
    # z='Mandarin Chinese',
    def __init__(self, language = "a"):
        self.pipeline = KPipeline(lang_code=language, repo_id='hexgrad/Kokoro-82M') # <= make sure lang_code matches voice
    
    def concat_audio(self, n):
        clips = [AudioFileClip(f"{i}.mp3") for i in range(n)]
        final_clip = concatenate_audioclips(clips)
        final_clip.write_audiofile("output.mp3")

    def text_to_speech(self, text, vspeed=1):
        generator = self.pipeline(
            text, voice='af_heart', # <= change voice here
            speed=vspeed , split_pattern=r'\n+'
        )
        # audio_number = len(tuple(generator))
        # print(audio_number)
        j = 1
        for i, (gs, ps, audio) in enumerate(generator):
            # print(i)  # i => index
            # print(gs) # gs => graphemes/text
            # print(ps) # ps => phonemes
            sf.write(f'{i}.mp3', audio, 24000) # save each audio file
            j = max(j, i)
        self.concat_audio(j)