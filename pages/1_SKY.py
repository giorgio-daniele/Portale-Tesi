# import math
# import os
# import re
# import yaml
# import numpy
# import pandas
# import streamlit
# import plotly.express
# import plotly.graph_objects

import os
import re
import yaml
import math
import pandas
import streamlit
import plotly.express
import plotly.graph_objects

#############################################################
# Constants (they may be useful later in the code)          #
#############################################################
SETTINGS = os.path.join(os.getcwd(), "data", "settings.yaml")

TCP_COMPLETE_TRACING_FILE_DESKTOP_00MBITS = os.path.join(os.getcwd(), "data/sky/desktop/00Mbits", "log_tcp_complete")
TCP_PERIODIC_TRACING_FILE_DESKTOP_00MBITS = os.path.join(os.getcwd(), "data/sky/desktop/00Mbits", "log_tcp_periodic")
BOT_TRACING_FILE_DESKTOP_00MBITS = os.path.join(os.getcwd(), "data/sky/desktop/00Mbits", "streambot_trace.csv")

TCP_COMPLETE_TRACING_FILE_DESKTOP_4MBITS = os.path.join(os.getcwd(), "data/sky/desktop/4Mbits", "log_tcp_complete")
TCP_PERIODIC_TRACING_FILE_DESKTOP_4MBITS = os.path.join(os.getcwd(), "data/sky/desktop/4Mbits", "log_tcp_periodic")
BOT_TRACING_FILE_DESKTOP_4MBITS = os.path.join(os.getcwd(), "data/sky/desktop/4Mbits", "streambot_trace.csv")

TCP_COMPLETE_TRACING_FILE_DESKTOP_1MBITS = os.path.join(os.getcwd(), "data/sky/desktop/1Mbits", "log_tcp_complete")
TCP_PERIODIC_TRACING_FILE_DESKTOP_1MBITS = os.path.join(os.getcwd(), "data/sky/desktop/1Mbits", "log_tcp_periodic")
BOT_TRACING_FILE_DESKTOP_1MBITS = os.path.join(os.getcwd(), "data/sky/desktop/1Mbits", "streambot_trace.csv")


def generate_frame(file: str, mapping: dict, delimiter: str) -> pandas.DataFrame:

    frame = pandas.read_csv(filepath_or_buffer=file, delimiter=delimiter)

    frame.columns = [re.sub(r'[#:0-9]', '', column) for column in frame.columns]

    frame.rename(columns=mapping, inplace=True)

    frame = frame[list(mapping.values())]

    return frame

def generate_bot_frame(file: str, settings: dict) -> pandas.DataFrame:

    return generate_frame(mapping=settings["streambot"]["columns"], 
                          delimiter=" ", file=file)

def generate_tcp_complete_frame(file: str, settings: dict) -> pandas.DataFrame:

    def generate_token(row: dict) -> str:

        tls, http, token = 8192, 1, ""

        if row["connection_type"] == tls:
            token = row["sni_client_hello"]
        if row["connection_type"] == http:
            token = row["web_server_name"]

        if token == "-" or token == "":
            token = row["dns_server_name"]

        if token == "-" or token == "":
            return "?"

        parts = token.split(".")
        token = ".".join(parts[-3:-1]) if len(parts) >= 3 else ".".join(parts)
        token = re.sub(r"\d+", "#", token)

        return token

    # Generate phisically the pandas DataFrame
    tcp = generate_frame(mapping=settings["tstat"]["tcp"]["complete"]["columns"], 
                          delimiter=" ", file=file)
    
    # If "token" column does not exists in the current pandas DataFrame, 
    # generate a new one
    if "token" not in tcp.columns:
        tcp["token"] = tcp.apply(lambda record: generate_token(record), 
                                             axis=1)
    
    return tcp

def generate_tcp_periodic_frame(file: str, settings: dict) -> pandas.DataFrame:

    return generate_frame(mapping=settings["tstat"]["tcp"]["periodic"]["columns"], 
                          delimiter=" ", file=file)

def reset_frame_timestamp(frame: pandas.DataFrame, bot: pandas.DataFrame, column: str):

    frame[column] -= float(bot.loc[0, "event_absolute_unix_ms"])

def process_tcp_periodic_frame(tcp_periodic: pandas.DataFrame, 
                               tcp_complete: pandas.DataFrame, bot: pandas.DataFrame) -> pandas.DataFrame:

    if "f_point_unix_mx" not in tcp_periodic.columns:
        tcp_periodic["f_point_unix_ms"]  = tcp_periodic["s_point_unix_ms"] + tcp_periodic["duration"]

    # If "s_point_unix_dt" column does not exist in the current pandas DataFrame, generate
    # a new one. This is just the date-time representation of a Unix timestamp.
    if "s_point_unix_dt" not in tcp_periodic.columns:
        tcp_periodic["s_point_unix_dt"] = pandas.to_datetime(tcp_periodic["s_point_unix_ms"],  
                                                             unit="ms", origin="unix")
        
    # If "f_point_unix_dt" column does not exist in the current pandas DataFrame, generate
    # a new one. This is just the date-time representation of a Unix timestamp.
    if "f_point_unix_dt" not in tcp_periodic.columns:
        tcp_periodic["f_point_unix_dt"] = pandas.to_datetime(tcp_periodic["f_point_unix_ms"],
                                                             unit="ms", origin="unix")
            
    # Group by the TCP periodic dataframe by using the source IP address, the destination
    # IP address, then the source port and the destination port.
    groups = tcp_periodic.groupby(["client_ip", "server_ip", "client_port", "server_port"])

    # List to store the updated group DataFrames
    pedics = []

    # Iterate through each group
    for (client_ip, server_ip, client_port, server_port), group in groups:

        # Fetch the corresponding token from tcp_complete
        matching_row = tcp_complete[
            (tcp_complete["client_ip"] == client_ip) &
            (tcp_complete["server_ip"] == server_ip) &
            (tcp_complete["client_port"] == client_port) &
            (tcp_complete["server_port"] == server_port)
        ]
        
        if not matching_row.empty:
            token = matching_row["token"].values[0]
            group["token"] = token  # Add the token to the group DataFrame
        else:
            group["token"] = None  # If no matching row, set token as None
        
        pedics.append(group)

    return pandas.concat(pedics, ignore_index=True)

def tcp_complete_tokens_distribution(tcp: pandas.DataFrame, 
                                     bot: pandas.DataFrame, token: str, title: str):

    def generate_volume(b) -> str:

        units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
        
        if b == 0:
            return "0 B"

        power = min(int(math.log(b, 1024)), len(units) - 1)
        scaled_value = b / (1024 ** power)
        
        return f"{scaled_value:.2f} {units[power]}"

    def generate_description(record):

        ts = record['fst_packet_observed_unix_ms'] // 1000
        te = record['lst_packet_observed_unix_ms'] // 1000
        
        server_app_xmitted_bytes = generate_volume(record["server_app_xmitted_bytes"])
        client_app_xmitted_bytes = generate_volume(record["client_app_xmitted_bytes"])

        return (f"Token: <b>{record['token']}</b><br>"
                    f"First Packet Observed after [sec]: {ts:.2f}<br>"
                    f"Last  Packet Observed after [sec]: {te:.2f}<br>"
                    f"TCP Stream Duration [sec]: {(te - ts):.2f}<br>"
                    f"TCP Stream Duration [min]: {((te - ts) // 60):.2f}<br>"
                    f"Application Bytes from Client: {client_app_xmitted_bytes}<br>"
                    f"Application Bytes from Server: {server_app_xmitted_bytes}<br>")

    # If "fst_packet_observed_dt" column does not exist in the current pandas DataFrame, generate
    # a new one. This is just the date-time representation of a Unix timestamp.
    if "fst_packet_observed_dt" not in tcp.columns:
        tcp["fst_packet_observed_dt"] = pandas.to_datetime(tcp["fst_packet_observed_unix_ms"],  
                                                            unit="ms", origin="unix")
        
    # If "lst_packet_observed_dt" column does not exist in the current pandas DataFrame, generate
    # a new one. This is just the date-time representation of a Unix timestamp.
    if "lst_packet_observed_dt" not in tcp.columns:
        tcp["lst_packet_observed_dt"] = pandas.to_datetime(tcp["lst_packet_observed_unix_ms"],
                                                            unit="ms", origin="unix")
    
    # If "description" column does not exist in the current pandas DataFrame, generate a new one.
    # This is just a summary about the current flow.
    if "description" not in tcp.columns:
        tcp["description"] = tcp.apply(lambda record: generate_description(record),
                                       axis=1)
        
    # If "color" column does not exists in the current pandas DataFrame, generate a new one
    if "color" not in tcp.columns:
        low, high  = "rgba(0, 0, 255, 0.2)", "rgba(0, 0, 255, 1.0)"
        tcp["color"] = tcp["token"].apply(lambda x: high if x == token else low)

    # Generate the figure containing the timeline
    fig = plotly.express.timeline(data_frame=tcp,
                                  # Define the x-axis (the length of the segment)
                                  x_start="fst_packet_observed_dt", x_end="lst_packet_observed_dt", 
                                  # Define the y-axis (the height of the segment)
                                  y=tcp.index,
                                  # Use the color column to highlight the segment
                                  color="color", 
                                  custom_data=["description"],
                                  title=title,
                                  color_discrete_map={low: low, high: high})


    # Add a tiny flow description for each flow in the diagram bu updating
    # alld the traces in the figure
    fig.update_traces(hovertemplate="%{customdata[0]}",
                      hoverlabel=dict(bgcolor='white', 
                                      font_size=12, 
                                      font_family="Courier New"), opacity=0.7, width=0.7)
    
    # Add the Streambot actions reference
    for _, record in bot.iterrows():
        x0 = pandas.to_datetime(record["event_from_origin_millis"], unit="ms", origin="unix")
        fig.add_shape(dict(type="line", 
                           x0=x0, y0=0, 
                           x1=x0, y1=len(tcp),
                           line=dict(color="red", width=0.4, dash="dot")))

        fig.add_annotation(x=x0, y=len(tcp),
                           text=record["event_name"],
                           showarrow=True,
                           arrowhead=2, ax=0, ay=-40)
        
        fig.add_annotation(x=x0, y=0,
                           text=record["event_name"],
                           showarrow=True,
                           arrowhead=2, ax=0, ay=40)
    
    # Define the x-axis interval
    xs = pandas.to_datetime(bot["event_from_origin_millis"].min(), unit="ms", origin="unix")
    xe = pandas.to_datetime(bot["event_from_origin_millis"].max(), unit="ms", origin="unix")

    # Define the x-axis range
    values = pandas.date_range(start=xs, end=xe, freq="20s")
    labels = [v.strftime("%M:%S") for v in values]

    # Define the x-axis labels
    fig.update_yaxes(gridwidth=0.03, 
                     title="Flow", showgrid=True,
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))
    fig.update_xaxes(gridwidth=0.03, 
                     title="Time (M:S)", showgrid=True, 
                     tickvals=values, ticktext=labels, 
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))    

    # Remove the legend
    fig.update_layout(showlegend=False)

    return fig

def tcp_complete_tokens_volume_distribution(tcp: pandas.DataFrame, 
                                            bot: pandas.DataFrame, side: str, title: str):

    def generate_volume(b) -> str:

        units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
        
        if b == 0:
            return "0 B"

        power = min(int(math.log(b, 1024)), len(units) - 1)
        scaled_value = b / (1024 ** power)
        
        return f"{scaled_value:.2f} {units[power]}"

    def generate_description(record):

        ts = record['fst_packet_observed_unix_ms'] // 1000
        te = record['lst_packet_observed_unix_ms'] // 1000
        
        server_app_xmitted_bytes = generate_volume(record["server_app_xmitted_bytes"])
        client_app_xmitted_bytes = generate_volume(record["client_app_xmitted_bytes"])

        return (f"Token: <b>{record['token']}</b><br>"
                    f"First Packet Observed after [sec]: {ts:.2f}<br>"
                    f"Last  Packet Observed after [sec]: {te:.2f}<br>"
                    f"TCP Stream Duration [sec]: {(te - ts):.2f}<br>"
                    f"TCP Stream Duration [min]: {((te - ts) // 60):.2f}<br>"
                    f"Application Bytes from Client: {client_app_xmitted_bytes}<br>"
                    f"Application Bytes from Server: {server_app_xmitted_bytes}<br>")
    
    # If "fst_packet_observed_dt" column does not exist in the current pandas DataFrame, generate
    # a new one. This is just the date-time representation of a Unix timestamp.
    if "fst_packet_observed_dt" not in tcp.columns:
        tcp["fst_packet_observed_dt"] = pandas.to_datetime(tcp["fst_packet_observed_unix_ms"],  
                                                             unit="ms", origin="unix")
        
    # If "lst_packet_observed_dt" column does not exist in the current pandas DataFrame, generate
    # a new one. This is just the date-time representation of a Unix timestamp.
    if "lst_packet_observed_dt" not in tcp.columns:
        tcp["lst_packet_observed_dt"] = pandas.to_datetime(tcp["lst_packet_observed_unix_ms"],
                                                                unit="ms", origin="unix")
    
    # If "description" column does not exist in the current pandas DataFrame, generate a new one.
    # This is just a summary about the current flow.
    if "description" not in tcp.columns:
        tcp["description"] = tcp.apply(lambda record: generate_description(record),
                                       axis=1)
    
    # Generate the figure containing the timeline
    fig = plotly.express.timeline(data_frame=tcp,
                                  # Define the x-axis (the length of the segment)
                                  x_start="fst_packet_observed_dt", x_end="lst_packet_observed_dt", 
                                  # Define the y-axis (the height of the segment)
                                  y=tcp.index,
                                  # Use the color column to highlight the segment
                                  color=side, 
                                  custom_data=["description"],
                                  title=title,
                                  color_continuous_scale="Oranges")


    # Add a tiny flow description for each flow in the diagram bu updating
    # alld the traces in the figure
    fig.update_traces(hovertemplate="%{customdata[0]}",
                      hoverlabel=dict(bgcolor='white', 
                                      font_size=12, 
                                      font_family="Courier New"), opacity=0.7, width=0.7)
    
    # Add the Streambot actions reference
    for _, record in bot.iterrows():
        x0 = pandas.to_datetime(record["event_from_origin_millis"], unit="ms", origin="unix")
        fig.add_shape(dict(type="line", 
                           x0=x0, y0=0, 
                           x1=x0, y1=len(tcp),
                           line=dict(color="red", width=0.4, dash="dot")))

        fig.add_annotation(x=x0, y=len(tcp),
                           text=record["event_name"],
                           showarrow=True,
                           arrowhead=2, ax=0, ay=-40)
        
        fig.add_annotation(x=x0, y=0,
                           text=record["event_name"],
                           showarrow=True,
                           arrowhead=2, ax=0, ay=40)
    
    # Define the x-axis interval
    xs = pandas.to_datetime(bot["event_from_origin_millis"].min(), unit="ms", origin="unix")
    xe = pandas.to_datetime(bot["event_from_origin_millis"].max(), unit="ms", origin="unix")

    # Define the x-axis range
    values = pandas.date_range(start=xs, end=xe, freq="20s")
    labels = [v.strftime("%M:%S") for v in values]

    # Define the x-axis labels
    fig.update_yaxes(gridwidth=0.03, 
                     title="Flow", showgrid=True,
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))
    fig.update_xaxes(gridwidth=0.03, 
                     title="Time (M:S)", showgrid=True, 
                     tickvals=values, ticktext=labels, 
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))    

    # Remove the legend
    fig.update_layout(showlegend=False)

    return fig

def tcp_periodic_tokens_volume_distribution(mts: pandas.DataFrame, 
                                            bot: pandas.DataFrame, token: str, title: str):
    
    def generate_volume(b):

        units = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
        
        if b == 0:
            return "0 B"

        power = min(int(math.log(b, 1024)), len(units) - 1)
        scaled_value = b / (1024 ** power)
        
        return f"{scaled_value:.2f} {units[power]}"
    
    def generate_throughput(b, s):
        units = ["B/s", "KB/s", "MB/s", "GB/s", "TB/s", "PB/s", "EB/s", "ZB/s", "YB/s"]
        
        if s == 0:
            return "0 B/s"
            
        throughput = b / s
        
        if throughput == 0:
            return "0 B/s"
        
        power = min(int(math.log(throughput, 1024)), len(units) - 1)
        scaled_value = throughput / (1024 ** power)
        
        return f"{scaled_value:.2f} {units[power]}"

    def generate_description(record):

        ts = record['s_point_unix_ms'] // 1000
        te = record['f_point_unix_ms'] // 1000
        
        server_app_xmitted_bytes = generate_volume(record["server_app_xmitted_bytes"])
        client_app_xmitted_bytes = generate_volume(record["client_app_xmitted_bytes"])

        server_app_goodput = generate_throughput(b=record["server_app_xmitted_bytes"], 
                                                 s=record["duration"])
        client_app_goodput = generate_throughput(b=record["client_app_xmitted_bytes"], 
                                                 s=record["duration"])
        
        server_app_packets = record["server_app_xmitted_pkts"]
        client_app_packets = record["client_app_xmitted_pkts"]

        return (f"Token: <b>{record['token']}</b><br>"
                    f"First Packet Observed after [sec]: {ts:.2f}<br>"
                    f"Last  Packet Observed after [sec]: {te:.2f}<br>"
                    f"TCP Stream Duration [sec]: {(te - ts):.2f}<br>"
                    f"TCP Stream Duration [min]: {((te - ts) // 60):.2f}<br>"
                    f"Application Bytes from Client: {client_app_xmitted_bytes}<br>"
                    f"Application Bytes from Server: {server_app_xmitted_bytes}<br>"
                    f"Application Packets from Client: {client_app_packets}<br>"
                    f"Application Packets from Server: {server_app_packets}<br>"
                    f"Client Goodput: {server_app_goodput}<br>"
                    f"Server Goodput: {client_app_goodput}<br>")

    def generate_color(record):

        black  = "rgba(0, 0, 0, 0.6)"
        red    = "rgba(255, 0, 0, 0.6)"
        green  = "rgba(0, 255, 0, 0.6)"
        purple = "rgba(128, 0, 128, 0.6)"  # Mixture

        if record["server_app_xmitted_bytes"] > 0 and record["client_app_xmitted_bytes"] > 0:
            return black
        if record["server_app_xmitted_bytes"] > 0 and record["client_app_xmitted_bytes"] == 0:
            return green
        if record["client_app_xmitted_bytes"] > 0 and record["server_app_xmitted_bytes"] == 0:
            return red
        # if record["client_app_xmitted_bytes"] == 0 and record["server_app_xmitted_bytes"] == 0:
        #     return black

    # Filter the frame for displaying only the requested token (use method copy()
    # for editing at free will the object in memory)
    copy = mts.loc[mts["token"] == token].copy()

    # Use .loc to avoid the SettingWithCopyWarning and create the 'index' column
    copy.loc[:, "index"] = mts.apply(lambda record: f":{record['client_port']}:{record['server_port']} {record['token']}", axis=1)

    # Generate a description
    copy["description"] = copy.apply(lambda record: generate_description(record), axis=1)

    # Generate a color by following this strategy: if the client and the server
    # are talking each other, use green + red; if the client only, use the red
    # if the server only, use the green.
    copy["color"] = copy.apply(lambda record: generate_color(record), axis=1)

    fig = plotly.express.timeline(data_frame=copy,
                                    # Define the x-axis (the length of the segment)
                                    x_start="s_point_unix_dt", x_end="f_point_unix_dt", 
                                    # Define the y-axis (the height of the segment)
                                    color="color", 
                                    y="index",
                                    title=title,
                                    color_discrete_map={
                                        "rgba(0, 0, 0, 0.6)":     "Black", 
                                        "rgba(255, 0, 0, 0.6)":   "Red", 
                                        "rgba(0, 255, 0, 0.6)":   "Green", 
                                        "rgba(128, 0, 128, 0.6)": "Purple"
                                    },
                                    custom_data=["description"])
    
    # Add a tiny flow description for each flow in the diagram bu updating
    # alld the traces in the figure
    fig.update_traces(hovertemplate="%{customdata[0]}",
                      hoverlabel=dict(bgcolor='white', 
                                      font_size=12, 
                                      font_family="Courier New"), opacity=0.7, width=0.7)
    
    # Define the x-axis interval
    xs = pandas.to_datetime(bot["event_from_origin_millis"].min(), unit="ms", origin="unix")
    xe = pandas.to_datetime(bot["event_from_origin_millis"].max(), unit="ms", origin="unix")

    # print(f"XS = {xs} XE = {xe}")

    # Define the x-axis range
    values = pandas.date_range(start=xs, end=xe, freq="3s")
    labels = [v.strftime("%M:%S") for v in values]

    # Define the x-axis labels
    fig.update_yaxes(gridwidth=0.03, 
                     title="Flow", showgrid=True,
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))
    fig.update_xaxes(gridwidth=0.03, 
                     title="Time (Minute:Seconds)", showgrid=True, 
                     tickvals=values, ticktext=labels, 
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))    

    # Remove the legend
    fig.update_layout(showlegend=False)

    return fig

def tcp_periodic_tokens_volume_progression(mts: pandas.DataFrame,
                                           bot: pandas.DataFrame, identity: str, title: str):
    
    pass

def process_tracing_data(bot_file, tcp_complete_file, tcp_periodic_file, settings):

    bot_frame = generate_bot_frame(file=bot_file, settings=settings)
    tcp_complete_frame = generate_tcp_complete_frame(file=tcp_complete_file, settings=settings)
    tcp_periodic_frame = generate_tcp_periodic_frame(file=tcp_periodic_file, settings=settings)

    reset_frame_timestamp(frame=tcp_complete_frame, bot=bot_frame, column="fst_packet_observed_unix_ms")
    reset_frame_timestamp(frame=tcp_complete_frame, bot=bot_frame, column="lst_packet_observed_unix_ms")
    reset_frame_timestamp(frame=tcp_periodic_frame, bot=bot_frame, column="s_point_unix_ms")

    tcp_periodic_frame = process_tcp_periodic_frame(tcp_complete=tcp_complete_frame, tcp_periodic=tcp_periodic_frame, bot=bot_frame)
    
    return (bot_frame, tcp_complete_frame, tcp_periodic_frame)

def main():

    with open(SETTINGS, "r") as f:
        settings = yaml.safe_load(f)

    mappings = {
        "illimitata": (BOT_TRACING_FILE_DESKTOP_00MBITS, TCP_COMPLETE_TRACING_FILE_DESKTOP_00MBITS, TCP_PERIODIC_TRACING_FILE_DESKTOP_00MBITS),
        "moderatamente limitata":  (BOT_TRACING_FILE_DESKTOP_4MBITS,  TCP_COMPLETE_TRACING_FILE_DESKTOP_4MBITS,  TCP_PERIODIC_TRACING_FILE_DESKTOP_4MBITS),
        "estremamente limitata":   (BOT_TRACING_FILE_DESKTOP_1MBITS,  TCP_COMPLETE_TRACING_FILE_DESKTOP_1MBITS,  TCP_PERIODIC_TRACING_FILE_DESKTOP_1MBITS)
    }

    # Print the homepage content
    with open(os.path.join(os.getcwd(), "htmls", "sky_over_tcp.html"), "r") as f:
        homepage_content = f.read()  
    
    streamlit.markdown(homepage_content, unsafe_allow_html=True)


    scenarios = {}
    for scenario, files in mappings.items():
        scenarios[scenario] = process_tracing_data(*files, settings=settings)
    
    token = streamlit.selectbox("Seleziona qui il token da filtrare", set(scenarios["illimitata"][1]["token"]))
    streamlit.plotly_chart(tcp_complete_tokens_distribution(tcp=scenarios["illimitata"][1], 
                                                            bot=scenarios["illimitata"][0],
                                                            token=token, 
                                                            title="Distribuzione dei token nel tempo"))
    
    # For each scenario, plot the download and the upload volumes associated with the tokens
    for scenario, frames in scenarios.items():
        title = f"Volumi traffico da server a client su trasferimenti TCP a banda {scenario}"
        streamlit.plotly_chart(tcp_complete_tokens_volume_distribution(tcp=frames[1],
                                                                       bot=frames[0],
                                                                       side="server_app_xmitted_bytes",
                                                                       title=title))
        title = f"Volumi traffico da client a server su trasferimenti TCP a banda {scenario}"
        streamlit.plotly_chart(tcp_complete_tokens_volume_distribution(tcp=frames[1],
                                                                       bot=frames[0],
                                                                       side="client_app_xmitted_bytes",
                                                                       title=title))
        streamlit.markdown("---")

    # For each scenario, plot the download and the upload volumes associated with the tokens, periodically
    # by following the insights in the Tstat log periodic
    for scenario, frames in scenarios.items():
        title = f"Analisi periodica dei token su trasferimenti TCP in condizione di banda {scenario}"
        streamlit.plotly_chart(tcp_periodic_tokens_volume_distribution(mts=frames[2], 
                                                                       bot=frames[0],
                                                                       token=token, 
                                                                       title=title))
        streamlit.markdown("---")

    streamlit.markdown("## Analisi del comportamento SKY al livello UDP")
    streamlit.markdown("---")
    streamlit.markdown("## Analisi del comportamento SKY al livello QUIC")

main()