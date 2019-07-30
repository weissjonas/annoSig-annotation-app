from kivy.app import App
from kivy.uix.image import Image

from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.properties import StringProperty, BooleanProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Rectangle, Color

from glob import glob
from os.path import join, dirname
import c
from math import sqrt


# Create an image class that supports drag behaviors
class DragImage(DragBehavior, Image):
    pass


# Create drop down menu class
class DropDownMenu(DropDown):
    def __init__(self):
        DropDown.__init__(self, auto_dismiss=False)
        self.menu_button = SwitchButton(text='menu', size_hint_y=None)
        self.example_button = SwitchButton(text='Instructions', size_hint_y=None)

        self.add_widget(self.menu_button)
        self.add_widget(self.example_button)


# Buttons to switch between screens
class SwitchButton(Button):
    background_normal = 'C:\\Users\\kvl_user\\PycharmProjects\\anno5i9\\example\\data\\navy.png'
    background_down = 'C:\\Users\\kvl_user\\PycharmProjects\\anno5i9\\example\\data\\pressed.jpg'
    font_size = Window.height / 35
    font_name = 'C:\\Users\\kvl_user\\PycharmProjects\\anno5i9\\example\\data\\Helvetica'
    bold = True


# Text featured in instruction screen
class TextLabel(Label):
    font_size = Window.height / 35
    text_size = (Window.width * 0.75, None)
    color = (0, 0, 128, 1)
    halign = 'center'
    font_name = 'C:\\Users\\kvl_user\\PycharmProjects\\anno5i9\\example\\data\\Helvetica'
    bold = True
    padding = (200, 200)


# Determine the drag distance and direction of drag
def calculate_dist(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    dist = sqrt((dx * dx) + (dy * dy))
    min_dist = sqrt((Window.height / 5) ** 2 + (Window.width / 5) ** 2)
    return min_dist, dist, dx, dy


# Drag image and score recording class
class Container(BoxLayout):
    label_text = StringProperty('')

    def __init__(self):
        # call the __init__ of the parent class once
        BoxLayout.__init__(self, orientation='vertical')
        self.counter = 0
        self.total_counter = 1

        # search for files in \images and append them to a list
        # From this list there are pulled
        self.pictures = []
        self.previous_pictures = []
        curdir = dirname(__file__)

        for filename in glob(join(curdir, 'images', '*')):
            self.pictures.append(filename)

        with open('user_score.csv', mode='r') as score_data:
            reader = csv.reader(score_data)
            for row in reader:
                if row[0] in self.pictures:
                    self.pictures.remove(row[0])

        if len(self.pictures) != 0:
            # Get total number of pictures to gauge progress
            self.prog_max = len([filename for filename in glob(join(curdir, 'images', '*'))])

            # The first image is updated with the first element in the list
            self.current = self.pictures.pop(0)

            # Create progress bar widget
            self.pb = ProgressBar(
                max=self.prog_max)

            self.box_layout = BoxLayout(orientation='vertical')
            self.grid_layout_menu = GridLayout(rows=1, spacing=50, padding=50)
            self.grid_layout_scores = GridLayout(
                cols=2,
                size_hint=(None, 0.2),
                spacing=Window.width / 20)
            self.grid_layout_bottom = GridLayout(cols=3, size_hint=(1, 0.2),
                                                 padding=10, spacing=Window.width / 25)

            self.display = Image(
                source=self.current)

            # Set initial progress
            self.pb.value = self.prog_max - len(self.pictures) - 1
            # Create label to display previous score
            # self.score_label = TextLabel(text='Your Scoring:')

            self.machine_score_label = TextLabel(text='Your Ranking:')
            self.test_label = Label(text='Score: ', color=(0, 0, 0, 1), size_hint_x=0.1, font_size=Window.height / 35)
            self.score_label = Label(size_hint_x=0.1, font_size=Window.height / 35)
            self.grid_layout_bottom.add_widget(self.pb)
            self.grid_layout_scores.add_widget(self.test_label)
            self.grid_layout_scores.add_widget(self.score_label)
            self.grid_layout_bottom.add_widget(self.grid_layout_scores)
            self.grid_layout_bottom.add_widget(self.machine_score_label)
            self.box_layout.add_widget(self.display)
            self.add_widget(self.box_layout)
            self.add_widget(self.grid_layout_bottom)


        # Display message if they have finished
        else:
            self.finish_label = TextLabel(text='You have annotated all the data currently available, great work!')
            self.add_widget(self.finish_label)

    # Record initial down click coordinates
    def on_touch_down(self, touch):
        super(Container, self).on_touch_down(touch)
        self.coord = []
        self.coord.append(touch.x)
        self.coord.append(touch.y)

    def on_touch_move(self, touch):
        super(Container, self).on_touch_move(touch)
        self.update_label(self.score_label, touch)

    # On click release calculate direction of drag and assign score
    def on_touch_up(self, touch):
        '''

        '''
        super(Container, self).on_touch_up(touch)

        self.coord.append(touch.x)
        self.coord.append(touch.y)

        min_dist, dist, dx, dy = calculate_dist(*self.coord)
        self.score_val = touch.y / Window.height

        # Check if drag movement is big enough
        if dist > min_dist and dx > Window.width / 5:
            # Assign score based on drag direction
            self.change_image(score=self.score_val)

            # Assign ranking based on comparison to machine learning score
            self.ranking = 0
            # abs(self.score_val -float(self.machine_score))
            if self.ranking < 0.1:
                self.ranking_label = 'Excellent!'
            elif self.ranking < 0.2:
                self.ranking_label = 'Very Good!'
            elif self.ranking < 0.3:
                self.ranking_label = 'Good!'
            elif self.ranking < 0.4:
                self.ranking_label = 'OK!'
            elif self.ranking < 0.5:
                self.ranking_label = 'Not Quite!'

            self.machine_score_label.text = 'Your Ranking: ' + self.ranking_label

        # Recenter display picture if drag is too small
        else:
            self.display.center = self.center

    # Record drag value in csv file and move to next image
    def change_image(self, score=None):
        '''
		Change the displayed image and write the filename and score to score.csv
		'''

        with open('user_score.csv', mode='a', newline='') as score_data:
            writer = csv.writer(score_data)
            writer.writerow([self.current, score])

        # Find score assigned by machine learner
        with open('machine_score.csv', mode='r') as machine:
            reader = csv.reader(machine)
            for row in reader:
                if row[0] == self.current:
                    self.machine_score = row[1]

        self.previous_images.append(self.current)

        # Update picture to new
        if len(self.pictures) == 0:
            self.clear_widgets()
            self.end_label = TextLabel(text='You have finished')

            self.add_widget(self.end_label)

        elif self.counter == 2:
            self.box_layout.remove_widget(self.display)
            self.cont_label = TextLabel(text='Do you want to continue? '
                                             '\n You\'ve annotated ' + str(self.total_counter)
                                             + ' signals this session!')
            self.cont_button = SwitchButton(
                text='Continue',
                size_hint=(0.2, 0.2))
            self.cont_button.bind(on_press=self.cont_anno)
            self.cont_grid_layout = GridLayout(rows=1, spacing=(Window.width / 30),
                                               size_hint_y=0.1,
                                               padding=(Window.width / 30, Window.height / 3))
            self.cont_grid_layout.add_widget(self.cont_label)
            self.cont_grid_layout.add_widget(self.cont_button)
            self.box_layout.add_widget(self.cont_grid_layout, index=1)


        else:
            self.current = self.pictures.pop(0)
            self.display.center = self.center
            self.display.source = self.current

            # Update progress bar
            self.pb.value = self.prog_max - len(self.pictures) - 1

            # Update counter
            self.counter = self.counter + 1
            self.total_counter = self.total_counter + 1

    def update_label(self, label, touch):
        score = int((touch.y / Window.height) * 100)

        label.text = str(score)

        if score > 75:
            label.color = (16, 96, 17, 1)
        elif score > 50:
            label.color = (157, 206, 34, 1)
        elif score > 35:
            label.color = (224, 166, 66, 1)
        elif score > 0:
            label.color = (1, 0, 0, 1)

    def cont_anno(self, *args):
        self.box_layout.remove_widget(self.cont_grid_layout)
        self.box_layout.add_widget(self.display)

        self.counter = 0
        self.change_image()


# Create Screen Manager
class ScreenManage(ScreenManager):
    def __init__(self):
        ScreenManager.__init__(self)
        self.menu = MenuScreen()
        self.anno = AnnotateScreen()
        self.inst1 = InstructionScreen1()
        self.inst2 = InstructionScreen2()
        self.inst3 = InstructionScreen3()
        self.inst4 = InstructionScreen4()
        self.tutorial = Tutorial()
        self.example = ExampleScreen()

        self.add_widget(self.menu)
        self.add_widget(self.anno)
        self.add_widget(self.inst1)
        self.add_widget(self.inst2)
        self.add_widget(self.inst3)
        self.add_widget(self.inst4)
        self.add_widget(self.tutorial)
        self.add_widget(self.example)


# Create Menu Screen
class MenuScreen(Screen):
    def __init__(self):
        Screen.__init__(self, name='menu')
        # Change Window Background color
        Window.clearcolor = (1, 1, 1, 1)
        # Create Box Layout for the screen
        self.box_layout = BoxLayout(orientation='vertical')
        # Create Grid Layout for the buttons and title/image
        self.grid_layout_title = GridLayout(cols=1, padding=(Window.width / 3, 20))
        self.grid_layout_buttons = GridLayout(cols=1, padding=(Window.width * 0.375, 30), size_hint=(1, 0.4),
                                              spacing=20)
        # Navigation buttons
        self.start_button = SwitchButton(text='Start')
        self.instruct_button = SwitchButton(text='Instructions')
        # Bind screen switching functions to buttons
        self.start_button.bind(on_release=self.anno_screen)
        self.instruct_button.bind(on_press=self.inst_screen)

        # Menu image
        self.pic = Image(source='C:\\Users\\kvl_user\\PycharmProjects\\anno5i9\\example\\data\\icon.png')
        # Game Title
        self.title = Label(
            text="Fetal ECG Annotation Game",
            color=(0, 0, 128, 1),
            size_hint_y=0.4,
            font_size=Window.height / 20,
            bold=True,
            font_name='C:\\Users\\kvl_user\\PycharmProjects\\anno5i9\\example\\data\\Helvetica')

        # Add widgets to grid layout
        self.grid_layout_buttons.add_widget(self.instruct_button)
        self.grid_layout_buttons.add_widget(self.start_button)
        self.grid_layout_title.add_widget(self.title)



        self.grid_layout_title.add_widget(self.pic)
        self.box_layout.add_widget(self.grid_layout_t


        self.box_layout.add_widget(self.grid_layout_b        # Add box layout to screen
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
        self.grid_layout = GridLayout(
            rows=1,
            size_hint_y=0.12,
            spacing=(Window.width / 30, Window.height / 50),
            padding=(Window.width / 30, Window.height / 50))
        self.menu_button = SwitchButton(text='Menu', size_hint=(None, 0.2))
        self.undo_button = SwitchButton(text='Undo', size_hint=(None, 0.2))
        self.skip_button = SwitchButton(text='Skip', size_hint=(None, 0.2))

        # Create drop down
        # self.drop_down = DropDownMenu()
        # self.drop_button = Button(
        # background_normal='menu_icon.png',
        # size_hint=(0.5,0.1))
        # Create Label
        self.label = Label(text='Annotations', color=(1, 1, 1, 1))
        # Bind switching functions to buttons
        # self.drop_button.bind(on_press=self.drop_down.open)
        # self.drop_down.menu_button.bind(on_press=self.menu_screen)
        # self.drop_down.example_button.bind(on_press=self.example_screen)
        self.menu_button.bind(on_press=self.menu_screen)
        self.skip_button.bind(on_press=self.skip)
        self.undo_button.bind(on_press=self.undo)

        # Add widgets to box layout
        self.grid_layout.add_widget(self.label)
        self.grid_layout.add_widget(self.menu_button)
        self.grid_layout.add_widget(self.undo_button)
        self.grid_layout.add_widget(self.skip_button)
        # self.grid_layout.add_widget(self.drop_button)

        self.box_layout.add_widget(self.grid_layout)
        self.box_layout.add_widget(self.cont)

        # Add box widget to screen
        self.add_widget(self.box_layout)

    def menu_screen(self, *args):
        self.manager.current = 'menu'
        self.manager.transition.direction = 'right'

    # self.drop_down.dismiss(self)

    def example_screen(self, *args):
        self.manager.current = 'example'
        self.manager.transition.direction = 'left'

    # self.drop_down.dismiss(self)

    def skip(self, *args):
        self.cont.change_image()

    def undo(self, *args):
        if len(self.previous_pictures) == 0 :
            return
        self.cont.pictures.insert(0, self.previous_pictures.pop())
        self.cont.change_image()


# First Instruction Screen
class InstructionScreen1(Screen):
    def __init__(self):
        Screen.__init__(self, name='inst1')

        # Create box layout to house all widgets
        self.box_layout = BoxLayout(orientation='vertical', padding=(20, 0))
        # Create grid layout to house buttons
        self.grid_layout = GridLayout(
            cols=2,
            rows=1,
            size_hint=(1, 0.2),
            padding=(Window.width / 50, 10),
            spacing=(Window.width / 1.7, 10))

        # Create drop down
        # self.drop_down = DropDownMenu()
        # self.drop_button = Button(
        # background_normal='menu_icon.png',
        # size_hint=(0.5, 0.1))
        # Create Label
        self.label = Label(text='Annotations', color=(1, 1, 1, 1))
        # Bind switching functions to buttons
        # self.drop_button.bind(on_press=self.drop_down.open)
        # self.drop_down.menu_button.bind(on_press=self.menu_screen)
        # self.drop_down.example_button.bind(on_press=self.example_screen)

        # Create buttons and spacing widgets
        self.menu_button = SwitchButton(text='Menu', size_hint_x=0.2)

        self.next_button = SwitchButton(text='Next', size_hint_x=0.2)
        # Bind switching functions to buttons
        self.menu_button.bind(on_press=self.menu_screen)
        self.next_button.bind(on_press=self.next_page)
        # Create ECG photo widget
        self.image = Image(source='C:\\Users\\kvl_user\\PycharmProjects\\anno5i9\\example\\data\\ECG.jpg')
        # Write text label for above photo
        self.label_1 = TextLabel(
            size_hint=(1, 0.3),
            text='An electrocardiogram (ECG) is a non-invasive procedure that measures '
                 'the electrical activity of the heart. ECGs are used to monitor a fetus\' health '
                 'in utero. Fetal ECG readings often contain a lot of noise and we must go '
                 'through and annotate these readings to record if it is usable or not.')
        # Write text label for below photo
        self.label_2 = TextLabel(
            size_hint=(1, 0.2),
            text='Annotating this data is extremely important, but also very time consuming. '
                 'Taking a few minutes to annotate using this app during a coffee break, commute, '
                 'waiting room, or before bed will greatly help ensure that only high quality ECG '
                 'data is used by doctors and researchers.')
        # Add buttons to grid layout
        self.grid_layout.add_widget(self.menu_button)
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
        self.manager.transition.direction = 'left'

    # self.drop_down.dismiss(self)

    def example_screen(self, *args):
        self.manager.current = 'example'
        self.manager.transition.direction = 'right'

    # self.drop_down.dismiss(self)

    def next_page(self, *args):
        self.manager.current = 'inst2'
        self.manager.transition.direction = 'left'


# Second Instruction Screen
class InstructionScreen2(Screen):
    def __init__(self):
        Screen.__init__(self, name='inst2')

        self.box_layout = BoxLayout(orientation='vertical', padding=(20, 0))
        # Create grid layout to house buttons
        self.grid_layout = GridLayout(
            cols=3,
            rows=1,
            size_hint=(1, 0.15),
            padding=(Window.width / 50, 10),
            spacing=(Window.width / 5, 10))
        # Create buttons and empty spacing widgets
        self.back_button = SwitchButton(text='Back', size_hint_x=0.85)
        self.menu_button = SwitchButton(text='Menu', size_hint_x=0.85)
        self.next_button = SwitchButton(text='Next', size_hint_x=0.85)
        # Bind switching functions
        self.back_button.bind(on_press=self.inst1_screen)
        self.menu_button.bind(on_press=self.menu_screen)
        self.next_button.bind(on_press=self.next_screen)
        # Create text labels
        self.label_1 = TextLabel(
            text='A high quality fetal ECG reading has clear fetal heartbeats visible between the mother\'s '
                 'heartbeats. \n There are typically two fetal heartbeats in between each maternal heartbeat. ',
            size_hint=(1, 0.1))
        self.image = Image(source='C:\\Users\\kvl_user\\PycharmProjects\\anno5i9\\example\\data\\inst1.png')

        # Add widgets
        self.grid_layout.add_widget(self.back_button)
        self.grid_layout.add_widget(self.menu_button)
        self.grid_layout.add_widget(self.next_button)
        self.box_layout.add_widget(self.label_1)
        self.box_layout.add_widget(self.image)
        self.box_layout.add_widget(self.grid_layout)
        self.add_widget(self.box_layout)

    def inst1_screen(self, *args):
        self.manager.current = 'inst1'
        self.manager.transition.direction = 'right'

    def menu_screen(self, *args):
        self.manager.current = 'menu'
        self.manager.transition.direction = 'right'

    def next_screen(self, *args):
        self.manager.current = 'inst3'
        self.manager.transition.direction = 'left'


# Third Instruction Screen
class InstructionScreen3(Screen):
    def __init__(self):
        Screen.__init__(self, name='inst3')

        self.box_layout = BoxLayout(orientation='vertical', padding=(20, 0))
        # Create grid layout to house buttons
        self.grid_layout = GridLayout(
            cols=3,
            rows=1,
            size_hint=(1, 0.17),
            padding=(Window.width / 50, 10),
            spacing=(Window.width / 5, 10))

        # Create buttons and empty spacing widgets
        self.back_button = SwitchButton(text='Back')
        self.menu_button = SwitchButton(text='Menu')
        self.next_button = SwitchButton(text='Next')
        # Bind switching functions
        self.back_button.bind(on_press=self.inst2_screen)
        self.menu_button.bind(on_press=self.menu_screen)
        self.next_button.bind(on_press=self.next_screen)
        # Create text labels
        self.label = TextLabel(
            text='The signals will be assigned a score between 0 and 100. '
                 'A score of 100 would be a high quality clear signal and a score of 0 would be a very poor '
                 'and noisy signal. A score is assigned by dragging the image to the right side of the screen.',
            size_hint=(1, 0.2))
        self.image = Image(source='C:\\Users\\kvl_user\\PycharmProjects\\anno5i9\\example\\data\\inst2.jpg')

        # Add widgets
        self.grid_layout.add_widget(self.back_button)
        self.grid_layout.add_widget(self.menu_button)
        self.grid_layout.add_widget(self.next_button)
        self.box_layout.add_widget(self.label)
        self.box_layout.add_widget(self.image)
        self.box_layout.add_widget(self.grid_layout)
        self.add_widget(self.box_layout)

    def inst2_screen(self, *args):
        self.manager.current = 'inst2'
        self.manager.transition.direction = 'right'

    def menu_screen(self, *args):
        self.manager.current = 'menu'
        self.manager.transition.direction = 'right'

    def next_screen(self, *args):
        self.manager.current = 'inst4'
        self.manager.transition.direction = 'left'


# Fourth Instruction Screen
class InstructionScreen4(Screen):
    def __init__(self):
        Screen.__init__(self, name='inst4')

        # Create box layout to house widgets
        self.box_layout = BoxLayout(orientation='vertical')
        # Create grid layout to house buttons
        self.grid_layout = GridLayout(cols=5, rows=1, size_hint=(1, 0.15))
        # Create buttons and empty spacing widgets
        self.back_button = SwitchButton(text='Back')
        self.empty1 = Label()
        self.menu_button = SwitchButton(text='Menu')
        self.empty2 = Label()
        self.next_button = SwitchButton(text='Next')
        # Bind switching functions
        self.back_button.bind(on_press=self.inst3_screen)
        self.menu_button.bind(on_press=self.menu_screen)
        self.next_button.bind(on_press=self.next_screen)

        self.label = TextLabel(text='Annotation Screen Layout', size_hint=(1, 0.1))
        self.image = Image(source='C:\\Users\\kvl_user\\PycharmProjects\\anno5i9\\example\\data\\anno_screen.png')

        # Add widgets
        self.grid_layout.add_widget(self.back_button)
        self.grid_layout.add_widget(self.empty1)
        self.grid_layout.add_widget(self.menu_button)
        self.grid_layout.add_widget(self.empty2)
        self.grid_layout.add_widget(self.next_button)
        self.box_layout.add_widget(self.label)
        self.box_layout.add_widget(self.image)
        self.box_layout.add_widget(self.grid_layout)
        self.add_widget(self.box_layout)

    def inst3_screen(self, *args):
        self.manager.current = 'inst3'
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
        self.grid_layout_img = GridLayout(cols=2, spacing=10)
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
