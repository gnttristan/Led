from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5 import QtCore, QtWidgets

from frontend.components.elements.element_value import ElementValue


class MusicPlayer(QtWidgets.QWidget):
    playClicked = QtCore.pyqtSignal(int)
    pauseClicked = QtCore.pyqtSignal(int)
    seekChanged = QtCore.pyqtSignal(int, float)
    WIDTH = 300
    HEIGHT = 50

    def __init__(
        self,
        index: int = 0,
        artist: str = "artist",
        title: str = "title",
        music_length: int | float = 0,
        music_position: ElementValue = ElementValue(0),
        disabled: bool = True,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setFixedSize(self.WIDTH, self.HEIGHT)

        self.index = index
        self.artist = artist
        self.title = title
        self.music_position = music_position
        self.music_length = music_length
        self.is_playing = False

        font = QFont()
        font.setPointSize(8)

        vbox_core = QtWidgets.QVBoxLayout(self)
        vbox_core.setContentsMargins(0, 0, 0, 0)
        vbox_core.setSpacing(0)

        hbox_metadatas = QtWidgets.QHBoxLayout()
        artist_label = QtWidgets.QLabel(self.artist)
        title_label = QtWidgets.QLabel(self.title)
        artist_label.setFont(font)
        title_label.setFont(font)

        hbox_metadatas.addWidget(artist_label)
        hbox_metadatas.addWidget(title_label)

        hbox_player = QtWidgets.QHBoxLayout()
        self.play_pause_button = QtWidgets.QPushButton("Play")

        self.music_position_label = QtWidgets.QLabel(f"{self.music_position.value:.2f}")
        self.music_length_label = QtWidgets.QLabel(f"{self.music_length:.2f}")
        self.music_position_label.setFont(font)
        self.music_length_label.setFont(font)

        self.music_position_slider = QtWidgets.QSlider()
        self.music_position_slider.setOrientation(Qt.Orientation.Horizontal)
        self.music_position_slider.setRange(0, 1000)
        self.music_position_slider.setValue(0)
        self.music_position_slider.setFixedWidth(200)
        self.music_position_slider.sliderMoved.connect(self.on_slider_moved)
        self.play_pause_button.clicked.connect(self.on_play_pause_clicked)

        hbox_player.addWidget(self.play_pause_button)
        hbox_player.addWidget(self.music_position_label)
        hbox_player.addWidget(self.music_position_slider)
        hbox_player.addWidget(self.music_length_label)

        vbox_core.addLayout(hbox_metadatas)
        vbox_core.addLayout(hbox_player)
        self.set_loaded(not disabled)

    def set_loaded(self, loaded):
        # QGraphicsOpacityEffect interacts poorly with zoomed proxy widgets.
        # Keep disabled styling lightweight so loaded/unloaded rows scale identically.
        if self.graphicsEffect() is not None:
            self.setGraphicsEffect(None)
        self.setStyleSheet("" if loaded else "QWidget { color: #7a7a7a; }")
        self.play_pause_button.setEnabled(loaded)
        self.music_position_slider.setEnabled(loaded)
        if not loaded:
            self.set_playing(False)

    def set_playing(self, playing):
        self.is_playing = bool(playing)
        self.play_pause_button.setText("Pause" if self.is_playing else "Play")

    def set_from_ratio(self, slider_value):
        position = float(slider_value) * float(self.music_length) / 1000.0
        self.music_position.value = position
        self.music_position_label.setText(f"{position:.2f}")

    def on_slider_moved(self, slider_value):
        self.set_from_ratio(slider_value)
        self.seekChanged.emit(self.index, float(slider_value) / 1000.0)

    def on_play_pause_clicked(self):
        if self.is_playing:
            self.set_playing(False)
            self.pauseClicked.emit(self.index)
        else:
            self.set_playing(True)
            self.playClicked.emit(self.index)
