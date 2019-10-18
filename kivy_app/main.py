#import csv
import datetime
import os
import re
from functools import partial
from glob import glob
from math import sqrt
from os.path import dirname, join
from pathlib import Path
from random import randint
import traceback

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, GraphicException, Point
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.widget import Widget
from kivy.uix.widget import WidgetException
from kivy.utils import platform
from kivy.uix.togglebutton import ToggleButton
from kivy.storage.jsonstore import JsonStore

#import requests
#from OpenSSL import SSL
from kivy.network.urlrequest import UrlRequest
#import ssl
import json

API_URL = "https://95.217.13.152:8000"
# API_URL = "https://127.0.0.1:8000"

API_TOKEN = "0e2d70b1f642f85550adb7ff20656462"

# Store user_id and user_age in global variable
# TODO: Read user_age and userid from file system

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

user_id = None
user_age = None
user_profession = None

# Create global variable to track user during tutorial
image = None
hint_text = None
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
user_store = JsonStore('user.json')
picture_store = JsonStore('pics.json')
tutorial_store = JsonStore('tutorial.json')
# Check if user has completed the tutorial
tutorial_check = False
# Check if user has annotated all available signals
is_finished = False
# Keep track of last screen
last_screen = None
# Number of signals to annotate before triggering continue screen
continue_trigger = 120
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
        global user, menu, anno, cont, tutorial, achievement, settings, start1,start2, inst1, inst2, inst3, tutorialend, \
            example, leaderboard, end, user_id ,user_age ,user_profession 

        end = EndScreen()
        start1 = StartScreen1()
        start2 = StartScreen2()
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
        if not(user_store.exists('user')):
            self.add_widget(start1)
            self.add_widget(start2)
        else:
            user_id = user_store['user']['user_id']
            user_age = user_store['user']['age']
            user_profession = user_store['user']['prof']


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



class StartScreen1(Screen):
    def start_screen2(self, *args):
        print('menu_screen called!')
        """Switch to menu screen on button press and writes user data to user_score.csv"""
        global user_age, user_id, menu,start2
    
        # Switch to menu screen
        self.manager.current = 'start2'
        self.manager.transition.direction = 'left'
        # Create user id for tracking stats



class StartScreen2(Screen):
    def menu_screen(self, *args):
        print('menu_screen called!')
        """Switch to menu screen on button press and writes user data to user_score.csv"""
        global user_age, user_id, menu
        # Set user_age to text entered by user
        user_age = self.ids.textinput.text
        # Make sure user enters a user_age
        # TODO: Fix user_age and user_id generation
            # TODO: make persistent
            # TODO: use guid
        if user_age != '':
            # Switch to menu screen
            self.manager.current = 'menu'
            self.manager.transition.direction = 'left'
            # Create user id for tracking stats
            user_id = randint(0, 9223372036854775) # When database is deployed add in check to ensure no ids are the same
            # Display welcome message after first launch
            menu.ids.welcome_label.text = 'Welcome!'
            # Write user_age to store file
            
            user_store.put('user',age=user_age,user_id=user_id,prof=user_profession)
        else:
            return

    def set_profession(self,prof):
        global user_profession
        print(user_profession)
        user_profession = prof
        print(user_profession)
        


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
        global user_age
        self.user_age = user_age
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
        global user_id, user_age, total_counter, score_dict, continue_trigger, is_finished
        
        
        # Initialize counter to track how many pictures are done in each grouping
        self.counter = 0
        self.display_start_time = datetime.datetime.now()
        # Create list to house pictures
        self.pictures = []
        # Create variable to store machine score of signals
        self.machine_score = float()
        # Add all pictures in the 'Images' folder to the pictures list
        for filename in glob(join(curdir, 'images', '*')):
            self.pictures.append(filename)
        #self.pictures = []
        #temp = ['103342124479115860764494120979080807844_id-rec137_ch6_seg2_0_2500_r2','104003418020284232555655959169766214191_id-rec215_ch4_seg5_2500_5000_r3','108424315516278844437876826536801896231_id-rec241_ch4_seg3_2500_5000_r5','110602515197517776149041812132966761827_id-rec225_ch8_seg2_2500_5000_r5','113309087399932004493557579386951962787_id-rec214_ch6_seg2_0_2500_r3','114381880660051014157103844956336606374_id-rec193_ch8_seg3_0_2500_r1','118379549032493637745414913782698014163_id-rec137_ch6_seg2_2500_5000_r2','122295059341840231348510206278187579892_id-rec241_ch4_seg3_0_2500_r5','124031967113562081206629242060741483292_id-rec241_ch6_seg2_0_2500_r4','126412482567058408355486091649557525850_id-rec130_ch7_seg1_2500_5000_r1','129178124031459039412095785060338943167_id-rec255_ch3_seg3_0_2500_r3','134830702200516705950663017348016733450_id-rec261_ch2_seg4_0_2500_r2','136856423510053043610179474432673761068_id-rec137_ch6_seg2_2500_5000_r2','139167602334530688053724310591288219867_id-rec225_ch7_seg3_0_2500_r5','143174633261773935338644530394491604113_id-rec182_ch8_seg1_0_2500_r1','1434353254090807253834487829475277737_id-rec193_ch8_seg3_2500_5000_r1','151517920024555261534015213981312993584_id-rec167_ch7_seg5_2500_5000_r4','15431470510892756039113353403967646662_id-rec214_ch8_seg1_2500_5000_r3','154456776377789949565536889182583079655_id-rec137_ch7_seg2_0_2500_r4','154704012032443159460302018379089377848_id-rec143_ch6_seg1_0_2500_r2','158762776571818504723423129871679606629_id-rec257_ch5_seg5_0_2500_r2','160226813045286227218909080220537827717_id-rec166_ch8_seg3_0_2500_r4','160715270629679929593324366627270426402_id-rec214_ch8_seg1_2500_5000_r3','16260067393067756885292598139889968654_id-rec143_ch6_seg1_0_2500_r2','165154113504818783459240444465504855997_id-rec255_ch3_seg3_2500_5000_r3','166544545971697118681857065861478158652_id-rec257_ch5_seg5_2500_5000_r2','169199518217158465522984805550452915808_id-rec241_ch4_seg3_2500_5000_r5','171426256444735006695119266665668749652_id-rec196_ch8_seg4_0_2500_r1','171702536120551666258804217294133862334_id-rec143_ch6_seg1_2500_5000_r2','173433710018398823158855240227711148792_id-rec261_ch3_seg3_2500_5000_r2','174663735498201448751486225680027334101_id-rec214_ch6_seg1_0_2500_r3','175255321508747137848762654186383606518_id-rec225_ch8_seg3_2500_5000_r5','178543775901762368806560842257142135880_id-rec214_ch6_seg1_2500_5000_r3','180273796508183697599919477685028650000_id-rec215_ch4_seg5_0_2500_r3','183879774793335805627856929189859504099_id-rec218_ch3_seg3_2500_5000_r3','185945007831736435413643158917363070340_id-rec212_ch8_seg1_0_2500_r1','190563526719099884068530297673166518212_id-rec255_ch3_seg3_2500_5000_r3','196275618322020641913374652894760049696_id-rec241_ch8_seg1_2500_5000_r4','197090194718352458526733073740714468815_id-rec213_ch6_seg2_0_2500_r1','206968038213177103674161468341594605876_id-rec142_ch8_seg5_2500_5000_r4','211642247656900184897472275724187046132_id-rec214_ch6_seg2_0_2500_r3','212480768011927867770284915690069686558_id-rec257_ch5_seg5_0_2500_r2','214208301659267085101217918422801229504_id-rec215_ch4_seg5_0_2500_r3','215329604565052444613668927050054549332_id-rec213_ch6_seg2_0_2500_r1','216634646943880918973820569155956354419_id-rec11_ch3_seg1_2500_5000_r5','21780316225224999301173270231949032516_id-rec11_ch3_seg1_0_2500_r5','217896310974835301601521279173597403346_id-rec182_ch8_seg1_0_2500_r1','21897520924028057184005132703111316318_id-rec213_ch6_seg2_2500_5000_r1','219454156581514580759062187041093493360_id-rec214_ch8_seg1_0_2500_r3','221608118697286195763101719455189793823_id-rec225_ch8_seg2_0_2500_r5','226589563190477628469520408797591792784_id-rec137_ch7_seg2_2500_5000_r4','230083356011600811365103213443605662044_id-rec137_ch6_seg2_0_2500_r2','233383199020761070183172229012043600497_id-rec241_ch6_seg2_0_2500_r4','23602987947466745463181775700079217510_id-rec218_ch3_seg3_0_2500_r3','236782571464524324669121387244173219041_id-rec214_ch6_seg2_2500_5000_r3','242336598335015644257544843436737349949_id-rec225_ch8_seg2_0_2500_r5','245617904043298294582398098550423577792_id-rec215_ch4_seg5_2500_5000_r3','246808707669960772545169912273910201713_id-rec141_ch7_seg3_0_2500_r2','247406143111833268868832959433200797987_id-rec261_ch3_seg3_0_2500_r2','247991657267984978056286276639887252570_id-rec261_ch3_seg3_0_2500_r2','250069680458132948161259751352696844087_id-rec137_ch7_seg2_2500_5000_r4','250320384136756314314107023364467788882_id-rec212_ch8_seg1_0_2500_r1','253723751536038217388993856743689545976_id-rec167_ch7_seg5_0_2500_r4','255572161448088691986954670124716423203_id-rec225_ch7_seg3_2500_5000_r5','257576478885031390712163019070774379876_id-rec255_ch6_seg2_2500_5000_r5','259496002526684944678334049361664504680_id-rec142_ch8_seg5_0_2500_r4','263746936742319239469693954915702938968_id-rec11_ch3_seg1_0_2500_r5','264185827296368241919066730942376298660_id-rec214_ch6_seg1_2500_5000_r3','266193306613298635087228709987223261140_id-rec255_ch6_seg2_0_2500_r5','266694970994393419280943216028892777599_id-rec255_ch6_seg2_2500_5000_r5','273431229923463470581219181971966744675_id-rec241_ch8_seg1_2500_5000_r4','277470877166694518503894079493892658753_id-rec182_ch8_seg1_2500_5000_r1','277909599715964513506923519117617001154_id-rec214_ch8_seg1_0_2500_r3','279811352528707338151643137839265565427_id-rec257_ch5_seg5_2500_5000_r2','284094762895345772713257735022979491518_id-rec130_ch7_seg1_0_2500_r1','284672280786868415395368456935270371215_id-rec193_ch8_seg3_2500_5000_r1','287215272372518196451410078038834121733_id-rec142_ch8_seg5_2500_5000_r4','290099519422824940965882981541106965155_id-rec241_ch8_seg1_0_2500_r4','29169571989450457451544377387119161810_id-rec141_ch7_seg3_0_2500_r2','292506496579566971397721257037483613085_id-rec255_ch3_seg3_0_2500_r3','299367948178506781806261135270732823081_id-rec130_ch7_seg1_2500_5000_r1','303753327898365095852136223012683477725_id-rec182_ch8_seg1_2500_5000_r1','304362106918192176006911668016327136064_id-rec212_ch8_seg1_2500_5000_r1','314839655668851932021492781322199333795_id-rec255_ch6_seg2_0_2500_r5','316334349458961512007067547240778165521_id-rec11_ch3_seg1_2500_5000_r5','320118425662491163987943376167180638278_id-rec137_ch7_seg2_0_2500_r4','320122348508191080960800835819988579600_id-rec225_ch8_seg3_0_2500_r5','322672148869416059080398571353732565892_id-rec193_ch8_seg3_0_2500_r1','322681453460850093858414582674473907791_id-rec212_ch8_seg1_2500_5000_r1','326089511761098604135693740374431046884_id-rec141_ch7_seg3_2500_5000_r2','326777456951499827424459889564139065317_id-rec225_ch7_seg3_0_2500_r5','327016416915657990939802545012449742978_id-rec241_ch6_seg2_2500_5000_r4','328552326667769839418802781614678227772_id-rec141_ch7_seg3_2500_5000_r2','328683356761119627329332346012830214955_id-rec218_ch3_seg3_0_2500_r3','331073658446504320996637363375619095449_id-rec213_ch6_seg2_2500_5000_r1','335197940996430825824080290088056172744_id-rec166_ch8_seg3_2500_5000_r4','36790349017105840585109702896881856059_id-rec241_ch4_seg3_0_2500_r5','3717000896725195894625940005322034047_id-rec214_ch6_seg1_0_2500_r3','3767720427912547991327956294366147541_id-rec225_ch8_seg3_0_2500_r5','41442826562827207579708879485945315212_id-rec241_ch8_seg1_0_2500_r4','42086431211517945148967864018901200107_id-rec225_ch7_seg3_2500_5000_r5','55390244473756998042011943027266396667_id-rec225_ch8_seg2_2500_5000_r5','58658159835039410455139360335377928650_id-rec167_ch7_seg5_2500_5000_r4','63614048980427456131427371879963483583_id-rec142_ch8_seg5_0_2500_r4','66057952889598686511354495082095115796_id-rec225_ch8_seg3_2500_5000_r5','67619924548597363146073205497287445189_id-rec241_ch6_seg2_2500_5000_r4','69882488835572840047560622409090278181_id-rec218_ch3_seg3_2500_5000_r3','72761162147403374622551657585041399052_id-rec166_ch8_seg3_2500_5000_r4','74406280578981420074194509329362012621_id-rec196_ch8_seg4_2500_5000_r1','75901344128827036928095701972462308982_id-rec214_ch6_seg2_2500_5000_r3','76137486784406306451478257859409868882_id-rec196_ch8_seg4_0_2500_r1','78924578309419803366175767339189744492_id-rec166_ch8_seg3_0_2500_r4','81878311499570425993592356534897798612_id-rec261_ch2_seg4_2500_5000_r2','85307528273069388282878502621196883791_id-rec143_ch6_seg1_2500_5000_r2','86405830975722188285697412053076020571_id-rec261_ch3_seg3_2500_5000_r2','91659141573906011174228855318849176595_id-rec167_ch7_seg5_0_2500_r4','9236241783810531373526902447929216614_id-rec196_ch8_seg4_2500_5000_r1','94002043808155071209562935348059758758_id-rec261_ch2_seg4_2500_5000_r2','97594062569699218644217220479325972336_id-rec261_ch2_seg4_0_2500_r2','97963471235033937264214788117292530549_id-rec130_ch7_seg1_0_2500_r1']
        #for i in temp:
        #    self.pictures.append(f'images/{i}')

        # Remove any pictures that have already been annotated
        unannotated_pictures = [p for p in self.pictures if not picture_store.exists(Path(p).name)]
        self.pictures = unannotated_pictures
        
        # Get total number of pictures to gauge progress
        self.prog_max = len(self.pictures)
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
        global end, user_age
        self.manager.current = 'end'
        self.manager.transition.direction = 'left'
        end.ids.label.text = 'Congratulations!'# + user_age + '!'

    def on_touch_down(self, touch):
       
        """Record the initial coordinates of the user touch"""
        super(AnnotateScreen, self).on_touch_down(touch)
        global lines, line_color
        self.coord = [touch.x, touch.y]
        self.annotation_start_time = datetime.datetime.now()

        with self.canvas:
            Color(1, 1, 0)
            touch.ud['line'] = Line(points=(touch.x, touch.y),width=3)


        # try:
        #     # Reset maching score ranking
        #     self.ids.ranking.text = ''
        # # Prevent error when click on end screen
        # except AttributeError:
        #     print(traceback.format_exc())
        #     return True
        # Draw swipe line on canvas

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
        
        touch.ud['line'].points += [touch.x, touch.y]

        if len(touch.ud['line'].points) > 30:
            touch.ud['line'].points.pop(0)
            touch.ud['line'].points.pop(0)
        
        try:
            # Update score label
            self.update_label(touch)
        # Avoid app crashing from user touch on end screen
        except AttributeError:
            print(traceback.format_exc())
            return

    def on_touch_up(self, touch):
        """Calculate the user score based on the direction of their touch and ensure the movement was big enough"""
        super(AnnotateScreen, self).on_touch_up(touch)
        global lines
        self.annotation_end_time = datetime.datetime.now()
        
        self.canvas.remove(touch.ud['line'])

        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        # Remove all points

        try:
            # Add coordinates of end of touch motion
            self.coord.append(touch.x)
            self.coord.append(touch.y)
            # Calculate distance of swipe
            min_dist, dist, dx, dy = calculate_dist(*self.coord)
            # Calculate score of swipe
            self.score_val = touch.y / Window.height
            # Check if drag movement is big enough
#            if dist > min_dist and dx > Window.width / 10:
            self.prev_pictures.append(self.current)
            # Assign ranking based on comparison to machine learning score
            self.ranking = abs(self.score_val - float(self.machine_score))
            # if self.ranking < 0.1:
            #     self.ids.ranking.text = 'ExcelExcellent!'
            # elif self.ranking < 0.2:
            #     self.ids.ranking.text = 'Very Good!'
            # elif self.ranking < 0.3:
            #     self.ids.ranking.text = 'Good!'
            # elif self.ranking < 0.4:
            #     self.ids.ranking.text = 'OK!'
            # elif self.ranking < 0.5:
            #     self.ids.ranking.text = 'Not Quite!'

            # Assign score based on drag direction
            self.change_image(score=self.score_val)

            # Recenter display picture if drag is too small
            # else:
            #     self.ids.display.center = self.center
            #     self.ids.ranking.text = 'Try Again'
        # Prevent crashing from user touches on end screen
        except (AttributeError, TypeError):
            print(traceback.format_exc())
            return

    def change_image(self, score=None):
        """Change the displayed image and write the filename and score to score.csv"""
        global total_counter, continue_trigger,user_profession
        # try:
        temp_json = {
            "picture_name":Path(self.current).name,
            "score":"{:0.2f}".format(score),
            "display_time_before_swipe":(self.annotation_start_time-self.display_start_time).total_seconds(),
            "swipe_time":(self.annotation_end_time-self.annotation_start_time).total_seconds(),
            "user_id":user_id,
            "user_age":user_age,
            "user_profession":user_profession,
            }
        UrlRequest('https://95.217.13.152:8000/upload',
                 req_body=json.dumps(temp_json), 
                 req_headers={"Authorization": "0e2d70b1f642f85550adb7ff20656462"},
                 #ca_file="ssl/ca.pem",
                 verify=False)

        # resp = requests.post(
        #     f"{API_URL}/upload",
        #     headers={
        #         "Authorization": API_TOKEN,
        #     },
        #     , 
        #     verify="ssl/ca.pem"
        # )
        # resp.raise_for_status()
        # # except requests.RequestException as err:
        #     # print("Error:", err)

        picture_store.put(Path(self.current).name,score="{:0.2f}".format(score))

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
        self.display_start_time = datetime.datetime.now()
        

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
            print(traceback.format_exc())
            return

    def cont_screen(self, *args):
        """Switch to continue screen and update user_age in label on continue screen"""
        global cont, total_counter, total_annos, user_age
        update_rankings()

        cont.ids.label_1.text = 'Keep it up ' + user_age + '!'
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
        global hint_text
        Screen.__init__(self, name='tutorial')
        # Create list variable to store pictures and solutions
        self.pictures = []
        self.prev_pictures = []
        self.solutions = []
        self.prev_soln = []
        self.counter = 0
        self.tracker = 'signal'
        tutorial_store.put("tutorial/1022380972125450986188591405613469310_snr10.75-fm-8-_sym-0",score=0.7)
        tutorial_store.put("tutorial/113517786603254924505956454605192607998_snr9-fm-8-_sym-0",score=0.7)
        tutorial_store.put("tutorial/123611501510187344704721435103936331349_snr12-fm-8-_sym-1",score=0.9)
        tutorial_store.put("tutorial/128064603395639113168054621785134605595_snr0-fm-8-_sym-1",score=0.1)
        tutorial_store.put("tutorial/129856835604392568804938960162535432020_snr10.75-fm-8-_sym-1",score=0.7)
        tutorial_store.put("tutorial/138730835150962509465512050703867809976_snr12-fm-8-_sym-0",score=0.9)
        tutorial_store.put("tutorial/173482865249683137776937383287428385637_snr9-fm-8-_sym-1",score=0.5)
        tutorial_store.put("tutorial/233244275429460543641561647697539591898_snr6-fm-12-_sym-0",score=0.3)
        tutorial_store.put("tutorial/24742080245223662240483161477616182262_snr0-fm-8-_sym-0",score=0.2)
        tutorial_store.put("tutorial/260855217038528838463799779261291927571_snr10.75-fm-8-_sym-0",score=0.7)
        tutorial_store.put("tutorial/302503443708780369655847777284615658262_snr6-fm-12-_sym-1",score=0.4)
        tutorial_store.put("tutorial/322445027347025434838792917077778333388_snr0-fm-8-_sym-1",score=0.1)
        tutorial_store.put("tutorial/324694552020281424678033071442173176736_snr12-fm-8-_sym-1",score=0.9)
        tutorial_store.put("tutorial/335739967582357681107170832790956262377_snr9-fm-8-_sym-0",score=0.5)
        tutorial_store.put("tutorial/62808095554229018563057127496377662682_snr6-fm-12-_sym-0",score=0.3)        
        # tutorial_store.put('tutorial/100197593811532956605821187933449634966_id-rec166_ch8_seg3_0_1250_r4',score=0.7)
        # tutorial_store.put('tutorial/112781594720694379961220168083223467217_id-rec241_ch4_seg3_0_1250_r5',score=0.9)
        # tutorial_store.put('tutorial/142146466129250066498252306113988096885_id-rec215_ch4_seg5_1250_3750_r3',score=0.5)
        # tutorial_store.put('tutorial/149385383516548197136831187222857158025_id-rec225_ch8_seg2_0_1250_r5',score=0.9)
        # tutorial_store.put('tutorial/57950949682994718579646967904790952352_id-rec143_ch6_seg1_0_1250_r2',score=0.3)
        # tutorial_store.put('tutorial/61141798589456279075042645491742630473_id-rec167_ch7_seg5_1250_3750_r4',score=0.7)
        # tutorial_store.put('tutorial/64149075328788167416347321113165539714_id-rec218_ch3_seg3_1250_3750_r3',score=0.5)
        # tutorial_store.put('tutorial/64392110901409340062579086792869080176_id-rec196_ch8_seg4_1250_3750_r1',score=0.1)
        # tutorial_store.put('tutorial/64713429581887926222903156210961811462_id-rec225_ch8_seg3_1250_3750_r5',score=0.9)
        # tutorial_store.put('tutorial/78039171360641645100633690273658768483_id-rec241_ch8_seg1_1250_3750_r4',score=0.7)
        # tutorial_store.put('tutorial/82991842728810816810315025719824352858_id-rec257_ch5_seg5_0_1250_r2',score=0.3)
        # tutorial_store.put('tutorial/90322133198237501627536537910755457261_id-rec182_ch8_seg1_0_1250_r1',score=0.1)
        # tutorial_store.put('tutorial/94656331109381391290276046782538880963_id-rec261_ch3_seg3_1250_3750_r2',score=0.3)
        # tutorial_store.put('tutorial/99019776797575122013666953082928345046_id-rec130_ch7_seg1_1250_3750_r1',score=0.1)
        # tutorial_store.put('tutorial/99310062842742358038133096485812137218_id-rec214_ch8_seg1_1250_3750_r3',score=0.5)
        # Add all pictures in tutorial folder to list
        for filename in glob(join(curdir, 'tutorial', '*')):
            self.pictures.append(filename)
#        self.pictures = []
#        temp = ['100197593811532956605821187933449634966_id-rec166_ch8_seg3_0_1250_r4','112781594720694379961220168083223467217_id-rec241_ch4_seg3_0_1250_r5','142146466129250066498252306113988096885_id-rec215_ch4_seg5_1250_3750_r3','149385383516548197136831187222857158025_id-rec225_ch8_seg2_0_1250_r5','57950949682994718579646967904790952352_id-rec143_ch6_seg1_0_1250_r2','61141798589456279075042645491742630473_id-rec167_ch7_seg5_1250_3750_r4','64149075328788167416347321113165539714_id-rec218_ch3_seg3_1250_3750_r3','64392110901409340062579086792869080176_id-rec196_ch8_seg4_1250_3750_r1','64713429581887926222903156210961811462_id-rec225_ch8_seg3_1250_3750_r5','78039171360641645100633690273658768483_id-rec241_ch8_seg1_1250_3750_r4','82991842728810816810315025719824352858_id-rec257_ch5_seg5_0_1250_r2','90322133198237501627536537910755457261_id-rec182_ch8_seg1_0_1250_r1','94656331109381391290276046782538880963_id-rec261_ch3_seg3_1250_3750_r2','99019776797575122013666953082928345046_id-rec130_ch7_seg1_1250_3750_r1','99310062842742358038133096485812137218_id-rec214_ch8_seg1_1250_3750_r3']
        self.ids.pb.max = len(self.pictures)
        # Set initial progress of progress bar
        self.ids.pb.value = 0
        # for i in temp:
        #     self.pictures.append(f'tutorial/{i}')
        # Pull out all solution pictures into a separate list
        #for filename in glob(join(curdir, 'tutorial', '*_soln.png')):
        #    self.solutions.append(filename)
        # Remove all solution pictures from the original pictures list
        #self.pictures = [pic for pic in self.pictures if pic not in self.solutions]
        self.pictures.sort()
        #self.solutions.sort()
        # Display first picture
        self.current = self.pictures.pop(0)
        self.soln_current = ''

        self.ids.display.source = self.current
        self.ids.pb.value = self.counter
        print(self.current)

        if tutorial_store.exists(self.current):
            self.ids.hint_text.text = 'score: ~{}'.format(int(float(tutorial_store[self.current]['score'])*100))


    # Record initial down click coordinates
    def on_touch_down(self, touch):
        """Record the initial coordinates of the user touch"""
        super(TutorialScreen, self).on_touch_down(touch)
        global lines

        self.coord = [touch.x, touch.y]
        self.annotation_start_time = datetime.datetime.now()

        with self.canvas:
            Color(1, 1, 0)
            touch.ud['line'] = Line(points=(touch.x, touch.y),width=3)

        try:
            self.ids.ranking.text = ''
        # Prevent error when click on end screen
        except AttributeError:
            print(traceback.format_exc())
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

        touch.ud['line'].points += [touch.x, touch.y]

        if len(touch.ud['line'].points) > 30:
            touch.ud['line'].points.pop(0)
            touch.ud['line'].points.pop(0)

        try:
            self.update_label(touch)

        # Avoid app crashing from user touch on end screen
        except AttributeError:
            print(traceback.format_exc())
            return

    def on_touch_up(self, touch):
        """Calculate the user score based on the direction of their touch and ensure the movement was big enough"""
        super(TutorialScreen, self).on_touch_up(touch)
        global lines

        self.canvas.remove(touch.ud['line'])

        print(self.ids.display.canvas)
        if touch.grab_current is not self:
            return
        touch.ungrab(self)

        try:
            self.coord.append(touch.x)
            self.coord.append(touch.y)
            #min_dist, dist, dx, dy = calculate_dist(*self.coord)
            self.score_val = touch.y / Window.height
        
            if tutorial_store.exists(self.current):
                self.machine_score = tutorial_store[self.current]['score']

            self.tracker = 'soln'
            # Assign ranking based on comparison to machine learning score
            self.ranking = abs(self.score_val -float(self.machine_score))
            if self.ranking < 0.1:
                self.ids.ranking.text = 'Excellent'
            elif self.ranking < 0.2:
                self.ids.ranking.text = 'Very Good'
            elif self.ranking < 0.25:
                self.ids.ranking.text = 'Good'
            elif self.ranking < 0.3:
                self.ids.ranking.text = 'OK'
            elif self.ranking < 0.5:
                self.ids.ranking.text = 'Not Quite'

            self.ids.pb.value += 1
            try:
                self.prev_pictures.append(Path(self.current).name)
                self.ids.float.remove_widget(self.ids.display)
                self.ids.label.text = ''
                self.ids.float.add_widget(self.ids.image, index=2)
                self.next()
                self.soln_current = self.solutions.pop(0)
                self.ids.image.source = self.soln_current
                self.ids.grid.remove_widget(self.ids.empty)
                self.ids.grid.add_widget(self.ids.next_button)
                self.counter = self.counter + 1
                #self.ids.pb.value += 1

            # Prevent crashing from drag on solution screen
            except (WidgetException, IndexError):
                print(traceback.format_exc())
                return

            # # Recenter display picture if drag is too small
            # else:
            #     self.ids.display.center = self.center
            #     if dist < 5:
            #         self.ids.ranking.text = ''
            #     else:
            #         self.ids.ranking.text = 'Try Again'
        # Prevent crashing from user touches on end screen
        except (AttributeError, TypeError):
            print(traceback.format_exc())
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
            print(traceback.format_exc())
            return

    def next(self, *args):
        """Removes the solution image and re-adds the signal to annotate, updates the progress bar"""
        global screen_manager, tutorial
        
        
        if len(self.pictures) == 0:
            self.manager.current = 'tutorialend'
            self.manager.transition.direction = 'left'
            # Record if user has completed the tutorial
            if user_store.exists('tutorial_done'):
                self.check = True
            else:
                user_store.put('tutorial_done',value='True')

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

            if tutorial_store.exists(self.current):
                self.machine_score = tutorial_store[self.current]['score']
                self.ids.hint_text.text = 'score: ~{}'.format(int(float(tutorial_store[self.current]['score'])*100))
            
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
        global user_age
        Screen.__init__(self)
        self.user_age = user_age
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
        global user_age, continue_trigger

    def unbind_all(self, *args):
        # Unbind button functions
        self.ids.save_changes_button.unbind(on_press=self.save_user_age)
        self.ids.save_changes_button.unbind(on_press=self.save_continues)

    def grid_widgets(self):
        """Adds default widgets to grid layout for settings screen"""
        # Add user_age label
        self.ids.grid.add_widget(self.ids.user_label)
        # Add user_age
        self.ids.grid.add_widget(self.ids.user)
        # Add change user_age button
        self.ids.grid.add_widget(self.ids.change_user_age_button)
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
        """Allows user to cancel choosing their new user_age"""
        # Clear all widgets
        self.clear_all()
        # Add default widgets back to the grid
        self.grid_widgets()
        self.ids.top_grid.padding = Window.width/25
        self.ids.box.add_widget(self.ids.top_grid)
        self.ids.box.add_widget(self.ids.grid)

    def change_user_age(self, *args):
        """Allows user to change their user_age"""
        # Reset text box text
        self.ids.textinput.text = ''
        # Remove all widgets
        self.clear_all()
        self.ids.top_grid.padding = Window.width/20
        # Unbind button
        self.unbind_all()
        # Bind save user_age function to button
        self.ids.save_changes_button.bind(on_press=self.save_user_age)
        # Add user_age label
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

    def save_user_age(self, *args):
        """Saves new user_age in csv and changes appropriate widgets"""
        global user_age, menu, anno, user
        # Get user_age typed by user
        if self.ids.textinput.text != '':
            # Save text user entered as user_age
            user_age = self.ids.textinput.text
            # Remove all widgets
            self.clear_all()
            self.ids.top_grid.padding = Window.width / 25
            # Add default widgets
            self.grid_widgets()
            self.ids.box.add_widget(self.ids.top_grid)
            self.ids.box.add_widget(self.ids.grid)
            # Add in label with new user_age
            self.ids.user.text = user_age
            # Change user_age in end screen
            end.ids.label.text = 'Congratulations ' + user_age + '!'
            # Reset welcome label on menu screen with new user_age
            menu.ids.welcome_label.text = 'Welcome ' + user_age +'!'
            # Write new user_age in user_scores.csv file
            #csvdir = App.get_running_app().csvdir
            #with open(os.path.join(csvdir, 'user_score.csv'), mode='a', newline='') as score_data:
            #    writer = csv.writer(score_data)
            #    writer.writerow(['picture_name','score','display_start_time','annotation_start_time','annotation_end_time','user_id','user_age','user_profession'])
        else:
            return

    def change_continues(self, *args):
        """Allows user to change their user_age"""
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
            # Add in label with new user_age
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
    """Updates user_age, total annotations, average ranking, and other user stats by reading csv file"""
    global total_annos, avg_ranking, tutorial_check, total_exc, date_tracker, score_dict, time_check

    # Set user_age on user profile screen
    user.ids.user.text = user_age
    # Set user_age on settings screen
    settings.ids.user.text = user_age
    # Set user_age on achievements screen
    achievement.ids.label.text = user_age + '\'s Achievements'
    # Set user_age on continue screen
    cont.ids.label_1.text = 'Keep it up ' + user_age + '!'
    # Update continue trigger on settings screen
    settings.ids.cont_num.text = str(continue_trigger)
    # Read csv file
    # csvdir = App.get_running_app().csvdir
    # with open(os.path.join(csvdir, 'user_score.csv'), mode='r') as score_data:
    #     reader = csv.reader(score_data)
    #     time = []
    #     for row in reader:
    #         # Adds most recent scores to score dictionary from csv file
    #         score_dict[row[2]] = (row[3], row[4])
    #         # Adds dates to date dictionary
    #         d = row[0].split()
    #         if len(d) == 2:
    #             date_tracker[d[0]] = d[1]
    #             time.append(d[1])
    #         # Check if user has completed tutorial
    #         if row[0] == 'tutorial':
    #             tutorial_check = True
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
        print(traceback.format_exc())
        return

    if total_annos > 0:
        # Calculate user's lifetime ranking (compared to machine learning score for signal)
        avg_ranking = 100 - int((total_ranking / total_annos) * 100)
        user.ids.ranking.text = str(avg_ranking) + '%'


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

        # if platform == 'android':
        #     from android.permissions import request_permissions, check_permission, Permission

        #     print('Getting permissions...')
        #     permissions = [
        #         Permission.WRITE_EXTERNAL_STORAGE,
        #         Permission.READ_EXTERNAL_STORAGE,
        #     ]
        #     request_permissions(permissions)

        #     from android.storage import primary_external_storage_path
        #     primary_ext_storage = primary_external_storage_path()

        #     # Make sure user scores file exists
        #     self.csvdir = os.path.join(primary_ext_storage, 'anno5i9')
        #     Path(self.csvdir).mkdir(exist_ok=True)
        #     user_score = Path(self.csvdir) / 'user_score.csv'
        #     user_score.touch()

        # else:
        #     self.csvdir = os.path.join(os.path.dirname(__file__), 'csv')

        # TODO: Load user_age here if file exists, else create user_id here


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
