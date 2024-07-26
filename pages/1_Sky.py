import os
import pandas
import streamlit
import plotly.express
import plotly.graph_objects


log_tcp_complete = os.path.join(os.getcwd(), "data/sky/desktop", "log_tcp_complete.enhanced")
log_udp_complete = os.path.join(os.getcwd(), "data/sky/desktop", "log_udp_complete.enhanced")
log_tcp_periodic = os.path.join(os.getcwd(), "data/sky/desktop", "log_tcp_periodic.enhanced")
log_bot_complete = os.path.join(os.getcwd(), "data/sky/desktop", "streambot_trace.csv")

tcp_complete = pandas.read_csv(filepath_or_buffer=log_tcp_complete, delimiter=" ")
tcp_periodic = pandas.read_csv(filepath_or_buffer=log_tcp_periodic, delimiter=" ")
udp_complete = pandas.read_csv(filepath_or_buffer=log_udp_complete, delimiter=" ")
bot_complete = pandas.read_csv(filepath_or_buffer=log_bot_complete, delimiter=" ")

tcp_periodic["session_id"] = tcp_periodic.apply(
    lambda row: f"{row['s_ip']}:{row['s_pt']} -- {row['c_ip']}:{row['c_pt']}", axis=1)

def log_tcp_complete_description(record: dict) -> str:

    ts_millis = record["unix_ts"]
    te_millis = record["unix_te"]

    ts_seconds = ts_millis // 1000
    te_seconds = te_millis // 1000

    sz_millis  = te_millis - ts_millis
    sz_seconds = sz_millis  // 1000
    sz_minutes = sz_seconds // 60
        
    dwload = record["dwload"]
    upload = record["upload"]

    return (f"Token: <b>{record['token']}</b><br>"
            f"Client IP: {record['c_ip']}<br>"
            f"Server IP: {record['s_ip']}<br>"
            f"Client Port: {record['c_pt']}<br>"
            f"Server Port: {record['s_pt']}<br>"
            f"Started  [mis]: {ts_millis:4.2f}<br>"
            f"Finished [mis]: {te_millis:4.2f}<br>"
            f"Started  [sec]: {ts_seconds:4.2f}<br>"
            f"Finished [sec]: {te_seconds:4.2f}<br>"
            f"TCP Stream Duration [mis]: {sz_millis:4.2f}<br>"
            f"TCP Stream Duration [sec]: {sz_seconds:4.2f}<br>"
            f"TCP Stream Duration [min]: {sz_minutes:4.2f}<br>"
            f"Application Bytes from Client: {upload}<br>"
            f"Application Bytes from Server: {dwload}<br>"
            f"Application Protocol: {record['layer7']}")

def log_tcp_periodic_description(record: dict) -> str:

    ts_millis = record["unix_ts"]
    te_millis = record["unix_te"]

    ts_seconds = ts_millis // 1000
    te_seconds = te_millis // 1000

    sz_millis  = te_millis - ts_millis
    sz_seconds = sz_millis  // 1000
    sz_minutes = sz_seconds // 60
        
    dwload = record["dwload"]
    upload = record["upload"]

    return (f"Token: <b>{record['token']}</b><br>"
            f"Client IP: {record['c_ip']}<br>"
            f"Server IP: {record['s_ip']}<br>"
            f"Client Port: {record['c_pt']}<br>"
            f"Server Port: {record['s_pt']}<br>"
            f"Started  [mis]: {ts_millis:4.2f}<br>"
            f"Finished [mis]: {te_millis:4.2f}<br>"
            f"Started  [sec]: {ts_seconds:4.2f}<br>"
            f"Finished [sec]: {te_seconds:4.2f}<br>"
            f"TCP Stream Duration [mis]: {sz_millis:4.2f}<br>"
            f"TCP Stream Duration [sec]: {sz_seconds:4.2f}<br>"
            f"TCP Stream Duration [min]: {sz_minutes:4.2f}<br>"
            f"Application Bytes from Client: {upload}<br>"
            f"Application Bytes from Server: {dwload}<br>")

def log_udp_complete_description(record: dict, side: str) -> str:

    if side == "server":
        ts_seconds = record["s_unix_ts"] // 1000
        te_seconds = record["s_unix_te"] // 1000
    if side == "client":
        ts_seconds = record["c_unix_ts"] // 1000
        te_seconds = record["c_unix_te"] // 1000

    sz_seconds = te_seconds - ts_seconds
    sz_minutes = f"{int((sz_seconds) / 60)} minutes, {int((sz_seconds) % 60)} seconds"
        
    dwload = record["dwload"]
    upload = record["upload"]

    return (f"Token: <b>{record['token']}</b><br>"
            f"Started  [sec]: {ts_seconds:4.2f}<br>"
            f"Finished [sec]: {te_seconds:4.2f}<br>"
            f"TCP Stream Duration: {sz_minutes}<br>"
            f"Application Bytes from Client: {upload}<br>"
            f"Application Bytes from Server: {dwload}<br>"
            f"Application Protocol: {record['layer7']}")

def log_tcp_complete_timeline(feature: str | None, token: str | None):


    if "ds" not in tcp_complete.columns:
        tcp_complete["ds"] = tcp_complete.apply(lambda r: log_tcp_complete_description(r), axis=1)

    if not feature and not token:
        color  = "token"
        figure = plotly.express.timeline(data_frame=tcp_complete,
                                         x_start="date_ts", x_end="date_te",
                                         color=color,
                                         custom_data=["ds"], y=tcp_complete.index)
        
    if feature and not token:
        color  = feature
        figure = plotly.express.timeline(data_frame=tcp_complete,
                                         x_start="date_ts", x_end="date_te",
                                         color=color,
                                         custom_data=["ds"], y=tcp_complete.index)
        
    if not feature and token:
        if "color" not in tcp_complete.columns:
            low, high  = "rgba(0, 0, 255, 0.2)", "rgba(0, 0, 255, 1.0)"
            tcp_complete["color"] = tcp_complete["token"].apply(lambda x: high if x == token else low)

        figure = plotly.express.timeline(data_frame=tcp_complete,
                                         x_start="date_ts", x_end="date_te",
                                         color="color",
                                         custom_data=["ds"], y=tcp_complete.index,
                                         color_discrete_map={low: low, high: high})
    
    figure.update_traces(hovertemplate="%{customdata[0]}",
                      hoverlabel=dict(bgcolor='white', 
                                      font_size=12, 
                                      font_family="Courier New"), opacity=0.7, width=0.7)
    
    for _, record in bot_complete.iterrows():

        x0 = pandas.to_datetime(record["from_origin_ms"], unit="ms", origin="unix")
        figure.add_shape(dict(type="line", 
                           x0=x0, y0=0, 
                           x1=x0, y1=len(tcp_complete),
                           line=dict(color="red", width=0.4, dash="dot")))

        figure.add_annotation(x=x0, y=len(tcp_complete),
                           text=record["event"],
                           showarrow=True,
                           arrowhead=2, ax=0, ay=-40)
        
        figure.add_annotation(x=x0, y=0,
                           text=record["event"],
                           showarrow=True,
                           arrowhead=2, ax=0, ay=40)
    
    # Define the x-axis interval
    xs = pandas.to_datetime(bot_complete["from_origin_ms"].min(), unit="ms", origin="unix")
    xe = pandas.to_datetime(bot_complete["from_origin_ms"].max(), unit="ms", origin="unix")

    # Define the x-axis range
    values = pandas.date_range(start=xs, end=xe, freq="20s")
    labels = [v.strftime("%M:%S") for v in values]

    # Define the x-axis labels
    figure.update_yaxes(gridwidth=0.03, 
                     title="Flow", showgrid=True,
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))
    figure.update_xaxes(gridwidth=0.03, 
                     title="Time (minutes:seconds)", showgrid=True, 
                     tickvals=values, ticktext=labels, 
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))    

    # Display the legend
    if not token and not feature:
        figure.update_layout(showlegend=True)
    else:
        figure.update_layout(showlegend=False)

    return figure

def log_udp_complete_timeline(feature: str | None, token: str | None, side: str):

    start  = "c_date_ts" if side == "client" else "s_date_ts"
    finish = "c_date_te" if side == "client" else "s_date_te"

    if "ds" not in udp_complete.columns:
        udp_complete["ds"] = udp_complete.apply(lambda r: log_udp_complete_description(r, side=side), axis=1)

    figure = plotly.express.timeline(data_frame=udp_complete,
                                         x_start=start, x_end=finish,
                                         color="token",
                                         custom_data=["ds"], 
                                         y=udp_complete.index)
    
    figure.update_traces(hovertemplate="%{customdata[0]}",
                      hoverlabel=dict(bgcolor='white', 
                                      font_size=12, 
                                      font_family="Courier New"), opacity=0.7, width=0.7)
    
    for _, record in bot_complete.iterrows():

        x0 = pandas.to_datetime(record["from_origin_ms"], unit="ms", origin="unix")
        figure.add_shape(dict(type="line", 
                           x0=x0, y0=0, 
                           x1=x0, y1=len(udp_complete),
                           line=dict(color="red", width=0.4, dash="dot")))

        figure.add_annotation(x=x0, y=len(udp_complete),
                           text=record["event"],
                           showarrow=True,
                           arrowhead=2, ax=0, ay=-40)
        
        figure.add_annotation(x=x0, y=0,
                           text=record["event"],
                           showarrow=True,
                           arrowhead=2, ax=0, ay=40)
    
    # Define the x-axis interval
    xs = pandas.to_datetime(bot_complete["from_origin_ms"].min(), unit="ms", origin="unix")
    xe = pandas.to_datetime(bot_complete["from_origin_ms"].max(), unit="ms", origin="unix")

    # Define the x-axis range
    values = pandas.date_range(start=xs, end=xe, freq="20s")
    labels = [v.strftime("%M:%S") for v in values]

    # Define the x-axis labels
    figure.update_yaxes(gridwidth=0.03, 
                     title="Flow", showgrid=True,
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))
    figure.update_xaxes(gridwidth=0.03, 
                     title="Time (minutes:seconds)", showgrid=True, 
                     tickvals=values, ticktext=labels, 
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))    

    # Display the legend
    figure.update_layout(showlegend=True)

    return figure

def log_tcp_periodic_timeline(token: str):

    selects = tcp_periodic.loc[tcp_periodic["token"] == token].copy()

    if "ds" not in selects.columns:
        selects["ds"] = selects.apply(lambda r: log_tcp_periodic_description(r), axis=1)

    figure = plotly.express.timeline(data_frame=selects,
                                     x_start="date_ts", x_end="date_te",
                                     color="session_id",
                                     custom_data=["ds"], 
                                     y="session_id")
    
    figure.update_traces(hovertemplate="%{customdata[0]}",
                      hoverlabel=dict(bgcolor='white', 
                                      font_size=12, 
                                      font_family="Courier New"), opacity=0.7, width=0.7)

    num_sessions = len(selects["session_id"].unique())
    for _, record in bot_complete.iterrows():
        x0 = pandas.to_datetime(record["from_origin_ms"], unit="ms", origin="unix")

        figure.add_shape(dict(type="line", 
                            x0=x0, y0=0, 
                            x1=x0, y1=num_sessions,
                            line=dict(color="red", width=0.4, dash="dot")))

        # Annotation at the top
        figure.add_annotation(x=x0, y=num_sessions - 1, yref="y",
                            text=record["event"],
                            showarrow=True,
                            arrowhead=2, ax=0, ay=-40)

        # Annotation at the bottom
        figure.add_annotation(x=x0, y=0, yref="y",
                            text=record["event"],
                            showarrow=True,
                            arrowhead=2, ax=0, ay=40)
    
    # Define the x-axis interval
    xs = pandas.to_datetime(bot_complete["from_origin_ms"].min(), unit="ms", origin="unix")
    xe = pandas.to_datetime(bot_complete["from_origin_ms"].max(), unit="ms", origin="unix")

    # Define the x-axis range
    values = pandas.date_range(start=xs, end=xe, freq="20s")
    labels = [v.strftime("%M:%S") for v in values]

    # Define the x-axis labels
    figure.update_yaxes(gridwidth=0.03, 
                     title="Flow", showgrid=True,
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))
    figure.update_xaxes(gridwidth=0.03, 
                     title="Time (minutes:seconds)", showgrid=True, 
                     tickvals=values, ticktext=labels, 
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))  
    
    figure.update_layout(showlegend=False)

    return figure

def log_tcp_periodic_series(session_id: str):

    selects = tcp_periodic.loc[tcp_periodic["session_id"] == session_id].copy()

    if "ds" not in selects.columns:
        selects["ds"] = selects.apply(lambda r: log_tcp_periodic_description(r), axis=1)

    selects['s_app_byts'] = selects['s_app_byts'].replace(0, 1)
    selects['c_app_byts'] = selects['c_app_byts'].replace(0, 1)

    figure = plotly.graph_objects.Figure()

    def create_step_data(df, x_col_start, x_col_end, y_col, text_col):

        x_vals = []
        y_vals = []
        text_vals = []
        
        for i in range(len(df)):
            # Add start point
            x_vals.append(df.iloc[i][x_col_start])
            y_vals.append(df.iloc[i][y_col])
            text_vals.append(df.iloc[i][text_col])
            
            # Add end point
            x_vals.append(df.iloc[i][x_col_end])
            y_vals.append(df.iloc[i][y_col])
            text_vals.append(df.iloc[i][text_col])
        
        return x_vals, y_vals, text_vals

    # Add scatter plot with log scale on y-axis
    x_vals_c, y_vals_c, text_c = create_step_data(selects, 'date_ts', 'date_te', 'c_app_byts', 'ds')
    figure.add_trace(plotly.graph_objects.Scatter(x=x_vals_c, y=y_vals_c,
                                                  mode='lines',
                                                  name='s_app_byts',
                                                  line=dict(shape='hv'),
                                                  text=text_c,
                                                  marker=dict(color='red'), hoverinfo='text'))
    
    x_vals_s, y_vals_s, text_s = create_step_data(selects, 'date_ts', 'date_te', 's_app_byts', 'ds')
    figure.add_trace(plotly.graph_objects.Scatter(x=x_vals_s, y=y_vals_s,
                                                  mode='lines',
                                                  name='c_app_byts',
                                                  line=dict(shape='hv'),
                                                  text=text_s,
                                                  marker=dict(color='green'), hoverinfo='text'))
    
    # Define the x-axis interval
    xs = pandas.to_datetime(selects["unix_ts"].min(), unit="ms", origin="unix")
    xe = pandas.to_datetime(selects["unix_te"].max(), unit="ms", origin="unix")

    # Define the x-axis range
    values = pandas.date_range(start=xs, end=xe, freq="20s")
    labels = [v.strftime("%M:%S") for v in values]

    figure.update_yaxes(gridwidth=0.03,
                     title="Volumes", showgrid=True,
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))
    figure.update_xaxes(gridwidth=0.03, 
                     title="Time (minutes:seconds)", showgrid=True, 
                     tickvals=values, ticktext=labels, 
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))   

    # Update layout to set log scale for y-axis
    figure.update_layout(title='Silence and Talks',
                         yaxis=dict(type='log'))
    
    figure.update_layout(showlegend=False)

    return figure


streamlit.markdown("## Data traffic over TCP")
token = streamlit.selectbox("Seleziona qui il token da filtrare", 
                            list(set(tcp_complete["token"])))

streamlit.plotly_chart(log_tcp_complete_timeline(feature=None, token=token))
# streamlit.plotly_chart(log_tcp_complete_timeline(feature=None, token=None))
streamlit.plotly_chart(log_tcp_complete_timeline(feature="s_app_byts", token=None))
streamlit.plotly_chart(log_tcp_complete_timeline(feature="c_app_byts", token=None))
streamlit.plotly_chart(log_tcp_periodic_timeline(token=token))

session_id = streamlit.selectbox("Seleziona qui il flusso da analizzare nel dettaglio", 
                            list(set(tcp_periodic.loc[tcp_periodic["token"] == token]["session_id"])))
streamlit.plotly_chart(log_tcp_periodic_series(session_id=session_id))

streamlit.markdown("## Data traffic over UDP")
streamlit.plotly_chart(log_udp_complete_timeline(feature=None, token=token, side="client"))
streamlit.plotly_chart(log_udp_complete_timeline(feature=None, token=token, side="server"))


