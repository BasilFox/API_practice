import os
import sys

import requests
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow


class Example(QMainWindow):
    def __init__(self):
        self.maptype_words = ['Схема', 'Спутник', 'Гибрид']
        self.maptype_API = ['map', 'sat', 'sat,skl']
        self.maptype = 0
        super().__init__()
        uic.loadUi('map.ui', self)
        self.setWindowTitle('Отображение карты')
        self.lineEdit.textChanged.connect(self.getImage)
        self.lineEdit_2.textChanged.connect(self.getImage)
        self.horizontalSlider.sliderMoved.connect(self.getImage)
        self.maptypeButton.clicked.connect(self.maptypechanger)
        self.search.clicked.connect(self.searchfunc)
        self.clearBut.clicked.connect(self.clear)
        self.point_cords = -500, -500
        self.search_flag = False
        self.postal_flag = False
        self.checkBox.stateChanged.connect(self.postal_view)

    def getImage(self):
        if self.point_cords[0] != -500 and self.point_cords[1] != -500:
            self.search_flag = True
        else:
            self.search_flag = False
        if self.search_flag == False:
            params = {
                'll': ','.join([self.lineEdit_2.text(), self.lineEdit.text()]),
                'z': str(self.horizontalSlider.sliderPosition()),
                'l': self.maptype_API[self.maptype % 3]
            }
            server = "http://static-maps.yandex.ru/1.x"
            response = requests.get(server, params=params)

            if response:
                self.map_file = "map.png"
                with open(self.map_file, "wb") as file:
                    file.write(response.content)
                pixmap = QPixmap(self.map_file)
                self.image.setPixmap(pixmap)
        else:

            params = {
                'll': ','.join([self.lineEdit_2.text(), self.lineEdit.text()]),
                'z': str(self.horizontalSlider.sliderPosition()),
                'l': self.maptype_API[self.maptype % 3],
                "pt": f"{self.point_cords[0]},{self.point_cords[1]},pmwtm1"
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
            self.horizontalSlider.setSliderPosition(self.horizontalSlider.sliderPosition() + 1)
            self.getImage()
        elif event.key() == Qt.Key_PageDown:
            self.horizontalSlider.setSliderPosition(self.horizontalSlider.sliderPosition() - 1)
            self.getImage()
        elif event.key() == Qt.Key_Up:
            self.lineEdit.setText(str(float(self.lineEdit.text()) + self.degree.value()))
            self.getImage()
        elif event.key() == Qt.Key_Down:
            self.lineEdit.setText(str(float(self.lineEdit.text()) - self.degree.value()))
            self.getImage()
        elif int(event.modifiers()) == Qt.AltModifier:
            if event.key() == Qt.Key_Left:
                self.lineEdit_2.setText(str(float(self.lineEdit_2.text()) - self.degree.value()))
                self.getImage()
            elif event.key() == Qt.Key_Right:
                self.lineEdit_2.setText(str(float(self.lineEdit_2.text()) + self.degree.value()))
                self.getImage()
        elif event.key() == Qt.Key_Enter:
            self.searchfunc()
        elif event.key() == Qt.Key_Escape:
            self.clear()

    def maptypechanger(self):
        self.maptype += 1
        self.maptypeButton.setText(self.maptype_words[self.maptype % 3])
        self.getImage()

    def searchfunc(self):
        toponym_to_find = self.searchline.text()

        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": toponym_to_find,
            "format": "json"}
        response1 = requests.get(geocoder_api_server, params=geocoder_params)
        if not response1:
            self.search_flag = False
        else:
            self.adressBox_2.clear()
            json_response = response1.json()
            toponym = json_response["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
            if self.postal_flag is False:
                self.adressBox_2.append(
                    toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["formatted"])
            else:
                self.adressBox_2.append(
                    toponym["metaDataProperty"]["GeocoderMetaData"]["Address"][
                        "formatted"] + '\n' + f'Индекс {toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]}')
            toponym_coodrinates = toponym["Point"]["pos"]
            toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
            self.point_cords = toponym_longitude, toponym_lattitude
            self.search_flag = True
            self.lineEdit.setText(toponym_lattitude)
            self.lineEdit_2.setText(toponym_longitude)
            self.horizontalSlider.setSliderPosition(17)
            self.getImage()
            self.search_flag = False

    def closeEvent(self, event):
        os.remove(self.map_file)

    def clear(self):
        self.point_cords = -500, -500
        self.searchline.clear()
        self.adressBox_2.clear()
        self.getImage()

    def postal_view(self):
        if self.checkBox.checkState() == 2:
            self.postal_flag = True
            self.searchfunc()
        else:
            self.postal_flag = False
            self.searchfunc()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
