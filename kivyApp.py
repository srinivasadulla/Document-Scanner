from kivymd.app import MDApp
from kivy.uix.image import Image, AsyncImage
from kivy.core.window import Window
from kivy.uix.widget import Widget

# Window.size = (360, 640)


class scannerApp(MDApp):
    def build(self):
        # img = Image(source="document.jpg")
        return docScanner()
        
        


scannerApp().run()