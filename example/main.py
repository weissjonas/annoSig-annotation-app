from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.widget import WidgetException
from kivy.graphics import Color, Point, GraphicException
from kivy.clock import Clock
from kivy.utils import platform

from glob import glob
import os
from os.path import join, dirname
from pathlib import Path
from random import randint
import csv
from math import sqrt
import ntpath
import datetime
from functools import partial
import re


# Store user_id and username in global variable
user_id = None
username = ''
# Create global variables to access screens
user = None
menu = None
anno = None
cont = None
settings = None
screen_manager = None
tutorial = None
tutorialend = None
achievement = None
start = None
inst1 = None
inst2 = None
inst3 = None
example = None
leaderboard = None
end = None
# Create global variable to track user during tutorial
image = None
# Create global variable to store info for swipe overlay
lines = None
line_color = [0, 0, 255, 0.01]
# Store how many annotations completed by user
total_annos = 0
total_counter = 0
total_exc = 0
# Store lifetime ranking of user
avg_ranking = 0
# Create dictionary to track which days user does annotations
date_tracker = {}
time_check = False
# Create dictionary to store scores
score_dict = {}
# Check if user has completed the tutorial
tutorial_check = False
# Check if user has annotated all available signals
is_finished = False
# Keep track of last screen
last_screen = None
# Number of signals to annotate before triggering continue screen
continue_trigger = 10
# Store directory name in a variable
curdir = dirname(__file__)

# Move screen when user acivates virtual keyboard on mobile
Window.softinput_mode = 'pan'


class AchievementBadge(GridLayout):
    def __init__(self, trophy_source, title_text, description, max_progress):
        GridLayout.__init__(self)
        self.ids.trophy.source = trophy_source
        self.ids.title.text = title_text
        self.ids.desc.text = description
        self.ids.pb.max = max_progress


class LeaderGrid(GridLayout):
    def __init__(self, usr, score, ranking, display):
        GridLayout.__init__(self, cols=5, size_hint_y=None, height=Window.height/3)


# Buttons to switch between screens
class SwitchButton(Button):
    pass


# Text used for titles
class TitleText(Label):
    pass


# Text featured in instruction screen
class TextLabel(Label):
    pass


# Create Screen Manager to house different screens within the app
class ScreenManage(ScreenManager):
    def __init__(self):
        ScreenManager.__init__(self)
        global user, menu, anno, cont, tutorial, achievement, settings, start, inst1, inst2, inst3, tutorialend, \
            example, leaderboard, end

        end = EndScreen()
        start = StartScreen()
        anno = AnnotateScreen()
        menu = MenuScreen()
        inst1 = InstructionScreen1()
        inst2 = InstructionScreen2()
        inst3 = InstructionScreen3()
        tutorial = TutorialScreen()
        tutorialend = TutorialEndScreen()
        example = ExampleScreen()
        user = UserScreen()
        cont = ContScreen()
        achievement = AchievementScreen()
        settings = SettingsScreen()
        leaderboard = LeaderboardScreen()


        # Check if it is user's first time using app
        self.empty = True
        csvdir = App.get_running_app().csvdir
        with open(os.path.join(csvdir, 'user_score.csv'), mode='r') as score_data:
            reader = csv.reader(score_data)
            for row in reader:
                if row != '':
                    self.empty = False
        if self.empty == True:
            self.add_widget(start)

        # Add screens to screen manager
        self.add_widget(menu)
        self.add_widget(end)
        self.add_widget(anno)
        self.add_widget(inst1)
        self.add_widget(inst2)
        self.add_widget(inst3)
        self.add_widget(tutorial)
        self.add_widget(tutorialend)
        self.add_widget(example)
        self.add_widget(user)
        self.add_widget(cont)
        self.add_widget(achievement)
        self.add_widget(settings)
        self.add_widget(leaderboard)


def dict_from_class(cls):
    return dict(
        (key, value) for (key, value) in cls.__dict__.items()
        )


class StartScreen(Screen):
    def menu_screen(self, *args):
        """Switch to menu screen on button press and writes user data to user_score.csv"""
        global username, user_id, menu
        # Set username to text entered by user
        username = self.ids.textinput.text
        # Make sure user enters a username
        if username != '':
            # Switch to menu screen
            self.manager.current = 'menu'
            self.manager.transition.direction = 'left'
            # Create user id for tracking stats
            user_id = randint(0, 99999) # When database is deployed add in check to ensure no ids are the same
            # Display welcome message after first launch
            menu.ids.welcome_label.text = 'Welcome ' + username + '!'
            # Write username to csv file
            csvdir = App.get_running_app().csvdir
            with open(os.path.join(csvdir, 'user_score.csv'), mode='a', newline='') as score_data:
                writer = csv.writer(score_data)
                writer.writerow(['', user_id, '', '', '', username])
        else:
            return


class UserScreen(Screen):
    def settings_screen(self):
        self.manager.current = 'settings'
        self.manager.transition.direction = 'left'
        settings.clear_all()
        settings.ids.box.add_widget(settings.ids.top_grid)
        settings.ids.box.add_widget(settings.ids.grid)
        settings.grid_widgets()


class MenuScreen(Screen):
    def __init__(self):
        global username
        self.username = username
        Screen.__init__(self)

    def anno_screen(self, *args):
        """Change screen to annotation game"""
        global last_screen, anno
        if is_finished:
            self.manager.current = 'end'
            self.manager.transition.direction = 'left'
        else:
            self.manager.current = 'annotate'
            self.manager.transition.direction = 'left'
            last_screen = 'annotate'

    def inst_screen(self, *args):
        """Change screen to instruction screen"""
        global last_screen
        self.manager.current = 'inst1'
        self.manager.transition.direction = 'left'
        last_screen = 'tutorial'
        tutorial.ids.grid.remove_widget(tutorial.ids.next_button)
        tutorial.ids.float.remove_widget(tutorial.ids.image)

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
    # Set screen background to white
    Window.clearcolor = (1, 1, 1, 1)

    def __init__(self):
        Screen.__init__(self)
        global user_id, username, total_counter, score_dict, continue_trigger, is_finished
        # Initialize counter to track how many pictures are done in each grouping
        self.counter = 0
        # Create variable to store current date
        self.date = datetime.datetime.now()
        # Create list to house pictures
        self.pictures = []
        # Create variable to store machine score of signals
        self.machine_score = float()
        # Add all pictures in the 'Images' folder to the pictures list
        for filename in glob(join(curdir, 'images', '*')):
            self.pictures.append(filename)
        # Remove any pictures that have already been annotated
        csvdir = App.get_running_app().csvdir
        with open(os.path.join(csvdir, 'user_score.csv'), mode='r') as score_data:
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
        self.ids.pb.max = self.prog_max
        # Set initial progress of progress bar
        self.ids.pb.value = self.prog_max - len(self.pictures) - 1
        # Check if there are still pictures left to annotate
        if len(self.pictures) != 0:
            # The first image is updated with the first element in the list
            self.current = self.pictures.pop(0)
            self.prev_pictures = []
            self.ids.display.source = self.current
        # Display message if they have finished
        else:
            is_finished = True

    def end_screen(self, *args):
        """Display end screen when there are no variables left to annotate"""
        global end, username
        self.manager.current = 'end'
        self.manager.transition.direction = 'left'
        end.ids.label.text = 'Congratulations ' + username + '!'

    def on_touch_down(self, touch):
        """Record the initial coordinates of the user touch"""
        super(AnnotateScreen, self).on_touch_down(touch)
        global lines, line_color
        self.coord = [touch.x, touch.y]
        try:
            # Reset maching score ranking
            self.ids.ranking.text = ''
        # Prevent error when click on end screen
        except AttributeError:
            return True
        # Draw swipe line on canvas
        with self.ids.display.canvas:
            # Set color
            Color(*line_color)
            # Set line coordinates and size
            line = Point(points=(touch.x, touch.y), pointsize=Window.height/30, group='g')
            # Store points in lines variable
            lines = line.points
            # Remove drawing after 0.3 s
            Clock.schedule_once(partial(self.remove_point, group='g'), 0.3)
            self.groups = ['g']
        touch.grab(self)
        return True

    def remove_point(self, *args, **kwargs):
        """Removes drawing group from canvas"""
        group = kwargs['group']
        self.ids.display.canvas.remove_group(group)

    def on_touch_move(self, touch):
        """ Update the user score of the signal in real time as their touch is moving"""
        super(AnnotateScreen, self).on_touch_move(touch)
        global lines, line_color
        while True:
            # Store old coordinates
            oldx, oldy = lines[-2], lines[-1]
            break
        # Calculate where to draw new points
        points = line_dist(oldx, oldy, touch.x, touch.y)

        if points:
            try:
                for idx in range(0, len(points), 2):
                    # Assign each point its own group name
                    group = randint(0, 999999)
                    with self.ids.display.canvas:
                        # Set point color
                        Color(*line_color)
                        # Draw new points
                        Point(points=(points[idx], points[idx+1]), pointsize=Window.height/30, group=str(group))
                    # Store new points in lines variable
                    lines.append(points[idx])
                    lines.append(points[idx + 1])
                    # Remove new points after scheduled time
                    Clock.schedule_once(partial(self.remove_point, group=str(group)), 0.3)
                    # Store group name of each point
                    self.groups.append(str(group))
            except GraphicException:
                pass
        try:
            # Update score label
            self.update_label(touch)
        # Avoid app crashing from user touch on end screen
        except AttributeError:
            return

    def on_touch_up(self, touch):
        """Calculate the user score based on the direction of their touch and ensure the movement was big enough"""
        super(AnnotateScreen, self).on_touch_up(touch)
        global lines

        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        # Remove all points
        for group in self.groups:
            self.ids.display.canvas.remove_group(group)
        try:
            # Add coordinates of end of touch motion
            self.coord.append(touch.x)
            self.coord.append(touch.y)
            # Calculate distance of swipe
            min_dist, dist, dx, dy = calculate_dist(*self.coord)
            # Calculate score of swipe
            self.score_val = touch.y / Window.height
            # Check if drag movement is big enough
            if dist > min_dist and dx > Window.width / 10:
                self.prev_pictures.append(self.current)
                # Assign ranking based on comparison to machine learning score
                self.ranking = abs(self.score_val - float(self.machine_score))
                if self.ranking < 0.1:
                    self.ids.ranking.text = 'Excellent!'
                elif self.ranking < 0.2:
                    self.ids.ranking.text = 'Very Good!'
                elif self.ranking < 0.3:
                    self.ids.ranking.text = 'Good!'
                elif self.ranking < 0.4:
                    self.ids.ranking.text = 'OK!'
                elif self.ranking < 0.5:
                    self.ids.ranking.text = 'Not Quite!'

                # Assign score based on drag direction
                self.change_image(score=self.score_val)

            # Recenter display picture if drag is too small
            else:
                self.ids.display.center = self.center
                self.ids.ranking.text = 'Try Again'
        # Prevent crashing from user touches on end screen
        except (AttributeError, TypeError):
            return

    def change_image(self, score=None):
        """Change the displayed image and write the filename and score to score.csv"""
        global total_counter, continue_trigger
        try:
            # Write picture name and score to csv
            csvdir = App.get_running_app().csvdir
            with open(os.path.join(csvdir, 'user_score.csv'), mode='a', newline='') as score_data:
                writer = csv.writer(score_data)
                writer.writerow([self.date.strftime("%d-%m-%Y %H.%M"), user_id, ntpath.basename(self.current), score,
                                 self.ranking, ''])
            # Find score assigned by machine learner
            with open(join(curdir, 'csv', 'machine_score.csv'), mode='r') as machine:
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
        # If no pictures left call end screen
        if len(self.pictures) == 0:
            self.end_screen()
        # Ask user if they want to continue annotating after a certain amount of pictures
        elif self.counter >= continue_trigger - 1:
            # Move to next picture
            self.current = self.pictures.pop(0)
            self.ids.display.center = self.center
            self.ids.display.source = self.current
            # Reset score
            self.ids.score.text = ''
            # Increase counters
            self.counter = self.counter + 1
            total_counter = total_counter + 1
            # Update progress bar
            self.ids.pb.value = self.prog_max - len(self.pictures) - 1
            self.cont_screen()
        else:
            # Move to next picture
            self.current = self.pictures.pop(0)
            self.ids.display.center = self.center
            self.ids.display.source = self.current
            # Reset score
            self.ids.score.text = ''
            # Increase counters
            self.counter = self.counter + 1
            total_counter = total_counter + 1
            # Update progress bar
            self.ids.pb.value = self.prog_max - len(self.pictures) - 1

    def update_label(self, touch):
        """Changes the users score and color of the score for the signal in real time"""
        score = int((touch.y / Window.height) * 100)
        self.ids.score.text = str(score)
        if score > 75:
            self.ids.score.color = (0, 150, 0, 1)
        elif score > 50:
            self.ids.score.color = (0, 50, 0, 1)
        elif score > 25:
            self.ids.score.color = (5, 50, 0, 1)
        elif score > 0:
            self.ids.score.color = (50, 0, 0, 1)

    def skip(self, *args):
        """Skip to the next picture to annotate"""
        global continue_trigger
        # Check if user is on the last picture
        if len(self.pictures) > 0:
            # Record the current picture
            self.prev_pictures.append(self.current)
            # Skip to the next picture
            self.current = self.pictures.pop(0)
            self.ids.display.source = self.current
            # Increment the progress bar
            self.ids.pb.value = self.ids.pb.value + 1
            # Increment the counter
            # Switch to continue screen
            if self.counter >= continue_trigger - 1:
                # Move to next picture
                self.current = self.pictures.pop(0)
                self.ids.display.center = self.center
                self.ids.display.source = self.current
                # Reset score
                self.ids.score.text = ''
                # Increase counters
                self.counter = self.counter + 1
                # Update progress bar
                self.ids.pb.value = self.prog_max - len(self.pictures) - 1
                self.cont_screen()
            elif self.counter <= continue_trigger - 1:
                self.counter = self.counter + 1

    def undo(self, *args):
        """Go back to the previous picture to annotate and update progress bar and counters"""
        global total_counter
        try:
            # Check if user is on the last picture
            if len(self.pictures) > 0:
                self.save_current = self.current
                # Insert previous picture in the pictures list
                self.pictures.insert(0, self.prev_pictures.pop(-1))
                # Decrease the progress bar
                self.ids.pb.value = self.ids.pb.value - 1
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
                self.ids.display.source = self.current
                self.pictures.insert(0, self.save_current)

        except IndexError:
            return

    def cont_screen(self, *args):
        """Switch to continue screen and update username in label on continue screen"""
        global cont, total_counter, total_annos, username
        update_rankings()

        cont.ids.label_1.text = 'Keep it up ' + username + '!'
        cont.ids.session_annos.text = str(total_counter)
        cont.ids.tot_annos.text = str(total_annos)
        self.manager.current = 'cont'
        self.manager.transition.direction = 'left'


class ContScreen(Screen):
    global anno
    def cont_anno(self, *args):

        if len(anno.pictures) == 0:
            anno.end_screen()

        else:
            self.manager.current = 'annotate'
            self.manager.transition.direction = 'left'
            anno.ids.display.center = Window.center
            anno.counter = 0

    def menu_screen(self, *args):
        anno.counter = 0
        self.manager.current = 'menu'
        self.manager.transition.direction = 'right'


class InstructionScreen1(Screen):
    pass


class InstructionScreen2(Screen):
    pass

class InstructionScreen3(Screen):
    pass

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

        # Add all pictures in tutorial folder to list
        for filename in glob(join(curdir, 'tutorial', '*')):
            self.pictures.append(filename)
        print(self.pictures)
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

        self.ids.display.source = self.current
        self.ids.pb.value = self.counter

    # Record initial down click coordinates
    def on_touch_down(self, touch):
        """Record the initial coordinates of the user touch"""
        super(TutorialScreen, self).on_touch_down(touch)
        global lines
        self.coord = [touch.x, touch.y]

        try:
            self.ids.ranking.text = ''
        # Prevent error when click on end screen
        except AttributeError:
            return True

        with self.ids.display.canvas:

            Color(*line_color)
            line = Point(points=(touch.x, touch.y), pointsize=Window.height / 30, group='g')
            lines = line.points
            Clock.schedule_once(partial(self.remove_point, group='g'), 0.3)
            self.groups = ['g']

        touch.grab(self)
        return True

    def remove_point(self, *args, **kwargs):
        group = kwargs['group']
        self.ids.display.canvas.remove_group(group)

    def on_touch_move(self, touch):
        """ Update the user score of the signal in real time as their touch is moving"""
        super(TutorialScreen, self).on_touch_move(touch)
        global lines

        while True:
            oldx, oldy = lines[-2], lines[-1]
            break
        points = line_dist(oldx, oldy, touch.x, touch.y)

        if points:
            try:
                for idx in range(0, len(points), 2):
                    group = randint(0, 999999)
                    with self.ids.display.canvas:
                        Color(*line_color)
                        Point(points=(points[idx], points[idx + 1]), pointsize=Window.height / 30, group=str(group))

                    lines.append(points[idx])
                    lines.append(points[idx + 1])

                    Clock.schedule_once(partial(self.remove_point, group=str(group)), 0.3)
                    self.groups.append(str(group))

            except GraphicException:
                pass

        try:
            self.update_label(touch)

        # Avoid app crashing from user touch on end screen
        except AttributeError:
            return

    def on_touch_up(self, touch):
        """Calculate the user score based on the direction of their touch and ensure the movement was big enough"""
        super(TutorialScreen, self).on_touch_up(touch)
        global lines

        if touch.grab_current is not self:
            return
        touch.ungrab(self)

        for group in self.groups:
            self.ids.display.canvas.remove_group(group)

        try:
            self.coord.append(touch.x)
            self.coord.append(touch.y)
            min_dist, dist, dx, dy = calculate_dist(*self.coord)
            self.score_val = touch.y / Window.height

            with open(join(curdir, 'csv','tutorial_score.csv'), mode='r') as machine:
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
                    self.ids.ranking.text = 'Excellent!'
                elif self.ranking < 0.2:
                    self.ids.ranking.text = 'Very Good!'
                elif self.ranking < 0.3:
                    self.ids.ranking.text = 'Good!'
                elif self.ranking < 0.4:
                    self.ids.ranking.text = 'OK!'
                elif self.ranking < 0.5:
                    self.ids.ranking.text = 'Not Quite!'

                try:
                    self.prev_pictures.append(self.current)
                    self.ids.float.remove_widget(self.ids.display)
                    self.ids.label.text = ''
                    self.ids.float.add_widget(self.ids.image, index=2)
                    self.next()
                    self.soln_current = self.solutions.pop(0)
                    self.ids.image.source = self.soln_current
                    self.ids.grid.remove_widget(self.ids.empty)
                    self.ids.grid.add_widget(self.ids.next_button)
                    self.counter = self.counter + 1
                    self.ids.pb.value = self.counter

                # Prevent crashing from drag on solution screen
                except (WidgetException, IndexError):
                    return

            # Recenter display picture if drag is too small
            else:
                self.ids.display.center = self.center
                if dist < 5:
                    self.ids.ranking.text = ''
                else:
                    self.ids.ranking.text = 'Try Again'
        # Prevent crashing from user touches on end screen
        except (AttributeError, TypeError):
            return

    def update_label(self, touch):
        """Changes the users score and color of the score for the signal in real time"""
        score = int((touch.y / Window.height) * 100)
        self.ids.score.text = str(score)
        if score > 75:
            self.ids.score.color = (0,150,0,1)
        elif score > 50:
            self.ids.score.color = (0, 50, 0, 1)
        elif score > 25:
            self.ids.score.color = (5, 50, 0, 1)
        elif score > 0:
            self.ids.score.color = (50, 0, 0, 1)


    def skip(self, *args):
        """Skips to the next picture to annotate"""
        # Check if user is on the last picture
        if len(self.solutions) > 0:
            # Check if on a solution picture
            if self.tracker == 'soln':
                # Remove solution picture
                self.ids.float.remove_widget(self.ids.image)
                # Add last solution to previous solutions list
                self.prev_soln.append(self.soln_current)
                # Add new signal picture to screen
                self.current = self.pictures.pop(0)
                self.ids.display.source = self.current
                self.ids.float.add_widget(self.ids.display, index=2)
                # Remove 'next' button
                self.ids.grid.add_widget(self.ids.empty)
                self.ids.grid.remove_widget(self.ids.next_button)
                self.ids.label.text = 'Try annotating this signal!'
                # Update tracker to indicate on a signal picture
                self.tracker = 'signal'
            # Check if currently on a signal picture
            elif self.tracker == 'signal':
                # Remove signal picture
                self.ids.float.remove_widget(self.ids.display)
                self.ids.label.text = ''
                # Add solution picture
                self.ids.float.add_widget(self.ids.image, index=2)
                # Add previous signal to previous pictures list
                self.prev_pictures.append(self.current)
                self.soln_current = self.solutions.pop(0)
                self.ids.image.source = self.soln_current
                # Add 'next' button to screen
                self.ids.grid.remove_widget(self.ids.empty)
                self.ids.grid.add_widget(self.ids.next_button)
                # Update tracker to show currently on a solution picture
                self.tracker = 'soln'
            # Update counter and progress bar
            self.counter = self.counter + 1
            self.ids.pb.value = self.counter

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
                    self.ids.float.remove_widget(self.ids.image)
                    # Add the new signal picture
                    self.current = self.pictures.pop(0)
                    self.ids.display.source = self.current
                    self.ids.float.add_widget(self.ids.display, index=2)
                    # Remove the 'next button'
                    self.ids.grid.add_widget(self.ids.empty)
                    self.ids.grid.remove_widget(self.ids.next_button)
                    self.ids.label.text = 'Try annotating this signal!'
                    # Make sure counter does not go negative
                    if self.counter > 0:
                        self.counter = self.counter - 1
                    else:
                        self.counter = 0
                    # Update progress bar
                    self.ids.pb.value = self.counter
                    # Change tracker to indicate it is now on a signal picture
                    self.tracker = 'signal'
                # Check if screen is on a 'signal' picture
                elif self.tracker == 'signal':
                    # Insert previous picture in the pictures list
                    self.solutions.insert(0, self.prev_soln.pop(-1))
                    self.pictures.insert(0, self.current)
                    # Remove the signal picture
                    self.ids.float.remove_widget(self.ids.display)
                    self.ids.label.text = ''
                    # Add the solution picture
                    self.ids.float.add_widget(self.ids.image, index=2)
                    self.soln_current = self.solutions.pop(0)
                    self.ids.image.source = self.soln_current
                    # Add the next button
                    self.ids.grid.remove_widget(self.ids.empty)
                    self.ids.grid.add_widget(self.ids.next_button)
                    # Make sure counter does not go negative
                    if self.counter > 0:
                        self.counter = self.counter - 1
                    else:
                        self.counter = 0
                    # Update the progress bar
                    self.ids.pb.value = self.counter
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
            csvdir = App.get_running_app().csvdir
            with open(os.path.join(csvdir, 'user_score.csv'), mode='r+', newline='') as score_data:
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
            self.ids.float.remove_widget(self.ids.image)
            # Add signal picture
            self.current = self.pictures.pop(0)
            self.ids.display.source = self.current
            self.ids.float.add_widget(self.ids.display, index=2)
            # Remove next button
            self.ids.grid.add_widget(self.ids.empty)
            self.ids.grid.remove_widget(self.ids.next_button)
            self.ids.label.text = 'Try annotating this signal!'
            # Update counter
            self.counter = self.counter + 1
            # Update progress bar
            self.ids.pb.value = self.counter
            # Update tracker to indicate on signal picture
            self.tracker = 'signal'


class TutorialEndScreen(Screen):
    pass


class ExampleScreen(Screen):
    global last_screen, anno

    def back_screen(self, *args):
        # Check if user is accessing example screen from anno screen or from tutorial
        if last_screen == 'annotate':
            self.manager.current = 'annotate'
            anno.ids.display.center = Window.center
        elif last_screen == 'tutorial':
            self.manager.current = 'tutorial'
        self.manager.transition.direction = 'right'


class AchievementScreen(Screen):
    def __init__(self):
        global username
        Screen.__init__(self)
        self.username = username
        # Create image widgets for achievements
        self.tut_badge = AchievementBadge(trophy_source='pictures/trophy.png', title_text='Mastering the Basics',
                                          description='Complete the tutorial', max_progress=1)
        self.anno_badge = AchievementBadge(trophy_source='pictures/trophy.png', title_text='Most Dedicated Player',
                                           description='Lifetime number of annotations', max_progress=1)
        self.ranking_badge = AchievementBadge(trophy_source='pictures/trophy.png', title_text='Honour Roll',
                                              description='Lifetime average ranking', max_progress=25)
        self.excellent_badge = AchievementBadge(trophy_source='pictures/trophy.png', title_text='Admirable Annotator',
                                                description='Lifetime number of \'Excellent\' rankings', max_progress=1)
        self.days_badge = AchievementBadge(trophy_source='pictures/trophy.png', title_text='Repeat Offender',
                                           description='How many days you have annotated',
                                           max_progress=1)
        self.night_badge = AchievementBadge(trophy_source='pictures/trophy.png', title_text='Night Owl',
                                            description='Annotate between midnight and 5 a.m.',
                                            max_progress=1)

        # Add trophies to grid layout
        self.ids.grid.add_widget(self.tut_badge)
        self.ids.grid.add_widget(self.anno_badge)
        self.ids.grid.add_widget(self.ranking_badge)
        self.ids.grid.add_widget(self.excellent_badge)
        self.ids.grid.add_widget(self.days_badge)
        self.ids.grid.add_widget(self.night_badge)


class SettingsScreen(Screen):
    def __init__(self):
        Screen.__init__(self)
        global username, continue_trigger

    def unbind_all(self, *args):
        # Unbind button functions
        self.ids.save_changes_button.unbind(on_press=self.save_username)
        self.ids.save_changes_button.unbind(on_press=self.save_continues)

    def grid_widgets(self):
        """Adds default widgets to grid layout for settings screen"""
        # Add username label
        self.ids.grid.add_widget(self.ids.user_label)
        # Add username
        self.ids.grid.add_widget(self.ids.user)
        # Add change username button
        self.ids.grid.add_widget(self.ids.change_username_button)
        # Add continue label
        self.ids.grid.add_widget(self.ids.cont_label)
        # Add continue number
        self.ids.grid.add_widget(self.ids.cont_num)
        # Add change continue number button
        self.ids.grid.add_widget(self.ids.change_cont_button)

    def clear_all(self):
        """Clears all widgets from all grid layouts and the box layout"""
        self.ids.grid.clear_widgets()
        self.ids.change_user_grid.clear_widgets()
        self.ids.change_btn_grid.clear_widgets()
        self.ids.box.clear_widgets()

    def back(self, *args):
        """Changes screen back to user profile screen"""
        # Update user rankings
        update_rankings()
        # Clear all widgets from the grid
        self.clear_all()
        # Add default widgets back to the grid
        self.grid_widgets()
        self.ids.top_grid.padding = Window.width/20
        self.ids.box.add_widget(self.ids.top_grid)
        self.ids.box.add_widget(self.ids.grid)
        # Switch screen back to user screen
        self.manager.current = 'user'
        self.manager.transition.direction = 'right'

    def cancel(self, *args):
        """Allows user to cancel choosing their new username"""
        # Clear all widgets
        self.clear_all()
        # Add default widgets back to the grid
        self.grid_widgets()
        self.ids.top_grid.padding = Window.width/25
        self.ids.box.add_widget(self.ids.top_grid)
        self.ids.box.add_widget(self.ids.grid)

    def change_username(self, *args):
        """Allows user to change their username"""
        # Reset text box text
        self.ids.textinput.text = ''
        # Remove all widgets
        self.clear_all()
        self.ids.top_grid.padding = Window.width/20
        # Unbind button
        self.unbind_all()
        # Bind save username function to button
        self.ids.save_changes_button.bind(on_press=self.save_username)
        # Add username label
        self.ids.change_user_grid.add_widget(self.ids.user_label)
        # Add textbox
        self.ids.change_user_grid.add_widget(self.ids.textinput)
        # Add cancel button
        self.ids.change_btn_grid.add_widget(self.ids.cancel_button)
        # Add save changes button
        self.ids.change_btn_grid.add_widget(self.ids.save_changes_button)
        # Add widgets to screen
        self.ids.box.add_widget(self.ids.top_grid)
        self.ids.box.add_widget(self.ids.change_user_grid)
        self.ids.box.add_widget(self.ids.change_btn_grid)

    def save_username(self, *args):
        """Saves new username in csv and changes appropriate widgets"""
        global username, menu, anno, user
        # Get username typed by user
        if self.ids.textinput.text != '':
            # Save text user entered as username
            username = self.ids.textinput.text
            # Remove all widgets
            self.clear_all()
            self.ids.top_grid.padding = Window.width / 25
            # Add default widgets
            self.grid_widgets()
            self.ids.box.add_widget(self.ids.top_grid)
            self.ids.box.add_widget(self.ids.grid)
            # Add in label with new username
            self.ids.user.text = username
            # Change username in end screen
            end.ids.label.text = 'Congratulations ' + username + '!'
            # Reset welcome label on menu screen with new username
            menu.ids.welcome_label.text = 'Welcome ' + username +'!'
            # Write new username in user_scores.csv file
            csvdir = App.get_running_app().csvdir
            with open(os.path.join(csvdir, 'user_score.csv'), mode='a', newline='') as score_data:
                writer = csv.writer(score_data)
                writer.writerow(['', user_id, '', '', '', username])
        else:
            return

    def change_continues(self, *args):
        """Allows user to change their username"""
        # Clear textbox text
        self.ids.textinput.text = ''
        # Clear all widgets from screen
        self.clear_all()
        self.ids.top_grid.padding = Window.width / 20
        # Unbind all button functions
        self.unbind_all()
        # Bind save continue function to save changes button
        self.ids.save_changes_button.bind(on_press=self.save_continues)
        # Add widgets to layout
        self.ids.change_user_grid.add_widget(self.ids.cont_label)
        self.ids.change_user_grid.add_widget(self.ids.textinput)
        self.ids.textinput.hint_text = 'Please enter a number'
        self.ids.change_btn_grid.add_widget(self.ids.cancel_button)
        self.ids.change_btn_grid.add_widget(self.ids.save_changes_button)
        self.ids.box.add_widget(self.ids.top_grid)
        self.ids.box.add_widget(self.ids.change_user_grid)
        self.ids.box.add_widget(self.ids.change_btn_grid)

    def save_continues(self, *args):
        global continue_trigger
        if self.ids.textinput.text.isdigit():
            # Save user text as continue trigger
            continue_trigger = int(self.ids.textinput.text)
            # Remove widgets
            self.clear_all()
            self.ids.top_grid.padding = Window.width / 25
            # Add default widgets
            self.grid_widgets()
            self.ids.box.add_widget(self.ids.top_grid)
            self.ids.box.add_widget(self.ids.grid)
            # Add in label with new username
            self.ids.cont_num.text = str(continue_trigger)
        else:
            return


class LeaderboardScreen(Screen):
    pass


class EndScreen(Screen):
    pass

def calculate_dist(x1, y1, x2, y2):
    """Determine the direction and magnitude of the dragging of the image"""
    dx = x2 - x1
    dy = y2 - y1
    dist = sqrt((dx * dx) + (dy * dy))
    min_dist = sqrt((Window.height / 10) ** 2 + (Window.width / 10) ** 2)
    return min_dist, dist, dx, dy


def line_dist(x1, y1, x2, y2):
    """Calculate where to draw the new points for swipe overlay"""
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
    global total_annos, avg_ranking, tutorial_check, total_exc, date_tracker, score_dict, time_check

    # Set username on user profile screen
    user.ids.user.text = username
    # Set username on settings screen
    settings.ids.user.text = username
    # Set username on achievements screen
    achievement.ids.label.text = username + '\'s Achievements'
    # Set username on continue screen
    cont.ids.label_1.text = 'Keep it up ' + username + '!'
    # Update continue trigger on settings screen
    settings.ids.cont_num.text = str(continue_trigger)
    # Read csv file
    csvdir = App.get_running_app().csvdir
    with open(os.path.join(csvdir, 'user_score.csv'), mode='r') as score_data:
        reader = csv.reader(score_data)
        time = []
        for row in reader:
            # Adds most recent scores to score dictionary from csv file
            score_dict[row[2]] = (row[3], row[4])
            # Adds dates to date dictionary
            d = row[0].split()
            if len(d) == 2:
                date_tracker[d[0]] = d[1]
                time.append(d[1])
            # Check if user has completed tutorial
            if row[0] == 'tutorial':
                tutorial_check = True
    for t in time:
        if float(t) > 0 and float(t) < 5:
            time_check = True
    try:
        # Delete empty row containing user name from score dictionary
        del score_dict['']
        # Get user's total amount of annotations completed
        total_annos = len(score_dict)
        # Update total annotations label
        user.ids.total.text = str(total_annos)
        # Get user's total ranking (compared to machine learning score for signal)
        total_ranking = 0
        # Store how many 'excellent' rankings the user has received
        total_exc = 0
        # Calculate users total ranking and number of excellents
        for key in score_dict:
            total_ranking = total_ranking + float(score_dict[key][1])
            if float(score_dict[key][1]) <= 0.1:
                total_exc += 1
    except KeyError:
        return

    try:
        # Calculate user's lifetime ranking (compared to machine learning score for signal)
        avg_ranking = 100 - int((total_ranking / total_annos) * 100)
        user.ids.ranking.text = str(avg_ranking) + '%'
    except ZeroDivisionError:
        return


def update_other_achievement():
    """Updates trophy and progess bar for non-standard achievements"""
    global tutorial_check, avg_ranking, achievement, time_check
    # User has completed tutorial achievement
    if tutorial_check:
        achievement.tut_badge.ids.trophy.source = 'pictures/tut_compl.png'
        achievement.tut_badge.ids.pb.max = 1
        achievement.tut_badge.ids.pb.value = 1

    if time_check:
        achievement.night_badge.ids.trophy.source = 'pictures/trophy_night.png'
        achievement.night_badge.ids.pb.max = 1
        achievement.night_badge.ids.pb.value = 1

    # Average ranking achievement
    if avg_ranking >= 90:
        achievement.ranking_badge.ids.trophy.source = 'pictures/ranking_90.png'
        achievement.ranking_badge.ids.pb.max = 90
    elif avg_ranking >= 75:
        achievement.ranking_badge.ids.trophy.source = 'pictures/ranking_75.png'
        achievement.ranking_badge.ids.pb.max = 90
    elif avg_ranking >= 50:
        achievement.ranking_badge.ids.trophy.source = 'pictures/ranking_50.png'
        achievement.ranking_badge.ids.pb.max = 75
    elif avg_ranking >= 25:
        achievement.ranking_badge.ids.trophy.source = 'pictures/ranking_25.png'
        achievement.ranking_badge.ids.pb.max = 50
    achievement.ranking_badge.ids.pb.value = avg_ranking


def update_std_achievements(var, badge):
    """Updates trophy and progress bar for achievements following the '1, 10, 25, 50' format"""
    # Total number of lifetime annotations achievement
    if var >= 50:
        badge.ids.trophy.source = 'pictures/trophy_50.png'
        badge.ids.pb.max = 50
    elif var >= 25:
        badge.ids.trophy.source = 'pictures/trophy_25.png'
        badge.ids.pb.max = 50
    elif var >= 10:
        badge.ids.trophy.source = 'pictures/trophy_10.png'
        badge.ids.pb.max = 25
    elif var >= 1:
        badge.ids.trophy.source = 'pictures/trophy_1.png'
        badge.ids.pb.max = 10
    # Update progress bar
    badge.ids.pb.value = var


# Create app class
class ScorePicturesApp(App):
    def __init__(self):
        super().__init__()

        if platform == 'android':
            from android.permissions import request_permissions, check_permission, Permission

            print('Getting permissions...')
            permissions = [
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
            ]
            request_permissions(permissions)

            from android.storage import primary_external_storage_path
            primary_ext_storage = primary_external_storage_path()

            # Make sure user scores file exists
            self.csvdir = os.path.join(primary_ext_storage, 'anno5i9')
            Path(self.csvdir).mkdir(exist_ok=True)
            user_score = Path(self.csvdir) / 'user_score.csv'
            user_score.touch()

        else:
            self.csvdir = os.path.join(os.path.dirname(__file__), 'csv')

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
