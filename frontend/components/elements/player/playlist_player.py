from typing import Sequence

from PyQt5 import QtCore, QtWidgets

from frontend.components.elements.player.music_player import MusicPlayer


class PlaylistPlayer(QtWidgets.QWidget):
    playRequested = QtCore.pyqtSignal(int)
    pauseRequested = QtCore.pyqtSignal(int)
    seekRequested = QtCore.pyqtSignal(int, float)

    def __init__(
        self,
        playlist_metadata: Sequence[dict[str, object]] | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setMinimumWidth(300)
        self.music_players = []
        self.playlist_metadata = playlist_metadata or []

        self.music_player_container = QtWidgets.QWidget(self)
        self.music_player_layout = QtWidgets.QVBoxLayout(self.music_player_container)
        self.music_player_layout.setContentsMargins(0, 0, 0, 0)
        self.music_player_layout.setSpacing(2)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.music_player_container)

        self.set_playlist_metadata(self.playlist_metadata)

    def set_playlist_metadata(self, playlist_metadata):
        self.playlist_metadata = playlist_metadata or []
        self.music_players = []

        while self.music_player_layout.count():
            item = self.music_player_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for index, music_metadata in enumerate(self.playlist_metadata):
            artist = music_metadata.get("artist", "")
            title = music_metadata.get("title", "")
            duration = float(music_metadata.get("duration", 0))

            music_player = MusicPlayer(
                index=index,
                artist=artist,
                title=title,
                music_length=duration,
                disabled=True,
            )
            music_player.playClicked.connect(self.on_play_clicked)
            music_player.pauseClicked.connect(self.on_pause_clicked)
            music_player.seekChanged.connect(self.on_seek_changed)

            self.music_player_layout.addWidget(music_player)
            self.music_players.append(music_player)

        self.music_player_container.adjustSize()
        self.adjustSize()

    def set_loaded(self, index, loaded=True):
        if 0 <= index < len(self.music_players):
            self.music_players[index].set_loaded(loaded)

    def set_position(self, index, position):
        if 0 <= index < len(self.music_players):
            self.music_players[index].set_position(position)

    def on_play_clicked(self, index):
        for i, player in enumerate(self.music_players):
            if i != index:
                player.set_playing(False)
        self.playRequested.emit(index)

    def on_pause_clicked(self, index):
        self.pauseRequested.emit(index)

    def on_seek_changed(self, index, ratio):
        self.seekRequested.emit(index, ratio)
