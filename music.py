"""Five local tracks, streamed sequentially. Missing audio never blocks play."""
import pygame as pg
from settings import BASE_DIR
MUSIC_END=pg.USEREVENT+7
class MusicPlayer:
    def __init__(self,root=None,volume=.35):
        root=root or BASE_DIR/'assets/music'
        try:self.tracks=sorted((p for p in root.iterdir() if p.is_file() and p.suffix.lower() in ('.mp3','.ogg','.wav')),key=lambda p:p.name.casefold())[:5] if root.exists() else []
        except OSError:self.tracks=[]
        self.index=-1; self.volume=volume; self.muted=False; self.paused=False; self.failed=set(); self.current=None
        if pg.mixer.get_init(): pg.mixer.music.set_endevent(MUSIC_END)
        self.next()
    @property
    def label(self):
        if not self.tracks:return 'SEM MP3 • adicione em assets/music'
        if not pg.mixer.get_init():return 'ÁUDIO INDISPONÍVEL'
        if self.current is None:return 'FAIXAS INVÁLIDAS • verifique os arquivos'
        return ('MUDO • ' if self.muted else '')+f'{self.index+1}/{len(self.tracks)} '+self.current.stem
    def next(self):
        if not self.tracks or not pg.mixer.get_init():return
        for _ in self.tracks:
            self.index=(self.index+1)%len(self.tracks)
            if self.index in self.failed:continue
            try:
                pg.mixer.music.load(str(self.tracks[self.index])); pg.mixer.music.set_volume(0 if self.muted else self.volume)
                pg.mixer.music.play(); self.current=self.tracks[self.index]
                if self.paused:pg.mixer.music.pause()
                return
            except (pg.error,OSError):self.failed.add(self.index)
        self.current=None
    def handle_end(self):
        # Replacing a track can leave an end event queued for the previous one.
        if self.paused or pg.mixer.get_init() and pg.mixer.music.get_busy():return
        self.next()
    def set_volume(self,value):
        self.volume=max(0,min(1,value))
        if pg.mixer.get_init(): pg.mixer.music.set_volume(0 if self.muted else self.volume)
    def toggle(self):
        self.muted=not self.muted; self.set_volume(self.volume)
    def pause(self,value):
        if value==self.paused:return
        self.paused=value
        if pg.mixer.get_init():
            if value:pg.mixer.music.pause()
            else:pg.mixer.music.unpause()
