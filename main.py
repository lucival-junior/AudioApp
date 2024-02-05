import streamlit as st
import json
import unicodedata
import speech_recognition as sr
import plotly.graph_objs as go
import streamlit.components.v1 as components


st.set_page_config(
     page_title="App",
     layout="wide",
     initial_sidebar_state="auto",
)
st.sidebar.write("**INPUT FILE**")

# credit reference for using third party audios
credits_audio = '**Créditos audio:** Parte de audio extraído de: Fábio Porchat,' \
                ' Judite:Esteremos fazendo o cancelamento, Youtube. Disponível em:' \
                ' <https://www.youtube.com/watch?v=vEaNCoCXcdk&t=11s>. Acesso em: 20 de abril de 2021.'

# list of key words
keywords = ['anatel', 'cancelar', 'procon', 'puta', 'caralho', 'porra']
# list of key words
indicators_offensive_words = ['caralho', 'puta']
indicators_service_cancellation = ['cancelar', 'reclamacao']

# receives the audio file
upload_files_audio = st.sidebar.file_uploader('Choose file', accept_multiple_files=True, help='Ex. mp3, wav')
# choose between simulated test or real test
simulation = st.sidebar.radio('Simulation:', ('Yes', 'No'))


# function for removing accent and special characters
def strip_accents(text: str) -> str:
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    text = str(text)

    return text


# mock function to show transcribed audio with highlight
def audio_transcript() -> None:

    if upload_files_audio is not None:
        # Reads the audio and stores it in the variable data bytes
        for uploaded_file in upload_files_audio:
            data_bytes = uploaded_file.read()
            st.audio(data_bytes, format='audio/ogg')

            # get the name of the audio to save location
            file_name_audio = uploaded_file.name
            with open('file_teste/'+file_name_audio, "wb") as out:
                out.write(data_bytes)

            # shows the keywords available in the list
            # select_keywords = st.multiselect('Keywords:', keywords, keywords)

            # simulated test or real test
            if simulation == 'No':
                audio_transcript_google_free(file_name_audio, keywords)
            else:
                # for simulated test
                with open('file_teste/exemple.json', 'r', encoding='utf8') as file:
                    # loads the json file and performs the reading.
                    data_json = json.load(file)
                    text = data_json['alternative'][1]['transcript']
                    # It then converts to lowercase letters and removes accentuation
                    lower_case = text.lower()
                    txt_raw = strip_accents(lower_case)

                    # performs a division in the text by space
                    txt_list = txt_raw.split(' ')

                    # performs a loop to identify offensive words and canceled services, based on key words
                    words_found = [word for word in keywords if word in txt_list]
                    offensive_words = [ow for ow in indicators_offensive_words if ow in words_found]
                    service_cancellation = [sc for sc in indicators_service_cancellation if sc in words_found]

                    # takes the position of the word in the text to highlight
                    for highlight in words_found:
                        index = txt_list.index(highlight.__str__())
                        highlight_format = f'<span style="background-color: #FFFF00">{highlight}</span>'
                        txt_list[index] = highlight_format

                    # transforms the string list into continuous text
                    final_txt_format = ' '.join(txt_list)
                # prints the result
                highlight_html(final_txt_format)

                # call method to generate indicator graphs


                # prints the result
                st.multiselect('Offensive Words:', offensive_words, offensive_words)
                st.multiselect('Service Cancellation:', service_cancellation, service_cancellation)
                indicators(offensive_words, service_cancellation)
                st.write(data_json)
                st.markdown(credits_audio)


# function to transcribe audio using api speech recognition
def audio_transcript_google_free(file_name_audio: str, select_keywords: list) -> None:
    # function responsible for hearing and recognizing speech
    recognizer = sr.Recognizer()
    # informing the limit for silence
    recognizer.energy_threshold = 300

    # To convert our audio file to an AudioData
    with sr.AudioFile('file_teste/'+file_name_audio) as source:
        audio_file = recognizer.record(source)

    # Stores the return information in the result variable
    result = recognizer.recognize_google(audio_data=audio_file, language="pt-BR", show_all=True)

    # saves the results in a Json file
    with open('file_teste/'+file_name_audio+'.json', 'w', encoding='utf8') as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    # read the json file
    with open('file_teste/'+file_name_audio+'.json', 'r', encoding='utf8') as file:
        data_json = json.load(file)

        # get the main result of the transcript
        text = data_json['alternative'][0]['transcript']
        # It then converts to lowercase letters and removes accentuation
        lower_case = text.lower()
        txt_raw = strip_accents(lower_case)
        # performs a division in the text by space
        txt_list = txt_raw.split(' ')

        # performs a loop to identify offensive words and canceled
        words_found = [word for word in select_keywords if word in txt_list]

        offensive_words = [ow for ow in indicators_offensive_words if ow in words_found]
        service_cancellation = [sc for sc in indicators_service_cancellation if sc in words_found]

        # takes the position of the word in the text to highlight
        for highlight in words_found:
            index = txt_list.index(highlight.__str__())
            highlight_format = f'<span style="background-color: #FFFF00">{highlight}</span>'
            txt_list[index] = highlight_format
        # transforms the string list into continuous text
        final_txt_format = ' '.join(txt_list)
        # prints the result
        highlight_html(final_txt_format)
    # call method to generate indicator graphs
    indicators(offensive_words, service_cancellation)
    # prints the result
    st.multiselect('Offensive Words:', offensive_words, offensive_words)
    st.multiselect('Service Cancellation:', service_cancellation, service_cancellation)
    st.write(data_json)


# function to generate indicator graphs, based on a string list
def indicators(indicators_offensive: list, indicators_service: list) -> None:
    indicators_keys = [len(indicators_offensive), len(indicators_service)]
    trace = go.Bar(x=['Offensive Words', 'Service Cancellation'],
                   y=indicators_keys,
                   text=indicators_keys,
                   textposition='auto')

    subtitle = go.Layout(title='Call Evaluation',
                         xaxis={'title': 'Indicators'},
                         yaxis={'title': 'Amount'})

    figure = go.Figure(data=trace, layout=subtitle)
    st.write(figure)


def highlight_html(transcription_highlight):
    components.html(
        f"""
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css"
         integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" 
         integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN"
          crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"
         integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl"
          crossorigin="anonymous"></script>
        <div id="accordion">
          <div class="card">
            <div class="card-header" id="headingOne">
              <h5 class="mb-0">
                <button class="btn btn-link" data-toggle="collapse" data-target="#collapseOne"
                 aria-expanded="true" aria-controls="collapseOne">
                Transcription
                </button>
              </h5>
            </div>
            <div id="collapseOne" class="collapse show" aria-labelledby="headingOne" data-parent="#accordion">
              <div class="card-body">
                {transcription_highlight}
              </div>
            </div>
          </div>
        </div>
        """,
        height=350,
        scrolling=True,
    )


if __name__ == '__main__':
    audio_transcript()
