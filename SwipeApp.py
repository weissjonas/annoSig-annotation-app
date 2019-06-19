import kivy
from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
from kivy.uix.button import Button

from glob import glob
from os.path import join,dirname

image_list = []

class CustImage(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(CustImage, self).__init__(**kwargs)

class LayoutWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(LayoutWidget, self).__init__(**kwargs)

        for filename in glob("*.png"):
            im = str(filename)
            image_list.append(im)

    def replace_image(self, widget):

        self.ids.boxlayout.remove_widget(widget)
        self.ids.boxlayout.add_widget(CustImage(source='test2.png'))









class SwipeApp(App):
    def build(self):
        return LayoutWidget()

if __name__=="__main__":
    SwipeApp().run()