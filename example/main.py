

from kivy.app import App
from kivy.uix.image import Image

from kivy.uix.button import Button
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle
from kivy.uix.behaviors import DragBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.progressbar import ProgressBar
from functools import partial


from glob import glob
from os.path import join, dirname
import csv
from math import sqrt


# Create an image class that supports drag behaviors
class DragImage(DragBehavior, Image):
	pass


# Buttons to switch between screens
class SwitchButton(Button):
	background_normal = 'navy.png'
	background_down = 'pressed.png'
	font_size = 16
	bold = True


# Text featured in instruction screen
class TextLabel(Label):
	font_size = 16
	text_size = (Window.width-10, None)
	color = (0, 0, 128, 1)
	halign = 'center'
	padding = (200, 200)


#Determine the drag distance and direction of drag
def calculate_dist(x1, y1, x2, y2):
	dx = x2 - x1
	dy = y2 - y1
	dist = sqrt((dx * dx) + (dy * dy))
	min_dist = sqrt((Window.height/5)**2 + (Window.width/5)**2)
	return min_dist, dist, dx, dy


# Drag image and score recording class
class Container(BoxLayout):
	label_text = StringProperty('')
	def __init__(self):
		# call the __init__ of the parent class once
		BoxLayout.__init__(self, orientation='vertical', size=Window.size)

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

		# Get total number of pictures to gauge progress
		self.prog_max = len([filename for filename in glob(join(curdir, 'images', '*'))])

		# The first image is updated with the first element in the list
		self.current = self.pictures.pop(0)

		# Create progress bar widget
		self.pb = ProgressBar(
			size_hint=(0.9, 0.1),
			max=self.prog_max)

		# Use anchor layout to keep progress bar centered
		self.grid_layout = GridLayout(cols=3, size_hint=(1,0.2))
		self.anchor = AnchorLayout(
			anchor_x='center',
			anchor_y='center',
			size_hint=(1, 0.1))
		# Create draggable image widget
		self.display = DragImage(
			source=self.current,
			drag_rect_height=Window.height,
			drag_rect_width=Window.width)
		# Set initial progress
		self.pb.value = self.prog_max - len(self.pictures) - 1
		# Create label to display previous score
		self.score_label = Label(text='Your Scoring:', color=(0,0,182,1), size_hint=(0.2,1))
		# Add picture and progress bar
		self.anchor.add_widget(self.pb)
		self.grid_layout.add_widget(self.anchor)
		self.grid_layout.add_widget(self.score_label)
		self.add_widget(self.grid_layout)
		self.add_widget(self.display)

	# Record initial down click coordinates
	def on_touch_down(self, touch):
		super(Container, self).on_touch_down(touch)
		self.coord = []
		self.coord.append(touch.x)
		self.coord.append(touch.y)

	# On click release calculate direction of drag and assign score
	def on_touch_up(self, touch):
		super(Container, self).on_touch_up(touch)
		self.coord.append(touch.x)
		self.coord.append(touch.y)
		min_dist, dist, dx, dy = calculate_dist(*self.coord)
		self.score_val = touch.y/Window.height

		# Check if drag movement is big enough
		if dist > min_dist and dx > Window.width/5:
			# Assign score based on drag direction
			self.change_image(score=self.score_val)
			self.score_label.text = 'Your Scoring: ' + str(int(self.score_val*100))
		# Recenter display picture if drag is too small
		else:
			self.display.center = self.center

	# Record drag value in csv file and move to next image
	def change_image(self,score=None):
		'''
		Change the displayed image and write the filename and score to score.csv
		'''

		with open('score.csv', mode='a', newline='') as score_data:
			writer = csv.writer(score_data)
			writer.writerow([self.current, score])
		# Update picture to new
		if len(self.pictures) == 0:
			self.remove_widget(self.grid_layout)
			self.remove_widget(self.display)
			self.end_label = Label(text='U Done It', color=(1,0,0,1))
			self.add_widget(self.end_label)
		else:
			self.current = self.pictures.pop(0)
			self.display.source = self.current
			self.display.center = Window.center
			# Update progress bar
			self.pb.value = self.prog_max - len(self.pictures) - 1
		return None

	# Change score label text when score changes
	def on_label_text(self, *args):
		self.score_label.text = str(self.label_text)


# Create Screen Manager
class ScreenManage(ScreenManager):
	def __init__(self):
		ScreenManager.__init__(self)
		self.menu = MenuScreen()
		self.anno = AnnotateScreen()
		self.inst1 = InstructionScreen1()
		self.inst2 = InstructionScreen2()
		self.tutorial = Tutorial()
		self.example = ExampleScreen()

		self.add_widget(self.menu)
		self.add_widget(self.anno)
		self.add_widget(self.inst1)
		self.add_widget(self.inst2)
		self.add_widget(self.tutorial)
		self.add_widget(self.example)


# Create Menu Screen
class MenuScreen(Screen):
	def __init__(self):
		Screen.__init__(self, name='menu')
		# Change Window Background color
		Window.clearcolor = (1, 1, 1, 1)
		# Create Box Layout for the screen
		self.box_layout = BoxLayout(orientation='vertical', padding=(0,0))
		# Create Grid Layout for the buttons and title/image
		self.grid_layout_title = GridLayout(cols=1, padding=(200, 20))
		self.grid_layout_buttons = GridLayout(cols=1, padding=(300, 20), size_hint=(1, 0.4))
		# Navigation buttons
		self.start_button = SwitchButton(text='Start Annotations')
		self.instruct_button = SwitchButton(text='Instructions')
		# Bind screen switching functions to buttons
		self.start_button.bind(on_press=self.anno_screen)
		self.instruct_button.bind(on_press=self.inst_screen)
		# Menu image
		self.pic = Image(source='cover.png', keep_ratio='False')
		# Game Title
		self.title = Label(
			text="Fetal ECG Annotation Game",
			color=(0,0,128,1),
			size_hint_y=0.4,
			font_size=30,
			bold=True)

		# Add widgets to grid layout
		self.grid_layout_buttons.add_widget(self.instruct_button)
		self.grid_layout_buttons.add_widget(self.start_button)
		self.grid_layout_title.add_widget(self.title)
		self.grid_layout_title.add_widget(self.pic)
		self.box_layout.add_widget(self.grid_layout_title)
		self.box_layout.add_widget(self.grid_layout_buttons)

		# Add box layout to screen
		self.add_widget(self.box_layout)

	# Change screen to annotation game
	def anno_screen(self, *args):
		self.manager.current = 'annotate'
		self.manager.transition.direction = 'left'

	# Change screen to instructions page
	def inst_screen(self, *args):
		self.manager.current = 'inst1'
		self.manager.transition.direction = 'left'


# Annotation game screen
class AnnotateScreen(Screen):
	def __init__(self):
		Screen.__init__(self, name='annotate')
		# Create box layout to house all widgets
		self.box_layout = BoxLayout(orientation='vertical')
		# Create container object which houses annotation game
		self.cont = Container()
		# Create grid layout to house the screen buttons
		self.grid_layout = GridLayout(cols=3, rows=2, size_hint=(1, 0.1))
		# Create buttons
		self.menu_button = SwitchButton(text='Menu', size_hint=(0.2, 0.1))
		self.example_button = SwitchButton(text='Examples', size_hint=(0.2, 0.1))
		# Bind switching functions to buttons
		self.menu_button.bind(on_press=self.menu_screen)
		self.example_button.bind(on_press=self.example_screen)
		# Create empty widget for spacing purposes
		self.empty = Label()
		# Add widgets to box layout
		self.grid_layout.add_widget(self.menu_button)
		self.grid_layout.add_widget(self.empty)
		self.grid_layout.add_widget(self.example_button)
		self.box_layout.add_widget(self.cont)
		self.box_layout.add_widget(self.grid_layout)
		# Add box widget to screen
		self.add_widget(self.box_layout)

	def menu_screen(self, *args):
		self.manager.current = 'menu'
		self.manager.transition.direction = 'right'

	def example_screen(self, *args):
		self.manager.current = 'example'
		self.manager.transition.direction = 'left'


# First Instruction Screen
class InstructionScreen1(Screen):
	def __init__(self):
		Screen.__init__(self, name='inst1')

		# Create box layout to house all widgets
		self.box_layout = BoxLayout(orientation='vertical')
		# Create grid layout to house buttons
		self.grid_layout = GridLayout(cols=3, rows=1, size_hint=(1, 0.2))
		# Create buttons and spacing widgets
		self.menu_button = SwitchButton(text='Menu', size_hint_x=0.2)
		self.empty = Label()
		self.next_button = SwitchButton(text='Next', size_hint_x=0.2)
		# Bind switching functions to buttons
		self.menu_button.bind(on_press=self.menu_screen)
		self.next_button.bind(on_press=self.next_page)
		# Create ECG photo widget
		self.image = Image(source='ECG.jpg')
		# Write text label for above photo
		self.label_1 = TextLabel(
			size_hint=(1,0.3),
			text='An electrocardiogram (ECG) is a non-invasive procedure that measures '
				 'the electrical activity of the heart using electodes placed on the skin. '
				 'ECGs are used to monitor a fetuss health throughout the pregnancy')
		# Write text label for below photo
		self.label_2 = TextLabel(
			size_hint=(1,0.2),
			text='Fetal ECG readings are often accompanied by a lot of noise which makes it'
				  'necessary to select only data that is clear and usable. \n The annotation of the'
				  'data signals is an extremely important step in ensuring only high quality'
				  'fetal ECG data is used in the assessment of fetal health.')
		# Add buttons to grid layout
		self.grid_layout.add_widget(self.menu_button)
		self.grid_layout.add_widget(self.empty)
		self.grid_layout.add_widget(self.next_button)
		# Add widgets to box layout
		self.box_layout.add_widget(self.label_1)
		self.box_layout.add_widget(self.image)
		self.box_layout.add_widget(self.label_2)
		self.box_layout.add_widget(self.grid_layout)
		# Add box layout to screen
		self.add_widget(self.box_layout)

	def menu_screen(self, *args):
		self.manager.current = 'menu'
		self.manager.transition.direction = 'right'

	def next_page(self, *args):
		self.manager.current = 'inst2'
		self.manager.transition.direction = 'left'


# Second Instruction Screen
class InstructionScreen2(Screen):
	def __init__(self):
		Screen.__init__(self, name='inst2')

		# Create box layout to house widgets
		self.box_layout = BoxLayout(orientation='vertical')
		# Create grid layout to house buttons
		self.grid_layout = GridLayout(cols=5, rows=1, size_hint=(1, 0.2))
		# Create buttons and empty spacing widgets
		self.back_button = SwitchButton(text='Back')
		self.empty1 = Label()
		self.menu_button = SwitchButton(text='Menu')
		self.empty2 = Label()
		self.next_button = SwitchButton(text='Next')
		# Bind switching functions
		self.back_button.bind(on_press=self.inst1_screen)
		self.menu_button.bind(on_press=self.menu_screen)
		self.next_button.bind(on_press=self.next_screen)
		# Create text labels
		self.label_1 = TextLabel(text='This app allows for the crowd sourcing of the annotation of the fetal ECG data.'
									  'Annotating this data is extremely important, but also very time consuming.'
									  'Through this app and the generosity of people like you, we will be able to collect '
									  'multiple opinions quickly and remotely.')
		self.label_2 = TextLabel(text='Taking a few minutes during a coffee break, morning commute, waiting room'
									  'or before bed to annotate these fetal ECG signals will significantly improve'
									  'doctors and researchers ability to continuously improve the quality of care'
									  'provided to both mothers and fetus\'s throughout the gestational period ')

		# Add widgets
		self.grid_layout.add_widget(self.back_button)
		self.grid_layout.add_widget(self.empty1)
		self.grid_layout.add_widget(self.menu_button)
		self.grid_layout.add_widget(self.empty2)
		self.grid_layout.add_widget(self.next_button)
		self.box_layout.add_widget(self.label_1)
		self.box_layout.add_widget(self.label_2)
		self.box_layout.add_widget(self.grid_layout)
		self.add_widget(self.box_layout)

	def inst1_screen(self, *args):
		self.manager.current = 'inst1'
		self.manager.transition.direction = 'right'

	def menu_screen(self, *args):
		self.manager.current = 'menu'
		self.manager.transition.direction = 'right'

	def next_screen(self, *args):
		self.manager.current = 'tutorial'
		self.manager.transition.direction = 'left'


# Tutorial Screen (run through of the game)
class Tutorial(Screen):
	def __init__(self):
		Screen.__init__(self, name='tutorial')
		# Create box layout to house widgets
		self.box_layout = BoxLayout(orientation='vertical')
		# Create grid layout to house buttons
		self.grid_layout = GridLayout(cols=3, rows=1, size_hint=(1, 0.1))
		# Create buttons
		self.back_button = SwitchButton(text='Back')
		self.menu_button = SwitchButton(text='Menu')
		self.next_button = SwitchButton(text='Next')
		# Bind switching functions
		self.back_button.bind(on_press=self.inst2_screen)
		self.menu_button.bind(on_press=self.menu_screen)
		self.next_button.bind(on_press=self.next_screen)
		# Add widgets
		self.grid_layout.add_widget(self.back_button)
		self.grid_layout.add_widget(self.menu_button)
		self.grid_layout.add_widget(self.next_button)
		self.box_layout.add_widget(self.grid_layout)
		self.add_widget(self.box_layout)

	def inst2_screen(self, *args):
		self.manager.current = 'inst2'
		self.manager.transition.direction = 'right'

	def menu_screen(self, *args):
		self.manager.current = 'menu'
		self.manager.transition.direction = 'right'

	def next_screen(self, *args):
		self.manager.current = 'tutorial'
		self.manager.transition.direction = 'right'


# Example screen accessed during anno game from anno screen
class ExampleScreen(Screen):
	def __init__(self):
		Screen.__init__(self, name='example')
		# Create box layout to house widgets
		self.box_layout = BoxLayout(orientation='vertical')
		# Create grid layout to house images
		self.grid_layout_img = GridLayout(cols=2)
		# Create grid layout to house buttons
		self.grid_layout_btn = GridLayout(cols=2, size_hint_y=0.1)
		# Create buttons and empty spacing widget
		self.back_button = SwitchButton(text='Back', size_hint_x=0.15)
		self.empty = Label()
		# Bind screen switching function to button
		self.back_button.bind(on_press=self.anno_screen)
		# Create example images and labels
		self.good_im = Image(source='good.png')
		self.unclear_im = Image(source='unclear.png')
		self.bad_im = Image(source='bad.png')
		self.good_lab = TextLabel(text='GOOD:', size_hint_x=0.5)
		self.unclear_lab = TextLabel(text="UNCLEAR:", size_hint_x=0.5)
		self.bad_lab = TextLabel(text='BAD:', size_hint_x=0.5)
		# Add images and labels to grid layout
		self.grid_layout_img.add_widget(self.good_lab)
		self.grid_layout_img.add_widget(self.good_im)
		self.grid_layout_img.add_widget(self.unclear_lab)
		self.grid_layout_img.add_widget(self.unclear_im)
		self.grid_layout_img.add_widget(self.bad_lab)
		self.grid_layout_img.add_widget(self.bad_im)
		# Add button to grid layout
		self.grid_layout_btn.add_widget(self.back_button)
		self.grid_layout_btn.add_widget(self.empty)
		# Add grid layouts to box layout
		self.box_layout.add_widget(self.grid_layout_img)
		self.box_layout.add_widget(self.grid_layout_btn)
		# Add box layout to screen
		self.add_widget(self.box_layout)

	def anno_screen(self, *args):
		self.manager.current = 'annotate'
		self.manager.transition.direction = 'right'


# Create app class
class ScorePicturesApp(App):
	def build(self):
		self.title = 'anno5i9 v0.1'
		return ScreenManage()

	# Pause app when switching between apps on mobile
	def on_pause(self):
		return True

	# Resume app when returning to app
	def on_resume(self):
		return True

# Run app
if __name__ == '__main__':
	ScorePicturesApp().run()