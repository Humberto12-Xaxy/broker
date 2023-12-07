import os
from client_open_ai import get_client as client
from time import time
from convert_audio import convert_mp3_to_wav_8000hz_mono

class TextToSpeech:

    def __init__(self) -> None:
        self.client = client()
        self.audio_name = 'speech.mp3'
        self.new_audio_name = 'speech.wav'

    def generate_audio(self, text:str) -> None:
        '''
        Crea un audio para que pueda ser reproducido para responder un cliente 
        Args:
            text: Texto que se convertirá en audio
        '''
        
        response = self.client.audio.speech.create(
            model = 'tts-1',
            voice = 'shimmer',
            input = text,
            response_format = 'mp3'
        )
        
        response.stream_to_file(self.audio_name)

        convert_mp3_to_wav_8000hz_mono(mp3_file_path= self.audio_name, wav_file_path= self.new_audio_name)

        os.remove(self.audio_name)

if __name__ == '__main__':
    text_to_speech = TextToSpeech()

    start = time()
    text_to_speech.generate_audio('Al conjunto de letras, signos de puntuación y números que hacen referencia a un texto bíblico en particular, le llamamos: cita bíblica.')
    end = time()

    time_trans = end - start

    print(time_trans)