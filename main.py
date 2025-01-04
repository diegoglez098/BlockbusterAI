import sys
import unicodedata
import requests
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QCompleter, QListWidget, QListWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QStringListModel, Qt, QObject, pyqtSignal

# Tu clave de API de TMDb
API_KEY = '20c4b27df6202262cc6bd7418d428594'

class Worker(QObject):
    finished = pyqtSignal(str, str)  # Signal to indicate the completion of the request

    def buscar_actor(self, actor):
        url_busqueda = f'https://api.themoviedb.org/3/search/person?api_key={API_KEY}&query={actor}'
        respuesta = requests.get(url_busqueda)
        
        if respuesta.status_code == 200:
            data = respuesta.json()
            if data['results']:
                actor_data = data['results'][0]
                imagen_path = actor_data['profile_path']
                if imagen_path:
                    imagen_url = f'https://image.tmdb.org/t/p/w500{imagen_path}'
                    self.finished.emit(actor, imagen_url)
                    return
        self.finished.emit(actor, None)

def normalizar_texto(texto):
    texto = texto.lower()  # Convertir a minúsculas
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def obtener_recomendacion():
    genero = genero_input.text()
    actor = actor_input.text()
    actriz = actriz_input.text()
    
    resultado_label.setText(f"Recomendación para {genero}, {actor}, {actriz}")

def buscar_actor(actor):
    worker = Worker()
    #worker.finished.connect(mostrar_imagen)  # Conectar la señal a la función de mostrar imagen
    thread = threading.Thread(target=worker.buscar_actor, args=(actor,))
    thread.start()

def mostrar_imagen(actor, url_imagen):
    if url_imagen:
        response = requests.get(url_imagen)
        if response.status_code == 200:
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            # Crear un item de lista con la imagen y el nombre del actor
            item = QListWidgetItem(actor)
            item.setIcon(QPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio)))  # Redimensionar imagen
            imagen_list.addItem(item)
        else:
            imagen_list.clear()  # Limpia la lista si no se encuentra
    else:
        imagen_list.clear()  # Limpia la lista si no se encuentra la URL

app = QApplication(sys.argv)
ventana = QWidget()
ventana.setWindowTitle("Recomendador para Directores")
ventana.setGeometry(100, 100, 400, 400)

layout = QVBoxLayout()

layout.addWidget(QLabel("Escribe el género:"))
genero_input = QLineEdit()
generos = [
    "Acción", "Comedia", "Drama", "Ciencia Ficción", "Terror", 
    "Fantasía", "Aventura", "Misterio", "Romance", "Animación", 
    "Crimen", "Documental", "Musical", "Histórico", "Guerra"
]
genero_completer = QCompleter(generos)
genero_input.setCompleter(genero_completer)
layout.addWidget(genero_input)

layout.addWidget(QLabel("Escribe el actor:"))
actor_input = QLineEdit()
actores = [
    "Leonardo DiCaprio", "Brad Pitt", "Robert Downey Jr.", 
    "Tom Hanks", "Denzel Washington", "Chris Hemsworth", 
    "Will Smith", "Morgan Freeman", "Harrison Ford", "Johnny Depp", 
    "Ryan Reynolds", "Christian Bale", "Joaquin Phoenix", 
    "Keanu Reeves", "Tom Cruise"
]
actor_completer = QCompleter(actores)
actor_input.setCompleter(actor_completer)
layout.addWidget(actor_input)

layout.addWidget(QLabel("Escribe la actriz:"))
actriz_input = QLineEdit()
actrices = [
    "Meryl Streep", "Scarlett Johansson", "Jennifer Lawrence", 
    "Emma Stone", "Natalie Portman", "Angelina Jolie", 
    "Sandra Bullock", "Anne Hathaway", "Charlize Theron", 
    "Cate Blanchett", "Nicole Kidman", "Viola Davis", 
    "Margot Robbie", "Emily Blunt", "Gal Gadot"
]
actriz_completer = QCompleter(actrices)
actriz_input.setCompleter(actriz_completer)
layout.addWidget(actriz_input)

# Lista para mostrar imágenes y nombres de actores
imagen_list = QListWidget()
layout.addWidget(imagen_list)

genero_input.textChanged.connect(lambda: buscar_actor(genero_input.text()))
actor_input.textChanged.connect(lambda: buscar_actor(actor_input.text()))
actriz_input.textChanged.connect(lambda: buscar_actor(actriz_input.text()))

boton = QPushButton("Obtener Recomendación")
boton.clicked.connect(obtener_recomendacion)
layout.addWidget(boton)

resultado_label = QLabel("")
layout.addWidget(resultado_label)

ventana.setLayout(layout)

ventana.show()
sys.exit(app.exec_())
