import kivy
from kivy.app import App

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ListProperty, BooleanProperty, DictProperty
from kivy.uix.button import Button

from glob import glob


image_list = []
count = 0

class CustImage(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super(CustImage, self).__init__(**kwargs)

class LayoutWidget(BoxLayout):
    dynamic_ids = DictProperty({})

    def __init__(self, **kwargs):
        super(LayoutWidget, self).__init__(**kwargs)

        for filename in glob("*.png"):
            im = str(filename)
            image_list.append(im)

    def replace_image(self, widget):
        global count
        if count < len(image_list):
            print(self.ids)

            self.ids.boxlayout.remove_widget(widget)
            id = 'image'+str(count)
            im = CustImage(source = str(image_list[count]), id = id)

            self.ids.boxlayout.add_widget(im)

            print(self.dynamic_ids)

            count += 1

            return im

    def callback(self, value):
        pass


class SwipeApp(App):
    def build(self):
        return LayoutWidget()

if __name__=="__main__":
    SwipeApp().run()