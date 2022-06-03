import cv2
from kivy.app import App
from kivy.core.camera import Camera
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ListProperty
from kivy.animation import Animation
from kivy.metrics import dp
import gtts
from playsound import playsound
import json
import os
import ast
from kivy.uix.widget import Widget
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.core.window import Window
import speech_recognition as sr
import pyttsx3


from pyzbar import pyzbar

Window.size = (350,600)

KV = '''
#:import RGBA kivy.utils.rgba

<ImageButton@ButtonBehavior+Image>:
    size_hint: None, None
    size: self.texture_size

    canvas.before:
        PushMatrix
        Scale:
            origin: self.center
            x: .75 if self.state == 'down' else 1
            y: .75 if self.state == 'down' else 1

    canvas.after:
        PopMatrix

BoxLayout:
    orientation: 'vertical'
    padding: dp(5), dp(5)
    RecycleView:
        id: rv
        data: app.messages
        viewclass: 'Message'
        do_scroll_x: False

        RecycleBoxLayout:
            id: box
            orientation: 'vertical'
            size_hint_y: None
            size: self.minimum_size
            default_size_hint: 1, None
            # magic value for the default height of the message
            default_size: 0, 38
            key_size: '_size'

    FloatLayout:
        size_hint_y: None
        height: 0
        Button:
            size_hint_y: None
            height: self.texture_size[1]
            opacity: 0 if not self.height else 1
            text:
                (
                'go to last message'
                if rv.height < box.height and rv.scroll_y > 0 else
                ''
                )
            pos_hint: {'pos': (5, 0)}
            on_release: app.scroll_bottom()
        
        Camera:
            id: camera
            resolution: (940, 980)
            play: False
        Button:
            text: 'Enrichisser dictionnaire'
            size_hint_y: None
            height: '38dp'
            on_release:app.Qr_Reader()
            on_press: camera.play

    BoxLayout:
        size_hint: 1, None
        size: self.minimum_size
        TextInput:
            id: ti
            size_hint: 1, None
            height: min(max(self.line_height, self.minimum_height), 150)
            multiline: False

            on_text_validate:
                app.send_message(self)

        ImageButton:
            source: 'data/logo/kivy-icon-48.png'
            on_release:
                app.send_message(ti)

<Message@FloatLayout>:
    message_id: -1
    bg_color: '#223344'
    side: 'left'
    text: ''
    size_hint_y: None
    _size: 0, 0
    size: self._size
    text_size: None, None
    opacity: min(1, self._size[0])

    Label:
        text: root.text
        padding: 10, 10
        size_hint: None, 1
        size: self.texture_size
        text_size: root.text_size

        on_texture_size:
            app.update_message_size(
            root.message_id,
            self.texture_size,
            root.width,
            )

        pos_hint:
            (
            {'x': 0, 'center_y': .5}
            if root.side == 'left' else
            {'right': 1, 'center_y': .5}
            )

        canvas.before:
            Color:
                rgba: RGBA(root.bg_color)
            RoundedRectangle:
                size: self.texture_size
                radius: dp(5), dp(5), dp(5), dp(5)
                pos: self.pos

        canvas.after:
            Color:
            Line:
                rounded_rectangle: self.pos + self.texture_size + [dp(5)]
                width: 1.01
'''

class MessengerApp(App):
    messages = ListProperty()

    def build(self):
        return Builder.load_string(KV)


    def Qr_Reader(self):
        cap = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_PLAIN

        while True:
            _, BoxLayout = cap.read()

            decodedObjects = pyzbar.decode(BoxLayout)
            for obj in decodedObjects:
                cv2.putText(BoxLayout, str(obj.data), (50, 50), font, 2,
                            (255, 0, 0), 3)
                print(obj.data)
                scannedPic=obj.data
                print(type(scannedPic))

                #add scanned pic to json file
                scannedPic = scannedPic.decode("UTF-8")
                mydata = ast.literal_eval(scannedPic)
                print(repr(mydata))
                print(type(mydata))
                with open("data.json", "r+") as fi:
                    data = json.load(fi)
                    data.update(mydata)
                    fi.seek(0)
                    json.dump(data, fi)



            key = cv2.waitKey(1)
            if key == 27:
                break

    def add_message(self, text, side, color):
        # create a message for the recycleview
        self.messages.append({
            'message_id': len(self.messages),
            'text': text,
            'side': side,
            'bg_color': color,
            'text_size': [None, None],
        })

    def update_message_size(self, message_id, texture_size, max_width):
        if max_width == 0:
            return

        one_line = dp(50)

        # if the texture is too big, limit its size
        if texture_size[0] >= max_width * 2 / 3:
            self.messages[message_id] = {
                **self.messages[message_id],
                'text_size': (max_width * 2 / 3, None),
            }

        # if it was limited, but is now too small to be limited, raise the limit
        elif texture_size[0] < max_width * 2 / 3 and \
                texture_size[1] > one_line:
            self.messages[message_id] = {
                **self.messages[message_id],
                'text_size': (max_width * 2 / 3, None),
                '_size': texture_size,
            }

        else:
            self.messages[message_id] = {
                **self.messages[message_id],
                '_size': texture_size,
            }

    @staticmethod
    def focus_textinput(textinput):
        textinput.focus = True

    def send_message(self, textinput):
        text = textinput.text
        textinput.text = ''
        self.add_message(text, 'right', '#223344')
        self.focus_textinput(textinput)
        Clock.schedule_once(lambda *args: self.SpecificationReply(text), 1)
        self.scroll_bottom()



    def addToJson(self, text, *args):
        self.add_message('Please insert the meaninig of this word ', 'left', '#332211')
        t1 = gtts.gTTS("thank you for teatch me other words , what do you mean ?")
        t1.save("yes.mp3")
        playsound("yes.mp3")
        textval = text
        print(textval)
        dictAdd = {text: textval}

        with open("data.json", "r+") as fi:
            data = json.load(fi)
            data.update(dictAdd)
            fi.seek(0)
            json.dump(data, fi)

    def answer(self, text, *args):
        if not (text == "yes"):
            try:
                JsonFile = open("data.json", "r")
                jsonContent = JsonFile.read()
                resJson = json.loads(jsonContent)
                result = resJson[text.lower()]
                print(result)
                self.add_message(result, 'left', '#332211')
            except:
                self.add_message('Input not found ', 'left', '#332211')
                t1 = gtts.gTTS("Incomprehensible input , Would you like to add this key meanning ?")
                t1.save("error.mp3")
                playsound("error.mp3")

        #else:
        #    self.add_message('Please insert the meaninig of this word ', 'left', '#332211')
        #    t1 = gtts.gTTS("thank you for teatch me other words , what do you mean ?")
        #    t1.save("yes.mp3")
        #    playsound("yes.mp3")
        #    textval = text
        #    print(textval)
        #    print(key)
        #    dictAdd = {text: textval}

        #   with open("data.json", "r+") as fi:
        #        data = json.load(fi)
        #        data.update(dictAdd)
        #        fi.seek(0)
        #        json.dump(data, fi)

    def SpecificationReply(self, text, *args):
        JsonFile = open("data.json", "r")
        jsonContent = JsonFile.read()
        key = text

        if text in jsonContent:
            print("true")
            JsonFile = open("data.json", "r")
            jsonContent = JsonFile.read()
            resJson = json.loads(jsonContent)
            result = resJson[text.lower()]
            print(result)
            self.add_message(result, 'left', '#332211')
        else:
            self.add_message('what do you mean ?', 'left', '#332211')
            t1 = gtts.gTTS("Incomprehensible input , what do you mean ?")
            t1.save("error.mp3")
            file = "error.mp3"
            os.system("mpg123 " + file)

            val = text
            print(val)

            dictAdd = {key: val}

            with open("data.json", "r+") as fi:
                data = json.load(fi)
                data.update(dictAdd)
                fi.seek(0)
                json.dump(data, fi)

    def scroll_bottom(self):
        rv = self.root.ids.rv
        box = self.root.ids.box
        if rv.height < box.height:
            Animation.cancel_all(rv, 'scroll_y')
            Animation(scroll_y=0, t='out_quad', d=.5).start(rv)


if __name__ == '__main__':
    MessengerApp().run()
