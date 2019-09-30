#import csv
import datetime
#import os
import re
from functools import partial
from glob import glob
from math import sqrt
#from os.path import dirname, join
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
import ssl
import json

API_URL = "https://95.217.13.152:8000"
# API_URL = "https://127.0.0.1:8000"

API_TOKEN = "0e2d70b1f642f85550adb7ff20656462"

# Store user_id and user_age in global variable
# TODO: Read user_age and userid from file system
user_id = None
user_age = ''
user_profession = 'other'

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
#curdir = dirname(__file__)

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
            example, leaderboard, end

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
        self.pictures = ['101386461387201568417948449838469701889_asym-fm4-SNR-12dB_1250_3750','102938605983409295714336240804183795512_asym-fm2-SNR-0dB_3750_6250','103816295986891413058595159792142688940_asym-fm4-SNR-9dB_1250_3750','108776939096942473457701722994053290920_asym-fm4-SNR-12dB_6250_8750','11190355415306468876267307038794198077_asym-fm2-SNR-0dB_6250_8750','112631446792391675623624266405087301257_sym-fm2-SNR-9dB_3750_6250','113169050665634613231662231387200902361_sym-fm4-SNR-12dB_11250_13750','113971189716700031972272563135840432490_asym-fm4-SNR-6dB_6250_8750','114295229073341578538208612948870791213_asym-fm4-SNR-10.8dB_8750_11250','114922679425879574442538237444906829067_asym-fm4-SNR-0dB_11250_13750','115591932089925178536835187296446557601_asym-fm8-SNR-12dB_6250_8750','116161180342623774946780928158175493539_asym-fm4-SNR-12dB_11250_13750','118983466657360622515101026895310397874_asym-fm8-SNR-10.8dB_6250_8750','121595226594098136474149918949526135801_sym-fm4-SNR-12dB_3750_6250','128629491853715749605091458845349750854_sym-fm8-SNR-0dB_1250_3750','129217223493224932089832292999237380479_sym-fm2-SNR-12dB_11250_13750','129378003887017676977129286937696449951_asym-fm8-SNR-6dB_1250_3750','131717182676443161919346140124486210686_sym-fm8-SNR-12dB_6250_8750','135060392315361915805751395548045555957_sym-fm8-SNR-9dB_1250_3750','137064368394167448591678663144012341960_sym-fm4-SNR-12dB_6250_8750','137534088669007762562064233190070619674_sym-fm2-SNR-9dB_11250_13750','140743128503468163728419614434881299683_asym-fm2-SNR-9dB_8750_11250','142861455629200504364333699238820556627_asym-fm4-SNR-6dB_3750_6250','144936506315656202252534609127463808837_sym-fm4-SNR-0dB_11250_13750','147500553718413805856487864810448164908_sym-fm4-SNR-10.8dB_8750_11250','148706759232151020354416952546074081764_asym-fm8-SNR-9dB_8750_11250','150758144868632234483354006658110036949_sym-fm2-SNR-0dB_3750_6250','15177562386238191467268415208819092786_asym-fm4-SNR-6dB_1250_3750','152608274903669601761234498173899050644_asym-fm2-SNR-0dB_11250_13750','153401866728622997936096297110757290529_asym-fm4-SNR-10.8dB_11250_13750','155685212051332572864542304109500151548_sym-fm2-SNR-10.8dB_3750_6250','161827464230079428733586488097250123430_asym-fm2-SNR-10.8dB_1250_3750','164146392652227406765514178873366319161_asym-fm2-SNR-6dB_11250_13750','165043755734495551219655443741956078580_sym-fm4-SNR-12dB_1250_3750','167177586571620980985453299404282972986_asym-fm8-SNR-0dB_8750_11250','168089579195138435052688436154129832211_asym-fm8-SNR-10.8dB_1250_3750','16831034799411185858109137353763718202_sym-fm2-SNR-12dB_6250_8750','174086245187058070728386544315753693360_sym-fm8-SNR-0dB_3750_6250','174442612141194238873224375686072419562_asym-fm2-SNR-12dB_3750_6250','178862807259226734486968335982766821380_asym-fm2-SNR-9dB_3750_6250','179097582148436985421847206656444753777_asym-fm2-SNR-12dB_6250_8750','179365326678401730378262172012142964146_asym-fm4-SNR-10.8dB_3750_6250','17970653058695003750701171635600902551_asym-fm2-SNR-12dB_8750_11250','18554525984262439217827847379010014678_sym-fm2-SNR-0dB_6250_8750','190538748886216715380758894987577840928_sym-fm2-SNR-12dB_3750_6250','195232381564377623846303997609484555481_asym-fm2-SNR-0dB_8750_11250','196244458685767216993035516791827997644_asym-fm4-SNR-12dB_3750_6250','197046228787377916164348867403985701017_sym-fm8-SNR-6dB_3750_6250','197250813900725360465554191657869366102_asym-fm2-SNR-6dB_6250_8750','201424563683795520236258902270817027515_asym-fm4-SNR-9dB_3750_6250','201990123428472189801470526514307057131_sym-fm8-SNR-10.8dB_8750_11250','203792090481212345706682633938796783716_asym-fm4-SNR-9dB_11250_13750','204169839598394360730323855403550584030_sym-fm2-SNR-6dB_3750_6250','208340137673882521745057930969422605866_asym-fm2-SNR-0dB_1250_3750','208665533463938898943277279255507733293_asym-fm8-SNR-6dB_8750_11250','209388692161082133116062067516565520379_asym-fm8-SNR-10.8dB_3750_6250','210517499175724485845063485745720567355_sym-fm8-SNR-9dB_6250_8750','211311811533823746569832323333983394123_sym-fm8-SNR-6dB_8750_11250','214431791759954348811102251522624471658_sym-fm4-SNR-10.8dB_3750_6250','215833854604085183509413457729854952659_asym-fm8-SNR-12dB_3750_6250','216553943101834912203429592758521415930_sym-fm8-SNR-6dB_1250_3750','217606020336159857142290641964680311438_asym-fm4-SNR-9dB_8750_11250','218741607921139413014089049480799482742_sym-fm8-SNR-10.8dB_1250_3750','218793349099064132547596572232364608806_sym-fm8-SNR-6dB_11250_13750','219377647686638954949726102254576896464_sym-fm2-SNR-10.8dB_6250_8750','224780392209592189838797211293355974937_sym-fm8-SNR-12dB_1250_3750','227297332295548973118163194292721297149_sym-fm2-SNR-9dB_8750_11250','227358437226967795548732473100741069538_asym-fm8-SNR-9dB_11250_13750','22799944593158886734478299836786325977_asym-fm2-SNR-9dB_11250_13750','229410803766004824323543852409436589729_asym-fm2-SNR-10.8dB_11250_13750','230053520329408203280581517417092858014_sym-fm4-SNR-10.8dB_6250_8750','233798913395705877385494458885112721394_asym-fm2-SNR-10.8dB_8750_11250','234107044838155133996957807863460752662_sym-fm4-SNR-6dB_11250_13750','235439208951830345038064020158797970900_asym-fm8-SNR-12dB_11250_13750','238194717427046012894871551420290810585_sym-fm8-SNR-10.8dB_11250_13750','238270624214895185434672909579560028906_sym-fm2-SNR-0dB_1250_3750','243150126816685476084582982324984804863_asym-fm2-SNR-12dB_1250_3750','244032791858590347318900594661238433126_asym-fm2-SNR-6dB_8750_11250','24551702020792147553494455150871964163_asym-fm4-SNR-6dB_11250_13750','248019142276737534499663732937639268401_asym-fm8-SNR-12dB_1250_3750','249090283157016850517218844005190750533_sym-fm8-SNR-10.8dB_6250_8750','25490271969167522298861352669658104078_sym-fm4-SNR-0dB_1250_3750','255281944759681247315729001597977207947_sym-fm4-SNR-6dB_3750_6250','255840436973285148963343401615933259977_sym-fm2-SNR-10.8dB_1250_3750','257850370336037221314121547158913364231_sym-fm8-SNR-12dB_8750_11250','260543695307689816698843264987496000153_sym-fm4-SNR-0dB_3750_6250','263984314890397401276084201215118984086_asym-fm2-SNR-9dB_6250_8750','266004240889837928985420339929521867707_sym-fm4-SNR-12dB_8750_11250','267214510130391298878708048182061005230_sym-fm8-SNR-9dB_3750_6250','269512822182309858202778522982212658349_sym-fm8-SNR-10.8dB_3750_6250','271269779920055217513661384700434954547_sym-fm4-SNR-9dB_11250_13750','275178104746213695279234605836108708664_sym-fm4-SNR-10.8dB_1250_3750','275783749893400817786102449654159494908_asym-fm2-SNR-10.8dB_6250_8750','281845356670920167685882519624066428796_sym-fm8-SNR-12dB_11250_13750','287231635215230665420862036228168339789_asym-fm2-SNR-6dB_1250_3750','287830477634105949273684035633459934561_asym-fm8-SNR-6dB_3750_6250','288935887971700623392624402463363859524_sym-fm8-SNR-0dB_8750_11250','299981712602357402250638997493512831300_sym-fm4-SNR-9dB_1250_3750','300011535376861068965933085425477761094_asym-fm8-SNR-0dB_3750_6250','300302427335487111527957651538039220359_asym-fm8-SNR-0dB_1250_3750','305283515332624891888467815234120670372_sym-fm2-SNR-9dB_1250_3750','308556835941084426696151343747383778285_asym-fm8-SNR-9dB_3750_6250','311065547437237803399992215698590841189_asym-fm2-SNR-12dB_11250_13750','312832972675604685998777227653051368364_sym-fm2-SNR-10.8dB_8750_11250','31374755318734456933707291388953182_asym-fm4-SNR-0dB_8750_11250','314424305351167864163554000133854041787_sym-fm4-SNR-9dB_6250_8750','320577711450055064122348748392472810130_sym-fm2-SNR-6dB_1250_3750','321097700614116151148055737762814959373_asym-fm4-SNR-10.8dB_1250_3750','323806809293356797219513001979645594778_sym-fm8-SNR-9dB_11250_13750','324367988954291176135924212933382671252_sym-fm4-SNR-0dB_8750_11250','328334031720832279403446472887676652040_asym-fm4-SNR-12dB_8750_11250','328946256682204348160171077638275463781_sym-fm4-SNR-6dB_1250_3750','329431773875248177102392064620740607625_asym-fm4-SNR-6dB_8750_11250','33163927502523146432765038182319156874_sym-fm8-SNR-0dB_11250_13750','334308056527180430351818366341737437655_asym-fm8-SNR-0dB_6250_8750','3621845667734640051200559466389021623_sym-fm8-SNR-6dB_6250_8750','36978958101474340128239670614220167766_sym-fm2-SNR-12dB_1250_3750','39976214882386914895408929216695239522_asym-fm8-SNR-12dB_8750_11250','41010419530641005163773837475294148617_sym-fm2-SNR-10.8dB_11250_13750','42157430995453535446284431401587749350_sym-fm2-SNR-6dB_8750_11250','44373663663760341525696535388811745687_asym-fm8-SNR-10.8dB_11250_13750','44785518456666472185283785554994819920_asym-fm8-SNR-10.8dB_8750_11250','45595830610051272980466381777522811893_asym-fm4-SNR-0dB_1250_3750','45830024586375341188001849789094979377_sym-fm2-SNR-9dB_6250_8750','45883942581810867500798451011016517254_sym-fm2-SNR-6dB_6250_8750','46703656826412496783344541681392500045_sym-fm4-SNR-0dB_6250_8750','49874626956555454365799307391437319555_sym-fm8-SNR-0dB_6250_8750','50569247416763755797235193773421667961_sym-fm2-SNR-0dB_11250_13750','52890446348324699772697011573897452064_sym-fm2-SNR-6dB_11250_13750','54745548622106086162577635509032801537_asym-fm2-SNR-10.8dB_3750_6250','56600895581208840834810581917736678039_asym-fm8-SNR-6dB_6250_8750','56756818909516704925197901476810371048_asym-fm4-SNR-0dB_6250_8750','57573432577498055313118095739005522466_asym-fm2-SNR-6dB_3750_6250','59936385657722380651909177446982791689_sym-fm4-SNR-6dB_6250_8750','603962197767583433347254667912023341_sym-fm8-SNR-12dB_3750_6250','60778443416566816526648989535845858130_sym-fm8-SNR-9dB_8750_11250','61871360200100626412411727402443661708_sym-fm4-SNR-9dB_3750_6250','64440115257179336188635426989947027393_sym-fm4-SNR-10.8dB_11250_13750','65304200756006426008864090709742145303_sym-fm4-SNR-6dB_8750_11250','65355551213441478948215956289617678711_sym-fm4-SNR-9dB_8750_11250','65406715677090344599506829607689885837_asym-fm4-SNR-0dB_3750_6250','75638105818974792311069590591285260634_sym-fm2-SNR-12dB_8750_11250','76211773845615802425220953159681086204_asym-fm2-SNR-9dB_1250_3750','7841340062079181374969621318617826311_asym-fm8-SNR-9dB_1250_3750','84535738702207038447888961300707200420_sym-fm2-SNR-0dB_8750_11250','9247235566151451320858828191280595929_asym-fm4-SNR-9dB_6250_8750','93253425297881063387330356425029220074_asym-fm8-SNR-0dB_11250_13750','93576762037668213048976794277950866483_asym-fm8-SNR-9dB_6250_8750','9391743859203713536498501981880577954_asym-fm8-SNR-6dB_11250_13750','98791882420541564542317388894776230098_asym-fm4-SNR-10.8dB_6250_8750']
        
        # Remove any pictures that have already been annotated
        
        for pic in self.pictures:
            if picture_store.exists(pic):
                self.pictures.remove(pic)
        # Get total number of pictures to gauge progress
        self.prog_max = 150
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
        end.ids.label.text = 'Congratulations ' + user_age + '!'

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
            #     self.ids.ranking.text = 'Excellent!'
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
        tutorial_store.put('168089579195138435052688436154129832211_asym-fm8-SNR-10.8dB_1250_3750',score=0.4)
        tutorial_store.put('174442612141194238873224375686072419562_asym-fm2-SNR-12dB_3750_6250',score=0.9)
        tutorial_store.put('178862807259226734486968335982766821380_asym-fm2-SNR-9dB_3750_6250',score=0.8)
        tutorial_store.put('179097582148436985421847206656444753777_asym-fm2-SNR-12dB_6250_8750',score=0.9)
        tutorial_store.put('179365326678401730378262172012142964146_asym-fm4-SNR-10.8dB_3750_6250',score=0.6)
        tutorial_store.put('195232381564377623846303997609484555481_asym-fm2-SNR-0dB_8750_11250',score=0.4)
        tutorial_store.put('197250813900725360465554191657869366102_asym-fm2-SNR-6dB_6250_8750',score=0.4)
        tutorial_store.put('201424563683795520236258902270817027515_asym-fm4-SNR-9dB_3750_6250',score=0.5)
        tutorial_store.put('208340137673882521745057930969422605866_asym-fm2-SNR-0dB_1250_3750',score=0.5)
        tutorial_store.put('208665533463938898943277279255507733293_asym-fm8-SNR-6dB_8750_11250',score=0.1)
        tutorial_store.put('209388692161082133116062067516565520379_asym-fm8-SNR-10.8dB_3750_6250',score=0.3)
        tutorial_store.put('215833854604085183509413457729854952659_asym-fm8-SNR-12dB_3750_6250',score=0.5)
        tutorial_store.put('217606020336159857142290641964680311438_asym-fm4-SNR-9dB_8750_11250',score=0.4)
        tutorial_store.put('227358437226967795548732473100741069538_asym-fm8-SNR-9dB_11250_13750',score=0.3)
        tutorial_store.put('229410803766004824323543852409436589729_asym-fm2-SNR-10.8dB_11250_13750',score=0.8)
        tutorial_store.put('233798913395705877385494458885112721394_asym-fm2-SNR-10.8dB_8750_11250',score=0.9)
        tutorial_store.put('235439208951830345038064020158797970900_asym-fm8-SNR-12dB_11250_13750',score=0.4)
        # Add all pictures in tutorial folder to list
        self.pictures = ['168089579195138435052688436154129832211_asym-fm8-SNR-10.8dB_1250_3750','174442612141194238873224375686072419562_asym-fm2-SNR-12dB_3750_6250','178862807259226734486968335982766821380_asym-fm2-SNR-9dB_3750_6250','179097582148436985421847206656444753777_asym-fm2-SNR-12dB_6250_8750','179365326678401730378262172012142964146_asym-fm4-SNR-10.8dB_3750_6250','195232381564377623846303997609484555481_asym-fm2-SNR-0dB_8750_11250','197250813900725360465554191657869366102_asym-fm2-SNR-6dB_6250_8750','201424563683795520236258902270817027515_asym-fm4-SNR-9dB_3750_6250','208340137673882521745057930969422605866_asym-fm2-SNR-0dB_1250_3750','208665533463938898943277279255507733293_asym-fm8-SNR-6dB_8750_11250','209388692161082133116062067516565520379_asym-fm8-SNR-10.8dB_3750_6250','215833854604085183509413457729854952659_asym-fm8-SNR-12dB_3750_6250','217606020336159857142290641964680311438_asym-fm4-SNR-9dB_8750_11250','227358437226967795548732473100741069538_asym-fm8-SNR-9dB_11250_13750','229410803766004824323543852409436589729_asym-fm2-SNR-10.8dB_11250_13750','233798913395705877385494458885112721394_asym-fm2-SNR-10.8dB_8750_11250','235439208951830345038064020158797970900_asym-fm8-SNR-12dB_11250_13750']
        print(self.pictures)
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
            if self.ranking < 0.02:
                self.ids.ranking.text = 'Excellent'
            elif self.ranking < 0.05:
                self.ids.ranking.text = 'Very Good'
            elif self.ranking < 0.1:
                self.ids.ranking.text = 'Good'
            elif self.ranking < 0.2:
                self.ids.ranking.text = 'OK'
            elif self.ranking < 0.5:
                self.ids.ranking.text = 'Not Quite'

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
                self.ids.pb.value = self.counter

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
