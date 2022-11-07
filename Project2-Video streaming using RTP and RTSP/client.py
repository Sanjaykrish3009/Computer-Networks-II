from re import A, X
import kivy
kivy.require('1.0.7')
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from ClientHelper import Client
import sys
import threading

Builder.load_string("""
<Screen1>:
    RelativeLayout:
        cols:2
        spacing: 5

        Label:
            id:header_label
            text: "ENTER YOUR NAME"
            size_hint_y: 0.4
            pos_hint: {'center_x': .4, 'center_y': .7}
            color: (17/255,252/255,205/255,1)

        TextInput:
            id: name
            multiline: False
            size_hint: (0.15,0.05)
            pos_hint: {'center_x':.6, 'center_y':.7}
            background_normal: ''
            background_color: (234/255,237/255,236/255,1)

        Button:
            text: "JOIN"
            size_hint: (0.15,0.07)
            pos_hint: {'center_x': 0.5, 'center_y':0.4}

            on_press:
                root.client_details()
                
<Screen2>:
    RelativeLayout:
        Label:
            id: choose
            text: "SELECT YOUR CHOICE"
            size_hint_y: 0.4
            pos_hint: {'center_x': 0.5, 'center_y': 0.65}
            color: (17/255,252/255,205/255,1)
        
        Button:
            text: 'VIDEO STREAMING'
            size_hint: (0.2,0.1)
            pos_hint: {'center_x': 0.35, 'center_y': 0.45}
            on_press: 
                root.stream_type(1)
                root.manager.transiion = "left"
                root.manager.duration = 1
                root.manager.current = "Thirdtab"

        Button:
            text: 'LIVE STREAMING'
            size_hint: (0.2,0.1)
            pos_hint: {'center_x': 0.65, 'center_y': 0.45}
            on_press: 
                root.stream_type(2)
                root.manager.transiion = "left"
                root.manager.duration = 1
                root.manager.current = "Fifthtab"

<Screen3>:
    RelativeLayout:
        cols:2
        spacing: 5

        Label:
            id:header_label
            text: "ENTER FILE NAME"
            size_hint_y: 0.4
            pos_hint: {'center_x': .4, 'center_y': .7}
            color: (17/255,252/255,205/255,1)

        TextInput:
            id: file
            multiline: False
            size_hint: (0.15,0.05)
            pos_hint: {'center_x':.6, 'center_y':.7}
            background_normal: ''
            background_color: (234/255,237/255,236/255,1)

        Button:
            text: "REQUEST"
            size_hint: (0.15,0.07)
            pos_hint: {'center_x': 0.5, 'center_y':0.4}
            on_press: 
                root.file_details()
         

<Screen4>:
    RelativeLayout:
		size: root.width, root.height
		cols:1
		orientation: "vertical"
        Image:
            id: vid
            source: 'videostreaming.jpeg'
            size_hint: 1,0.8
            pos_hint: {'center_x': 0.5, 'center_y': 0.55}
		BoxLayout:
			cols:3
			spacing: 5

			Button:
				text: "SETUP"
				size_hint: (0.2,0.1)
				on_press: root.setup()

			Button:
				text: "RESET"
				size_hint: (0.2,0.1)
				on_press:root.reset()

			Button:
				text: "PLAY"
				size_hint: (0.2,0.1)
				on_press:root.play()

			Button:
				text: "PAUSE"
				size_hint: (0.2,0.1)
				on_press: root.pause() 

            Button:
				text: "TEARDOWN"
				size_hint: (0.2,0.1)
				on_press: root.teardown()


<Screen5>:
    RelativeLayout:
		size: root.width, root.height
		cols:1
		orientation: "vertical"
        Image:
            id: vid
            source: 'livestreaming.jpeg'
            size_hint: 1,0.8
            pos_hint: {'center_x': 0.5, 'center_y': 0.55}
		BoxLayout:
			cols:3
			spacing: 5

			Button:
				text: "SETUP"
				size_hint: (0.2,0.1)
				on_press: root.setup()

			Button:
				text: "PLAY"
				size_hint: (0.2,0.1)
				on_press:root.play()

			Button:
				text: "PAUSE"
				size_hint: (0.2,0.1)
				on_press: root.pause() 

            Button:
				text: "TEARDOWN"
				size_hint: (0.2,0.1)
				on_press: root.teardown()
""")

class Screen1(Screen):

    def __init__(self,screen_manager, login, **kw):

        super(Screen1,self).__init__(**kw)
        self.login = login
        self.screen_manager = screen_manager
    def client_details(self):
       
       self.login.client_details(self.screen_manager)

    def showpopup(self):
        content = RelativeLayout(cols=1)
        cancel = Button(text='Close',
                        size_hint= (0.25,0.15),
                        pos_hint= {'center_x': 0.5, 'center_y':0.4})
        content.add_widget(cancel)
        content.add_widget(Label(text='PLEASE ENTER A VALID NAME!',
                                 size_hint_y=0.5,
                                 pos_hint={'center_x': .5, 'center_y': .7},
                                 color=(17/255,252/255,205/255,1)))
        popup = Popup(title='Invalid Name',
                      title_align='center',
                      title_color=(1,0,0,1),
                      content=content,
                      auto_dismiss=False,
                      size_hint=(0.5,0.5))
        cancel.bind(on_press=popup.dismiss)
        # open the popup
        popup.open()
    
    def movetonext(self):
        self.manager.transiion = "left"
        self.manager.duration = 1
        self.manager.current = "Secondtab"

    

class Screen2(Screen):
    def __init__(self,screen_manager, login, **kw):

        super(Screen2,self).__init__(**kw)
        self.login = login
        self.screen_manager = screen_manager
    def stream_type(self, type):
       
       self.login.stream_type(type)

class Screen3(Screen):

    def __init__(self,screen_manager, login, **kw):
        super(Screen3,self).__init__(**kw)
        self.login = login
        self.screen_manager = screen_manager

    def file_details(self):
       
       self.login.file_details(self.screen_manager)
    
    def showpopup(self):
        content = RelativeLayout(cols=1)
        cancel = Button(text='Close',
                        size_hint= (0.25,0.15),
                        pos_hint= {'center_x': 0.5, 'center_y':0.4})
        content.add_widget(cancel)
        content.add_widget(Label(text=' REQUESTED FILE DOES NOT EXIST!',
                                 size_hint_y=0.5,
                                 pos_hint={'center_x': .5, 'center_y': .7},
                                 color=(17/255,252/255,205/255,1)))
        popup = Popup(title='Invalid Filename',
                      title_align='center',
                      title_color=(1,0,0,1),
                      content=content,
                      auto_dismiss=False,
                      size_hint=(0.5,0.5))
        cancel.bind(on_press=popup.dismiss)
        # open the popup
        popup.open()
    

    def movetonext(self):
        self.manager.transiion = "left"
        self.manager.duration = 1
        self.manager.current = "Fourthtab"


class Screen4(Screen):

    def __init__(self,screen_manager, login, **kw):

        super(Screen4,self).__init__(**kw)
        self.login = login
        self.screen_manager = screen_manager
    
    def setup(self):
        self.login.setup_video()
    
    def reset(self):
        self.login.reset_video()
    
    def play(self):
        self.login.play_video(self.screen_manager)
    
    def pause(self):
        self.login.pause_video()  

    def teardown(self):
        self.login.teardown_video()  

class Screen5(Screen):

    def __init__(self,screen_manager, login, **kw):

        super(Screen5,self).__init__(**kw)
        self.login = login
        self.screen_manager = screen_manager
    
    def setup(self):
        self.login.setup_video()
    
    def play(self):
        self.login.play_video(self.screen_manager)
    
    def pause(self):
        self.login.pause_video()  

    def teardown(self):
        self.login.teardown_video()  


class MyApp(App):

    icon = 'custom-kivy-icon.png'
    title = 'RTP Streaming Application'

    def __init__(self,serverAddr, serverPort, rtpPort, audioport):

        super(MyApp,self).__init__()

        self.serverAddr = serverAddr
        self.serverPort = serverPort
        self.rtpPort    = rtpPort
        self.audioport  = audioport

    def build(self):

        self.login = Client(serverAddr, serverPort, rtpPort, audioport)
        self.screen_manager = ScreenManager()

        screen1 = Screen1(self.screen_manager, self.login, name='LoginScreen')
        self.screen_manager.add_widget(screen1)

        screen2 = Screen2(self.screen_manager, self.login,name='Secondtab')
        self.screen_manager.add_widget(screen2)

        screen3 = Screen3(self.screen_manager, self.login, name='Thirdtab')
        self.screen_manager.add_widget(screen3)

        screen4 = Screen4(self.screen_manager,self.login,name='Fourthtab')
        self.screen_manager.add_widget(screen4)

        screen5 = Screen5(self.screen_manager,self.login,name='Fifthtab')
        self.screen_manager.add_widget(screen5)

        return self.screen_manager

if __name__ == "__main__":

    answer = input('Would you like to connect (yes/no)? ')
    if answer.lower() != 'yes':
        sys.exit()
    try:
        serverAddr = sys.argv[1]
        serverPort = sys.argv[2]
        rtpPort = sys.argv[3]
        audioport = sys.argv[4]
    except:
        print("[Usage: ClientLauncher.py Server_name Server_port Video_port Audio_port]\n"    )
    
    root = MyApp(serverAddr, serverPort, rtpPort, audioport)
    GUIthread = threading.Thread(target=root.run).start()
    
else:
    print("Enter Choice correctly")

