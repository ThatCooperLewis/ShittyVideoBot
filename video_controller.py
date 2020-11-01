import os
import vlc
import pafy
import pyautogui
from time import sleep

class VideoPlaylist:

    def __init__(self):
        try:
            with open('queue.tweet', 'r') as f:
                list_string = f.readline()
                f.close()
            if list_string != '[]':
                self.queue = list_string.strip("[]'").split(',')
            else: raise Exception
        except:
            self.queue = []

    def __cache(self):
        with open('queue.tweet', 'w+') as f:
            f.write(str(self.queue))
            f.close()

    def add_to_queue(self, url):
        self.queue.append(url)
        self.__cache()

    def get_next(self):
        next = self.queue.pop(0)
        self.__cache()
        return next

    def _empty(self):
        return len(self.queue) == 0 

    is_empty = property(fget=_empty)

class VideoPlayer:

    def __init__(self):
        self.player = None
        self.playlist = VideoPlaylist()

    def _create_player(self, url: str):
        video = pafy.new(url) 
        best = video.streams[-1].url
        return vlc.MediaPlayer(best)


    def play_url(self, url: str):
        content = self._create_player(url)
        content.audio_set_volume(0)
        content.set_fullscreen(True)
        
        if self.player: self.player.stop()
        self.player = content
        self.player.play()
        
        # This clicks into VLC to hide taskbar notification
        pyautogui.click(x=100, y=100)


    def almost_over(self):
        if self.player:
            length = self.player.get_length()
            duration = self.player.get_time()
            if length - duration <= 10000:
                return True
        return False

    def play_next_if_ready(self):
        if self.playlist.is_empty:
            if self.almost_over():
                sleep(5)
                self.player.stop()
            return
        if self.player and not self.almost_over(): return
        self.play_url(self.playlist.get_next())

    def is_playing(self):
        if not self.player: return False
        return self.player.is_playing() == 1

    @classmethod
    def is_valid(cls, url):
        try:
            video = pafy.new(url)
        except:
            return False
        return (video.length <= 1800) and (video.viewcount > 1000)

        
if __name__ == "__main__":
    vid = VideoPlayer()
    print(vid.is_valid('https://www.youtube.com/watch?v=pTQJyZXBlkE'))