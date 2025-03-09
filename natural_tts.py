from kokoro import KPipeline
import soundfile as sf

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
    def __init__(self, language  = "a"):
        self.pipeline = KPipeline(lang_code='a') # <= make sure lang_code matches voice

    def text_to_speech(self, text, vspeed=1):
        generator = self.pipeline(
            text, voice='af_heart', # <= change voice here
            speed=vspeed #, split_pattern=r'\n+'
        )