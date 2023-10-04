import platform
from cslib import autopipImport

# SoundMap class based on platform
platformv = platform.system()
# Linux and macOS using simpleaudio
if platformv in ["Linux", "Darwin"]:
    _ = autopipImport("pydub")
    from pydub import AudioSegment
    import threading
    import subprocess
    class SoundMap():
        def __init__(self):
            self.play_thread = None
            self.stop_event = threading.Event()
            self.listLooping = False
        def playSound(self, mFile, loop=False):
            if self.play_thread and self.play_thread.is_alive():
                return  # Ignore if a sound is already playing
            audio = AudioSegment.from_file(mFile)
            self.stop_event.clear()  # Reset the stop event
            self.play_thread = threading.Thread(target=self._play_sound, args=(audio, loop))
            self.play_thread.start()
        def _play_sound(self, audio, loop):
            audio.export('/tmp/tmpaudio.wav', format='wav')  # Export the audio to a temporary WAV file
            command = ['ffplay', '-nodisp', '-autoexit', '/tmp/tmpaudio.wav']
            while loop and not self.stop_event.is_set():
                if self.stop_event.is_set():
                    break
                subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if not loop and not self.stop_event.is_set():
                subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        def _play_sound_list(self, audios, loop):
            if loop == True:
                self.listLooping = True
            ind = 0
            while self.listLooping == True:
                if ind > len(audios)-1:
                    if loop == True:
                        ind = 0
                    else:
                        break
                audio = audios[ind]
                self._play_sound(audio,False)
                ind += 1
        def stopAll(self):
            if self.listLooping == True:
                self.listLooping = False
                self.stopAll()
            self.stop_event.set()  # Set the stop event to exit the loop immediately
            if self.play_thread and self.play_thread.is_alive():
                self.play_thread.join(1)  # Wait for 1 second for the thread to finish gracefully
            self.play_thread = None
        def playList(self,list,loop=False):
            if self.play_thread and self.play_thread.is_alive():
                return  # Ignore if a sound is already playing
            audios = [AudioSegment.from_file(mFile) for mFile in list]
            self.stop_event.clear()  # Reset the stop event
            self.play_thread = threading.Thread(target=self._play_sound_list, args=(audios, loop))
            self.play_thread.start()
# Window using winsound
elif platformv == "Windows":
    _ = autopipImport("winsound")
    import winsound
    import threading
    import wave
    import time
    class SoundMap():
        def __init__(self):
            self.listLooping = False
            self.play_thread = None
        def _get_wav_duration(self,file_path):
            with wave.open(file_path, 'rb') as wav_file:
                # Get the number of frames and the frame rate (samples per second)
                num_frames = wav_file.getnframes()
                frame_rate = wav_file.getframerate()
                # Calculate the duration in seconds
                duration = num_frames / float(frame_rate)
                return duration
        def playSound(self,mFile,loop=False):
            if loop == True:
                winsound.PlaySound(mFile,winsound.SND_ASYNC | winsound.SND_LOOP)
            else:
                winsound.PlaySound(mFile,winsound.SND_ASYNC)
        def stopAll(self):
            if self.listLooping == True:
                self.listLooping = False
                self.stopAll()
            winsound.PlaySound(None, winsound.SND_PURGE)
            if self.play_thread != None:
                self.play_thread.join(1)
                self.play_thread = None
        def _play_sound_list(self,mFileS,loop):
            if loop == True:
                self.listLooping = True
            ind = 0
            while self.listLooping == True:
                if ind > len(mFileS)-1:
                    if loop == True:
                        ind = 0
                    else:
                        break
                mFile = mFileS[ind]
                _len = self._get_wav_duration(mFile)
                winsound.PlaySound(mFile,winsound.SND_ASYNC)
                time.sleep(_len)
                ind += 1
        def playList(self,list,loop=False):
            self.play_thread = threading.Thread(target=self._play_sound_list, args=(list, loop))
            self.play_thread.start()