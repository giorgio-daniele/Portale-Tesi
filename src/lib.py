import os
import pandas
import plotly.express
import plotly.graph_objects

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

    return (f"Token: <b>{record['stoken']}</b><br>"
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

    return (f"Token: <b>{record['stoken']}</b><br>"
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

    return (f"Token: <b>{record['stoken']}</b><br>"
            f"Started  [sec]: {ts_seconds:4.2f}<br>"
            f"Finished [sec]: {te_seconds:4.2f}<br>"
            f"TCP Stream Duration: {sz_minutes}<br>"
            f"Application Bytes from Client: {upload}<br>"
            f"Application Bytes from Server: {dwload}<br>"
            f"Application Protocol: {record['layer7']}")


def log_tcp_complete_timeline(tcp_complete: pandas.DataFrame,
                              bot_complete: pandas.DataFrame, feature: str | None, token: str | None):
    
    # Add the description to each flow if it does not exist yet
    # When rendering more than once the chart, the description
    # should not be generated
    if not "description" in tcp_complete.columns:
        tcp_complete["description"] = tcp_complete.apply(lambda r: log_tcp_complete_description(r), axis=1)

    # If not a feature neither a token is requested to be displayed,
    # generate a figure that associates a color to each existing
    # token in the plot
    if not feature and not token:
        figure = plotly.express.timeline(data_frame=tcp_complete,
                                         x_start="date_ts", x_end="date_te", y=tcp_complete.index, color="stoken",
                                         custom_data=["description"])

    # If not a feature but a token is requested to be displayed,
    # generate a figure that highlights all flows that have that
    # token
    if not feature and token:
        low, high  = "rgba(0, 0, 255, 0.2)", "rgba(0, 0, 255, 1.0)"
        tcp_complete["color"] = tcp_complete["stoken"].apply(lambda x: high if x == token else low)
        figure = plotly.express.timeline(data_frame=tcp_complete,
                                         x_start="date_ts", x_end="date_te", y=tcp_complete.index, color="color",
                                         custom_data=["description"],
                                         color_discrete_map={low: low, high: high})
        
    # If not a token but a feature is requested to be displayed,
    # generate a figure that highlights that feature (a column)
    # in the dataframe
    if feature and not token:
        figure = plotly.express.timeline(data_frame=tcp_complete,
                                         x_start="date_ts", x_end="date_te", y=tcp_complete.index, color=feature,
                                         custom_data=["description"])

    # Update the traces by displaying the custom description, so that when the user
    # can appreciate more details
    figure.update_traces(hovertemplate="%{customdata[0]}",
                         hoverlabel=dict(bgcolor='white', font_size=12, font_family="Courier New"), 
                         opacity=0.7, width=0.7)

    # Loop over all events that are registed by the bot and plot a vertical line
    # corresponding to the instant when that event occurred
    n = len(tcp_complete)
    for _, record in bot_complete.iterrows():
        x0 = pandas.to_datetime(record["from_origin_ts"], unit="ms", origin="unix")

        # Dotted line
        figure.add_shape(dict(type="line", 
                            x0=x0, y0=0, 
                            x1=x0, y1=n,
                            line=dict(color="red", width=0.4, dash="dot")))

        # Annotation at the top
        figure.add_annotation(x=x0, y=n - 1, yref="y",
                            text=record["action"],
                            showarrow=True,
                            arrowhead=2, ax=0, ay=-40)

        # Annotation at the bottom
        figure.add_annotation(x=x0, y=0, yref="y",
                            text=record["action"],
                            showarrow=True,
                            arrowhead=2, ax=0, ay=40)
    
    # Define the x-axis interval
    xs = pandas.to_datetime(bot_complete["from_origin_ts"].min(), unit="ms", origin="unix")
    xe = pandas.to_datetime(bot_complete["from_origin_ts"].max(), unit="ms", origin="unix")

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


def log_tcp_periodic_timeline(tcp_periodic: pandas.DataFrame,
                              bot_complete: pandas.DataFrame, token: str):
    
    # From the original DataFrame genearate a copy containing all flows whose token
    # is the one requested by the user
    selects = tcp_periodic.loc[tcp_periodic["stoken"] == token].copy()

    # Add the description to each flow if it does not exist yet
    # When rendering more than once the chart, the description
    # should not be generated
    if not "description" in selects.columns:
        selects["description"] = selects.apply(lambda r: log_tcp_periodic_description(r), axis=1)

    # Generate the figure
    figure = plotly.express.timeline(data_frame=selects, 
                                     x_start="date_ts", x_end="date_te", y="session_id", color="session_id",
                                     custom_data=["description"])
    
    # Update the traces by displaying the custom description, so that when the user
    # can appreciate more details
    figure.update_traces(hovertemplate="%{customdata[0]}",
                         hoverlabel=dict(bgcolor='white', font_size=12, font_family="Courier New"), 
                         opacity=0.7, width=0.7)

    n = len(selects["session_id"])
    for _, record in bot_complete.iterrows():
        x0 = pandas.to_datetime(record["from_origin_ts"], unit="ms", origin="unix")

        # Dotted line spanning the whole y-axis
        figure.add_shape(type="line", 
                        x0=x0, y0=0, 
                        x1=x0, y1=1,
                        xref="x", yref="paper",
                        line=dict(color="red", width=0.4, dash="dot"))

        # Annotations
        for y, ay in [(1, -40), (0, 40)]:
            figure.add_annotation(x=x0, y=y, yref="paper",
                                text=record["action"],
                                showarrow=True,
                                arrowhead=2, ax=0, ay=ay)
    
    # Define the x-axis interval
    xs = pandas.to_datetime(bot_complete["from_origin_ts"].min(), unit="ms", origin="unix")
    xe = pandas.to_datetime(bot_complete["from_origin_ts"].max(), unit="ms", origin="unix")

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