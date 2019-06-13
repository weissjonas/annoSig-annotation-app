from kivy.app import App

from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.carousel import Carousel
from kivy.uix.button import Button


class LayoutWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(LayoutWidget, self).__init__(**kwargs)


class SwipeApp(App):
    def build(self):
        return LayoutWidget()




if __name__=="__main__":
    SwipeApp().run()