from pydub import AudioSegment

def convert_mp3_to_wav_8000hz_mono(mp3_file_path, wav_file_path):
    """
    Convert an MP3 file to a mono WAV file with 16-bit samples and 8000 Hz frame rate.

    :param mp3_file_path: Path to the input MP3 file.
    :param wav_file_path: Path where the output WAV file will be saved.
    :return: None
    """

    # Load the MP3 file
    AudioSegment.ffmpeg = r'C:\ProgramData\chocolatey\lib'
    AudioSegment.from_mp3(mp3_file_path).export(wav_file_path, format="wav", codec="pcm_mulaw", parameters=["-ar","8000"])


    print(f"MP3 file '{mp3_file_path}' has been converted to a mono WAV file '{wav_file_path}' with 16-bit samples and 8000 Hz frame rate.")



