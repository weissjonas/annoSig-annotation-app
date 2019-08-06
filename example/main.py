from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.properties import StringProperty
from kivy.uix.behaviors import DragBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import WidgetException

from glob import glob
from os.path import join, dirname
import csv
from math import sqrt
import ntpath


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
    background_normal = 'navy.png'
    background_down = 'pressed.jpg'
    font_size = Window.height / 35
    bold = True


# Text featured in instruction screen
class TextLabel(Label):
    font_size = Window.height / 35
    text_size = (Window.width * 0.75, None)
    color = (0, 0, 128, 1)
    halign = 'center'
    bold = True
    padding = (200, 200)


def calculate_dist(x1, y1, x2, y2):
    """Determine the direction and magnitude of the dragging of the image"""
    dx = x2 - x1
    dy = y2 - y1
    dist = sqrt((dx * dx) + (dy * dy))
    min_dist = sqrt((Window.height / 5) ** 2 + (Window.width / 5) ** 2)
    return min_dist, dist, dx, dy


# Drag image and score recording class
class Container(BoxLayout):
    label_text = StringProperty('')
    # Change Window Background color
    Window.clearcolor = (1, 1, 1, 1)

    def __init__(self):
        # call the __init__ of the parent class once
        BoxLayout.__init__(self, orientation='vertical')
        # Initialize counter to track how many pictures are done in each grouping
        self.counter = 1
        # Initialize counter to track how many pictures are done in the entire annotation session
        self.total_counter = 1
        # Create list to house pictures
        self.pictures = []
        self.machine_score = float()

        # Store file directory in a variable
        curdir = dirname(__file__)
        # Add all pictures in the 'Images' folder to the pictures list
        for filename in glob(join(curdir, 'images', '*')):
            self.pictures.append(filename)

        # Remove any pictures that have already been annotated
        with open('user_score.csv', mode='r') as score_data:
            reader = csv.reader(score_data)
            for row in reader:
                for pic in self.pictures:
                    if row[0] == ntpath.basename(pic):
                        self.pictures.remove(pic)

        # Check if there are still pictures left to annotate
        if len(self.pictures) != 0:
            # Get total number of pictures to gauge progress
            self.prog_max = len([filename for filename in glob(join(curdir, 'images', '*'))])
            # The first image is updated with the first element in the list
            self.current = self.pictures.pop(0)
            self.prev_pictures = [self.current]
            # Create progress bar widget
            self.pb = ProgressBar(max=self.prog_max)
            # Create layouts and widgets
            self.float_layout = FloatLayout()
            self.grid_layout_scores = GridLayout(cols=2,size_hint=(None, 0.2), spacing=0)
            self.grid_layout_ranking = GridLayout(cols=2,size_hint=(None, 0.2), spacing=100)
            self.grid_layout_bottom = GridLayout(cols=4, size_hint=(1, 0.2),
                                                 padding=(20, 0), spacing=(Window.width/15, 0),
                                                 pos=(20, Window.height-100))
            self.display = DragImage(source=self.current, drag_rect_width=Window.width, drag_rect_height=Window.height)
            # Set initial progress of progress bar
            self.pb.value = self.prog_max - len(self.pictures) - 1
            # Create label to display the ranking comparing user score to machine score
            self.machine_score_label = TextLabel(text='')
            # Create label to display the score the user is assigning to
            self.score = Label(size_hint_x=0.1, font_size=Window.height / 35, bold=True)
            # Create labels for 'Score:' and 'Ranking:'
            self.score_label = Label(text='Score: ', color=(0, 0, 0, 1), size_hint_x=0.1, font_size=Window.height/35)
            self.machine_label = Label(text='Your Ranking: ', color=(0, 0, 0, 1), size_hint_x=0.1,
                                       font_size=Window.height/35)
            # Add widgets to grid layouts
            self.grid_layout_bottom.add_widget(self.pb)
            self.grid_layout_scores.add_widget(self.score_label)
            self.grid_layout_scores.add_widget(self.score)
            self.grid_layout_bottom.add_widget(self.grid_layout_scores)
            self.grid_layout_ranking.add_widget(self.machine_label)
            self.grid_layout_ranking.add_widget(self.machine_score_label)
            self.grid_layout_bottom.add_widget(self.grid_layout_ranking)
            # Add widgets to the float layout
            self.float_layout.add_widget(self.display)
            self.float_layout.add_widget(self.grid_layout_bottom)
            # Add float layout to the screen
            self.add_widget(self.float_layout)

        # Display message if they have finished
        else:
            self.finish_label = TextLabel(text='You have annotated all the data currently available, great work!')
            self.add_widget(self.finish_label)

    # Record initial down click coordinates
    def on_touch_down(self, touch):
        """Record the initial coordinates of the user touch"""
        super(Container, self).on_touch_down(touch)
        self.coord = []
        self.coord.append(touch.x)
        self.coord.append(touch.y)

        try:
            self.machine_score_label.text = ''
        # Prevent error when click on end screen
        except AttributeError:
            return

    def on_touch_move(self, touch):
        """ Update the user score of the signal in real time as their touch is moving"""
        super(Container, self).on_touch_move(touch)

        try:
            self.update_label(self.score, touch)
        # Avoid app crashing from user touch on end screen
        except AttributeError:
            return

    def on_touch_up(self, touch):
        """Calculate the user score based on the direction of their touch and ensure the movement was big enough"""
        super(Container, self).on_touch_up(touch)

        try:
            self.coord.append(touch.x)
            self.coord.append(touch.y)
            min_dist, dist, dx, dy = calculate_dist(*self.coord)
            self.score_val = touch.y / Window.height

            # Check if drag movement is big enough
            if dist > min_dist and dx > Window.width / 5:
                # Assign score based on drag direction
                self.change_image(score=self.score_val)
                self.prev_pictures.append(self.current)
                # Assign ranking based on comparison to machine learning score
                self.ranking = abs(self.score_val -float(self.machine_score))
                if self.ranking < 0.1:
                    self.machine_score_label.text = 'Excellent!'
                elif self.ranking < 0.2:
                    self.machine_score_label.text = 'Very Good!'
                elif self.ranking < 0.3:
                    self.machine_score_label.text = 'Good!'
                elif self.ranking < 0.4:
                    self.machine_score_label.text = 'OK!'
                elif self.ranking < 0.5:
                    self.machine_score_label.text = 'Not Quite!'

            # Recenter display picture if drag is too small
            else:
                self.display.center = self.center
                self.machine_score_label.text = 'Try Again'
        # Prevent crashing from user touches on end screen
        except (AttributeError, TypeError):
            return

    def change_image(self, score=None):
        """Change the displayed image and write the filename and score to score.csv"""

        try:
            # Write picture name and score to csv
            with open('user_score.csv', mode='a', newline='') as score_data:
                writer = csv.writer(score_data)
                writer.writerow([ntpath.basename(self.current), score])

            # Find score assigned by machine learner
            with open('machine_score.csv', mode='r') as machine:
                reader = csv.reader(machine)
                for row in reader:
                    if row[0] == ntpath.basename(self.current):
                        if row[1] != '':
                            self.machine_score = row[1]
                        else:
                            self.machine_score = ''
        # Avoid app crashing from user touch on end screen
        except AttributeError:
            return

        if len(self.pictures) == 0:
            self.clear_widgets()
            self.end_label = TextLabel(text='You have finished')
            self.add_widget(self.end_label)

        # Ask user if they want to continue annotating after a certain amount of pictures
        elif self.counter == 9:
            # Remove display widget
            self.float_layout.remove_widget(self.display)
            # Create label to display continue message
            self.cont_label = TextLabel(text='Do you want to continue? '
                                             '\n You\'ve annotated ' + str(self.total_counter)
                                             + ' signals this session!')
            # Create continue button
            self.cont_button = SwitchButton(text='Continue',size_hint=(0.2, 0.2))
            self.cont_button.bind(on_press=self.cont_anno)
            # Add buttons to grid
            self.cont_grid_layout = GridLayout(rows=1, spacing=(Window.width / 30),
                                               padding=(Window.width / 20, Window.height / 2.5))
            self.cont_grid_layout.add_widget(self.cont_label)
            self.cont_grid_layout.add_widget(self.cont_button)
            # Add grid to screen
            self.float_layout.add_widget(self.cont_grid_layout)

        else:
            # Move to next picture
            self.current = self.pictures.pop(0)
            self.display.center = self.center
            self.display.source = self.current
            # Reset score
            self.score.text = ''
            # Increase counters
            self.counter = self.counter + 1
            self.total_counter = self.total_counter + 1
            # Update progress bar
            self.pb.value = self.prog_max - len(self.pictures) - 1


    def update_label(self, label, touch):
        """Changes the users score and color of the score for the signal in real time"""
        score = int((touch.y / Window.height) * 100)
        label.text = str(score)
        if score > 75:
            label.color = (0,150,0,1)
        elif score > 50:
            label.color = (0, 50, 0, 1)
        elif score > 25:
            label.color = (5, 50, 0, 1)
        elif score > 0:
            label.color = (50, 0, 0, 1)

    def cont_anno(self, *args):
        """Fired by a button to continue the annotation game after certain amount of pictures have been annotated"""
        self.float_layout.remove_widget(self.cont_grid_layout)
        self.float_layout.add_widget(self.display, index=1)
        self.counter = 0
        self.change_image()


# Create Screen Manager to house different screens within the app
class ScreenManage(ScreenManager):
    def __init__(self):
        ScreenManager.__init__(self)
        self.menu = MenuScreen()
        self.anno = AnnotateScreen()
        self.inst1 = InstructionScreen()
        self.tutorial1 = TutorialScreen_1()
        self.tutorial2 = TutorialScreen_2()
        self.example = ExampleScreen()
        self.add_widget(self.menu)
        self.add_widget(self.anno)
        self.add_widget(self.inst1)
        self.add_widget(self.tutorial1)
        self.add_widget(self.tutorial2)
        self.add_widget(self.example)


# Create Menu Screen
class MenuScreen(Screen):
    def __init__(self):
        Screen.__init__(self, name='menu')

        # Create Box Layout for the screen
        self.box_layout = BoxLayout(orientation='vertical')
        # Create Grid Layout for the buttons and title/image
        self.grid_layout_title = GridLayout(cols=1, padding=Window.height/50)
        self.grid_layout_buttons = GridLayout(cols=1, padding=(Window.width * 0.375, 30), size_hint=(1, 0.5),
                                              spacing=10)
        # Navigation buttons
        self.start_button = SwitchButton(text='Start')
        self.instruct_button = SwitchButton(text='Instructions')
        self.tutorial_button = SwitchButton(text='Tutorial')
        # Bind screen switching functions to buttons
        self.start_button.bind(on_release=self.anno_screen)
        self.instruct_button.bind(on_press=self.inst_screen)
        self.tutorial_button.bind(on_press=self.tutorial_screen)
        # Menu image
        self.pic = Image(source='fecg_logo.png')

        # Add widgets to grid layout
        self.grid_layout_buttons.add_widget(self.instruct_button)
        self.grid_layout_buttons.add_widget(self.tutorial_button)
        self.grid_layout_buttons.add_widget(self.start_button)
        self.grid_layout_title.add_widget(self.pic)
        self.box_layout.add_widget(self.grid_layout_title)
        self.box_layout.add_widget(self.grid_layout_buttons)
        self.add_widget(self.box_layout)

    def anno_screen(self, *args):
        """Change screen to annotation game"""
        self.manager.current = 'annotate'
        self.manager.transition.direction = 'left'

    def inst_screen(self, *args):
        """Change screen to instruction screen"""
        self.manager.current = 'inst1'
        self.manager.transition.direction = 'left'

    def tutorial_screen(self, *args):
        """Change screen to tutorial screen"""
        self.manager.current = 'tutorial1'
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
        self.grid_layout = GridLayout(rows=1, size_hint_y=0.12, spacing=(Window.width / 30, Window.height / 50),
                                      padding=(Window.width / 30, Window.height / 50))
        self.menu_button = SwitchButton(text='Menu', size_hint=(None, 0.2))
        self.undo_button = SwitchButton(text='Undo', size_hint=(None, 0.2))
        self.skip_button = SwitchButton(text='Skip', size_hint=(None, 0.2))
        self.example_button = SwitchButton(text='Examples', size_hint=(None, 0.2))
        # Create Label
        self.label = Label(text='Annotations', color=(0, 0, 128, 1), font_size=Window.height/30)
        # Bind switching functions to buttons
        self.menu_button.bind(on_press=self.menu_screen)
        self.skip_button.bind(on_press=self.skip)
        self.undo_button.bind(on_press=self.undo)
        self.example_button.bind(on_press=self.example_screen)
        # Add widgets to grid layout
        self.grid_layout.add_widget(self.label)
        self.grid_layout.add_widget(self.menu_button)
        self.grid_layout.add_widget(self.undo_button)
        self.grid_layout.add_widget(self.skip_button)
        self.grid_layout.add_widget(self.example_button)
        # Add widgets to box layout
        self.box_layout.add_widget(self.cont)
        self.box_layout.add_widget(self.grid_layout)
        # Add box widget to screen
        self.add_widget(self.box_layout)

    def menu_screen(self, *args):
        """Change screen to menu screen"""
        self.manager.current = 'menu'
        self.manager.transition.direction = 'right'

    def example_screen(self, *args):
        """Change screen to example screen"""
        self.manager.current = 'example'
        self.manager.transition.direction = 'left'

    def skip(self, *args):
        """Skip to the next picture to annotate"""
        # Check if user is on the last picture
        if len(self.cont.pictures) > 0:
            # Record the current picture
            self.cont.prev_pictures.append(self.cont.current)
            # Skip to the next picture
            self.cont.change_image()
            # Increment the progress bar
            self.cont.pb.value = self.cont.pb.value + 1

    def undo(self, *args):
        """Go back to the previous picture to annotate"""
        try:
            # Check if user is on the last picture
            if len(self.cont.pictures) > 0:
                # Insert previous picture in the pictures list
                self.cont.pictures.insert(0, self.cont.prev_pictures.pop(-2))
                # Change to the previous picture
                self.cont.change_image()
                # Decrease the progress bar
                self.cont.pb.value = self.cont.pb.value - 1
                # Decrease counters
                self.cont.counter = self.cont.counter - 1
                self.cont.total_counter = self.cont.total_counter - 1
        except IndexError:
            return


class InstructionScreen(Screen):
    def __init__(self):
        Screen.__init__(self, name='inst1')

        # Create box layout to house all widgets
        self.box_layout = BoxLayout(orientation='vertical', padding=(20, 0))
        # Create grid layout to house buttons
        self.grid_layout = GridLayout(cols=3, rows=1, size_hint=(1, 0.2), padding=(Window.width / 50, 10),
                                      spacing=(Window.width / 5, 10))

        # Create buttons and spacing widgets
        self.menu_button = SwitchButton(text='Menu', size_hint_x=0.2)
        self.next_button = SwitchButton(text='Next', size_hint_x=0.2)
        self.back_button = SwitchButton(text='Back', size_hint_x=0.2)
        self.blank = Label(size_hint_x=0.2)

        # Bind switching functions to buttons
        self.menu_button.bind(on_press=self.menu_screen)
        self.next_button.bind(on_press=self.page_2)
        # Create photo widget
        self.image = Image(source='ECG.jpg')
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
        self.grid_layout.add_widget(self.blank)
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
        self.page_1()

    def unbind_all(self):
        """Unbind all functions from buttons"""
        self.next_button.unbind(on_press=self.page_1)
        self.next_button.unbind(on_press=self.page_2)
        self.next_button.unbind(on_press=self.page_3)
        self.back_button.unbind(on_press=self.page_1)
        self.back_button.unbind(on_press=self.page_2)
        self.back_button.unbind(on_press=self.page_3)

    def page_1(self, *args):
        """Create buttons and text for first instruction page"""

        self.label_1.text = 'An electrocardiogram (ECG) is a non-invasive procedure that measures '\
                            'the electrical activity of the heart. ECGs are used to monitor a fetus\' health '\
                            'in utero. Fetal ECG readings often contain a lot of noise and we must go '\
                            'through and annotate these readings to record if it is usable or not.'
        self.label_2.text = 'Annotating this data is extremely important, but also very time consuming. '\
                            'Taking a few minutes to annotate using this app during a coffee break, commute, '\
                            'waiting room, or before bed will greatly help ensure that only high quality ECG '\
                            'data is used by doctors and researchers.'
        self.image.source = 'ECG.jpg'
        # Remove all widgets from previous page
        self.grid_layout.clear_widgets()
        # Add buttons for this page
        self.grid_layout.add_widget(self.menu_button)
        self.grid_layout.add_widget(self.blank)
        self.grid_layout.add_widget(self.next_button)
        # Call function to unbind all button functions
        self.unbind_all()
        # Bind correct page to the next button
        self.next_button.bind(on_press=self.page_2)

    def page_2(self, *args):
        """Create buttons and text for second instruction page"""
        self.label_1.text = 'A high quality fetal ECG reading has clear fetal heartbeats visible between the mother\'s'\
                            ' heartbeats. There are typically two fetal heartbeats in between each maternal heartbeat. '
        self.image.source = 'inst1.png'
        self.label_2.text = ''
        # Remove all widgets from previous page
        self.grid_layout.clear_widgets()
        # Add buttons for this page
        self.grid_layout.add_widget(self.menu_button)
        self.grid_layout.add_widget(self.back_button)
        self.grid_layout.add_widget(self.next_button)

        self.unbind_all()
        # Bind correct page to back and next buttons
        self.back_button.bind(on_press=self.page_1)
        self.next_button.bind(on_press=self.page_3)

    def page_3(self, *args):
        """Create buttons and text for third instruction page"""
        self.label_1.text = 'The signals will be assigned a score between 0 and 100. '\
                            'A score of 100 would be a high quality clear signal and a score of 0 would be a very poor '\
                            'and noisy signal. A score is assigned by dragging the image to the right side of the screen.'
        self.image.source = 'inst2.jpg'
        self.label_2.text = ''
        # Remove all widgets from previous page
        self.grid_layout.clear_widgets()
        # Add buttons for this page
        self.grid_layout.add_widget(self.menu_button)
        self.grid_layout.add_widget(self.back_button)
        self.grid_layout.add_widget(self.blank)
        self.unbind_all()
        # Bind correct page to next buttons
        self.back_button.bind(on_press=self.page_2)


class TutorialScreen_1(Screen):
    def __init__(self):
        Screen.__init__(self, name='tutorial1')
        # Create box layout to house widgets
        self.float_layout = FloatLayout()
        self.grid_layout = GridLayout(cols=1)
        self.grid_layout_buttons = GridLayout(cols=3, spacing=(Window.width/3, 10), padding=(Window.width/50, 10),
                                              size_hint=(0.2,0.15))
        self.label = Label(text='Layout of Annotation Screen:', font_size=Window.height/30, pos=(0, Window.height*0.4),
                           color=(0, 0, 128, 1), bold=True, size_hint_y=0.1)
        self.next_label = Label(text='Click "Next:" to start the tutorial ', color=(1, 0, 0, 1), size_hint=(0.2, 0.2))
        self.image = Image(source='anno_screen.png', size_hint_y=1)
        # Create buttons
        self.menu_button = SwitchButton(text='Menu')
        self.next_button = SwitchButton(text='Next')
        # Bind switching functions to buttons
        self.menu_button.bind(on_press=self.menu_screen)
        self.next_button.bind(on_press=self.next_screen)
        # Add buttons to grid layout
        self.grid_layout_buttons.add_widget(self.menu_button)
        self.grid_layout_buttons.add_widget(self.next_label)
        self.grid_layout_buttons.add_widget(self.next_button)
        # Add widgets to layout
        self.grid_layout.add_widget(self.label)
        self.grid_layout.add_widget(self.image)
        self.grid_layout.add_widget(self.grid_layout_buttons)
        # Add layout to screen
        self.add_widget(self.grid_layout)

        # Create widgets for tutorial game

    def menu_screen(self, *args):
        self.manager.current = 'menu'
        self.manager.transition.direction = 'right'

    def next_screen(self, *args):
        self.manager.current = 'tutorial2'
        self.manager.transition.direction = 'left'


class TutorialScreen_2(Screen):
    def __init__(self):
        Screen.__init__(self, name='tutorial2')
        # Create list variable to store pictures and solutions
        self.pictures = []
        self.solutions = []
        self.counter = 0
        # Store directory name in a variable
        curdir = dirname(__file__)
        # Add all pictures in tutorial folder to list
        for filename in glob(join(curdir, 'tutorial', '*')):
            self.pictures.append(filename)
        # Pull out all solution pictures into a separate list
        for pic in range(1, len(self.pictures), 2):
            self.solutions.append(self.pictures[pic])
        # Remove all solution pictures from the original pictures list
        self.pictures = [pic for pic in self.pictures if pic not in self.solutions]
        # Display first picture
        self.current = self.pictures.pop(0)
        self.soln_current = ''

        # Create layout widgets
        self.float_layout = FloatLayout()
        self.grid_layout_scores = GridLayout(cols=2, size_hint=(None, 0.2), spacing=0)
        self.grid_layout_ranking = GridLayout(cols=2, size_hint=(None, 0.2), spacing=90)
        self.grid_layout_top = GridLayout(cols=4, size_hint=(1, 0.2), padding=(40, 40), spacing=(Window.width / 15, 0),
                                          pos=(20, Window.height - 100))
        self.display = DragImage(source=self.current, drag_rect_width=Window.width, drag_rect_height=Window.height)
        self.image = Image(source=self.soln_current)
        # Create progress bar widget
        self.pb = ProgressBar(max=5)
        self.pb.value = self.counter
        # Create label to display the ranking comparing user score to machine score
        self.machine_score_label = TextLabel(text='')
        # Create label to display the score the user is assigning to
        self.score = Label(size_hint_x=0.1, font_size=Window.height / 35, bold=True)
        # Create labels for 'Score:' and 'Ranking:'
        self.score_label = Label(text='Score: ', color=(0, 0, 0, 1), size_hint_x=0.1, font_size=Window.height / 35)
        self.machine_label = Label(text='Your Ranking: ', color=(0, 0, 0, 1), size_hint_x=0.1,
                                   font_size=Window.height / 35)
        # Create buttons for widgets
        self.grid_layout_buttons = GridLayout(rows=1, size_hint_y=0.12, spacing=(Window.width / 30, Window.height / 50),
                                      padding=(Window.width / 25, Window.height / 50))
        self.menu_button = SwitchButton(text='Menu', size_hint=(None, 0.2))
        self.undo_button = SwitchButton(text='Undo', size_hint=(None, 0.2))
        self.skip_button = SwitchButton(text='Skip', size_hint=(None, 0.2))
        self.example_button = SwitchButton(text='Examples', size_hint=(None, 0.2))
        self.next_button = SwitchButton(text='Next', size_hint=(None, 0.2))
        # Create Label
        self.label = Label(text='Try annotating this signal', color=(1, 0, 0, 1), font_size=Window.height / 35)
        self.end_label = Label(text='Congratulations! \n Please return to the menu to \n start your annotations!',
                               color=(0, 0, 128, 1), font_size=Window.height/20, bold=True)
        # Bind switching functions to buttons
        self.menu_button.bind(on_press=self.menu_screen)
        self.skip_button.bind(on_press=self.skip)
        self.undo_button.bind(on_press=self.undo)
        self.example_button.bind(on_press=self.example_screen)
        self.next_button.bind(on_press=self.next)
        # Add widgets to grid layout
        self.grid_layout_buttons.add_widget(self.label)
        self.grid_layout_buttons.add_widget(self.menu_button)
        self.grid_layout_buttons.add_widget(self.undo_button)
        self.grid_layout_buttons.add_widget(self.skip_button)
        self.grid_layout_buttons.add_widget(self.example_button)
        # Add widgets to grid layouts
        self.grid_layout_top.add_widget(self.pb)
        self.grid_layout_scores.add_widget(self.score_label)
        self.grid_layout_scores.add_widget(self.score)
        self.grid_layout_top.add_widget(self.grid_layout_scores)
        self.grid_layout_ranking.add_widget(self.machine_label)
        self.grid_layout_ranking.add_widget(self.machine_score_label)
        self.grid_layout_top.add_widget(self.grid_layout_ranking)
        # Add widgets to the float layout
        self.float_layout.add_widget(self.display)
        self.float_layout.add_widget(self.grid_layout_top)
        self.float_layout.add_widget(self.grid_layout_buttons)
        # Add float layout to the screen
        self.add_widget(self.float_layout)

    # Record initial down click coordinates
    def on_touch_down(self, touch):
        """Record the initial coordinates of the user touch"""
        super(TutorialScreen_2, self).on_touch_down(touch)
        self.coord = []
        self.coord.append(touch.x)
        self.coord.append(touch.y)

        try:
            self.machine_score_label.text = ''
        # Prevent error when click on end screen
        except AttributeError:
            return

    def on_touch_move(self, touch):
        """ Update the user score of the signal in real time as their touch is moving"""
        super(TutorialScreen_2, self).on_touch_move(touch)

        try:
            self.update_label(self.score, touch)
        # Avoid app crashing from user touch on end screen
        except AttributeError:
            return

    def on_touch_up(self, touch):
        """Calculate the user score based on the direction of their touch and ensure the movement was big enough"""
        super(TutorialScreen_2, self).on_touch_up(touch)

        try:
            self.coord.append(touch.x)
            self.coord.append(touch.y)
            min_dist, dist, dx, dy = calculate_dist(*self.coord)
            self.score_val = touch.y / Window.height

            with open('tutorial_score.csv', mode='r') as machine:
                reader = csv.reader(machine)
                for row in reader:
                    if row[0] == ntpath.basename(self.current):
                        if row[1] != '':
                            self.machine_score = row[1]
                        else:
                            self.machine_score = ''

            # Check if drag movement is big enough
            if dist > min_dist and dx > Window.width / 5:
                # Assign ranking based on comparison to machine learning score
                self.ranking = abs(self.score_val -float(self.machine_score))
                if self.ranking < 0.1:
                    self.machine_score_label.text = 'Excellent!'
                elif self.ranking < 0.2:
                    self.machine_score_label.text = 'Very Good!'
                elif self.ranking < 0.3:
                    self.machine_score_label.text = 'Good!'
                elif self.ranking < 0.4:
                    self.machine_score_label.text = 'OK!'
                elif self.ranking < 0.5:
                    self.machine_score_label.text = 'Not Quite!'

                try:
                    self.float_layout.remove_widget(self.display)
                    self.label.text = 'Compare your score to the \n suggested scoring and check \n your ranking!'
                    self.float_layout.add_widget(self.image, index=2)
                    self.soln_current = self.solutions.pop(0)
                    self.image.source = self.soln_current

                    self.grid_layout_top.rows = 2
                    self.grid_layout_top.add_widget(self.next_button)
                    self.prev_pictures.append(self.current)

                # Prevent crashing from drag on solution screen
                except WidgetException:
                    return

            # Recenter display picture if drag is too small
            else:
                self.display.center = self.center
                if dist < 5:
                    self.machine_score_label.text = ''
                else:
                    self.machine_score_label.text = 'Try Again'
        # Prevent crashing from user touches on end screen
        except (AttributeError, TypeError):
            return

    def update_label(self, label, touch):
        """Changes the users score and color of the score for the signal in real time"""
        score = int((touch.y / Window.height) * 100)
        label.text = str(score)
        if score > 75:
            label.color = (0,150,0,1)
        elif score > 50:
            label.color = (0, 50, 0, 1)
        elif score > 25:
            label.color = (5, 50, 0, 1)
        elif score > 0:
            label.color = (50, 0, 0, 1)

    def menu_screen(self, *args):
        """Changes screen to menu screen"""
        self.manager.current = 'menu'
        self.manager.transition.direction = 'right'

    def example_screen(self, *args):
        """Changes screen to example screen"""
        self.manager.current = 'example'
        self.manager.transition.direction = 'left'

    def skip(self, *args):
        """Skips to the next picture to annotate"""
        # Check if user is on the last picture
        if len(self.pictures) > 0:
            # Record the current picture
            self.cont.prev_pictures.append(self.cont.current)
            # Skip to the next picture
            self.cont.change_image()
            # Increment the progress bar
            self.cont.pb.value = self.cont.pb.value + 1

    def undo(self, *args):
        """Goes back to the previous picture to annotate"""
        try:
            # Check if user is on the last picture
            if len(self.cont.pictures) > 0:
                # Insert previous picture in the pictures list
                self.cont.pictures.insert(0, self.cont.prev_pictures.pop(-2))
                # Change to the previous picture
                self.cont.change_image()
                # Decrease the progress bar
                self.cont.pb.value = self.cont.pb.value - 1
                # Decrease counters
                self.cont.counter = self.cont.counter - 1
        except IndexError:
            return

    def next(self, *args):
        """Removes the solution image and re-adds the signal to annotate and updates the progress bar"""
        if self.counter == 4:
            self.float_layout.clear_widgets()
            self.float_layout.add_widget(self.end_label)
            self.grid_layout_buttons.remove_widget(self.menu_button)
            self.menu_button.size_hint = (None, None)
            self.float_layout.add_widget(self.menu_button)
        else:
            self.float_layout.remove_widget(self.image)
            self.current = self.pictures.pop(0)
            self.display.source = self.current
            self.float_layout.add_widget(self.display, index=2)
            self.grid_layout_top.remove_widget(self.next_button)
            self.label.text = 'Try annotating this signal!'
            self.counter = self.counter + 1
            self.pb.value = self.counter


# Example screen accessed during anno game from anno screen
class ExampleScreen(Screen):
    def __init__(self):
        Screen.__init__(self, name='example')
        # Create box layout to house widgets
        self.box_layout = BoxLayout(orientation='vertical')
        # Create grid layout to house images and buttons
        self.grid_layout_img = GridLayout(cols=2, spacing=10)
        self.grid_layout_btn = GridLayout(cols=1, size_hint_y=0.11, size_hint_x=0.15, padding=Window.width/100)
        # Create buttons and empty spacing widget
        self.back_button = SwitchButton(text='Back', size_hint_x=0.15)
        self.empty = Label()
        # Bind screen switching function to button
        self.back_button.bind(on_press=self.anno_screen)
        # Create example images and labels
        self.good_im = Image(source='good.png')
        self.unclear_im = Image(source='unclear.png')
        self.bad_im = Image(source='bad.png')
        self.good_lab = Label(text='GOOD:', color=(0, 0, 128, 1), bold=True,
                              font_size=Window.height/20, halign='right')
        self.unclear_lab = Label(text='UNCLEAR:', color=(0, 0, 128, 1), bold=True,
                                 font_size=Window.height/20)
        self.bad_lab = Label(text='BAD:', color=(0, 0, 128, 1), bold=True,
                             font_size=Window.height/20)

        # Add images and labels to grid layout
        self.grid_layout_img.add_widget(self.good_lab)
        self.grid_layout_img.add_widget(self.good_im)
        self.grid_layout_img.add_widget(self.unclear_lab)
        self.grid_layout_img.add_widget(self.unclear_im)
        self.grid_layout_img.add_widget(self.bad_lab)
        self.grid_layout_img.add_widget(self.bad_im)
        # Add button to grid layout
        self.grid_layout_btn.add_widget(self.back_button)

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

    def on_pause(self):
        """Pauses app when switching between apps"""
        return True

    def on_resume(self):
        """Resume app when switching from another app"""
        return True

# Run app
if __name__ == '__main__':
    ScorePicturesApp().run()
