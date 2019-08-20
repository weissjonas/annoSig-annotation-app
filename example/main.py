from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import DragBehavior
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import WidgetException
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Rectangle, Color, Point, GraphicException
from kivy.clock import Clock
from glob import glob
from os.path import join, dirname
from random import randint
import csv
from math import sqrt
import ntpath
import datetime
from functools import partial


# Store user_id and username in global variable
user_id = None
username = ''
# Store screens in global variable to access within other classes
user = None
menu = None
anno = None
cont = None
settings = None
screen_manager = None
tutorial = None
achievement = None
image = None
lines = None
line_color = [0, 0, 128, 1]
# Store how many annotations completed by user
total_annos = 0
total_counter = 0
total_exc = 0
# Store lifetime ranking of user
avg_ranking = 0
# Create dictionary to track which days user does annotations
date_tracker = {}
# Create dictionary to store scores
score_dict = {}
# Check if user has completed the tutorial
tutorial_check = False
# Keep track of last screen
last_screen = None
# Number of signals to annotate before triggering continue screen
continue_trigger = 5
# Move screen when user acivates virtual keyboard on mobile
Window.softinput_mode = 'pan'


# Create an image class that supports drag behaviors
class DragImage(DragBehavior, Image):
    pass


class AchievementBadge(GridLayout):
    def __init__(self, trophy_source, title_text, description, max_progress):
        GridLayout.__init__(self, cols=2, size_hint_y=None, height=Window.height/3)
        # Create grid to hold text and progress bar
        self.grid = GridLayout(cols=1, padding=Window.width/20, spacing=Window.height/30)
        # Create image widget for trophy picture
        self.trophy = Image(source=trophy_source, size_hint_y=None, height=Window.height/3)
        # Create label widget for achievement title
        self.title = Label(text=title_text, color=(0, 0, 128, 1), bold=True, font_size=Window.height/25,
                           size_hint=(1, 1), text_size=(Window.width/2.5, None), halign='center')
        # Create label widget for description title
        self.description = Label(text=description, color=(0, 0, 128, 1), font_size=Window.height/30,
                                 size_hint=(1, 1), halign='center', text_size=(Window.width/2.5, None))
        # Create progress bar widget
        self.progress = ProgressBar(max=max_progress)
        # Add progress widgets to grid

        # Add widgets to grid
        self.grid.add_widget(self.title)
        self.grid.add_widget(self.description)
        self.grid.add_widget(self.progress)
        # Add grid to layout
        self.add_widget(self.trophy)
        self.add_widget(self.grid)


class LeaderGrid(GridLayout):
    def __init__(self, usr, score, ranking, display):
        GridLayout.__init__(self, cols=5, size_hint_y=None, height=Window.height/3)


# Buttons to switch between screens
class SwitchButton(Button):
    background_normal = 'navy.png'
    background_down = 'pressed.png'
    font_size = Window.height*0.035
    bold = True
    halign = 'center'


# Text used for titles
class TitleText(Label):
    font_size = Window.height/10
    color = (0, 0, 128, 1)
    bold = True
    text_size = (Window.width*0.8, None)
    halign = 'center'


# Text featured in instruction screen
class TextLabel(Label):
    font_size = Window.height/20
    text_size = (Window.width * 0.8, None)
    color = (0, 0, 128, 1)
    halign = 'center'
    bold = True
    padding = (200, 200)


# Create Screen Manager to house different screens within the app
class ScreenManage(ScreenManager):
    def __init__(self):
        ScreenManager.__init__(self)
        global user, menu, anno, cont, tutorial, achievement, settings

        self.start = StartScreen()
        anno = AnnotateScreen()
        menu = MenuScreen()
        self.inst1 = InstructionScreen()
        tutorial = TutorialScreen()
        self.tutorialend = TutorialEndScreen()
        self.example = ExampleScreen()
        user = UserScreen()
        cont = ContScreen()
        achievement = AchievementScreen()
        settings = SettingsScreen()
        self.leaderboard = LeaderboardScreen()


        self.empty = True

        # Check if it is user's first time using app
        with open('user_score.csv', mode='r') as score_data:
            reader = csv.reader(score_data)
            for row in reader:
                if row != '':
                    self.empty = False
        if self.empty == True:
            self.add_widget(self.start)

        self.add_widget(menu)
        self.add_widget(anno)
        self.add_widget(self.inst1)
        self.add_widget(tutorial)
        self.add_widget(self.tutorialend)
        self.add_widget(self.example)
        self.add_widget(user)
        self.add_widget(cont)
        self.add_widget(achievement)
        self.add_widget(settings)
        self.add_widget(self.leaderboard)


class StartScreen(Screen):
    def __init__(self):
        Screen.__init__(self, name='start')

        # Create box layout to house widgets
        self.box_layout = BoxLayout(orientation='vertical')
        # Create grid layout to house username label and text box
        self.grid_layout_usr = GridLayout(cols=2, padding=(Window.width / 5, Window.height/11),
                                          spacing=(Window.width / 30, Window.height / 12), size_hint_y=0.4)
        self.grid_layout_button = GridLayout(cols=1, padding=(Window.width/2.5, Window.height/20),
                                             spacing=(Window.width/20, Window.height/20), size_hint_y=0.3)
        # Create start screen widgets
        self.image = Image(source='fecg_logo.png')
        self.username_label = TextLabel(text='Username:')
        self.text_box_usr = TextInput(multiline=False, cursor_color=(0, 0, 128, 1), hint_text='Please Enter a Username',
                                      size_hint_y=0.15)
        self.menu_button = SwitchButton(text='Ok!', size_hint=(0.2, 0.5))
        self.menu_button.bind(on_press=self.menu_screen)
        # Add username widgets to grid layout
        self.grid_layout_usr.add_widget(self.username_label)
        self.grid_layout_usr.add_widget(self.text_box_usr)
        self.grid_layout_button.add_widget(self.menu_button)
        # Add widgets to box layout
        self.box_layout.add_widget(self.image)
        self.box_layout.add_widget(self.grid_layout_usr)
        self.box_layout.add_widget(self.grid_layout_button)
        # Add box layout to screen
        self.add_widget(self.box_layout)

    def menu_screen(self, *args):
        """Switch to menu screen on button press and writes user data to user_score.csv"""
        global username, user_id
        # Set username to text entered by user
        username = self.text_box_usr.text
        if username != '':
            self.manager.current = 'menu'
            self.manager.transition.direction = 'left'
            # Create user id for tracking stats
            user_id = randint(0, 99999) # When database is deployed add in check to ensure no ids are the same
            # Display welcome message after first launch
            menu.welcome_label.text = 'Welcome ' + username + '!'
            # Write username to csv file
            with open('user_score.csv', mode='a', newline='') as score_data:
                writer = csv.writer(score_data)
                writer.writerow(['', user_id, '', '', '', username])
        else:
            return


class UserScreen(Screen):
    def __init__(self):
        Screen.__init__(self, name='user')
        # Create box layout to hold image and grid layouts
        self.box_layout = BoxLayout(orientation='vertical')
        # Create grid layout to hold user stats
        self.grid_layout = GridLayout(cols=2, padding=(Window.width/5, Window.height/15),
                                      spacing=(Window.width/30, Window.height/35))
        # Create grid layout to hold and format button
        self.grid_layout_button = GridLayout(cols=4, padding=(Window.width/12, Window.height/40),
                                             spacing=(Window.width/30, Window.height/15), size_hint_y=0.4)
        # Create image and text widgets
        self.image = Image(source='icon.png')
        self.username_label = TextLabel(text='Username:')
        self.usr = TextLabel()

        self.totals = TextLabel(text='Total Annotations:')
        self.tot = TextLabel()
        self.ranking = TextLabel(text='Overall Ranking:')
        self.rnk = TextLabel()
        self.menu_button = SwitchButton(text='Menu')
        self.leaderboard_button = SwitchButton(text='Leaderboard')
        self.badge_button = SwitchButton(text='Achievements')
        self.settings_button = SwitchButton(text='Settings')

        # Bind switching function to button
        self.menu_button.bind(on_press=self.menu_screen)
        self.leaderboard_button.bind(on_press=self.leaderboard_screen)
        self.badge_button.bind(on_press=self.achievement_screen)

        self.settings_button.bind(on_press=self.settings_screen)
        # Add widgets to grid layouts
        self.grid_layout.add_widget(self.username_label)
        self.grid_layout.add_widget(self.usr)
        self.grid_layout.add_widget(self.totals)
        self.grid_layout.add_widget(self.tot)
        self.grid_layout.add_widget(self.ranking)
        self.grid_layout.add_widget(self.rnk)
        self.grid_layout_button.add_widget(self.menu_button)
        self.grid_layout_button.add_widget(self.badge_button)
        self.grid_layout_button.add_widget(self.leaderboard_button)
        self.grid_layout_button.add_widget(self.settings_button)

        # Add widgets to box layout
        self.box_layout.add_widget(self.image)
        self.box_layout.add_widget(self.grid_layout)
        self.box_layout.add_widget(self.grid_layout_button)
        # Add box layout to screen
        self.add_widget(self.box_layout)

    def menu_screen(self, *args):
        """Switches current screen to menu screen on button press"""
        self.manager.current = 'menu'
        self.manager.transition.direction = 'right'

    def settings_screen(self, *args):
        """Changes screen to settings screen"""
        self.manager.current = 'settings'
        self.manager.transition.direction = 'left'

    def achievement_screen(self, *args):
        """Changes screen to achievement screen and updates source photos and progress for badges"""
        self.manager.current = 'achievement'
        self.manager.transition.direction = 'left'

    def leaderboard_screen(self, *args):
        """Changes screen to leaderboard screen"""
        self.manager.current = 'leaderboard'
        self.manager.transition.direction = 'left'


class MenuScreen(Screen):
    def __init__(self):
        global username, achievement, total_annos
        Screen.__init__(self, name='menu')

        # Create Box Layout for the screen
        self.box_layout = BoxLayout(orientation='vertical')
        # Create Grid Layout for the buttons and title/image
        self.grid_layout_title = GridLayout(cols=1)
        self.grid_layout_buttons = GridLayout(cols=1, padding=(Window.width/3, Window.height/30), size_hint=(1, 0.5),
                                              spacing=5)
        # Navigation buttons
        self.start_button = SwitchButton(text='Start')
        self.instruct_button = SwitchButton(text='Instructions')
        self.user_button = SwitchButton(text='User Profile')
        # Welcome label
        self.welcome_label = TextLabel(text='Welcome ' + username + '!')
        # Bind screen switching functions to buttons
        self.start_button.bind(on_release=self.anno_screen)
        self.instruct_button.bind(on_press=self.inst_screen)
        self.user_button.bind(on_press=self.user_screen)
        # Menu image
        self.pic = Image(source='fecg_logo.png', size_hint=(0.6, 0.6))

        # Add widgets to grid layout
        self.grid_layout_buttons.add_widget(self.welcome_label)
        self.grid_layout_buttons.add_widget(self.instruct_button)
        self.grid_layout_buttons.add_widget(self.start_button)
        self.grid_layout_buttons.add_widget(self.user_button)
        self.grid_layout_title.add_widget(self.pic)
        self.box_layout.add_widget(self.grid_layout_title)
        self.box_layout.add_widget(self.grid_layout_buttons)
        self.add_widget(self.box_layout)

    def anno_screen(self, *args):
        """Change screen to annotation game"""
        global last_screen, anno
        self.manager.current = 'annotate'
        self.manager.transition.direction = 'left'
        last_screen = 'annotate'

    def inst_screen(self, *args):
        """Change screen to instruction screen"""
        global last_screen
        self.manager.current = 'inst1'
        self.manager.transition.direction = 'left'
        last_screen = 'tutorial'

    def user_screen(self, *args):
        """Change screen to user profile screen and updates user stats"""
        self.manager.current = 'user'
        self.manager.transition.direction = 'left'
        # Update user stats and achievement badges
        update_rankings()
        update_other_achievement()
        update_std_achievements(var=total_annos, badge=achievement.anno_badge)
        update_std_achievements(var=total_exc, badge=achievement.excellent_badge)
        update_std_achievements(var=len(date_tracker), badge=achievement.days_badge)


class AnnotateScreen(Screen):
    # Create property to record user score and display label on screen in real time

    def __init__(self):
        Screen.__init__(self, name='annotate')

        # Change Window Background color
        Window.clearcolor = (1, 1, 1, 1)
        global user_id, username, total_counter, score_dict, continue_trigger

        # Initialize counter to track how many pictures are done in each grouping
        self.counter = 0
        # Initialize counter to track how many pictures are done in the entire annotation session
        total_counter = 0

        # Create variable to store current date
        self.date = datetime.datetime.now()
        # Create list to house pictures
        self.pictures = []
        # Create variable to store machine score of signals
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
                # Get user's id
                user_id = row[1]
                # Get user's username
                if row[5] != '':
                    username = row[5]
                for pic in self.pictures:
                    if row[2] == ntpath.basename(pic):
                        self.pictures.remove(pic)

        # Get total number of pictures to gauge progress
        self.prog_max = len([filename for filename in glob(join(curdir, 'images', '*'))])
        # Create progress bar widget
        self.pb = ProgressBar(max=self.prog_max)
        # Create layouts and widgets
        self.float_layout = FloatLayout()
        self.box_layout = BoxLayout(orientation='vertical')
        self.grid_layout_scores = GridLayout(cols=2, size_hint=(0.5, 0.2), spacing=0)
        self.grid_layout_ranking = GridLayout(cols=2, size_hint=(0.5, 0.2), spacing=150)
        self.grid_layout_top = GridLayout(cols=4, size_hint=(1, 0.2), padding=(50, 0), spacing=(Window.width / 15, 0),
                                          pos=(20, Window.height * 0.8))
        # Create grid layout to house the screen buttons
        self.grid_layout_buttons = GridLayout(rows=1, size_hint_y=0.12, spacing=(Window.width/40, Window.height/50),
                                              padding=(Window.width/30, Window.height/50))
        self.display = Image()
        # Create end screen widgets
        self.end_box_layout = BoxLayout(orientation='vertical', padding=Window.width/20)
        self.end_grid_layout = GridLayout(cols=1, padding=(Window.width / 3, 0), size_hint_y=0.15)
        self.end_label_1 = TitleText(text='Congratulations ' + username + '!', size_hint_y=0.2)
        self.end_label_2 = TextLabel(text='You\'ve annotated all the signals \n currently available! '
                                      '\n More signals will be available soon.')
        self.end_box_layout.add_widget(self.end_label_1)
        self.end_box_layout.add_widget(self.end_label_2)
        # Set initial progress of progress bar
        self.pb.value = self.prog_max - len(self.pictures) - 1
        # Create label to display the ranking comparing user score to machine score
        self.machine_score_label = TextLabel(text='')
        # Create label to display the score the user is assigning to
        self.score = Label(size_hint_x=0.1, font_size=Window.height/15, bold=True)
        # Create text labels
        self.score_label = Label(text='Score:', color=(0, 0, 0, 1), size_hint_x=0.1, font_size=Window.height/25)
        self.machine_label = Label(text='Your Ranking:    ', color=(0, 0, 0, 1), size_hint_x=0.1,
                                   font_size=Window.height/25)
        self.label = TextLabel(text='', size_hint_x=1)
        # Create buttons
        self.menu_button = SwitchButton(text='Menu', size_hint=(1, 0.2))
        self.undo_button = SwitchButton(text='Undo', size_hint=(1, 0.2))
        self.skip_button = SwitchButton(text='Skip', size_hint=(1, 0.2))
        self.example_button = SwitchButton(text='Examples', size_hint=(1, 0.2))
        # Bind switching functions to buttons
        self.menu_button.bind(on_press=self.menu_screen)
        self.skip_button.bind(on_press=self.skip)
        self.undo_button.bind(on_press=self.undo)
        self.example_button.bind(on_press=self.example_screen)

        # Check if there are still pictures left to annotate
        if len(self.pictures) != 0:

            # The first image is updated with the first element in the list
            self.current = self.pictures.pop(0)
            self.prev_pictures = []
            self.display.source = self.current
            # Add buttons to grid layout
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
            self.box_layout.add_widget(self.float_layout)
            self.box_layout.add_widget(self.grid_layout_buttons)
            # Add box widget to screen
            self.add_widget(self.box_layout)

        # Display message if they have finished
        else:
            self.clear_widgets()
            self.grid_layout_buttons.remove_widget(self.menu_button)
            self.end_grid_layout.add_widget(self.menu_button)
            self.end_box_layout.add_widget(self.end_grid_layout)
            self.add_widget(self.end_box_layout)

    # Record initial down click coordinates
    def on_touch_down(self, touch):
        """Record the initial coordinates of the user touch"""
        super(AnnotateScreen, self).on_touch_down(touch)
        global lines
        self.coord = []
        self.coord.append(touch.x)
        self.coord.append(touch.y)

        try:
            self.machine_score_label.text = ''
        # Prevent error when click on end screen
        except AttributeError:
            return True

        with self.display.canvas:

            Color(*[0, 0, 128, 0.05])
            line = Point(points=(touch.x, touch.y), pointsize=Window.height/30, group='g')
            lines = line.points
            Clock.schedule_once(partial(self.remove_point, group='g'), 0.3)
            self.groups = ['g']

        touch.grab(self)
        return True

    def remove_point(self, *args, **kwargs):
        group=kwargs['group']
        self.display.canvas.remove_group(group)


    def on_touch_move(self, touch):
        """ Update the user score of the signal in real time as their touch is moving"""
        super(AnnotateScreen, self).on_touch_move(touch)
        global lines

        while True:
                oldx, oldy = lines[-2], lines[-1]
                break
        points = line_dist(oldx, oldy, touch.x, touch.y)

        if points:
            try:
                for idx in range(0, len(points), 2):
                    group = randint(0,999999)
                    with self.display.canvas:
                        Color(*[0, 0, 128, 0.05])
                        Point(points=(points[idx], points[idx+1]), pointsize=Window.height/30, group=str(group))

                    lines.append(points[idx])
                    lines.append(points[idx + 1])

                    Clock.schedule_once(partial(self.remove_point, group=str(group)), 0.3)
                    self.groups.append(str(group))

            except GraphicException:
                pass


        try:
            self.update_label(self.score, touch)

        # Avoid app crashing from user touch on end screen
        except AttributeError:
            return

    def on_touch_up(self, touch):
        """Calculate the user score based on the direction of their touch and ensure the movement was big enough"""
        super(AnnotateScreen, self).on_touch_up(touch)
        global total_ranking, lines

        if touch.grab_current is not self:
            return
        touch.ungrab(self)

        for group in self.groups:
            self.display.canvas.remove_group(group)


        try:
            self.coord.append(touch.x)
            self.coord.append(touch.y)
            min_dist, dist, dx, dy = calculate_dist(*self.coord)
            self.score_val = touch.y / Window.height

            # Check if drag movement is big enough
            if dist > min_dist and dx > Window.width / 5:
                self.prev_pictures.append(self.current)
                # Assign ranking based on comparison to machine learning score
                self.ranking = abs(self.score_val - float(self.machine_score))
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

                # Assign score based on drag direction

                self.change_image(score=self.score_val)

            # Recenter display picture if drag is too small
            else:
                self.display.center = self.center
                self.machine_score_label.text = 'Try Again'
        # Prevent crashing from user touches on end screen
        except (AttributeError, TypeError):
            return

    def change_image(self, score=None):
        """Change the displayed image and write the filename and score to score.csv"""
        global total_counter
        try:
            # Write picture name and score to csv
            with open('user_score.csv', mode='a', newline='') as score_data:
                writer = csv.writer(score_data)
                writer.writerow([self.date.strftime("%d-%m-%Y"), user_id, ntpath.basename(self.current), score,
                                 self.ranking, ''])

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
            self.grid_layout_buttons.remove_widget(self.menu_button)
            self.end_grid_layout.add_widget(self.menu_button)
            self.end_box_layout.add_widget(self.end_grid_layout)
            self.add_widget(self.end_box_layout)

        # Ask user if they want to continue annotating after a certain amount of pictures
        elif self.counter == continue_trigger:
            # Move to next picture
            self.current = self.pictures.pop(0)
            self.display.center = self.center
            self.display.source = self.current
            # Reset score
            self.score.text = ''
            # Increase counters
            self.counter = self.counter + 1
            total_counter = total_counter + 1
            # Update progress bar
            self.pb.value = self.prog_max - len(self.pictures) - 1
            self.cont_screen()

        else:
            # Move to next picture
            self.current = self.pictures.pop(0)
            self.display.center = self.center
            self.display.source = self.current
            # Reset score
            self.score.text = ''
            # Increase counters
            self.counter = self.counter + 1
            total_counter = total_counter + 1
            # Update progress bar
            self.pb.value = self.prog_max - len(self.pictures) - 1

    def update_label(self, label, touch):
        """Changes the users score and color of the score for the signal in real time"""
        score = int((touch.y / Window.height) * 100)
        label.text = str(score)
        if score > 75:
            label.color = (0, 150, 0, 1)
        elif score > 50:
            label.color = (0, 50, 0, 1)
        elif score > 25:
            label.color = (5, 50, 0, 1)
        elif score > 0:
            label.color = (50, 0, 0, 1)

    def skip(self, *args):
        """Skip to the next picture to annotate"""
        global continue_trigger
        # Check if user is on the last picture
        if len(self.pictures) > 0:
            # Record the current picture
            self.prev_pictures.append(self.current)
            # Skip to the next picture
            self.current = self.pictures.pop(0)
            self.display.source = self.current
            # Increment the progress bar
            self.pb.value = self.pb.value + 1
            # Increment the counter
            # Switch to continue screen
            if self.counter == continue_trigger:
                # Move to next picture
                self.current = self.pictures.pop(0)
                self.display.center = self.center
                self.display.source = self.current
                # Reset score
                self.score.text = ''
                # Increase counters
                self.counter = self.counter + 1
                # Update progress bar
                self.pb.value = self.prog_max - len(self.pictures) - 1
                self.cont_screen()
            elif self.counter <= continue_trigger:
                self.counter = self.counter + 1

    def undo(self, *args):
        """Go back to the previous picture to annotate"""
        global total_counter
        try:
            # Check if user is on the last picture
            if len(self.pictures) > 0:
                self.save_current = self.current
                # Insert previous picture in the pictures list
                self.pictures.insert(0, self.prev_pictures.pop(-1))
                # Decrease the progress bar
                self.pb.value = self.pb.value - 1
                # Decrease counters
                if self.counter <= 0:
                    self.counter = 0
                else:
                    self.counter = self.counter - 1
                if total_counter <= 0:
                    total_counter = 0
                else:
                    total_counter = total_counter - 1
                # Change to the previous picture
                self.current = self.pictures.pop(0)
                self.display.source = self.current
                self.pictures.insert(0, self.save_current)

        except IndexError:
            return

    def cont_screen(self, *args):
        global cont,total_counter, total_annos, username
        update_rankings()
        print(total_annos)
        cont.label_1.text = 'Keep it up ' + username + '!'
        cont.anno_sess_label.text = str(total_counter)
        cont.anno_tot_label.text = str(total_annos)
        self.manager.current = 'cont'
        self.manager.transition.direction = 'left'

    def menu_screen(self, *args):
        """Change screen to menu screen"""
        self.manager.current = 'menu'
        self.manager.transition.direction = 'right'

    def example_screen(self, *args):
        """Change screen to example screen"""
        self.manager.current = 'example'
        self.manager.transition.direction = 'left'


class ContScreen(Screen):
    def __init__(self):
        Screen.__init__(self, name='cont')
        global anno, username
        self.box_layout = BoxLayout(orientation='vertical')
        self.grid_layout = GridLayout(cols=2, spacing=(Window.width / 10),
                                      padding=(Window.width / 5, Window.height / 10))
        self.label_1 = Label(text='Keep it up ' + username + '!', color=(0, 0, 128, 1), font_size=Window.height / 10,
                             bold=True, halign='center', size_hint_y=0.2)

        self.label_2 = Label(text='Annotations this session: ',
                             color=(0, 0, 128, 1), font_size=Window.height / 20, halign='center')
        self.anno_sess_label = TextLabel(text=str(total_counter))
        self.label_3 = Label(text='Total annotations: ',
                             color=(0, 0, 128, 1), font_size=Window.height / 20, halign='center')
        self.anno_tot_label = TextLabel(text=str(total_annos))

        self.cont_label = TextLabel(text='Do you want to continue? ')
        # Create continue button
        self.cont_button = SwitchButton(text='Continue', size_hint=(0.2, 0.7))
        self.menu_button = SwitchButton(text='Menu', size_hint=(0.2, 0.7))
        self.cont_button.bind(on_press=self.cont_anno)
        self.menu_button.bind(on_press=self.menu_screen)
        # Add buttons to grid

        self.grid_layout.add_widget(self.label_2)
        self.grid_layout.add_widget(self.anno_sess_label)
        self.grid_layout.add_widget(self.label_3)
        self.grid_layout.add_widget(self.anno_tot_label)
        self.grid_layout.add_widget(self.menu_button)
        self.grid_layout.add_widget(self.cont_button)
        self.box_layout.add_widget(self.label_1)
        self.box_layout.add_widget(self.grid_layout)
        # Add grid to screen
        self.add_widget(self.box_layout)

    def cont_anno(self, *args):

        if len(anno.pictures) == 0:
            self.clear_widgets()
            anno.grid_layout_buttons.remove_widget(anno.menu_button)
            anno.end_grid_layout.add_widget(anno.menu_button)
            anno.end_box_layout.add_widget(anno.end_grid_layout)
            self.add_widget(anno.end_box_layout)
        else:
            self.manager.current = 'annotate'
            self.manager.transition.direction = 'left'
            anno.display.center = Window.center
            anno.counter = 0

    def menu_screen(self, *args):
        anno.counter = 0
        self.manager.current = 'menu'
        self.manager.transition.direction = 'right'


class InstructionScreen(Screen):
    def __init__(self):
        Screen.__init__(self, name='inst1')

        # Create box layout to house all widgets
        self.box_layout = BoxLayout(orientation='vertical', padding=(20, 0))
        # Create grid layout to house buttons
        self.grid_layout = GridLayout(cols=3, rows=1, size_hint=(1, 0.15), padding=(Window.width/50, 10),
                                      spacing=(Window.width / 5, 10))
        # Create buttons and spacing widgets
        self.menu_button = SwitchButton(text='Menu', size_hint_x=0.2)
        self.next_button = SwitchButton(text='Next', size_hint_x=0.2)
        self.back_button = SwitchButton(text='Back', size_hint_x=0.2)
        self.tutorial_button = SwitchButton(text='Start Tutorial', size_hint_x=0.2)
        self.blank = Label(size_hint_x=0.2)

        # Bind switching functions to buttons
        self.menu_button.bind(on_press=self.menu_screen)
        self.next_button.bind(on_press=self.page_2)
        # Create photo widget
        self.image = Image(source='tut_1.png')
        # Write text label for above photo
        self.label_1 = TextLabel(size_hint=(1, 0.2), text='Layout of Annotation Screen')
        # Add buttons to grid layout
        self.grid_layout.add_widget(self.menu_button)
        self.grid_layout.add_widget(self.blank)
        self.grid_layout.add_widget(self.next_button)
        self.tutorial_button.bind(on_press=self.tutorial)
        # Add widgets to box layout
        self.box_layout.add_widget(self.label_1)
        self.box_layout.add_widget(self.image)
        self.box_layout.add_widget(self.grid_layout)
        # Add box layout to screen
        self.add_widget(self.box_layout)

    def menu_screen(self, *args):
        self.manager.current = 'menu'
        self.manager.transition.direction = 'right'

    def tutorial(self, *args):
        self.manager.current = 'tutorial'
        self.manager.transition.direction = 'left'

    def unbind_all(self):
        """Unbind all functions from buttons"""
        self.next_button.unbind(on_press=self.page_1)
        self.next_button.unbind(on_press=self.page_2)
        self.back_button.unbind(on_press=self.page_1)
        self.back_button.unbind(on_press=self.page_2)

    def page_1(self, *args):
        """Create buttons and text for first instruction page"""

        self.label_1.text = 'Layout of Annotation Screen'
        self.image.source = 'tut_1.png'
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
        self.label_1.text = 'Annotate the signal by swiping it to the right and assigning a score'
        self.image.source = 'tut_2.png'
        # Remove all widgets from previous page
        self.grid_layout.clear_widgets()
        # Add buttons for this page
        self.grid_layout.add_widget(self.menu_button)
        self.grid_layout.add_widget(self.back_button)
        self.grid_layout.add_widget(self.tutorial_button)

        self.unbind_all()
        # Bind correct page to back and next buttons
        self.back_button.bind(on_press=self.page_1)


class TutorialScreen(Screen):
    def __init__(self):
        Screen.__init__(self, name='tutorial')
        # Create list variable to store pictures and solutions
        self.pictures = []
        self.prev_pictures = []
        self.solutions = []
        self.prev_soln = []
        self.counter = 0
        self.tracker = 'signal'
        # Store directory name in a variable
        curdir = dirname(__file__)
        # Add all pictures in tutorial folder to list
        for filename in glob(join(curdir, 'tutorial', '*')):
            self.pictures.append(filename)
        # Pull out all solution pictures into a separate list
        for filename in glob(join(curdir, 'tutorial', '*_soln.png')):
            self.solutions.append(filename)
        # Remove all solution pictures from the original pictures list
        self.pictures = [pic for pic in self.pictures if pic not in self.solutions]
        self.pictures.sort()
        self.solutions.sort()
        # Display first picture
        self.current = self.pictures.pop(0)
        self.soln_current = ''

        # Create layout widgets
        self.float_layout = FloatLayout()
        self.grid_layout_scores = GridLayout(cols=2, size_hint=(0.5, 0.2), spacing=10)
        self.grid_layout_ranking = GridLayout(cols=2, size_hint=(0.5, 0.2), spacing=150)
        self.grid_layout_top = GridLayout(cols=4, size_hint=(1, 0.2), padding=(Window.width/30, Window.height/15),
                                          spacing=(Window.width/15, 0), pos=(20, Window.height * 0.8))
        self.display = Image(source=self.current)
        self.image = Image(source=self.soln_current)
        # Create progress bar widget
        self.pb = ProgressBar(max=10)
        self.pb.value = self.counter
        # Create label to display the ranking comparing user score to machine score
        self.machine_score_label = Label(text='', color=(0, 0, 128, 1), font_size=Window.height/25, halign='left',
                                         bold=True)
        # Create label to display the score the user is assigning to
        self.score = Label(size_hint_x=0.1, font_size=Window.height/15, bold=True)
        # Create labels for 'Score:' and 'Ranking:'
        self.score_label = Label(text='Score:', color=(0, 0, 0, 1), size_hint_x=0.1, font_size=Window.height/25)
        self.machine_label = Label(text='Your Ranking:    ', color=(0, 0, 0, 1), size_hint_x=0.1,
                                   font_size=Window.height/25)
        # Create buttons for widgets
        self.grid_layout_buttons = GridLayout(rows=1, size_hint_y=0.12, spacing=(Window.width/40, Window.height/50),
                                              padding=(Window.width/25, Window.height/50))
        self.menu_button = SwitchButton(text='Menu', size_hint=(0.9, 0.2))
        self.undo_button = SwitchButton(text='Undo', size_hint=(0.9, 0.2))
        self.skip_button = SwitchButton(text='Skip', size_hint=(0.9, 0.2))
        self.example_button = SwitchButton(text='Examples', size_hint=(0.9, 0.2))
        self.next_button = SwitchButton(text='Next', size_hint=(0.4, 0.1))
        self.empty_button = Label(size_hint=(0.4, 0.1))
        # Create Label
        self.label = Label(text='Try annotating this signal', color=(1, 0, 0, 1), font_size=Window.height/35,
                           size_hint_x=1)

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
        self.grid_layout_top.add_widget(self.empty_button)
        # Add widgets to the float layout
        self.float_layout.add_widget(self.display)
        self.float_layout.add_widget(self.grid_layout_top)
        self.float_layout.add_widget(self.grid_layout_buttons)
        # Add float layout to the screen
        self.add_widget(self.float_layout)

    # Record initial down click coordinates
    def on_touch_down(self, touch):
        """Record the initial coordinates of the user touch"""
        super(TutorialScreen, self).on_touch_down(touch)
        global lines
        self.coord = []
        self.coord.append(touch.x)
        self.coord.append(touch.y)

        try:
            self.machine_score_label.text = ''
        # Prevent error when click on end screen
        except AttributeError:
            return True

        with self.display.canvas:
            color = [0, 0, 128, 0.05]
            Color(*color, group='group')
            lines = [Point(points=(touch.x, touch.y), pointsize=15, group='group')]

        touch.grab(self)
        return True

    def on_touch_move(self, touch):
        """ Update the user score of the signal in real time as their touch is moving"""
        super(TutorialScreen, self).on_touch_move(touch)
        global lines
        index = -1

        while True:
            try:
                points = lines[index].points
                oldx, oldy = points[-2], points[-1]
                break
            except:
                index -= 1

        points = line_dist(oldx, oldy, touch.x, touch.y)

        if points:
            try:
                lp = lines[-1].add_point
                for idx in range(0, len(points), 2):
                    lp(points[idx], points[idx + 1])
            except GraphicException:
                pass
        try:
            self.update_label(self.score, touch)

        # Avoid app crashing from user touch on end screen
        except AttributeError:
            return

    def on_touch_up(self, touch):
        """Calculate the user score based on the direction of their touch and ensure the movement was big enough"""
        super(TutorialScreen, self).on_touch_up(touch)
        global total_ranking, lines

        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        self.display.canvas.remove_group('group')
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

                self.tracker = 'soln'
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
                    self.prev_pictures.append(self.current)
                    self.float_layout.remove_widget(self.display)
                    self.label.text = ''
                    self.float_layout.add_widget(self.image, index=2)
                    self.soln_current = self.solutions.pop(0)
                    self.image.source = self.soln_current
                    self.grid_layout_top.remove_widget(self.empty_button)
                    self.grid_layout_top.add_widget(self.next_button)
                    self.counter = self.counter + 1
                    self.pb.value = self.counter

                # Prevent crashing from drag on solution screen
                except (WidgetException, IndexError):
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
        if len(self.solutions) > 0:
            # Check if on a solution picture
            if self.tracker == 'soln':
                # Remove solution picture
                self.float_layout.remove_widget(self.image)
                # Add last solution to previous solutions list
                self.prev_soln.append(self.soln_current)
                # Add new signal picture to screen
                self.current = self.pictures.pop(0)
                self.display.source = self.current
                self.float_layout.add_widget(self.display, index=2)
                # Remove 'next' button
                self.grid_layout_top.add_widget(self.empty_button)
                self.grid_layout_top.remove_widget(self.next_button)
                self.label.text = 'Try annotating this signal!'
                # Update tracker to indicate on a signal picture
                self.tracker = 'signal'
            # Check if currently on a signal picture
            elif self.tracker == 'signal':
                # Remove signal picture
                self.float_layout.remove_widget(self.display)
                self.label.text = ''
                # Add solution picture
                self.float_layout.add_widget(self.image, index=2)
                # Add previous signal to previous pictures list
                self.prev_pictures.append(self.current)
                self.soln_current = self.solutions.pop(0)
                self.image.source = self.soln_current
                # Add 'next' button to screen
                self.grid_layout_top.remove_widget(self.empty_button)
                self.grid_layout_top.add_widget(self.next_button)
                # Update tracker to show currently on a solution picture
                self.tracker = 'soln'
            # Update counter and progress bar
            self.counter = self.counter + 1
            self.pb.value = self.counter

    def undo(self, *args):
        """Goes back to the previous picture to annotate"""
        # Check if user is on the last picture
        try:
            if len(self.solutions) > 0:
                # Check if screen is on a 'solution' picture
                if self.tracker == 'soln':
                    # Insert previous picture in the pictures list
                    self.pictures.insert(0, self.prev_pictures.pop(-1))
                    # Insert previous solution in the solutions list
                    self.solutions.insert(0, self.soln_current)
                    # Remove the solution picture
                    self.float_layout.remove_widget(self.image)
                    # Add the new signal picture
                    self.current = self.pictures.pop(0)
                    self.display.source = self.current
                    self.float_layout.add_widget(self.display, index=2)
                    # Remove the 'next button'
                    self.grid_layout_top.add_widget(self.empty_button)
                    self.grid_layout_top.remove_widget(self.next_button)
                    self.label.text = 'Try annotating this signal!'
                    # Make sure counter does not go negative
                    if self.counter > 0:
                        self.counter = self.counter - 1
                    else:
                        self.counter = 0
                    # Update progress bar
                    self.pb.value = self.counter
                    # Change tracker to indicate it is now on a signal picture
                    self.tracker = 'signal'
                # Check if screen is on a 'signal' picture
                elif self.tracker == 'signal':
                    # Insert previous picture in the pictures list
                    self.solutions.insert(0, self.prev_soln.pop(-1))
                    self.pictures.insert(0, self.current)
                    # Remove the signal picture
                    self.float_layout.remove_widget(self.display)
                    self.label.text = ''
                    # Add the solution picture
                    self.float_layout.add_widget(self.image, index=2)
                    self.soln_current = self.solutions.pop(0)
                    self.image.source = self.soln_current
                    # Add the next button
                    self.grid_layout_top.remove_widget(self.empty_button)
                    self.grid_layout_top.add_widget(self.next_button)
                    # Make sure counter does not go negative
                    if self.counter > 0:
                        self.counter = self.counter - 1
                    else:
                        self.counter = 0
                    # Update the progress bar
                    self.pb.value = self.counter
                    # Change the tracker to indicate it is now on a solution picture
                    self.tracker = 'soln'
        except IndexError:
            return

    def next(self, *args):
        """Removes the solution image and re-adds the signal to annotate, updates the progress bar"""
        global screen_manager, tutorial
        if len(self.pictures) == 0:
            self.manager.current = 'tutorialend'
            self.manager.transition.direction = 'left'
            # Record if user has completed the tutorial
            with open('user_score.csv', mode='r+', newline='') as score_data:
                reader = csv.reader(score_data)
                writer = csv.writer(score_data)
                # Check if user has previously completed the tutorial
                self.check = False
                for row in reader:
                    if row[0]== 'tutorial':
                        self.check = True
                # If first time completing tutorial, write in csv
                if self.check == False:
                    writer.writerow(['tutorial', user_id, '', 1, '', ''])
            # Recreate tutorial widget to allow for user to redo the tutorial if they want
            screen_manager.remove_widget(tutorial)
            tutorial = TutorialScreen()
            screen_manager.add_widget(tutorial)

        else:
            # Add solution to previous solutions list
            self.prev_soln.append(self.soln_current)
            # Remove solution picture
            self.float_layout.remove_widget(self.image)
            # Add signal picture
            self.current = self.pictures.pop(0)
            self.display.source = self.current
            self.float_layout.add_widget(self.display, index=2)
            # Remove next button
            self.grid_layout_top.add_widget(self.empty_button)
            self.grid_layout_top.remove_widget(self.next_button)
            self.label.text = 'Try annotating this signal!'
            # Update counter
            self.counter = self.counter + 1
            # Update progress bar
            self.pb.value = self.counter
            # Update tracker to indicate on signal picture
            self.tracker = 'signal'


class TutorialEndScreen(Screen):
    def __init__(self):
        Screen.__init__(self, name='tutorialend')
        self.box_layout = BoxLayout(orientation='vertical')
        # Create Grid Layout for the buttons and title/image
        self.grid_layout_title = GridLayout(cols=1, padding=Window.height/30, spacing=Window.height/30)
        self.grid_layout_buttons = GridLayout(cols=1, padding=(Window.width/2.5, 40), size_hint=(1, 0.3))
        # Navigation buttons
        self.menu_button = SwitchButton(text='Menu', size_hint=(0.3, 0.5))

        # Bind screen switching functions to buttons
        self.menu_button.bind(on_release=self.menu_screen)
        self.image = Image(source='tut_compl.png')
        self.title_label = TitleText(text='Congratulations! ', size_hint_y=0.2)
        self.text_label = TextLabel(text='You\'ve completed the tutorial! \n You are now ready to start your '
                                         'annotations. \n Please return to the menu to get started!')

        # Add widgets to grid layout
        self.grid_layout_buttons.add_widget(self.menu_button)
        self.grid_layout_title.add_widget(self.title_label)
        self.grid_layout_title.add_widget(self.image)
        self.grid_layout_title.add_widget(self.text_label)
        self.box_layout.add_widget(self.grid_layout_title)
        self.box_layout.add_widget(self.grid_layout_buttons)
        self.add_widget(self.box_layout)


    def menu_screen(self, *args):
        """Changes screen to menu screen"""
        self.manager.current = 'menu'
        self.manager.transition.direction = 'right'


class ExampleScreen(Screen):
    def __init__(self):
        Screen.__init__(self, name='example')
        global last_screen
        self.box = BoxLayout(padding=(Window.width/30, 0))
        # Create scrollview widget
        self.scroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        # Create box layout to house widgets
        self.grid_layout = GridLayout(cols=1, size_hint_y=None, padding=Window.width/30)
        # Make sure the height is such that there is something to scroll.
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))
        # Create grid layout to house images and buttons
        self.grid_layout_img = GridLayout(cols=2, size_hint_y=None, height=Window.height*1.5,
                                          padding=(Window.width/30, 0))
        self.grid_layout_btn = GridLayout(cols=2, padding=(0, Window.height/30), size_hint_y=None,
                                          height=Window.height/7)
        # Create buttons and empty spacing widget
        self.back_button = SwitchButton(text='Back', size_hint_x=0.15)
        self.label = TitleText(text='Examples')
        # Bind screen switching function to button
        self.back_button.bind(on_press=self.back_screen)
        # Create example images and labels
        self.good_im = Image(source='good.png')
        print(self.good_im.size)
        self.unclear_im = Image(source='unclear.png')
        self.bad_im = Image(source='bad.png')
        self.good_lab = TextLabel(text='GOOD:')
        self.unclear_lab = TextLabel(text='UNCLEAR:')
        self.bad_lab = TextLabel(text='BAD:')

        # Add images and labels to grid layout
        self.grid_layout_img.add_widget(self.good_lab)
        self.grid_layout_img.add_widget(self.good_im)
        self.grid_layout_img.add_widget(self.unclear_lab)
        self.grid_layout_img.add_widget(self.unclear_im)
        self.grid_layout_img.add_widget(self.bad_lab)
        self.grid_layout_img.add_widget(self.bad_im)
        # Add button to grid layout
        self.grid_layout_btn.add_widget(self.back_button)
        self.grid_layout_btn.add_widget(self.label)

        # Add grid layouts to box layout
        self.grid_layout.add_widget(self.grid_layout_btn)
        self.grid_layout.add_widget(self.grid_layout_img)
        # Add box layout to screen
        self.scroll.add_widget(self.grid_layout)
        self.box.add_widget(self.scroll)
        self.add_widget(self.box)

    def back_screen(self, *args):
        # Check if user is accessing example screen from anno screen or from tutorial
        if last_screen == 'annotate':
            self.manager.current = 'annotate'
        elif last_screen == 'tutorial':
            self.manager.current = 'tutorial'
        self.manager.transition.direction = 'right'


class AchievementScreen(Screen):
    def __init__(self):
        Screen.__init__(self, name='achievement')
        # Create box layout
        self.box = BoxLayout(padding=Window.width/30)
        # Create grid layouts
        self.grid_layout = GridLayout(cols=1, spacing=(Window.width/20, Window.height/30), size_hint_y=None,
                                      padding=Window.width/50)
        self.grid_layout_btn = GridLayout(cols=2, size_hint_y=None, padding=Window.width/30,
                                          spacing=Window.width/4, height=Window.height/5)
        # Make sure the height is such that there is something to scroll.
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))
        # Create back button
        self.back_button = SwitchButton(text='Back', size_hint_x=0.5)
        self.label = Label(text=username + '\'s Achievements', color=(0, 0, 128, 1), bold=True,
                           font_size=Window.height/15, halign='right')
        # Bind switching function to back button
        self.back_button.bind(on_press=self.back)
        # Create image widgets for achievements
        self.tut_badge = AchievementBadge(trophy_source='trophy.png', title_text='Mastering the Basics',
                                          description='Complete the tutorial', max_progress=1)
        self.anno_badge = AchievementBadge(trophy_source='trophy.png', title_text='Most Dedicated Player',
                                           description='Lifetime number of annotations', max_progress=1)
        self.ranking_badge = AchievementBadge(trophy_source='trophy.png', title_text='Honour Roll',
                                              description='Lifetime average ranking', max_progress=25)
        self.excellent_badge = AchievementBadge(trophy_source='trophy.png', title_text='Admirable Annotator',
                                                description='Lifetime number of \'Excellent\' rankings', max_progress=1)
        self.days_badge = AchievementBadge(trophy_source='trophy.png', title_text='Repeat Offender',
                                           description='How many days you have done at least one annotation',
                                           max_progress=1)
        self.night_badge = AchievementBadge(trophy_source='trophy.png', title_text='Night Owl',
                                            description='Complete an annotation between midnight and 5 a.m.',
                                            max_progress=1)

        # Add buttons to grid layout
        self.grid_layout_btn.add_widget(self.back_button)
        self.grid_layout_btn.add_widget(self.label)
        # Add trophies to grid layout
        self.grid_layout.add_widget(self.grid_layout_btn)
        self.grid_layout.add_widget(self.tut_badge)
        self.grid_layout.add_widget(self.anno_badge)
        self.grid_layout.add_widget(self.ranking_badge)
        self.grid_layout.add_widget(self.excellent_badge)
        self.grid_layout.add_widget(self.days_badge)
        self.grid_layout.add_widget(self.night_badge)

        self.scroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        self.scroll.add_widget(self.grid_layout)
        self.box.add_widget(self.scroll)
        self.add_widget(self.box)

    def back(self, *args):
        """Navigates back to user screen on button push"""
        self.manager.current = 'user'
        self.manager.transition.direction = 'right'


class SettingsScreen(Screen):
    def __init__(self):
        Screen.__init__(self, name='settings')
        global username, line_color, continue_trigger
        # Create layouts
        self.box_layout = BoxLayout(orientation='vertical', padding=(Window.width/30, 0))
        self.top_grid = GridLayout(cols=2, size_hint_y=0.3, padding=Window.width/25, spacing=Window.width/10)
        self.grid_layout = GridLayout(cols=3, spacing=(Window.width/15, Window.height/6), padding=Window.width/30)
        self.change_user_grid = GridLayout(cols=2, spacing=Window.width/4, padding=(Window.width/10, Window.height/5),
                                           size_hint_y=0.5)
        self.change_btn_grid = GridLayout(cols=2, spacing=Window.width/4, padding=Window.height/12,
                                          size_hint_y=0.3)
        # Create label widgets
        self.title = TitleText(text='Settings')
        self.user_label = TextLabel(text='Username: ')
        self.username = TextLabel(text=username)
        self.cont_label = TextLabel(text='Annotations before \n \'Continue\' prompt: ')
        self.cont_num = TextLabel(text=str(continue_trigger))
        # Create button widgets
        self.change_username_button = SwitchButton(text='Change \n Username', size_hint=(0.6, 0.2))
        self.change_cont_button = SwitchButton(text='Change \n Continues', size_hint=(0.6, 0.2))
        self.cancel_button = SwitchButton(text='Cancel', size_hint=(0.6, 0.2))
        self.save_changes_button = SwitchButton(text='Save \n Changes', size_hint=(0.6, 0.2))
        self.back_button = SwitchButton(text='Back', size_hint_x=0.3, size_hint_y=0.9)
        # Create text box widget for changing username
        self.text_box_usr = TextInput(multiline=False, cursor_color=(0, 0, 128, 1), hint_text='Please Enter a Username',
                                      size_hint_y=0.1)
        # Bind functions to buttons
        self.change_username_button.bind(on_press=self.change_username)
        self.change_cont_button.bind(on_press=self.change_continues)
        self.cancel_button.bind(on_press=self.cancel)
        self.back_button.bind(on_press=self.back)
        # Add widgets to grid layout
        self.grid_widgets()
        # Add widgets to top of screen grid layout
        self.top_grid.add_widget(self.back_button)
        self.top_grid.add_widget(self.title)
        # Add widgets to box layout
        self.box_layout.add_widget(self.top_grid)
        self.box_layout.add_widget(self.grid_layout)
        # Add box layout to screen
        self.add_widget(self.box_layout)

    def unbind_all(self, *args):
        self.save_changes_button.unbind(on_press=self.save_username)
        self.save_changes_button.unbind(on_press=self.save_continues())

    def grid_widgets(self):
        """Adds default widgets to grid layout for settings screen"""
        self.grid_layout.add_widget(self.user_label)
        self.grid_layout.add_widget(self.username)
        self.grid_layout.add_widget(self.change_username_button)
        self.grid_layout.add_widget(self.cont_label)
        self.grid_layout.add_widget(self.cont_num)
        self.grid_layout.add_widget(self.change_cont_button)

    def clear_all(self):
        """Clears all widgets from all grid layouts and the box layout"""
        self.grid_layout.clear_widgets()
        self.change_user_grid.clear_widgets()
        self.change_btn_grid.clear_widgets()
        self.box_layout.clear_widgets()

    def back(self, *args):
        """Changes screen back to user profile screen"""
        update_rankings()
        self.clear_all()
        self.grid_widgets()
        self.top_grid.padding = Window.width/20
        self.box_layout.add_widget(self.top_grid)
        self.box_layout.add_widget(self.grid_layout)
        self.manager.current = 'user'
        self.manager.transition.direction = 'right'

    def cancel(self, *args):
        """Allows user to cancel choosing their new username"""
        self.clear_all()
        self.grid_widgets()
        self.top_grid.padding = Window.width/25
        self.box_layout.add_widget(self.top_grid)
        self.box_layout.add_widget(self.grid_layout)

    def change_username(self, *args):
        """Allows user to change their username"""
        # Remove old menu screen username label
        self.text_box_usr.text = ''
        self.clear_all()
        self.top_grid.padding = Window.width/20
        self.unbind_all()
        self.save_changes_button.bind(on_press=self.save_username)
        # Add cancel button to layout
        self.change_user_grid.add_widget(self.user_label)
        self.change_user_grid.add_widget(self.text_box_usr)
        self.change_btn_grid.add_widget(self.cancel_button)
        self.change_btn_grid.add_widget(self.save_changes_button)
        self.box_layout.add_widget(self.top_grid)
        self.box_layout.add_widget(self.change_user_grid)
        self.box_layout.add_widget(self.change_btn_grid)

    def save_username(self, *args):
        """Saves new username in csv and changes appropriate widgets"""
        global username, menu, anno, user
        # Get username typed by user
        if self.text_box_usr.text != '':
            username = self.text_box_usr.text
            # Remove text box
            self.clear_all()
            self.top_grid.padding = Window.width / 25
            self.grid_widgets()
            self.box_layout.add_widget(self.top_grid)
            self.box_layout.add_widget(self.grid_layout)
            # Add in label with new username
            self.username.text = username
            # Change username in end screen
            anno.end_label_1.text = 'Congratulations ' + username + '!'

            # Reset welcome label on menu screen with new username
            menu.welcome_label.text = 'Welcome ' + username +'!'
            # Write new username in user_scores.csv file
            with open('user_score.csv', mode='a', newline='') as score_data:
                writer = csv.writer(score_data)
                writer.writerow(['', user_id, '', '', '', username])
        else:
            return

    def change_continues(self, *args):
        """Allows user to change their username"""
        # Remove old menu screen username label
        self.text_box_usr.text = ''
        self.clear_all()
        self.top_grid.padding = Window.width / 20
        self.unbind_all()
        self.save_changes_button.bind(on_press=self.save_continues)
        # Add cancel button to layout
        self.change_user_grid.add_widget(self.cont_label)
        self.change_user_grid.add_widget(self.text_box_usr)
        self.text_box_usr.hint_text = 'Please enter a number'
        self.change_btn_grid.add_widget(self.cancel_button)
        self.change_btn_grid.add_widget(self.save_changes_button)
        self.box_layout.add_widget(self.top_grid)
        self.box_layout.add_widget(self.change_user_grid)
        self.box_layout.add_widget(self.change_btn_grid)

    def save_continues(self, *args):
        global continue_trigger
        if self.text_box_usr.text.isdigit():
            continue_trigger = self.text_box_usr.text
            # Remove text box
            self.clear_all()
            self.top_grid.padding = Window.width / 25
            self.grid_widgets()
            self.box_layout.add_widget(self.top_grid)
            self.box_layout.add_widget(self.grid_layout)
            # Add in label with new username
            self.cont_num.text = str(continue_trigger)
        else:
            return


class LeaderboardScreen(Screen):
    def __init__(self):
        Screen.__init__(self, name='leaderboard')
        # Create box layout
        self.box = BoxLayout(padding=Window.width / 30)
        # Create grid layouts
        self.grid_layout = GridLayout(cols=1, spacing=(Window.width / 20, Window.height / 30), size_hint_y=None,
                                      padding=Window.width / 50)
        self.grid_layout_btn = GridLayout(cols=2, size_hint_y=None, padding=Window.width / 30,
                                          spacing=Window.width / 4, height=Window.height / 5)
        # Make sure the height is such that there is something to scroll.
        self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))
        # Create back button
        self.back_button = SwitchButton(text='Back', size_hint_x=0.5)
        self.label = Label(text='Leaderboard', color=(0, 0, 128, 1), bold=True,
                           font_size=Window.height / 15, halign='right')
        # Bind switching function to back button
        self.back_button.bind(on_press=self.back)
        # Add buttons to grid layout
        self.grid_layout_btn.add_widget(self.back_button)
        self.grid_layout_btn.add_widget(self.label)
        # Add trophies to grid layout
        self.grid_layout.add_widget(self.grid_layout_btn)


        self.scroll = ScrollView(size_hint=(1, None), size=(Window.width, Window.height))
        self.scroll.add_widget(self.grid_layout)
        self.box.add_widget(self.scroll)
        self.add_widget(self.box)

    def back(self, *args):
        """Navigates back to user screen on button push"""
        self.manager.current = 'user'
        self.manager.transition.direction = 'right'


def calculate_dist(x1, y1, x2, y2):
    """Determine the direction and magnitude of the dragging of the image"""
    dx = x2 - x1
    dy = y2 - y1
    dist = sqrt((dx * dx) + (dy * dy))
    min_dist = sqrt((Window.height / 5) ** 2 + (Window.width / 5) ** 2)
    return min_dist, dist, dx, dy


def line_dist(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    dist = sqrt(dx * dx + dy * dy)
    o = []

    for i in range(1, int(dist)):
        lastx = x1 + dx * (i / dist)
        lasty = y1 + dy * (i / dist)
        o.extend([lastx, lasty])
    return o


def update_rankings():
    """Updates username, total annotations, average ranking, and other user stats by reading csv file"""
    global user, username, total_ranking, total_annos, avg_ranking, tutorial_check, total_exc, date_tracker, settings
    # Set username
    user.usr.text = username
    settings.username.text = username
    achievement.label.text = username + '\'s Achievements'
    cont.label_1.text = 'Keep it up ' + username + '!'
    with open('user_score.csv', mode='r') as score_data:
        reader = csv.reader(score_data)
        for row in reader:
            # Adds most recent scores to score dictionary from csv file
            score_dict[row[2]] = (row[3], row[4])
            # Adds dates to date dictionary
            date_tracker[row[0]] = 1
            if row[0] == 'tutorial':
                tutorial_check = True
    try:
        # Delete empty row containing user name from score dictionary
        del score_dict['']
        # Delete empty row containing username and tutorial completion from date dictionary
        del date_tracker[''], date_tracker['tutorial']
    except KeyError:
        return
    # Get user's total amount of annotations completed
    total_annos = len(score_dict)
    print(total_annos)
    # Get user's total ranking (compared to machine learning score for signal)
    total_ranking = 0
    total_exc = 0
    # Store how many 'excellent' rankings the user has received
    for key in score_dict:
        total_ranking = total_ranking + float(score_dict[key][1])
        if float(score_dict[key][1]) <= 0.1:
            total_exc += 1

    # Update total annotations label
    user.tot.text = str(total_annos)
    try:
        # Calculate user's lifetime ranking (compared to machine learning score for signal)
        avg_ranking = 100 - int((total_ranking / total_annos) * 100)
    except ZeroDivisionError:
        return
    # Update user ranking label
    user.rnk.text = str(avg_ranking) + '%'


def update_other_achievement():
    """Updates trophy and progess bar for non-standard achievements"""
    global tutorial_check, avg_ranking, achievement
    # User has completed tutorial achievement
    if tutorial_check:
        achievement.tut_badge.trophy.source = 'tut_compl.png'
        achievement.tut_badge.progress.max = 1
        achievement.tut_badge.progress.value = 1

    # Average ranking achievement
    if avg_ranking >= 90:
        achievement.ranking_badge.trophy.source = 'ranking_90.png'
        achievement.ranking_badge.progress.max = 90
    elif avg_ranking >= 75:
        achievement.ranking_badge.trophy.source = 'ranking_75.png'
        achievement.ranking_badge.progress.max = 90
    elif avg_ranking >= 50:
        achievement.ranking_badge.trophy.source = 'ranking_50.png'
        achievement.ranking_badge.progress.max = 75
    elif avg_ranking >= 25:
        achievement.ranking_badge.trophy.source = 'ranking_25.png'
        achievement.ranking_badge.progress.max = 50
    achievement.ranking_badge.progress.value = avg_ranking


def update_std_achievements(var, badge):
    """Updates trophy and progress bar for achievements following the '1, 10, 25, 50' format"""
    # Total number of lifetime annotations achievement
    if var >= 50:
        badge.trophy.source = 'trophy_50.png'
        badge.progress.max = 50
    elif var >= 25:
        badge.trophy.source = 'trophy_25.png'
        badge.progress.max = 50
    elif var >= 10:
        badge.trophy.source = 'trophy_10.png'
        badge.progress.max = 25
    elif var >= 1:
        badge.trophy.source = 'trophy_1.png'
        badge.progress.max = 10
    # Update progress bar
    badge.progress.value = var


# Create app class
class ScorePicturesApp(App):
    def build(self):
        global screen_manager
        self.title = 'anno5i9 v0.1'
        screen_manager = ScreenManage()
        return screen_manager

    def on_pause(self):
        """Pauses app when switching between apps"""
        return True

    def on_resume(self):
        """Resume app when switching from another app"""
        return True


# Run app
if __name__ == '__main__':
    ScorePicturesApp().run()
