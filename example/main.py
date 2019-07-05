

from kivy.app import App
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.behaviors import DragBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from functools import partial

from glob import glob
from os.path import join, dirname
import csv
from math import sqrt

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

#Create an image class that supports drag behaviors
class DragImage(DragBehavior, Image):
	pass


#Determine the drag distance and direction of drag
def calculate_dist(x1, y1, x2, y2):

	dx = x2 - x1
	dy = y2 - y1
	dist = sqrt((dx * dx) + (dy * dy))
	min_dist = sqrt((Window.height/5)**2 + (Window.width/5)**2)
	return min_dist, dist, dx, dy


#App layout
class Container(BoxLayout):
	def __init__(self):
		# call the __init__ of the parent class once
		BoxLayout.__init__(self, orientation='vertical')

		# search for files in \images and append them to a list
		# From this list there are pulled
		self.pictures = []
		curdir = dirname(__file__)

		for filename in glob(join(curdir, 'images', '*')):
			self.pictures.append(filename)

		with open('score.csv', mode='r') as score_data:
			reader = csv.reader(score_data)
			for row in reader:
				if row[0] in self.pictures:
					self.pictures.remove(row[0])

		# The first image is updated with the first element in the list
		self.current = self.pictures.pop(0)
		self.display = DragImage(source=self.current,
								 drag_rect_width=Window.width,
								 drag_rect_height=Window.height)

		# Add some nice buttons, with partial
		# functools are a great lib in python, if you do not know it
		# I would highly recommend to read the docs
		# https://python.readthedocs.io/en/latest/library/functools.html
		self.horiz_box = BoxLayout(orientation='horizontal')
		self.left_label = Label(text='bad', size_hint=(0.1,1))
		self.right_label = Label(text='good', size_hint=(0.1,1))
		self.upper_label = Label(text='unclear', size_hint=(1,0.2), valign='top')

		#self.add_widget(self.A)
		self.horiz_box.add_widget(self.left_label)
		self.horiz_box.add_widget(self.display)
		self.horiz_box.add_widget(self.right_label)
		self.add_widget(self.upper_label)
		self.add_widget(self.horiz_box)

	#Record initial down click coordinates
	def on_touch_down(self, touch):
		super(Container, self).on_touch_down(touch)
		self.coord = []
		self.coord.append(touch.x)
		self.coord.append(touch.y)

	#On click release calculate direction of drag and assign score
	def on_touch_up(self, touch):
		'''
		Call the calculate_dist function to determine the direction of the swipe
		and the magnitude of the swipe. Checks the distance of the magnitude
		of the drag motion to ensure it is big enough to register the score.
		Writes the score (Good, Bad, Unclear) based on the direction of the swipe.
		'''
		super(Container, self).on_touch_up(touch)
		self.coord.append(touch.x)
		self.coord.append(touch.y)
		min_dist, dist, dx, dy = calculate_dist(*self.coord)

		#Check if drag movement is big enough
		if dist > min_dist:
			#Assign score based on drag direction
			if dx < 0 and dy < 50:
				self.change_image(score='Bad')

			elif (dx > -50 and dx < 50) and dy > 0:
				self.change_image(score='Unclear')

			elif dx > 0 and dy < 50:
				self.change_image(score='Good')
		#Recenter display picture if drag magnitude is too small
		else:
			self.display.center = Window.center


	# Record keystroke value in csv file and move to next image
	def change_image(self,score=None):
		'''
		Change the displayed image and write the filename and score to score.csv
		'''
		with open('score.csv', mode='a', newline='') as score_data:
			writer = csv.writer(score_data)
			writer.writerow([self.current, score])

		self.current = self.pictures.pop(0)
		self.display.source = self.current
		self.display.center = Window.center
		return None


class ScorePicturesApp(App):
	def build(self):
		self.title = 'anno5i9 v0.1'
		return Container()


if __name__ == "__main__":

	ScorePicturesApp().run()