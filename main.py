#
# This file is part of The Principles of Modern Game AI.
# Copyright (c) 2015, AiGameDev.com KG.
#

import vispy                    # Main application support.
import window                   # Terminal input and display.
import nltk.chat
import win32com.client

class HAL9000(object):

    def __init__(self, terminal):
        """Constructor for the agent, stores references to systems and initializes internal memory.
        """
        self.terminal = terminal
        self.location = 'unknown'
        self.output_count = 0
        self.rooms = [r'kitchen', r'hangar', r'bridge']
        self.room_items = {
            r'kitchen': [r'fridge', r'cooker', r'gas tank'],
            r'hangar': [r'locked crate', r'container', r'shipping log'],
            r'bridge': [r'map', r'control panel', r'captain seat'],
        }

        agent_responses = [
            (r'([\w\s]*?)where am i([\w\s]*?)([\?\.\!]??)', # Pattern
             ['You are in the {}.'.format(self.location)]),

            (r'([\w\s]*?)you are ([\w\s]+)([\?\.\!]??)', # Pattern
             ['Yes, I am %2.', # Response 1a.
              'Oh, sooo %2.']),

            (r'([\w\s]*?)are you ([\w\s]+)([\?\.\!]??)', # Pattern
             ["Why would you think I am %2?",
              "Would you like me to be %2?"]),

            (r'', # Pattern
             ["Is everything OK?",
              "Can you still communicate?"])
        ]
        self.chatbot = nltk.chat.Chat(agent_responses, nltk.chat.util.reflections)

        self.voice = win32com.client.Dispatch("SAPI.SpVoice")

    def on_input(self, evt):
        """Called when user types anything in the terminal, connected via event.
        """
        response = self.chatbot.respond(evt.text.lower())
        if self.output_count == 0:
            response = r'Hi, ' + response

        self.terminal.log(response, align='right', color='#00805A')

        self.voice.Speak(response)

        self.output_count += 1

    def on_command(self, evt):
        """Called when user types a command starting with `/` also done via events.
        """
        if evt.text == 'quit':
            vispy.app.quit()

        elif evt.text.startswith('relocate'):
            self.location = evt.text[9:]
            self.terminal.log('', align='center', color='#404040')
            self.terminal.log('\u2014 Now in the {}. \u2014'.format(self.location), \
            align='center', color='#404040')

        elif evt.text.startswith('rooms'):
            self.terminal.log('', align='center', color='#404040')
            self.terminal.log('\u2014 Valid rooms are: {}. \u2014'.format(self.rooms), \
            align='center', color='#404040')

        elif evt.text.startswith('relocate'):
            target_location = evt.text[9:]
            if target_location in self.rooms:
                self.location = target_location
                self.terminal.log('', align='center', color='#404040')
                self.terminal.log('\u2014 Now in the {}. \u2014'.format(target_location), \
                    align='center', color='#404040')
                self.terminal.log(target_location in self.rooms, \
                    align='center', color='#404040')
            else:
                self.terminal.log('', align='center', color='#404040')
                self.terminal.log('\u2014 {} is not a valid room. \u2014'.format(target_location), \
                    align='center', color='#404040')

        else:
            self.terminal.log('Command `{}` unknown.'.format(evt.text), \
            align='left', color='#ff3000')
            self.terminal.log("I'm afraid I can't do that.", align='right', color='#00805A')

    def update(self, _):
        """Main update called once per second via the timer.
        """
        pass


class Application(object):

    def __init__(self):
        # Create and open the window for user interaction.
        self.window = window.TerminalWindow()

        # Print some default lines in the terminal as hints.
        self.window.log('Operator started the chat.', align='left', color='#808080')
        self.window.log('HAL9000 joined.', align='right', color='#808080')

        # Construct and initialize the agent for this simulation.
        self.agent = HAL9000(self.window)

        # Connect the terminal's existing events.
        self.window.events.user_input.connect(self.agent.on_input)
        self.window.events.user_command.connect(self.agent.on_command)

    def run(self):
        timer = vispy.app.Timer(interval=1.0)
        timer.connect(self.agent.update)
        timer.start()

        vispy.app.run()


if __name__ == "__main__":
    vispy.set_log_level('WARNING')
    vispy.use(app='glfw')

    app = Application()
    app.run()
