from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix import floatlayout, label
Builder.load_string("""
<MenuScreen>:
    BoxLayout:
        Button:
            text: 'Goto settings'
            on_press: root.manager.current = 'settings'
        Button:
            text: 'Quit'
    FloatLayout:
        size: (1,1)
        Label:
            pos_hint: {'y': 0.48,'x': 0.48}
            text: '100'
        Label:
            pos_hint: {'y': .288,'x': 0.48}
            text: ' 80'
        Label:
            pos_hint: {'y': 0.096,'x': 0.48}
            text: ' 60'
        Label:
            pos_hint: {'y': -0.096,'x': 0.48}
            text: ' 40'
        Label:
            pos_hint: {'y': -0.288,'x': 0.48}
            text: ' 20'
        Label:
            pos_hint: {'y': -0.48,'x': 0.48}
            text: '  0'

    

<SettingsScreen>:
    BoxLayout:
        Button:
            text: 'My settings button'
        Button:
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'
""")

# Declare both screens
class MenuScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

# Create the screen manager
sm = ScreenManager()
sm.add_widget(MenuScreen(name='menu'))
sm.add_widget(SettingsScreen(name='settings'))

class TestApp(App):

    def build(self):
        return sm

if __name__ == '__main__':
    TestApp().run()