from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from functools import partial

from os import listdir
from glob import glob
from os.path import join, dirname
import csv

'''
# Very basic example of the "change Picture with a persistent score" App

I'm not very deep into the kv language, thats why I choose raw python.
I hope you get the point, and this is helpfull.

The Key feature you missed is bind().
You have to give the scope of the variables a second thougth if you 
pass something with bind(). I recomend to read something about the scope
of variables.

Maybe it is helpfull for you to know, that i spend some ours on reading
deeper in Kivy myself, before I was able to programm this - the lib is higly complex
and it is not an easy task for you. 
I'm totaly aware of this, but I'm convinced that you will benefit from it.  
'''

class Container(BoxLayout):
	def __init__(self):
		# call the __init__ of the parent class once
		BoxLayout.__init__(self, orientation='horizontal')

		# search for files in \images and append them to a list
		# From this list there are pulled
		self.pictures = []
		curdir = dirname(__file__)

		for filename in glob(join(curdir, 'images', '*')):
			self.pictures.append(filename)

		# The first image is updated with the first element in the list
		self.current = self.pictures.pop(0)
		self.display = Image(source=self.current)

		# Add some nice buttons, with partial
		# functools are a great lib in python, if you do not know it
		# I would highly recommend to read the docs
		# https://python.readthedocs.io/en/latest/library/functools.html
		self.left_label = Label(text='bad', size_hint=(0.05,1))
		self.right_label = Label(text='good', size_hint=(0.05,1))

		#self.add_widget(self.A)
		self.add_widget(self.left_label)
		self.add_widget(self.display)
		self.add_widget(self.right_label)

		# Run keyboard function on key press
		Window.bind(on_key_down=self.on_keyboard_down)


	# Pass the value of the key pressed to the change_image function
	def on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
		if keycode == 80:
			self.change_image(score='Bad')

		elif keycode == 79:
			self.change_image(score='Good')


	# Record keystroke value in csv file and move to next image
	def change_image(self,score=None):
		'''
		Change the displayed image and write the filename and score to score.csv
		'''
		with open('score.csv', mode='a') as score_data:
			writer = csv.writer(score_data)
			writer.writerow([self.current, score])

		self.current = self.pictures.pop(0)
		self.display.source = self.current
		return None


class ScorePicturesApp(App):
	def build(self):
		self.title = 'Awesome app!!!'
		return Container()


if __name__ == "__main__":
	ScorePicturesApp().run()