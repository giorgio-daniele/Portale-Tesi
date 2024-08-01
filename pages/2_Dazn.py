import os
import pandas as pd
import streamlit as st
import src
import src.lib


def data_over_tcp(path: str):

    tcp_complete_frame = pd.read_csv(os.path.join(path, "log_tcp_complete.csv"), delimiter= " ") 
    tcp_periodic_frame = pd.read_csv(os.path.join(path, "log_tcp_periodic.csv"), delimiter= " ") 
    bot_complete_frame = pd.read_csv(os.path.join(path, "streambot_trace.csv"),  delimiter= " ") 

    ##############################################
    # Plot the evolution of data exchange over TCP
    ##############################################

    tokens = list(set(tcp_complete_frame["app_token"]))
    token = st.selectbox("Seleziona qui il token da filtrare", tokens)

    st.markdown(f"### Analisi completa dei flussi di _{token}_")
    figure = src.lib.log_tcp_complete_timeline(tcp_complete=tcp_complete_frame, 
                                                        bot_complete=bot_complete_frame, 
                                                        feature=None, token=token)
    st.plotly_chart(figure)

    st.markdown("### Volumi in download dei flussi al livello TCP")
    figure = src.lib.log_tcp_complete_timeline(tcp_complete=tcp_complete_frame, 
                                               bot_complete=bot_complete_frame, 
                                               feature="s_app_byts", token=None)
    st.plotly_chart(figure)

    st.markdown("### Volumi in upload dei flussi al livello TCP")
    figure = src.lib.log_tcp_complete_timeline(tcp_complete=tcp_complete_frame, 
                                               bot_complete=bot_complete_frame, 
                                               feature="c_app_byts", token=None)
    st.plotly_chart(figure)

    ##############################################
    # Plot the periodic evolution of all flow that
    # are associated with the selected token
    ##############################################

    st.markdown("---")
    st.markdown(f"### Analisi periodica dei flussi di _{token}_")
    figure = src.lib.log_tcp_periodic_timeline(tcp_periodic=tcp_periodic_frame, 
                                               bot_complete=bot_complete_frame, token=token)
    st.plotly_chart(figure)

    connection_ids = list(set(tcp_complete_frame[tcp_complete_frame["app_token"] == token]["connection_id"]))
    connection_id  = st.selectbox("Seleziona qui il token da filtrare", connection_ids)

    st.markdown(f"### Analisi periodica dei volumi in download di _{connection_id}_ (bytes inviati)")
    figure = src.lib.log_tcp_periodic_flow_chart(tcp_periodic=tcp_periodic_frame, 
                                                 connection_id=connection_id, feature="s_app_byts")
    st.plotly_chart(figure)

    st.markdown(f"### Analisi periodica dei volumi in upload di _{connection_id}_ (bytes inviati)")
    figure = src.lib.log_tcp_periodic_flow_chart(tcp_periodic=tcp_periodic_frame, 
                                                 connection_id=connection_id, feature="c_app_byts")
    st.plotly_chart(figure)


    st.markdown(f"### Analisi periodica dei volumi in download di _{connection_id}_ (pacchetti inviati)")
    figure = src.lib.log_tcp_periodic_flow_chart(tcp_periodic=tcp_periodic_frame, 
                                                 connection_id=connection_id, feature="s_app_pkts")
    st.plotly_chart(figure)

    st.markdown(f"### Analisi periodica dei volumi in upload di _{connection_id}_ (pacchetti inviati)")
    figure = src.lib.log_tcp_periodic_flow_chart(tcp_periodic=tcp_periodic_frame, 
                                                 connection_id=connection_id, feature="c_app_pkts")
    st.plotly_chart(figure)



def main():

    device = "data/dazn/desktop"
    folder = os.path.join(os.path.dirname(__file__), "..", device)

    options = dict()

    for qos in os.listdir(folder):
        options[qos] = [exp for exp in os.listdir(os.path.join(folder, qos))]

    col1, col2 = st.columns(2)

    ############################################################
    # Select among available QoS testbed conditions
    ############################################################

    with col1:
        qos = st.selectbox(label="Scegli la condizione di QoS",
                           options=list(options.keys()),
                           help="Inserisci una tra le opzioni")
        
    ############################################################
    # Select among available experiments for that QoS condition
    ############################################################

    with col2:
        num = st.selectbox(label="Inserisci l'esperimento da visualizzare",
                           options=list(options[qos]),
                           help="Inserisci una tra le opzioni")
    
    st.write(f"You selected: qos = {qos}, num = {num}")

    data_over_tcp(path=os.path.join(folder, qos, num))
    

main()



