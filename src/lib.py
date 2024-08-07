import pandas
import numpy
import plotly.express
import plotly.graph_objects

def bytes_to_human_readable(b):

    for u in ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']:
        if b < 1024:
            return f"{b:.2f} {u}"
        b /= 1024

def bitrate_to_human_readable(b, milliseconds):

    if milliseconds == 0:
        return "0 bps"
    
    bps = (b * 8) / (milliseconds / 1000.0)
    units = ['bps', 'Kbps', 'Mbps', 'Gbps', 'Tbps', 'Pbps', 'Ebps', 'Zbps', 'Ybps']
    
    for unit in units:
        if bps < 1000:
            return f"{bps:.2f} {unit}"
        bps /= 1000
    
    return f"{bps:.2f} Ybps"

def tcp_description(record: dict, periodic: bool) -> str:


    app_proto = record["proto"]
    app_token = record["token"]

    c_ip = record["c_ip"]
    s_ip = record["s_ip"]
    c_pt = record["c_pt"]
    s_pt = record["s_pt"]


    ts = record["ts"]
    te = record["te"]

    ts_secnds = ts // 1000
    te_secnds = te // 1000

    ts_minuts = ts_secnds // 60
    te_minuts = te_secnds // 60
    
    millis_span = te - ts
    secnds_span = te_secnds - ts_secnds
    minuts_span = te_minuts - ts_minuts

    c_app_btes = record["c_app_byts"]
    s_app_btes = record["s_app_byts"]

    c_app_pkts = record["c_app_pkts"]
    s_app_pkts = record["s_app_pkts"]

    c_ack_pkts = record["c_ack_pkts"]
    s_ack_pkts = record["s_ack_pkts"]

    c_pure_ack_pkts = record["c_pure_ack_pkts"]
    s_pure_ack_pkts = record["s_pure_ack_pkts"]

    if periodic == False:
        return (
                f"<b>Client</b> <br>"
                f"IP Address:  {c_ip}<br>"
                f"Port Number: {c_pt}<br>"
                f"Application Bytes: {c_app_btes} B ~ {bytes_to_human_readable(c_app_btes)}<br>" 
                f"Application Pakts: {c_app_pkts}<br>" 
                f"Pure ACKs:  {c_pure_ack_pkts}<br>"
                f"     ACKs:  {c_ack_pkts}<br>"
                f"--------------------------<br>"

                f"<b>Server</b> <br>"
                f"IP Address:  {s_ip}<br>"
                f"Port Number: {s_pt}<br>"
                f"Application Bytes: {s_app_btes} B ~ {bytes_to_human_readable(s_app_btes)}<br>"  
                f"Application Pakts: {s_app_pkts}<br>" 
                f"Pure ACKs:  {s_pure_ack_pkts} <br>"
                f"     ACKs:  {s_ack_pkts}<br>"
                f"--------------------------<br>"

                f"<b>Timing</b> <br>"
                f"Start  [millis]: {ts:2.2f}<br>"
                f"Finish [millis]: {te:2.2f}<br>"
                f"Span [millis]: {millis_span:4.2f}<br>"
                f"Span [secnds]: {secnds_span:4.2f}<br>"
                f"Span [mintes]: {minuts_span:4.2f}<br>"
                
                f"Application Proto: {app_proto}<br>"
                f"Application Token: <b>{app_token}</b><br>")
    else:
        return (
                f"<b>Client</b> <br>"
                f"IP Address:  {c_ip}<br>"
                f"Port Number: {c_pt}<br>"
                f"Application Bytes: {c_app_btes:4.2f} B ~ {bytes_to_human_readable(c_app_btes)}<br>" 
                f"Application Rate:  {bitrate_to_human_readable(c_app_btes, milliseconds=record['size'])}<br>" 
                f"Application Pakts: {c_app_pkts}<br>" 
                f"Pure ACKs:  {c_pure_ack_pkts}<br>"
                f"     ACKs:  {c_ack_pkts}<br>"
                f"--------------------------<br>"

                f"<b>Server</b> <br>"
                f"IP Address:  {s_ip}<br>"
                f"Port Number: {s_pt}<br>"
                f"Application Bytes: {s_app_btes:4.2f} B ~ {bytes_to_human_readable(s_app_btes)}<br>" 
                f"Application Rate:  {bitrate_to_human_readable(s_app_btes, milliseconds=record['size'])}<br>"  
                f"Application Pakts: {s_app_pkts}<br>" 
                f"Pure ACKs:  {s_pure_ack_pkts} <br>"
                f"     ACKs:  {s_ack_pkts}<br>"
                f"--------------------------<br>"

                f"<b>Timing</b> <br>"
                f"Start  [millis]: {ts:2.2f}<br>"
                f"Finish [millis]: {te:2.2f}<br>"
                f"Span [millis]: {millis_span:4.2f}<br>"
                f"Span [secnds]: {secnds_span:4.2f}<br>"
                f"Span [mintes]: {minuts_span:4.2f}<br>"
                
                f"Application Token: <b>{app_token}</b><br>")      

def prepare_tcp_complete(complete: pandas.DataFrame):

    # Generate a description for each flow
    complete["info"] = complete.apply(lambda record: tcp_description(record, periodic=False), axis=1)

    # Generate a date-time object from timestamps
    complete["ts_datetime"] = pandas.to_datetime(arg=complete["ts"], unit="ms", origin="unix")  # ts (start of the flow)
    complete["te_datetime"] = pandas.to_datetime(arg=complete["te"], unit="ms", origin="unix")  # te (end of the flow)

def prepare_tcp_periodic(periodic: pandas.DataFrame):

    # Generate a description for each flow
    periodic["info"] = periodic.apply(lambda record: tcp_description(record, periodic=True), axis=1)

    # Generate a date-time object from timestamps
    periodic["ts_datetime"] = pandas.to_datetime(arg=periodic["ts"], unit="ms", origin="unix")  # ts (start of the flow)
    periodic["te_datetime"] = pandas.to_datetime(arg=periodic["te"], unit="ms", origin="unix")  # te (end of the flow)

def tcp_complete_timeline(tcp_complete: pandas.DataFrame, 
                          bot_complete: pandas.DataFrame, feature: str | None):

    if feature:
        figure = plotly.express.timeline(data_frame=tcp_complete, 
                                         x_start="ts_datetime", x_end="te_datetime", y="id",
                                         color=feature,
                                         custom_data=["info"], opacity=1.0, height=800)
    else:
        figure = plotly.express.timeline(data_frame=tcp_complete, 
                                        x_start="ts_datetime", x_end="te_datetime", y="id",
                                        template='plotly_dark',
                                        color_continuous_scale=plotly.express.colors.sequential.Electric, 
                                        color="token",
                                        custom_data=["info"],opacity=1.0, height=800)
    
    figure.update_traces(hovertemplate="%{customdata[0]}",
                         hoverlabel=dict(bgcolor='white', font_size=16, font_family="Courier New"), 
                         opacity=0.7, width=1.0)

    # Define the x-axis interval
    xs = pandas.to_datetime(bot_complete["from"].min(), unit="ms", origin="unix")
    xe = pandas.to_datetime(bot_complete["from"].max(), unit="ms", origin="unix")

    # Define the x-axis range
    xvalues = pandas.date_range(start=xs, end=xe, freq="20s")
    xlabels = [v.strftime("%M:%S") for v in xvalues]

    # Define the y-axis range
    yvalues = [i for i in range(0, len(tcp_complete))]
    ylabels = [f"{i}" for i, record in tcp_complete.iterrows()]

    figure.update_yaxes(gridwidth=0.03, 
                        title="Flow Identifier", showgrid=True,
                        tickvals=yvalues, ticktext=ylabels, 
                        title_font=dict(family="Courier New"), tickfont=dict(family="Courier New", size=10))
    
    figure.update_xaxes(gridwidth=0.03, 
                        title="Time (minutes:seconds)", showgrid=True,
                        tickvals=xvalues, ticktext=xlabels, 
                        title_font=dict(family="Courier New"), tickfont=dict(family="Courier New", size=10)) 

    n = len(tcp_complete)
    for _, record in bot_complete.iterrows():
        x0 = pandas.to_datetime(record["from"], unit="ms", origin="unix")

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
                                arrowhead=2, 
                                ax=0, 
                                ay=ay, 
                                textangle=90,
                                xanchor="left" if y == 1  else "right",
                                yanchor="top"  if y == 1  else "bottom", 
                                font=dict(family="Courier New", size=10, color="black", weight="bold"))
            
    return figure


def tcp_periodic_timeline(tcp_periodic: pandas.DataFrame, 
                          bot_complete: pandas.DataFrame, token: str, id: str | None, feature: str | None):
    
    def get_line_color(feature):
        if "s_app" in feature:
            return "rgba(0, 128, 0, 0.6)"  # Darker Green
        if "c_app" in feature:
            return "rgba(139, 0, 0, 0.6)"  # Darker Red
        return "rgba(0, 0, 139, 0.6)"      # Default Dark Blue
    
    if id is None and feature is None:
        #########################################################
        # Periodic all flows that are associated to a given token
        #########################################################
        data = tcp_periodic.loc[tcp_periodic["token"] == token]
        figure = plotly.express.timeline(data_frame=data, 
                                         x_start="ts_datetime", x_end="te_datetime", y="id",
                                         color_continuous_scale=plotly.express.colors.sequential.Agsunset, 
                                         #template='plotly_dark', 
                                         color="id",
                                         custom_data=["info"], 
                                         opacity=1.0, height=800)

        figure.update_traces(hovertemplate="%{customdata[0]}", 
                             hoverlabel=dict(bgcolor='white', font_size=16, font_family="Courier New"), 
                             opacity=0.7, width=1.0)
        
        # Define the x-axis interval
        xs = pandas.to_datetime(bot_complete["from"].min(), unit="ms", origin="unix")
        xe = pandas.to_datetime(bot_complete["from"].max(), unit="ms", origin="unix")

        # Define the x-axis range
        xvalues = pandas.date_range(start=xs, end=xe, freq="20s")
        xlabels = [v.strftime("%M:%S") for v in xvalues]

        # Define the y-axis range
        ylabels: dict[str] = {i: i.replace("#", " ") for i in data["id"].unique()}

        # Update the y-axis description
        figure.update_yaxes(gridwidth=0.03, 
                            title="Connection Id", showgrid=True,
                            tickvals=list(ylabels.keys()), 
                            ticktext=list(ylabels.values()),
                            title_font=dict(family="Courier New"), tickfont=dict(family="Courier New", size=10)) 
        
    else:
        #########################################################
        # Periodic all flows that are associated to a given id
        #########################################################
        select = tcp_periodic.loc[tcp_periodic["id"] == id]
        figure = plotly.graph_objects.Figure()

        for i, record in select.iterrows():

            xs = "ts"
            xe = "te"
            ys = feature
            ye = feature

            trace = plotly.graph_objects.Scatter(x=[record[xs], record[xe]], y=[record[ys], record[ye]],
                                                 line=dict(color=get_line_color(feature), width=2),
                                                 name=record["info"], hoverinfo="text", 
                                                 text=record["info"])
            figure.add_trace(trace)

        # Define the x-axis range and ticks
        xs = pandas.to_datetime(select["ts"].min(), unit="ms", origin="unix")
        ye = pandas.to_datetime(select["te"].max(), unit="ms", origin="unix")

        # Generate x-axis values (timestamps in milliseconds)
        xvalues = pandas.date_range(start=xs, end=ye, freq="15s").astype(int) / 10**6
        xlabels = [pandas.to_datetime(pos, unit='ms').strftime("%M:%S") for pos in xvalues]

        # Update the y-axis description
        figure.update_yaxes(gridwidth=0.03, 
                            title="# Bytes" if "byts" in feature else "# Packets", showgrid=True,
                            title_font=dict(family="Courier New"), tickfont=dict(family="Courier New", size=10))
        
    figure.update_xaxes(gridwidth=0.03, 
                        title="Time (minutes:seconds)", showgrid=True,
                        tickvals=xvalues, 
                        ticktext=xlabels, 
                        title_font=dict(family="Courier New"), tickfont=dict(family="Courier New", size=10)) 
    
    figure.update_layout(showlegend=False)
    return figure

    
    # def get_line_color(feature):
    #     if "s_app" in feature:
    #         return "rgba(0, 128, 0, 0.6)"  # Darker Green
    #     if "c_app" in feature:
    #         return "rgba(139, 0, 0, 0.6)"  # Darker Red
    #     return "rgba(0, 0, 139, 0.6)"      # Default Dark Blue
    
    # if id and feature: # Plot a single flow with a given id

    #     select = tcp_periodic.loc[tcp_periodic["id"] == id]
    #     figure = plotly.graph_objects.Figure()

    #     for i, record in select.iterrows():

    #         xs = "ts"
    #         xe = "te"
    #         ys = feature
    #         ye = feature

    #         trace = plotly.graph_objects.Scatter(x=[record[xs], record[xe]], y=[record[ys], record[ye]],
    #                                              line=dict(color=get_line_color(feature), width=2),
    #                                              name=record["info"], hoverinfo="text", 
    #                                              text=record["info"])
    #         figure.add_trace(trace)

    #     # Define the x-axis range and ticks
    #     xs = pandas.to_datetime(select["ts"].min(), unit="ms", origin="unix")
    #     ye = pandas.to_datetime(select["te"].max(), unit="ms", origin="unix")

    #     # Generate x-axis values (timestamps in milliseconds)
    #     xvalues = pandas.date_range(start=xs, end=ye, freq="15s").astype(int) / 10**6
    #     xlabels = [pandas.to_datetime(pos, unit='ms').strftime("%M:%S") for pos in xvalues]

    #     # Update the y-axis description
    #     figure.update_yaxes(gridwidth=0.03, 
    #                         title="# Bytes" if "byts" in feature else "# Packets", showgrid=True,
    #                         title_font=dict(family="Courier New"), tickfont=dict(family="Courier New", size=10))

    # else: # Plot all flows that are associated to a given token

    #     select = tcp_periodic.loc[tcp_periodic["token"] == token]
    #     figure = plotly.express.timeline(data_frame=select, 
    #                                     x_start="ts_datetime", x_end="te_datetime", y="id",
    #                                     color_continuous_scale=plotly.express.colors.sequential.Agsunset, 
    #                                     template='plotly_dark',
    #                                     color="id",
    #                                     custom_data=["info"],
    #                                     opacity=1.0, height=800)
    
    #     figure.update_traces(hovertemplate="%{customdata[0]}",
    #                         hoverlabel=dict(bgcolor='white', 
    #                                         font_size=16, 
    #                                         font_family="Courier New"), opacity=0.7, width=1.0)
        
    #     # Define the x-axis interval
    #     xs = pandas.to_datetime(bot_complete["from"].min(), unit="ms", origin="unix")
    #     xe = pandas.to_datetime(bot_complete["from"].max(), unit="ms", origin="unix")

    #     # Define the x-axis range
    #     xvalues = pandas.date_range(start=xs, end=xe, freq="20s")
    #     xlabels = [v.strftime("%M:%S") for v in xvalues]

    #     #Define the y-axis range
    #     ids = list(set(select["id"]))
    #     yvalues: list[int] = list([i for i in range(0, len(ids))])
    #     ylabels: list[str] = list(map(lambda r: r.replace("#", " "), ids))
    #     print()
    #     print(f"N VALUES = {len(yvalues)}")
    #     print(f"YVALUES = {ylabels}")

    #     # Update the y-axis description
    #     figure.update_yaxes(gridwidth=0.03, 
    #                         title="Flow Identifier", showgrid=True,
    #                         tickvals=yvalues, ticktext=ylabels, 
    #                         title_font=dict(family="Courier New"), tickfont=dict(family="Courier New", size=10))
        
    # # Update the x-axis description
    # figure.update_xaxes(gridwidth=0.03, 
    #                     title="Time (minutes:seconds)", showgrid=True,
    #                     tickvals=xvalues, ticktext=xlabels, 
    #                     title_font=dict(family="Courier New"), tickfont=dict(family="Courier New", size=10)) 

    # figure.update_layout(showlegend=False)
            
    # return figure

# def tcp_periodic_timeline_feature(tcp_periodic: pandas.DataFrame, bot_complete: pandas.DataFrame, id: str, feature: str):

#     def get_line_color(feature):
#         if "s_app" in feature:
#             return "rgba(0, 128, 0, 0.6)"  # Darker Green
#         if "c_app" in feature:
#             return "rgba(139, 0, 0, 0.6)"  # Darker Red
#         return "rgba(0, 0, 139, 0.6)"      # Default Dark Blue

#     data = tcp_periodic.loc[tcp_periodic["id"] == id]
#     figure = plotly.graph_objects.Figure()

#     for i, record in data.iterrows():

#         xs = "ts"
#         xe = "te"
#         ys = feature
#         ye = feature

#         trace = plotly.graph_objects.Scatter(x=[record[xs], record[xe]],
#                                              y=[record[ys], record[ye]],
#                                              line=dict(color=get_line_color(feature), width=2),
#                                              name=record["info"], 
#                                              hoverinfo="text", 
#                                              text=record["info"])
        
#         figure.add_trace(trace)


#     # Define the x-axis range and ticks
#     s = pandas.to_datetime(data["ts"].min(), unit="ms", origin="unix")
#     e = pandas.to_datetime(data["te"].max(), unit="ms", origin="unix")

#     # Generate x-axis values (timestamps in milliseconds)
#     xvalues = pandas.date_range(start=s, end=e, freq="15s").astype(int) / 10**6
#     xlabels = [pandas.to_datetime(pos, unit='ms').strftime("%M:%S") for pos in xvalues]

#     figure.update_yaxes(gridwidth=0.03, 
#                         title="# Bytes" if "byts" in feature else "# Packets", showgrid=True,
#                         title_font=dict(family="Courier New"), tickfont=dict(family="Courier New", size=10))
    
#     figure.update_xaxes(gridwidth=0.03, 
#                         title="Time (minutes:seconds)", showgrid=True,
#                         tickvals=xvalues, ticktext=xlabels, 
#                         title_font=dict(family="Courier New"), tickfont=dict(family="Courier New", size=10)) 
    
#     figure.update_layout(showlegend=False)

#     return figure