import os
import pandas
import streamlit
import src
import src.lib

log_tcp_complete = os.path.join(os.getcwd(), "data/dazn/desktop", "log_tcp_complete.enhanced")
log_udp_complete = os.path.join(os.getcwd(), "data/dazn/desktop", "log_udp_complete.enhanced")
log_tcp_periodic = os.path.join(os.getcwd(), "data/dazn/desktop", "log_tcp_periodic.enhanced")
log_bot_complete = os.path.join(os.getcwd(), "data/dazn/desktop", "streambot_trace.csv")

tcp_complete = pandas.read_csv(filepath_or_buffer=log_tcp_complete, delimiter=" ")
tcp_periodic = pandas.read_csv(filepath_or_buffer=log_tcp_periodic, delimiter=" ")
udp_complete = pandas.read_csv(filepath_or_buffer=log_udp_complete, delimiter=" ")
bot_complete = pandas.read_csv(filepath_or_buffer=log_bot_complete, delimiter=" ")

tcp_periodic["session_id"] = tcp_periodic.apply(lambda row: f"{row['s_ip']}:{row['s_pt']} -- {row['c_ip']}:{row['c_pt']}", axis=1)


def tcp_chapter():

    with open(os.path.join(os.getcwd(), "htmls", "tcp_complete_tokens_desc.html"), "r") as f:
        tcp_complete_description = f.read()  
    
    with open(os.path.join(os.getcwd(), "htmls", "tcp_complete_tokens_desc.html"), "r") as f:
        tcp_periodic_description = f.read()  

    streamlit.markdown("# Traffico applicativo al livello TCP")
    streamlit.markdown("---")
    streamlit.markdown("### Distribuzione dei token al livello TCP")
    streamlit.markdown(tcp_complete_description, unsafe_allow_html=True)

    options = list(set(tcp_complete["token"]))
    token = streamlit.selectbox("Seleziona qui il token da filtrare", options)

    streamlit.markdown(f"### Analisi completa dei flussi di _{token}_")
    streamlit.plotly_chart(src.lib.log_tcp_complete_timeline(tcp_complete=tcp_complete, bot_complete=bot_complete, feature=None, token=token))

    streamlit.markdown(f"### Analisi periodica dei flussi di _{token}_")
    streamlit.plotly_chart(src.lib.log_tcp_periodic_timeline(tcp_periodic=tcp_periodic, bot_complete=bot_complete, token=token))

    streamlit.markdown("---")
    streamlit.markdown("### Volumi applicativi")
    streamlit.markdown(tcp_periodic_description, unsafe_allow_html=True)

    streamlit.markdown("### Volumi in download dei flussi al livello TCP")
    streamlit.plotly_chart(src.lib.log_tcp_complete_timeline(tcp_complete=tcp_complete, bot_complete=bot_complete, feature="s_app_byts", token=None))

    streamlit.markdown("### Volumi in upload dei flussi al livello TCP")
    streamlit.plotly_chart(src.lib.log_tcp_complete_timeline(tcp_complete=tcp_complete, bot_complete=bot_complete, feature="c_app_byts", token=None))


tcp_chapter()


