import os
import pandas as pd
import streamlit
import src.lib


def data_over_tcp(path: str):

    tcp_complete_frame = pd.read_csv(os.path.join(path, "log_tcp_complete.csv"), delimiter= " ") 
    tcp_periodic_frame = pd.read_csv(os.path.join(path, "log_tcp_periodic.csv"), delimiter= " ") 
    bot_complete_frame = pd.read_csv(os.path.join(path, "streambot_trace.csv"),  delimiter= " ") 

    ##############################################
    # Token selection section
    ##############################################

    page = "token_section.html"
    path = os.path.join(os.path.dirname(__file__), "..", "htmls", page)
    with open(path, "r") as f:
        page_data = f.read()
    streamlit.markdown(page_data, unsafe_allow_html=True)

    tokens = list(set(tcp_complete_frame["app_token"]))
    token  = streamlit.selectbox("Seleziona qui il token da filtrare", tokens)
    figure = src.lib.tcp_complete_timeline(tcp_complete=tcp_complete_frame, 
                                           bot_complete=bot_complete_frame, feature=None, token=token)
                                           
    streamlit.plotly_chart(figure)
    streamlit.caption(f"_Token selezionato_: :blue[{token}]")
    streamlit.markdown("---")

    ##############################################
    # Volume section
    ##############################################

    page = "volume_section.html"
    path = os.path.join(os.path.dirname(__file__), "..", "htmls", page)
    with open(path, "r") as f:
        page_data = f.read()
    streamlit.markdown(page_data, unsafe_allow_html=True)

    figure = src.lib.tcp_complete_timeline(tcp_complete=tcp_complete_frame, 
                                           bot_complete=bot_complete_frame, feature="s_app_byts", token=None)
    streamlit.plotly_chart(figure)
    streamlit.caption(f"_Evoluzione del livello di :green[scaricamento] al livello TCP_")

    figure = src.lib.tcp_complete_timeline(tcp_complete=tcp_complete_frame, 
                                           bot_complete=bot_complete_frame, feature="c_app_byts", token=None)
    streamlit.plotly_chart(figure)
    streamlit.caption(f"_Evoluzione del livello di :red[caricamento] al livello TCP_")
    streamlit.markdown("---")

    ##############################################
    # Periodic plotting
    ##############################################

    page = "periodic_section.html"
    path = os.path.join(os.path.dirname(__file__), "..", "htmls", page)
    with open(path, "r") as f:
        page_data = f.read()
    streamlit.markdown(page_data, unsafe_allow_html=True)

    figure = src.lib.tcp_periodic_timeline(tcp_periodic=tcp_periodic_frame, bot_complete=bot_complete_frame, token=token)
    streamlit.plotly_chart(figure)
    streamlit.caption(f"_Evoluzione dei flussi ascrivibili al token_: :blue[{token}]")

    connection_ids = list(set(tcp_complete_frame[tcp_complete_frame["app_token"] == token]["connection_id"]))
    connection_id  = streamlit.selectbox("Seleziona qui il flusso da dettagliare", connection_ids)

    ##############################################
    # Packet progression (time domain)
    ##############################################

    col1, col2 = streamlit.columns(2)

    with col1:

        feature = "s_app_byts"
        figure  = src.lib.connection_id_timeline(tcp_periodic=tcp_periodic_frame, connection_id=connection_id, feature=feature)
        streamlit.plotly_chart(figure)
        streamlit.caption(f"_Progressione byte inviati dal server_")

        feature = "s_app_byts"
        figure  = src.lib.connection_id_discrete_fourier(tcp_periodic=tcp_periodic_frame, connection_id=connection_id, feature=feature)
        streamlit.plotly_chart(figure)
        streamlit.caption(f"_Spettro di frequenza del segnale_")

        feature = "s_app_pkts"
        figure = src.lib.connection_id_timeline(tcp_periodic=tcp_periodic_frame, connection_id=connection_id, feature=feature)
        streamlit.plotly_chart(figure)
        streamlit.caption(f"_Progressione pacchetti inviati dal server_")

        feature = "s_app_pkts"
        figure = src.lib.connection_id_discrete_fourier(tcp_periodic=tcp_periodic_frame, connection_id=connection_id, feature=feature)
        streamlit.plotly_chart(figure)
        streamlit.caption(f"_Spettro di frequenza del segnale_")
        streamlit.markdown("---")

        feature = "s_ack_pkts"
        figure = src.lib.connection_id_timeline(tcp_periodic=tcp_periodic_frame, connection_id=connection_id, feature=feature)
        streamlit.plotly_chart(figure)
        streamlit.caption(f"_Progressione pacchetti inviati dal server_")

        feature = "s_ack_pkts"
        figure = src.lib.connection_id_discrete_fourier(tcp_periodic=tcp_periodic_frame, connection_id=connection_id, feature=feature)
        streamlit.plotly_chart(figure)
        streamlit.caption(f"_Spettro di frequenza del segnale_")
        streamlit.markdown("---")

    with col2:

        feature = "c_app_byts"
        figure  = src.lib.connection_id_timeline(tcp_periodic=tcp_periodic_frame, connection_id=connection_id, feature=feature)
        streamlit.plotly_chart(figure)
        streamlit.caption(f"_Progressione byte inviati dal client_")

        feature = "c_app_byts"
        figure  = src.lib.connection_id_discrete_fourier(tcp_periodic=tcp_periodic_frame, connection_id=connection_id, feature=feature)
        streamlit.plotly_chart(figure)
        streamlit.caption(f"_Spettro di frequenza del segnale_")

        feature = "c_app_pkts"
        figure = src.lib.connection_id_timeline(tcp_periodic=tcp_periodic_frame, connection_id=connection_id, feature=feature)
        streamlit.plotly_chart(figure)
        streamlit.caption(f"_Progressione pacchetti inviati dal client_")

        feature = "c_app_pkts"
        figure = src.lib.connection_id_discrete_fourier(tcp_periodic=tcp_periodic_frame, connection_id=connection_id, feature=feature)
        streamlit.plotly_chart(figure)
        streamlit.caption(f"_Spettro di frequenza del segnale_")
        streamlit.markdown("---")

        feature = "c_ack_pkts"
        figure = src.lib.connection_id_timeline(tcp_periodic=tcp_periodic_frame, connection_id=connection_id, feature=feature)
        streamlit.plotly_chart(figure)
        streamlit.caption(f"_Progressione pacchetti inviati dal server_")

        feature = "c_ack_pkts"
        figure = src.lib.connection_id_discrete_fourier(tcp_periodic=tcp_periodic_frame, connection_id=connection_id, feature=feature)
        streamlit.plotly_chart(figure)
        streamlit.caption(f"_Spettro di frequenza del segnale_")
        streamlit.markdown("---")




def main():

    ########################
    # Header
    ########################
    streamlit.markdown("## Analisi traffico applicativo SKY")

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



