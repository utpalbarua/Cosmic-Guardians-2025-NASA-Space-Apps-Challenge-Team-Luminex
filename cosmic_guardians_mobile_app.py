from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
from kivy.properties import StringProperty, DictProperty, NumericProperty
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivymd.app import MDApp
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.list import OneLineListItem
from kivymd.toast import toast
from random import choice, randint
import json
import os
import threading

# Optional: Window.size = (360, 800)  # for desktop testing

KV = """
ScreenManager:
    SplashScreen:
    MainMenuScreen:
    CharacterSelectScreen:
    ChapterSelectScreen:
    GamePlayScreen:
    ForecastLabScreen:

<SplashScreen>:
    name: 'splash'
    MDFloatLayout:
        md_bg_color: app.theme_cls.primary_dark
        Image:
            source: 'assets/sun_icon.png' if app.asset_exists('assets/sun_icon.png') else ''
            size_hint: .4, .4
            pos_hint: {'center_x':.5, 'center_y':.6}
        MDLabel:
            text: 'Cosmic Guardians'
            font_style: 'H3'
            halign: 'center'
            pos_hint: {'center_x':.5, 'center_y':.35}
            theme_text_color: 'Custom'
            text_color: 1,1,1,1
        MDLabel:
            text: 'Defend Earth. Decode the Sun.'
            halign: 'center'
            pos_hint: {'center_x':.5, 'center_y':.28}
            theme_text_color: 'Custom'
            text_color: 1,1,1,1

<MainMenuScreen>:
    name: 'menu'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: 'Mission Control'
            left_action_items: [['menu', lambda x: None]]
        ScrollView:
            MDList:
                OneLineListItem:
                    text: 'Start Mission'
                    on_release: app.root.current = 'character'
                OneLineListItem:
                    text: 'Forecasting Lab'
                    on_release: app.root.current = 'forecast'
                OneLineListItem:
                    text: 'Solar Journal'
                    on_release: app.open_journal()
                OneLineListItem:
                    text: 'Settings'
                    on_release: app.open_settings()
                OneLineListItem:
                    text: 'Exit'
                    on_release: app.stop()

<CharacterSelectScreen>:
    name: 'character'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: 'Choose Perspective'
            left_action_items: [['arrow-left', lambda x: app.go_back()]]
        MDGridLayout:
            cols: 2
            padding: dp(12)
            spacing: dp(12)
            MDCard:
                size_hint: None, None
                size: dp(160), dp(240)
                elevation: 6
                padding: dp(8)
                MDBoxLayout:
                    orientation: 'vertical'
                    Image:
                        source: 'assets/guardian.png' if app.asset_exists('assets/guardian.png') else ''
                    MDLabel:
                        text: 'Guardian (Human)'
                        halign: 'center'
                    MDRaisedButton:
                        text: 'Select'
                        pos_hint: {'center_x': .5}
                        on_release: app.select_character('guardian')
            MDCard:
                size_hint: None, None
                size: dp(160), dp(240)
                elevation: 6
                padding: dp(8)
                MDBoxLayout:
                    orientation: 'vertical'
                    Image:
                        source: 'assets/solar.png' if app.asset_exists('assets/solar.png') else ''
                    MDLabel:
                        text: 'Solar Phenomena'
                        halign: 'center'
                    MDRaisedButton:
                        text: 'Select'
                        pos_hint: {'center_x': .5}
                        on_release: app.select_character('solar')

<ChapterSelectScreen>:
    name: 'chapters'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: 'Select Chapter'
            left_action_items: [['arrow-left', lambda x: app.go_back()]]
        ScrollView:
            MDList:
                OneLineListItem:
                    text: 'Chapter 1 — Heliographic Heights (Tutorial)'
                    on_release: app.start_chapter(1)
                OneLineListItem:
                    text: 'Chapter 2 — Solar Wind Routes (Intermediate)'
                    on_release: app.start_chapter(2)
                OneLineListItem:
                    text: 'Chapter 3 — CME Voyage (Advanced)'
                    on_release: app.start_chapter(3)
                OneLineListItem:
                    text: 'Chapter 4 — Magnetosphere Dance (Advanced)'
                    on_release: app.start_chapter(4)
                OneLineListItem:
                    text: 'Chapter 5 — Terrestrial Impact Zone (Scenario)'
                    on_release: app.start_chapter(5)

<GamePlayScreen>:
    name: 'game'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: 'Mission'
            left_action_items: [['arrow-left', lambda x: app.go_back()]]
        MDLabel:
            id: mission_text
            text: root.mission_text
            halign: 'center'
            size_hint_y: None
            height: dp(80)
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(12)
            spacing: dp(12)
            MDLabel:
                text: 'Situation:'
                halign: 'left'
            MDCard:
                size_hint_y: None
                height: dp(160)
                MDLabel:
                    id: situation_label
                    text: root.situation
                    halign: 'left'
                    padding: dp(12)
            MDLabel:
                text: 'Choose Action:'
            MDRaisedButton:
                text: 'Protect Satellite — Reduce risk to comms'
                on_release: root.make_choice('protect_sat')
            MDRaisedButton:
                text: 'Reroute Power — Ground grid mitigation'
                on_release: root.make_choice('reroute_power')
            MDRaisedButton:
                text: 'Do Nothing — observe and record'
                on_release: root.make_choice('observe')

<ForecastLabScreen>:
    name: 'forecast'
    MDBoxLayout:
        orientation: 'vertical'
        MDTopAppBar:
            title: 'Forecasting Lab'
            left_action_items: [['arrow-left', lambda x: app.go_back()]]
        MDLabel:
            text: 'Simulated NASA data & AI forecasting'
            halign: 'center'
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(12)
            spacing: dp(8)
            MDLabel:
                text: 'Latest solar index (simulated):'
            MDLabel:
                id: solar_index
                text: root.solar_index_text
                halign: 'center'
            MDLabel:
                text: 'AI Forecast (confidence):'
            MDLabel:
                id: forecast_label
                text: root.forecast_text
                halign: 'center'
            MDRaisedButton:
                text: 'Run Forecast'
                on_release: root.run_forecast()
            MDRaisedButton:
                text: 'Fetch NASA data (placeholder)'
                on_release: root.fetch_nasa_data()
"""


class SplashScreen(Screen):
    pass


class MainMenuScreen(Screen):
    pass


class CharacterSelectScreen(Screen):
    pass


class ChapterSelectScreen(Screen):
    pass


class GamePlayScreen(Screen):
    mission_text = StringProperty('')
    situation = StringProperty('')

    def on_pre_enter(self, *args):
        # Set up a random situation based on selected chapter
        app = MDApp.get_running_app()
        ch = app.state.get('chapter', 1)
        if app.state.get('perspective') == 'solar':
            self.mission_text = f'Solar Chronicle — Chapter {ch}'
        else:
            self.mission_text = f'Guardian Mission — Chapter {ch}'
        self.situation = app.generate_situation(ch)

    def make_choice(self, choice_key):
        app = MDApp.get_running_app()
        result, explanation = app.evaluate_choice(choice_key)
        Snackbar(text=f'Result: {result} — {explanation}').open()
        # Save mission outcome to journal
        app.append_journal({'chapter': app.state.get('chapter'), 'choice': choice_key, 'result': result})


class ForecastLabScreen(Screen):
    solar_index_text = StringProperty('N/A')
    forecast_text = StringProperty('No forecast run yet')

    def on_pre_enter(self, *args):
        # show existing simulated index
        self.solar_index_text = str(MDApp.get_running_app().state.get('solar_index', '0'))

    def run_forecast(self):
        # Simulate an AI forecast — in real app you'd call a model/service
        app = MDApp.get_running_app()
        si = app.state.get('solar_index', randint(0, 300))
        confidence = randint(50, 98)
        txt = f"High activity likely (index {si}) — confidence {confidence}%"
        self.forecast_text = txt
        app.state['last_forecast'] = {'index': si, 'confidence': confidence}
        toast('Forecast complete')

    def fetch_nasa_data(self):
        # Placeholder for NASA API integration — network code should run in a thread
        toast('Fetching NASA data — placeholder')
        # Example function in app: app.fetch_nasa_placeholder()
        threading.Thread(target=MDApp.get_running_app().fetch_nasa_placeholder).start()


class CosmicSM(ScreenManager):
    pass


class CosmicApp(MDApp):
    state = DictProperty({})
    store = None

    def build(self):
        self.theme_cls.primary_palette = 'BlueGray'
        self.theme_cls.theme_style = 'Dark'
        self.store = JsonStore('cosmic_guardians_save.json')
        # load state if exists
        if self.store.exists('state'):
            try:
                self.state = self.store.get('state')['data']
            except Exception:
                self.state = {}
        else:
            self.state = {'perspective': 'guardian', 'chapter': 1, 'solar_index': 42, 'journal': []}
        root = Builder.load_string(KV)
        # schedule splash -> menu
        Clock.schedule_once(self.go_menu, 1.6)
        return root

    def go_menu(self, dt):
        self.root.current = 'menu'

    def go_back(self):
        # simple back navigation
        if self.root.current == 'menu':
            return
        self.root.transition = SlideTransition(direction='right')
        self.root.current = 'menu'

    def select_character(self, c):
        self.state['perspective'] = c
        self.save_state()
        toast(f'Perspective set to {c}')
        self.root.current = 'chapters'

    def start_chapter(self, n):
        self.state['chapter'] = n
        self.save_state()
        self.root.current = 'game'

    def generate_situation(self, chapter):
        # creates a human-readable situation description based on chapter and perspective
        p = self.state.get('perspective', 'guardian')
        if p == 'solar':
            scenarios = [
                'You are a flare racing across the solar surface — will you brighten a stream or dissipate?',
                'You are a CME, shaping a massive wave — choose how concentrated your burst will be.',
            ]
        else:
            scenarios = [
                'Geomagnetic storm incoming — a satellite reports increased noise in communications.',
                'Power grid sensors show a spike — a CME-affected region might experience outages.',
                'High-latitude communities report aurora — but infrastructure could be stressed.'
            ]
        return choice(scenarios)

    def evaluate_choice(self, choice_key):
        # Simple rules engine for the prototype
        ch = self.state.get('chapter', 1)
        if choice_key == 'protect_sat':
            return 'Success', 'Satellite systems hardened and comms preserved.'
        if choice_key == 'reroute_power':
            # depends on chapter severity
            if ch >= 4:
                return 'Partial Success', 'Some grid nodes still affected.'
            return 'Success', 'Power grid successfully rerouted.'
        return 'Observation Only', 'No immediate action taken; data collected.'

    def append_journal(self, entry: dict):
        j = self.state.get('journal', [])
        j.append({'entry': entry, 'time': Clock.get_time()})
        self.state['journal'] = j
        self.save_state()

    def open_journal(self):
        j = self.state.get('journal', [])
        if not j:
            Snackbar(text='Journal empty').open()
            return
        # quick view: open a dialog or print to console; here we show a toast for demo
        toast(f'Journal has {len(j)} entries')

    def open_settings(self):
        toast('Settings stub — add volume, data toggles, accessibility options')

    def save_state(self):
        try:
            self.store.put('state', data=self.state)
        except Exception as e:
            print('Save failed:', e)

    def fetch_nasa_placeholder(self):
        """
        Placeholder: where you'd call NASA/NOAA APIs to get real solar data.
        Example (not executed here):

        import requests
        resp = requests.get('https://api.nasa.gov/DONKI/FLR?api_key=DEMO_KEY')
        data = resp.json()
        # parse and store relevant indices
        """
        import time
        time.sleep(2)
        # simulate updating solar index
        new_index = randint(10, 400)
        self.state['solar_index'] = new_index
        self.save_state()
        # update UI on main thread
        Clock.schedule_once(lambda dt: setattr(self.root.get_screen('forecast'), 'solar_index_text', str(new_index)))
        Clock.schedule_once(lambda dt: toast('NASA data updated (simulated)'))

    def asset_exists(self, path):
        return os.path.exists(path)


if __name__ == '__main__':
    CosmicApp().run()
