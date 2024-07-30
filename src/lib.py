import os
import pandas
import plotly.express
import plotly.graph_objects

def tcp_description(record: dict) -> str:

    ts_milliseconds = record["unix_ts_millis"]
    te_milliseconds = record["unix_te_millis"]

    ts_seconds = ts_milliseconds // 1000
    te_seconds = te_milliseconds // 1000

    duration_milliseconds = te_milliseconds - ts_milliseconds
    duration_seconds = duration_milliseconds // 1000
    duration_minutes = duration_seconds // 60
    
    client_volume = record["c_app_volume"]
    server_volume = record["s_app_volume"]

    server_rate = record["s_app_rate_kbits"]
    client_rate = record["c_app_rate_kbits"]

    application_token = record["app_token"]
    application_proto = record["app_proto"]

    return (f"Token: <b>{application_token}</b><br>"
            f"Client IP: {record['c_ip']}<br>"
            f"Server IP: {record['s_ip']}<br>"
            f"Client Port: {record['c_pt']}<br>"
            f"Server Port: {record['s_pt']}<br>"
            f"Started  [milliseconds]: {ts_milliseconds:4.2f}<br>"
            f"Finished [milliseconds]: {te_milliseconds:4.2f}<br>"
            f"Started  [seconds]: {ts_seconds:4.2f}<br>"
            f"Finished [seconds]: {te_seconds:4.2f}<br>"
            f"Duration [milliseconds]: {duration_milliseconds:4.2f}<br>"
            f"Duration [seconds]: {duration_seconds:4.2f}<br>"
            f"Duration [minutes]: {duration_minutes:4.2f}<br>"
            f"Client Application Rate: {client_rate}<br>"
            f"Server Application Rate: {server_rate}<br>"
            f"Client Application Data: {client_volume}<br>"
            f"Server Application Data: {server_volume}<br>"
            f"Application Protocol: {application_proto}")


def log_tcp_complete_timeline(tcp_complete: pandas.DataFrame,
                              bot_complete: pandas.DataFrame, feature: str | None, token: str | None):
    
    # Add the description to each flow if it does not exist yet
    # When rendering more than once the chart, the description
    # should not be generated
    if not "desc" in tcp_complete.columns:
        tcp_complete["desc"] = tcp_complete.apply(lambda r: tcp_description(r), axis=1)

    ts = "datetime_ts"
    te = "datetime_te"
    
    # If not a feature neither a token is requested to be displayed,
    # generate a figure that associates a color to each existing
    # token in the plot
    if not feature and not token:
        color = "app_token"
        figure = plotly.express.timeline(data_frame=tcp_complete,
                                         x_start=ts, x_end=te, y=tcp_complete.index, color=color,
                                         custom_data=["desc"])

    # If not a feature but a token is requested to be displayed,
    # generate a figure that highlights all flows that have that
    # token
    if not feature and token:
        color = "app_token"
        low, high  = "rgba(0, 0, 255, 0.2)", "rgba(0, 0, 255, 1.0)"
        tcp_complete["color"] = tcp_complete[color].apply(lambda x: high if x == token else low)
        figure = plotly.express.timeline(data_frame=tcp_complete,
                                         x_start=ts, x_end=te, y=tcp_complete.index, color="color",
                                         custom_data=["desc"],
                                         color_discrete_map={low: low, high: high})
        
    # If not a token but a feature is requested to be displayed,
    # generate a figure that highlights that feature (a column)
    # in the dataframe
    if feature and not token:
        figure = plotly.express.timeline(data_frame=tcp_complete,
                                         x_start=ts, x_end=te, y=tcp_complete.index, color=feature,
                                         custom_data=["desc"])

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
        for y, ay in [(1, -40), (0, 40)]:
            figure.add_annotation(x=x0, y=y, yref="paper",
                                text=record["action"],
                                showarrow=False,
                                arrowhead=2, ax=0, ay=ay, textangle=90,
                                xanchor="left" if y == 1 else "right",
                                yanchor="top" if y == 1 else "bottom", font=dict(family="Courier New", size=8))
    
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
    selects = tcp_periodic.loc[tcp_periodic["app_token"] == token].copy()

    # Add the description to each flow if it does not exist yet
    # When rendering more than once the chart, the description
    # should not be generated
    if not "desc" in selects.columns:
        selects["desc"] = selects.apply(lambda r: tcp_description(r), axis=1)

    ts = "datetime_ts"
    te = "datetime_te"
    id = "connection_id"

    # Generate the figure
    figure = plotly.express.timeline(data_frame=selects, 
                                     x_start=ts, x_end=te, y=id, color=id,
                                     custom_data=["desc"])
    
    # Update the traces by displaying the custom description, so that when the user
    # can appreciate more details
    figure.update_traces(hovertemplate="%{customdata[0]}",
                         hoverlabel=dict(bgcolor='white', font_size=12, font_family="Courier New"), 
                         opacity=0.7, width=0.7)

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
                                showarrow=False,
                                arrowhead=2, ax=0, ay=ay, textangle=90,
                                xanchor="left" if y == 1 else "right",
                                yanchor="top" if y == 1 else "bottom", font=dict(family="Courier New", size=8))
    
    # Define the x-axis interval
    xs = pandas.to_datetime(bot_complete["from_origin_ts"].min(), unit="ms", origin="unix")
    xe = pandas.to_datetime(bot_complete["from_origin_ts"].max(), unit="ms", origin="unix")

    # Define the x-axis range
    values = pandas.date_range(start=xs, end=xe, freq="15s")
    labels = [v.strftime("%M:%S") for v in values]

    # Define the x-axis labels
    figure.update_yaxes(gridwidth=0.03, 
                     title="Session ID", showgrid=True,
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))
    
    figure.update_xaxes(gridwidth=0.03, 
                     title="Time (minutes:seconds)", showgrid=True, 
                     tickvals=values, ticktext=labels, 
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))  
    
    figure.update_layout(showlegend=False)

    return figure

def log_tcp_periodic_flow_chart(tcp_periodic: pandas.DataFrame, connection_id: str, feature: str):

    # From the original DataFrame genearate a copy containing all flows whose token
    # is the one requested by the user
    selects = tcp_periodic.loc[tcp_periodic["connection_id"] == connection_id].copy()

    # Add the description to each flow if it does not exist yet
    # When rendering more than once the chart, the description
    # should not be generated
    if not "desc" in selects.columns:
        selects["desc"] = selects.apply(lambda r: tcp_description(r), axis=1)

    ts = "datetime_ts"
    te = "datetime_te"
    ys = feature

    figure = plotly.graph_objects.Figure()

    figure.add_traces([
        plotly.graph_objects.Scatter(
            x=[record[ts], record[te], record[te], record[ts], record[ts]],
            y=[record[ys], record[ys], record[ys] + 3, record[ys] + 3, record[ys]],
            line=dict(color='rgba(0, 100, 200, 0.6)', width=1),
            name=record['desc'],
            hoverinfo='text',
            text=record['desc'])
        for _, record in selects.iterrows()])
    
    for i in range(len(selects) - 1):
        sy = selects.iloc[i][ys] + 3
        ey = selects.iloc[i + 1][ys] + 3
        figure.add_trace(plotly.graph_objects.Scatter(
            x=[selects.iloc[i][te], selects.iloc[i + 1][ts]],
            y=[sy, ey],
            mode='lines',
            line=dict(color='rgba(0, 0, 0, 0.6)', width=0.4, dash='dot')))
        
    # Define the x-axis interval
    xs = pandas.to_datetime(selects["unix_ts_millis"].min(), unit="ms", origin="unix")
    xe = pandas.to_datetime(selects["unix_te_millis"].max(), unit="ms", origin="unix")

    # Define the x-axis range
    values = pandas.date_range(start=xs, end=xe, freq="15s")
    labels = [v.strftime("%M:%S") for v in values]

    # Define the x-axis labels
    figure.update_yaxes(gridwidth=0.03, 
                     title="Volume (B)", showgrid=True,
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))
    
    figure.update_xaxes(gridwidth=0.03, 
                     title="Time (minutes:seconds)", showgrid=True, 
                     tickvals=values, ticktext=labels, 
                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))  
    
    figure.update_layout(showlegend=False)

    return figure