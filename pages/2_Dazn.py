import os
import pandas
import streamlit
import src
import src.lib

# log_tcp_complete = os.path.join(os.getcwd(), "data/dazn/desktop", "log_tcp_complete.enhanced")
# log_udp_complete = os.path.join(os.getcwd(), "data/dazn/desktop", "log_udp_complete.enhanced")
# log_tcp_periodic = os.path.join(os.getcwd(), "data/dazn/desktop", "log_tcp_periodic.enhanced")
# log_bot_complete = os.path.join(os.getcwd(), "data/dazn/desktop", "streambot_trace.csv")

# tcp_complete = pandas.read_csv(filepath_or_buffer=log_tcp_complete, delimiter=" ")
# tcp_periodic = pandas.read_csv(filepath_or_buffer=log_tcp_periodic, delimiter=" ")
# udp_complete = pandas.read_csv(filepath_or_buffer=log_udp_complete, delimiter=" ")
# bot_complete = pandas.read_csv(filepath_or_buffer=log_bot_complete, delimiter=" ")

# tcp_periodic["session_id"] = tcp_periodic.apply(lambda row: f"{row['s_ip']}:{row['s_pt']} -- {row['c_ip']}:{row['c_pt']}", axis=1)


# def tcp_chapter():

#     with open(os.path.join(os.getcwd(), "htmls", "tcp_complete_tokens_desc.html"), "r") as f:
#         tcp_complete_description = f.read()  
    
#     with open(os.path.join(os.getcwd(), "htmls", "tcp_complete_tokens_desc.html"), "r") as f:
#         tcp_periodic_description = f.read()  

#     streamlit.markdown("# Traffico applicativo al livello TCP")
#     streamlit.markdown("---")
#     streamlit.markdown("### Distribuzione dei token al livello TCP")
#     streamlit.markdown(tcp_complete_description, unsafe_allow_html=True)

#     options = list(set(tcp_complete["stoken"]))
#     token = streamlit.selectbox("Seleziona qui il token da filtrare", options)

#     streamlit.markdown(f"### Analisi completa dei flussi di _{token}_")
#     streamlit.plotly_chart(src.lib.log_tcp_complete_timeline(tcp_complete=tcp_complete, bot_complete=bot_complete, feature=None, token=token))

#     streamlit.markdown(f"### Analisi periodica dei flussi di _{token}_")
#     streamlit.plotly_chart(src.lib.log_tcp_periodic_timeline(tcp_periodic=tcp_periodic, bot_complete=bot_complete, token=token))

#     streamlit.markdown("---")
#     streamlit.markdown("### Volumi applicativi")
#     streamlit.markdown(tcp_periodic_description, unsafe_allow_html=True)

#     streamlit.markdown("### Volumi in download dei flussi al livello TCP")
#     streamlit.plotly_chart(src.lib.log_tcp_complete_timeline(tcp_complete=tcp_complete, bot_complete=bot_complete, feature="s_app_byts", token=None))

#     streamlit.markdown("### Volumi in upload dei flussi al livello TCP")
#     streamlit.plotly_chart(src.lib.log_tcp_complete_timeline(tcp_complete=tcp_complete, bot_complete=bot_complete, feature="c_app_byts", token=None))


# tcp_chapter()

def data_over_tcp(path: str):

    tcp_complete_frame = pandas.read_csv(os.path.join(path, "log_tcp_complete.csv"), delimiter= " ") 
    tcp_periodic_frame = pandas.read_csv(os.path.join(path, "log_tcp_periodic.csv"), delimiter= " ") 
    bot_complete_frame = pandas.read_csv(os.path.join(path, "streambot_trace.csv"),  delimiter= " ") 

    ##############################################
    # Plot the evolution of data exchange over TCP
    ##############################################
    tokens = list(set(tcp_complete_frame["app_token"]))
    token = streamlit.selectbox("Seleziona qui il token da filtrare", tokens)

    streamlit.markdown(f"### Analisi completa dei flussi di _{token}_")
    figure = src.lib.log_tcp_complete_timeline(tcp_complete=tcp_complete_frame, 
                                                        bot_complete=bot_complete_frame, 
                                                        feature=None, token=token)
    streamlit.plotly_chart(figure)

    streamlit.markdown("### Volumi in download dei flussi al livello TCP")
    figure = src.lib.log_tcp_complete_timeline(tcp_complete=tcp_complete_frame, 
                                               bot_complete=bot_complete_frame, 
                                               feature="s_app_byts", token=None)
    streamlit.plotly_chart(figure)

    streamlit.markdown("### Volumi in upload dei flussi al livello TCP")
    figure = src.lib.log_tcp_complete_timeline(tcp_complete=tcp_complete_frame, 
                                               bot_complete=bot_complete_frame, 
                                               feature="c_app_byts", token=None)
    streamlit.plotly_chart(figure)

    ##############################################
    # Plot the periodic evolution of all flow that
    # are associated with the selected token
    ##############################################
    streamlit.markdown("---")
    streamlit.markdown(f"### Analisi periodica dei flussi di _{token}_")
    figure = src.lib.log_tcp_periodic_timeline(tcp_periodic=tcp_periodic_frame, 
                                               bot_complete=bot_complete_frame, token=token)
    streamlit.plotly_chart(figure)

    connection_ids = list(set(tcp_complete_frame[tcp_complete_frame["app_token"] == token]["connection_id"]))
    connection_id  = streamlit.selectbox("Seleziona qui il token da filtrare", connection_ids)

    streamlit.markdown(f"### Analisi periodica dei volumi in download di _{connection_id}_")
    figure = src.lib.log_tcp_periodic_flow_chart(tcp_periodic=tcp_periodic_frame, 
                                                 connection_id=connection_id, feature="s_app_byts")
    streamlit.plotly_chart(figure)

    streamlit.markdown(f"### Analisi periodica dei volumi in upload di _{connection_id}_")
    figure = src.lib.log_tcp_periodic_flow_chart(tcp_periodic=tcp_periodic_frame, 
                                                 connection_id=connection_id, feature="c_app_byts")
    streamlit.plotly_chart(figure)




def main():

    ######################################################################
    # Read all available experiment that have been conducted in a desktop
    # environment, namely a browser by which the user watch the streaming
    # TC channel
    #####################################################################

    name = os.path.dirname(os.path.abspath(__file__))
    root = os.path.join(name, "..", "data", "dazn", "desktop")

    folders = os.listdir(root)
    path = streamlit.selectbox("Scegli qui uno degli esperimenti disponibili", folders)

    data_over_tcp(path=os.path.join(root, path))
    

main()



