# Need to pre-install: pyttsx3, SpeechRecognition
#--trusted-host pypi.org --trusted-host files.pythonhosted.org
import pyttsx4
import speech_recognition as sr

# Our Avatar is responsible for:
# 1. Saying things - using text to speech
# 2. Listening for things - using Speech Recognition
#
# It has its own personal instance data:
# 1. Name
# 2. Useful things for system functions

# -------------------------------------------------------------------
# We use Text to Speech and Speech Recognition

class Avatar:

    def __init__(self, name="Elsa"): #constructor method
        self.name = name
        self.initVoice()
        self.initSR()
        self.introduce()

    def initSR(self):
        self.sample_rate = 48000
        self.chunk_size = 2048
        self.r = sr.Recognizer()
        self.useSR = False  # set this to True if using Speech Recognition

    def initVoice(self):
        '''
        Method: Initialise Text to Speech
        '''
        self.__engine = pyttsx4.init()
        self.__voices = self.__engine.getProperty('voices')
        self.__vix = 1
        self.__voice = self.__voices[self.__vix].id
        self.__engine.setProperty('voice', self.__voice)
        self.__engine.setProperty('rate', 150)
        self.__engine.setProperty('volume', 1.0)

    def say(self, words):
        self.__engine.say(words, self.name)
        self.__engine.runAndWait()

    def speak(self, words):
        print(words)
        self.__engine.say(words, self.name)
        self.__engine.runAndWait()

    def listen(self, prompt="I am listening, please speak:",useSR=True):
        words = ""
        if not useSR:
            useSR = self.useSR

        if useSR:
            try:
                #print(sr.Microphone.list_microphone_names())
                with sr.Microphone(sample_rate=self.sample_rate, chunk_size=self.chunk_size) as source:
                    # listen for 1 second to calibrate the energy threshold for ambient noise levels
                    self.r.adjust_for_ambient_noise(source)
                    self.say(prompt)
                    audio = self.r.listen(source)
                try:
                    #print("You said: '" + r.recognize_google(audio)+"'")
                    words = self.r.recognize_google(audio)
                except sr.UnknownValueError:
                    self.say("Could not understand what you said.")
                except sr.RequestError as e:
                    self.say("Could not request results; {0}".format(e))

            except:
                self.say(prompt)
                words = input(f"{prompt}")
        else:
            self.say(prompt, False)
            words = input(prompt)
        return words

    def introduce(self):
        self.say(f"Hello. My name is {self.name}")

# This is our test harness - that tests the Avatar functions to see if they work properly
def main():
    teacher = Avatar("Bob")
    teacher.say("How are you today?")
    #word = "hello"
    #for letter in word:
    #    teacher.say(letter)
    teacher.say(f"You said: {teacher.listen("say something: ")}")

if __name__ == "__main__":
    main()