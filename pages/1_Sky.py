import os
import pandas
import streamlit
from src.lib import prepare_tcp_complete
from src.lib import prepare_tcp_periodic
from src.lib import tcp_complete_timeline
from src.lib import tcp_periodic_timeline

def generate_header(page: str):
    page = "token_section.html"
    path = os.path.join(os.path.dirname(__file__), "..", "htmls", page)
    with open(path, "r") as f:
        page_data = f.read()
    streamlit.markdown(page_data, unsafe_allow_html=True)


def data_over_tcp(path: str):

    tcp_complete_frame = pandas.read_csv(os.path.join(path, "log_tcp_complete.csv"), delimiter= " ") 
    tcp_periodic_frame = pandas.read_csv(os.path.join(path, "log_tcp_periodic.csv"), delimiter= " ") 
    bot_complete_frame = pandas.read_csv(os.path.join(path, "streambot_trace.csv"),  delimiter= " ") 

    ###############################
    # Prepare each pandas Dataframe
    ###############################

    prepare_tcp_complete(complete=tcp_complete_frame)
    prepare_tcp_periodic(periodic=tcp_periodic_frame)

    generate_header(page="token_section.html")

    ################################
    # General view of all TCP flows
    ################################
    streamlit.plotly_chart(figure_or_data=tcp_complete_timeline(tcp_complete=tcp_complete_frame,  
                                                                bot_complete=bot_complete_frame, feature=None))
    
    ################################
    # Volumes view of all TCP flows
    ################################
    col1, col2 = streamlit.columns(2)
    with col1:
        streamlit.plotly_chart(figure_or_data=tcp_complete_timeline(tcp_complete=tcp_complete_frame, 
                                                                    bot_complete=bot_complete_frame, feature="s_app_byts"))
    with col2:
        streamlit.plotly_chart(figure_or_data=tcp_complete_timeline(tcp_complete=tcp_complete_frame, 
                                                                    bot_complete=bot_complete_frame, feature="c_app_byts"))
    streamlit.markdown("---")

    options = list(set(tcp_complete_frame["token"]))
    tk = streamlit.selectbox("Seleziona qui il token da filtrare", options)

    ids = list(set(tcp_complete_frame.loc[tcp_complete_frame["token"] == tk]["id"]))
    mapping = {id: id.replace("#", " ") for id in ids}
    options = list(mapping.values())
    id = streamlit.selectbox("Seleziona qui il flusso da analizzare", options)
    id = {v: k for k, v in mapping.items()}[id]

    ################################
    # Periodic view of a given id
    ################################
    streamlit.plotly_chart(figure_or_data=tcp_periodic_timeline(tcp_periodic=tcp_periodic_frame, 
                                                                bot_complete=bot_complete_frame, token=tk, id=None, feature=None))

    col1, col2 = streamlit.columns(2)
    with col1:
        streamlit.plotly_chart(figure_or_data=tcp_periodic_timeline(tcp_periodic=tcp_periodic_frame, 
                                                                    bot_complete=bot_complete_frame, token=tk, id=id, feature="s_app_byts"))
    with col2:
        streamlit.plotly_chart(figure_or_data=tcp_periodic_timeline(tcp_periodic=tcp_periodic_frame, 
                                                                    bot_complete=bot_complete_frame, token=tk, id=id, feature="c_app_byts"))
    streamlit.markdown("---")


def main():

    streamlit.set_page_config(layout="wide")

    ########################
    # Header
    ########################
    streamlit.markdown("## Analisi traffico applicativo Sky")

    device = "data/sky/desktop"
    folder = os.path.join(os.path.dirname(__file__), "..", device)

    options = dict()

    for qos in os.listdir(folder):
        options[qos] = [exp for exp in os.listdir(os.path.join(folder, qos))]

    col1, col2 = streamlit.columns(2)

    ############################################################
    # Select among available QoS testbed conditions
    ############################################################

    with col1:
        help = """
            Select here the QoS condition you like
            the most, in order to inspect differences 
            on volume, bitrate in each flow
        """
        qos = streamlit.selectbox(label="QoS setup selection",
                           options=list(options.keys()), help=help)
        
    ############################################################
    # Select among available experiments for that QoS condition
    ############################################################

    with col2:
        help = """
            Select here the experiment you like the
            most, according to the previous selection
            of QoS condition
        """
        num = streamlit.selectbox(label="Experiment selection",
                           options=list(options[qos]),  help=help)
    
    streamlit.markdown(f"#### Current selection")
    streamlit.caption(f"_Dataset_: :blue[{qos}] and experiment :green[{num}]")
    streamlit.markdown("---")

    data_over_tcp(path=os.path.join(folder, qos, num))
    

main()



