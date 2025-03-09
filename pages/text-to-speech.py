from pathlib import Path
from openai import OpenAI
from datetime import datetime
import os
from dotenv import load_dotenv
import streamlit as st
from content.tongue_twisters import TongueTwisters
import os
from pydub import AudioSegment

load_dotenv()

import os
from pydub import AudioSegment

class AudioCombiner:
    def __init__(self, directory):
        self.directory = directory
        self.audio_files = []

    def gather_audio_files(self):
        """Gathers all audio files from the specified directory, sorted by creation time."""
        audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.aac')
        # Create a list of tuples (file_path, creation_time)
        self.audio_files = [(file, os.path.getctime(os.path.join(self.directory, file))) 
                            for file in os.listdir(self.directory) 
                            if file.endswith(audio_extensions)]

        # Sort by creation time
        self.audio_files.sort(key=lambda x: x[1])  # Sort by the second element in the tuple (creation_time)

    def combine_audio_files(self, output_filename):
        """Combines the audio files into a single audio file."""
        if not self.audio_files:
            print("No audio files found to combine.")
            return

        combined = AudioSegment.empty()
        for audio_file, _ in self.audio_files:
            file_path = os.path.join(self.directory, audio_file)
            print(f"Combining {file_path}...")
            audio_segment = AudioSegment.from_file(file_path)
            combined += audio_segment

        output_path = os.path.join(self.directory, output_filename)
        combined.export(output_path, format=output_filename.split('.')[-1])
        print(f"Combined audio file saved as: {output_path}")

    def run(self, output_filename='combined_audio.mp3'):
        """Runs the process to combine audio files."""
        self.gather_audio_files()
        self.combine_audio_files(output_filename)

class OpenAITTS:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.models = {"tts-1":"tts-1", "tts-1-hd":"tts-1-hd"}
        self.model = self.models["tts-1"]
        self.voices = {"alloy":"alloy", "ash":"ash", "coral":"coral", "echo":"echo", "fable":"fable", "onyx":"onyx", "nova":"nova", "sage":"sage", "shimmer":"shimmer"}
        self.voice = self.voices["nova"]
        self.formats = {"mp3" : "mp3", "opus" : "opus", "aac" : "aac", "flac" : "flac", "wav" : "wav", "pcm" : "pcm"}
        self.format = self.formats["mp3"]
        self.languages_list = ["Afrikaans","Arabic","Armenian","Azerbaijani","Belarusian","Bosnian","Bulgarian","Catalan","Chinese","Croatian","Czech","Danish","Dutch","English","Estonian","Finnish","French","Galician","German","Greek","Hebrew","Hindi","Hungarian","Icelandic","Indonesian","Italian","Japanese","Kannada","Kazakh","Korean","Latvian","Lithuanian","Macedonian","Malay","Marathi","Maori","Nepali","Norwegian","Persian","Polish","Portuguese","Romanian","Russian","Serbian","Slovak","Slovenian","Spanish","Swahili","Swedish","Tagalog","Tamil","Thai","Turkish","Ukrainian","Urdu","Vietnamese","Welsh"]
        languages = {}
        self.languages = self.set_languages(languages)
        self.language  = self.languages["English"]
        self.speed = 1.0
        
        self.cwd = Path.cwd()
        self.default_filename = f"{self.model}-{datetime.now().strftime('%Y%m%d%H%M%S')}.{self.format}"
        self.default_path = f"{self.cwd}/content/audio_clips/{self.default_filename}"
        self.audio_clips_dir = "content/audio_clips"
        self.audio_clips_path = f"{self.audio_clips_dir}/{self.default_filename}"
        
    # check for the existence of a directory and create it if it doesn't exist
    def check_directory(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory

    def create_custom_path(self, text):
        self.custom_directory = f"{self.cwd}/content/audio_clips/{text}"
        self.check_directory(self.custom_directory)
        self.custom_filename = f"{text}-{self.model}-{datetime.now().strftime('%Y%m%d%H%M%S')}.{self.format}"
        self.custom_path = f"{self.custom_directory}/{self.custom_filename}"
        return self.custom_path

    def set_languages(self, languages):
        for language in self.languages_list:
            languages[language] = language
        self.languages = languages
        return self.languages

    def create_speech(self, text, path=None, speed=None):
        if not path:
            path = self.default_path
        if not speed:
            speed = self.speed
        response = self.client.audio.speech.create(model=self.model,voice=self.voice,input=text,speed=self.speed)
        written_response = response.write_to_file(path)
        return written_response

class SetTextToAudioSessionStates:
    openai_tts = OpenAITTS()
    twists = TongueTwisters()
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        
    def instantiate_session_states(self, **kwargs):
        for key, value in kwargs.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def update_state(self, key, value):
        if self.check_session_state(key):
            st.session_state[key] = value
        else:
            st.session_state[key] = value

    def check_session_state(self, key):
        if key not in st.session_state:
            return False
        return True

    def get_state(self, key):
        return st.session_state[key]
    
    def update_openai_tts(self, key):
        if key == "model":
            openai_tts.model = st.session_state.model
        if key == "voice":
            openai_tts.voice = st.session_state.voice
            twists.voice = st.session_state.voice
            twists.identity_statement = twists.identify(st.session_state.voice)
        if key == "language":
            openai_tts.language = st.session_state.language
        if key == "format":
            openai_tts.format = st.session_state.format
        if key == "custom_path":
            openai_tts.custom_path = st.session_state.custom_path
        if key == "default_path":
            openai_tts.default_path = st.session_state.default_path
        if key == "speed":
            openai_tts.speed = st.session_state.speed
            
class FlattenData:
    def __init__(self):
        self.twists = TongueTwisters()
        self.classic_twists = twists.classic_twists
        self.quick_twists = twists.quick_twists
        self.triple_twists = twists.triple_twists
    
    def flatten_twists(self):
        twists = []
        twists.extend(self.classic_twists)
        twists.extend(self.quick_twists)
        twists.extend(self.triple_twists)
        return twists

# Instantiate the OpenAITTS class
openai_tts = OpenAITTS()
ss = SetTextToAudioSessionStates()
twists = TongueTwisters()
fd = FlattenData()
flat_twists = fd.flatten_twists()

ss.instantiate_session_states(text = "", 
             models = openai_tts.models,
             voices = openai_tts.voices,
             languages = openai_tts.languages,
             formats = openai_tts.formats,
             twists = twists.twists,
             flat_twists = flat_twists,
             model = openai_tts.model,
             voice = openai_tts.voices["alloy"],
             identity_statement = twists.identify("None"),
             language = openai_tts.language, 
             format = openai_tts.format,
             speed = openai_tts.speed,
             default_path = openai_tts.default_path,
             custom_path = None,
             options_cont = None,
             twist = twists.get_random_twist()
             )

# st.write(st.session_state)

st.title("Create Speech From Text")

# Text input and selections; persist to session state

with st.sidebar:
    # Input fields with their respective keys
    st.selectbox("Select a model"   ,options=list(openai_tts.models.keys())   ,key="model"   ,on_change=ss.update_openai_tts("model"))
    st.selectbox("Select a voice"   ,options=list(openai_tts.voices.keys())   ,key="voice"   ,on_change=ss.update_openai_tts("voice"))
    st.slider("Select a speed"      ,min_value=0.25, max_value=4.0, step=0.25 ,key="speed"   ,on_change=ss.update_openai_tts("speed"))
    st.selectbox("Select a format"  ,options=list(openai_tts.formats.keys())  ,key="format"  ,on_change=ss.update_openai_tts("format"))
    # st.selectbox("Select a language",options=list(openai_tts.languages.keys()),key="language",on_change=ss.update_openai_tts("language"))
    
# Autofill options
options_expander = st.expander("Auto Fill Test Options", expanded=False)
options_cont = options_expander.container(height=250,border=True, key='options_cont')
selected_twist = ""
ids = twists.identity_statement
with options_cont:
    voice_intro  = st.toggle("Add a voice introduction", value=False)
    if voice_intro == True:
        st.write(ids)
        add_to_text_body = st.button("Add Intro", key="added_intro")
        if add_to_text_body:
            st.session_state.text = st.session_state.text + ids + " "

    tongue_twister  = st.toggle("Add a tongue twister", value=False)
    if tongue_twister == True:
        selected_twister = st.selectbox("Select a Tongue Twister", options=flat_twists, key="selected_twister")
        st.write(selected_twister)
        add_to_text_body = st.button("Add Tongue Twister", key="added_tongue_twister")
        if add_to_text_body:
            st.session_state.text = st.session_state.text + selected_twister + " "
            
# Create the text area widget after setting the session state
text_area = st.text_area("Place Text Here To Convert To Speech", key="text_area", height=150, value=st.session_state.text)
st.session_state.text = text_area


col1, col2, col3 = st.columns([4,2,2])

with col1:
    if st.button("NothingButton NothingButton NothingButton NothingButton", key="nothing_button", disabled=True):
        pass

with col2:
    if st.button("CLEAR TEXT", key="clear_text"):
        st.session_state.text = ""
with col3:
    if st.button("GenerateSpeech", key="generate_speech"):
        openai_tts.model = st.session_state.model
        openai_tts.voice = st.session_state.voice
        openai_tts.format = st.session_state.format
        # openai_tts.language = st.session_state.language
        custom_path  = openai_tts.create_custom_path(st.session_state.voice)
        # print(openai_tts.model, openai_tts.voice,openai_tts.format, openai_tts.language)
        response = openai_tts.create_speech(text=st.session_state.text, path=custom_path)
        # st.success("Speech generated and saved to: {}".format(openai_tts.file_path))




# Assuming openai_tts is already defined with the appropriate directory and file format
audio_players = st.container(border=True)

with audio_players:
    voice_dirs = [d for d in os.listdir(openai_tts.audio_clips_dir) 
                  if os.path.isdir(os.path.join(openai_tts.audio_clips_dir, d))]

    for dir_name in voice_dirs:
        # Create an expander for each voice directory
        with st.expander(dir_name, expanded=False):
            voice_dir_path = os.path.join(openai_tts.audio_clips_dir, dir_name)
            audio_files = [f for f in os.listdir(voice_dir_path) if f.endswith(openai_tts.format)]

            # Initialize session state for checkboxes if not exists
            checkbox_key = f"selected_files_{dir_name}"
            if checkbox_key not in st.session_state:
                st.session_state[checkbox_key] = []

            # Create rows of 2 columns each
            num_files = len(audio_files)
            num_rows = (num_files + 1) // 2

            for row_idx in range(num_rows):
                cols = st.columns(2)
                for col_idx in range(2):
                    file_idx = row_idx * 2 + col_idx
                    if file_idx < num_files:
                        audio_path = os.path.join(voice_dir_path, audio_files[file_idx])

                        # Create a checkbox and audio player in each column
                        with cols[col_idx]:
                            checkbox = st.checkbox(
                                audio_files[file_idx],
                                key=f"checkbox_{dir_name}_{file_idx}"
                            )
                            if checkbox:
                                if audio_files[file_idx] not in st.session_state[checkbox_key]:
                                    st.session_state[checkbox_key].append(audio_files[file_idx])
                            else:
                                if audio_files[file_idx] in st.session_state[checkbox_key]:
                                    st.session_state[checkbox_key].remove(audio_files[file_idx])

                            st.audio(data=audio_path, format=f"audio/{openai_tts.format}")

            # Single combine button for the expander
            if st.button("Combine Selected Files", key=f"combine_{dir_name}"):
                if st.session_state[checkbox_key]:
                    # Create a new instance of AudioCombiner
                    audio_combiner = AudioCombiner(voice_dir_path)

                    # Only combine selected files
                    audio_combiner.audio_files = [(f, os.path.getctime(os.path.join(voice_dir_path, f))) 
                                                for f in st.session_state[checkbox_key]]

                    # Generate unique filename with timestamp
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    combined_filename = f'combined_{timestamp}.{openai_tts.format}'

                    # Combine the files
                    audio_combiner.combine_audio_files(combined_filename)

                    # Display the combined file
                    combined_path = os.path.join(voice_dir_path, combined_filename)
                    st.success(f"Created combined audio file: {combined_filename}")
                    st.audio(combined_path, format=f"audio/{openai_tts.format}")

                    # Clear selections after combining
                    st.session_state[checkbox_key] = []
                else:
                    st.warning("Please select files to combine")