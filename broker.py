import io
import os
import threading

from ia import IA
from client_open_ai import get_client

import speech_recognition as sr

from pathlib import Path
import soundfile as sf
import sounddevice as sd


class Broker: 

    '''
        Esta clase sirve para organizar la llamada y redireccionar en caso de que el cliente quiera un paquete
    '''

    def __init__(self) -> None:
        
        # Instancias del microfono y reconocedor de audio
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        self.text = ''
        self.audio_name = 'speech.mp3'
        
        self.client = get_client()
        # Instancias de ia y text_to_speech
        self._ia = IA()

        # Variable para controlar el comportamiento del broker
        self.is_active = True

        # Variable para saber si el bot está hablando
        self.is_speaking = False


    def listen_start(self) -> None:
        self.listen_thread = threading.Thread(target= self.listen)
        self.listen_thread.start()

        print('Se inició el hilo')

    def listen(self) -> None:

        while self.is_active:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)

            with self.microphone as source:
                try:
                    print('Escuchando')
                    audio = self.recognizer.listen(source)
                    
                    buffer = io.BytesIO()

                    buffer.name = 'record.mp3'


                    audio.frame_data
                    # , language= 'es-MX', credentials_json= './key.json'
                    self.recognizer.listen_in_background()
                    self.text = self.recognizer.recognize_google(audio, language= 'es-MX')
                    print('Dijiste: '+ self.text)

                    if self.text != '' and self.is_speaking:
                        self.stop_audio()

                except sr.UnknownValueError:
                    print('No se pudo entender el audio')
                except sr.RequestError as e:
                    print(f'Error en la solicitud: {e}')

        self.is_active = False

    def response_ia(self):

        return self._ia.get_information(self.text)
    
    def play_audio(self, text:str) -> None:
        '''
        Crea un audio para que pueda ser reproducido para responder un cliente 
        Args:
            text: Texto que se convertirá en audio
        '''

        self.is_speaking = True

        speech_file_path = Path(__file__).parent / self.audio_name
        response = self.client.audio.speech.create(
            model = 'tts-1',
            voice = 'shimmer',
            input = text,
            response_format = 'mp3'
        )
        
        response.stream_to_file(self.audio_name)

        audio_data, sample_rate= sf.read(speech_file_path)

        sd.play(audio_data, sample_rate)
        sd.wait()

        os.remove(speech_file_path)

        self.is_speaking = False

    def stop_audio(self):
        self.is_speaking = False
        sd.stop()

        
if __name__ == '__main__':

    broker = Broker()
    
    broker.listen_start()

    while broker.is_active:
        if broker.text != '':
            response = broker.response_ia()
            print(response)
            broker.play_audio(response)

            if response.find('día') != -1 or response.find('222') != -1:
                broker.is_active = False

                broker.listen_thread.join()