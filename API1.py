import os
import sys

import requests
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5.QtCore import Qt

SCREEN_SIZE = [600, 500]


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('map.ui', self)
        self.setWindowTitle('Отображение карты')
        self.lineEdit.textChanged.connect(self.getImage)
        self.lineEdit_2.textChanged.connect(self.getImage)
        self.horizontalSlider.sliderMoved.connect(self.getImage)

    def getImage(self):
        params = {
            'll': ','.join([self.lineEdit_2.text(), self.lineEdit.text()]),
            'z': str(self.horizontalSlider.sliderPosition()),
            'l': 'map'
        }
        server = "http://static-maps.yandex.ru/1.x"
        response = requests.get(server, params=params)

        if response:
            self.map_file = "map.png"
            with open(self.map_file, "wb") as file:
                file.write(response.content)
            pixmap = QPixmap(self.map_file)
            self.image.setPixmap(pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.horizontalSlider.setSliderPosition(self.horizontalSlider.sliderPosition()+1)
            self.getImage()
        elif event.key() == Qt.Key_PageDown:
            self.horizontalSlider.setSliderPosition(self.horizontalSlider.sliderPosition()-1)
            self.getImage()

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
