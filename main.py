import time
from ia import IA
from text_to_speech import TextToSpeech

import base64
import json
import os
import audioop
import asyncio

import vosk
from google.cloud import speech

from pyngrok import ngrok

from flask import Flask, request
from flask_sock import Sock, ConnectionClosed

from twilio.twiml.voice_response import VoiceResponse, Connect
from twilio.rest import Client

from dotenv import load_dotenv 


load_dotenv()

app = Flask(__name__)
sock= Sock(app)

client = Client(os.getenv('TWILIO_KEY'), os.getenv('TWILIO_SECRET_KEY'))
model = vosk.Model('model')

ia = IA()
text_to_speech = TextToSpeech()

CL = '\x1b[0K'
BS = '\x08'

HTTP_SERVER_PORT = 5000

AUDIO_NAME = 'speech.wav' 

response = VoiceResponse()

@app.route('/call', methods = ['POST'])
def call():
    '''Accept a phone call'''
    connect = Connect()
    connect.stream(url= f'wss://{request.host}/stream')
    response.append(connect)

    print(f'Incoming call from {request.form["From"]}')

    return str(response), 200, {'Content-Type' : 'text/xml'}

@sock.route('/stream')
def stream(ws):
    try:
        print("Connection accepted")

        rec = vosk.KaldiRecognizer(model, 16000)
        message_count = 0

        while True:
            
            message = ws.receive()
            data = json.loads(message)
            response_message = ''

            if data['event'] == 'connected':
                print(f'Connected Message received: {message}')
        
            elif data['event'] == "start":
                print(f"\n Start Message received: {message}")
            elif data['event'] == "media":
                
                audio = base64.b64decode(data['media']['payload'])

                audio = audioop.ulaw2lin(audio, 2)
                audio = audioop.ratecv(audio, 2, 1, 8000, 16000, None)[0]

                if rec.AcceptWaveform(audio):
                    
                    r = json.loads(rec.Result())
                    text = r['text']
                    print(text, end='', flush= True)
                    
                    if text:
                        response_message = ia.get_information(text)

                        print(f'Respuesta de la IA: {response_message}', flush= True)
                        
                        text_to_speech.generate_audio(response_message)

                        asyncio.run(send_raw_audio(ws, data['streamSid'], AUDIO_NAME))
                        
                        if response_message.find('día') != -1 or response_message.find('222') != -1 or text.find('no importa') != -1:
                            print('Entré al if que finaliza la llamada')
                            response_message = ia.get_information(text)
                            time.sleep(2)
                            break
                        
                    
                    text = ''

                else:
                    r = json.loads(rec.PartialResult())     
                    print(CL + r['partial'] + BS * len(r['partial']), end= '', flush= True)
            elif data['event'] == "stop":
                print(f'\n Closed Message received: {message}')
                break
            message_count += 1

        print("Connection closed. Received a total of {} messages".format(message_count))

    except Exception as e:
        print(f'Error: {e}')


async def send_raw_audio(ws, stream_sid, audio_name):
    try:
        with open(audio_name, 'rb') as audio:
            while True:
                frame_data = audio.read(1024)

                if len(frame_data) == 0:
                    print('No more data')
                    break
                    
                base64_data = base64.b64encode(frame_data).decode(encoding='ascii')

                media_data = {
                    'event': 'media',
                    'streamSid' : stream_sid,
                    'media' : {
                        'payload' : base64_data
                    }
                }

                media = json.dumps(media_data)
                ws.send(media)
    except Exception as e:
        print(f'Error: {e}')        
    print('finished sending')


if __name__ == '__main__':
    public_url = ngrok.connect(HTTP_SERVER_PORT, bind_tls = True).public_url
    number = client.incoming_phone_numbers.list()[0]
    number.update(voice_url= public_url + '/call')

    print(f'Waiting for calls on {number.phone_number}')

    app.run(port= HTTP_SERVER_PORT)