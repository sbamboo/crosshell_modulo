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
        def stopAll(self):
            self.stop_event.set()  # Set the stop event to exit the loop immediately
            if self.play_thread and self.play_thread.is_alive():
                self.play_thread.join(1)  # Wait for 1 second for the thread to finish gracefully
            self.play_thread = None
# Window using winsound
elif platformv == "Windows":
    _ = autopipImport("winsound")
    import winsound
    class SoundMap():
        def __init__(self):
            pass
        def playSound(self,mFile,loop=False):
            if loop == True:
                winsound.PlaySound(mFile,winsound.SND_ASYNC | winsound.SND_LOOP)
            else:
                winsound.PlaySound(mFile,winsound.SND_ASYNC)
        def stopAll(self):
            winsound.PlaySound(None, winsound.SND_PURGE)