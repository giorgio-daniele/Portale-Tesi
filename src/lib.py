import pandas
import numpy
import plotly.express
import plotly.graph_objects
import scipy.interpolate


def tcp_description(record: dict, periodic: bool) -> str:

    #####################################################
    # Application level information
    #####################################################
    app_proto = record["app_proto"]
    app_token = record["app_token"]

    #####################################################
    # Socket level information
    #####################################################
    c_ip = record["c_ip"]
    s_ip = record["s_ip"]
    c_pt = record["c_pt"]
    s_pt = record["s_pt"]

    #####################################################
    # Timings
    #####################################################
    ts = record["unix_ts_millis"]
    te = record["unix_te_millis"]

    ts_secnds = ts // 1000
    te_secnds = te // 1000

    ts_minuts = ts_secnds // 60
    te_minuts = te_secnds // 60
    
    millis_span = te - ts
    secnds_span = te_secnds - ts_secnds
    minuts_span = te_minuts - ts_minuts

    #####################################################
    # Volumes
    #####################################################
    c_app_btes = record["c_app_volume"]
    s_app_btes = record["s_app_volume"]

    c_app_pkts = record["c_app_pkts"]
    s_app_pkts = record["s_app_pkts"]

    c_ack_pkts = record["c_ack_pkts"]
    s_ack_pkts = record["s_ack_pkts"]

    c_pure_ack_pkts = record["c_pure_ack_pkts"]
    s_pure_ack_pkts = record["s_pure_ack_pkts"]

    #####################################################
    # Volumes
    #####################################################

    if periodic == True:
        c_app_rate = record["c_app_rate_kbits"]
        s_app_rate = record["s_app_rate_kbits"]

    if periodic == True:
        return (
            f"<b> Client Related</b> <br>"
            f"IP: {c_ip} PT: {c_pt} <br>"
            f"Application Bytes: {c_app_btes} <br>" 
            f"Application Pakts: {c_app_pkts} <br>" 
            f"Application Rate:  {c_app_rate} <br>" 
            f"Pure ACKs:  {c_pure_ack_pkts} <br>"
            f"     ACKs:  {c_ack_pkts} <br>"

            f"<b> Server Related</b> <br>"
            f"IP: {s_ip} PT: {s_pt} <br>"
            f"Application Bytes: {s_app_btes} <br>" 
            f"Application Pakts: {s_app_pkts} <br>" 
            f"Application Rate:  {s_app_rate} <br>" 
            f"Pure ACKs:  {s_pure_ack_pkts} <br>"
            f"     ACKs:  {s_ack_pkts} <br>"

            f"<b> Timing Information</b> <br>"
            f"Start  [millis]: {ts:2.2f}<br>"
            f"Finish [millis]: {te:2.2f}<br>"
            f"Span [millis]: {millis_span:4.2f}<br>"
            f"Span [secnds]: {secnds_span:4.2f}<br>"
            f"Span [mintes]: {minuts_span:4.2f}<br>"
            
            f"Application Proto: {app_proto}<br>"
            f"Application Token: <b>{app_token}</b><br>")

    else:
        return (
            f"<b> Client Related</b> <br>"
            f"IP: {c_ip} PT: {c_pt} <br>"
            f"Application Bytes: {c_app_btes} <br>" 
            f"Application Pakts: {c_app_pkts} <br>" 
            f"Pure ACKs:  {c_pure_ack_pkts} <br>"
            f"     ACKs:  {c_ack_pkts} <br>"

            f"<b> Server Related</b> <br>"
            f"IP: {s_ip} PT: {s_pt} <br>"
            f"Application Bytes: {s_app_btes} <br>" 
            f"Application Pakts: {s_app_pkts} <br>" 
            f"Pure ACKs:  {s_pure_ack_pkts} <br>"
            f"     ACKs:  {s_ack_pkts} <br>"

            f"<b> Timing Information</b> <br>"
            f"Start  [millis]: {ts:2.2f}<br>"
            f"Finish [millis]: {te:2.2f}<br>"
            f"Span [millis]: {millis_span:4.2f}<br>"
            f"Span [secnds]: {secnds_span:4.2f}<br>"
            f"Span [mintes]: {minuts_span:4.2f}<br>"
            
            f"Application Proto: {app_proto}<br>"
            f"Application Token: <b>{app_token}</b><br>")


def tcp_complete_timeline(tcp_complete: pandas.DataFrame,
                          bot_complete: pandas.DataFrame, feature: str | None, token: str | None):
    
    # Add the description to each flow if it does not exist yet
    # When rendering more than once the chart, the description
    # should not be generated
    if not "desc" in tcp_complete.columns:
        tcp_complete["desc"] = tcp_complete.apply(lambda r: tcp_description(r, periodic=False), axis=1)

    ts = "datetime_ts"
    te = "datetime_te"
    
    # If not a feature neither a token is requested to be displayed,
    # generate a figure that associates a color to each existing
    # token in the plot
    if not feature and not token:
        color  = "app_token"
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
        if "s_app" in feature:
            color_scale = plotly.express.colors.sequential.Greens
        else:
            color_scale = plotly.express.colors.sequential.Reds
        figure = plotly.express.timeline(data_frame=tcp_complete,
                                         x_start=ts, x_end=te, y=tcp_complete.index, color=feature,
                                         color_continuous_scale=color_scale,
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

def tcp_periodic_timeline(tcp_periodic: pandas.DataFrame,
                          bot_complete: pandas.DataFrame, token: str):
    
    ##################################################
    # Generate a copy of the original pandas DataFrame
    # so we can edit it at free will
    ##################################################
    selects = tcp_periodic.loc[tcp_periodic["app_token"] == token].copy()

    # Add the description to each flow if it does not exist yet
    # When rendering more than once the chart, the description
    # should not be generated
    if not "desc" in selects.columns:
        selects["desc"] = selects.apply(lambda r: tcp_description(r, periodic=True), axis=1)

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

def get_line_color(feature):
    if "s_app" in feature:
        return "rgba(0, 128, 0, 0.6)"  # Darker Green
    if "c_app" in feature:
        return "rgba(139, 0, 0, 0.6)"  # Darker Red
    return "rgba(0, 0, 139, 0.6)"      # Default Dark Blue

def connection_id_timeline(frame: pandas.DataFrame, connection_id: str, feature: str):

    #################################################################
    # Generate a copy of the original pandas DataFrame according to 
    # the "connection_id" that has been selected by the user.
    #################################################################
    data = frame.loc[frame["connection_id"] == connection_id].copy()

    #################################################################
    # Generate a description for each scatter point, so that it is
    # easier to understand what the user is looking
    #################################################################
    data["info"] = data.apply(lambda r: tcp_description(r, periodic=True), axis=1)

    # Create Plotly figure
    figure = plotly.graph_objects.Figure()

    for i, record in data.iterrows():

        xs = "unix_ts_millis"
        xe = "unix_te_millis"
        ys = feature
        ye = feature

        trace = plotly.graph_objects.Scatter(x=[record[xs], record[xe]],
                                             y=[record[ys], record[ye]],
                                             line=dict(color=get_line_color(feature), width=2),
                                             name=record["info"], 
                                             hoverinfo="text", 
                                             text=record["info"])
        
        figure.add_trace(trace)

    # Define the x-axis range and ticks
    s = pandas.to_datetime(data["unix_ts_millis"].min(), unit="ms", origin="unix")
    e = pandas.to_datetime(data["unix_ts_millis"].max(), unit="ms", origin="unix")

    # Generate x-axis values (timestamps in milliseconds)
    values = pandas.date_range(start=s, end=e, freq="15s").astype(int) / 10**6
    labels = [pandas.to_datetime(pos, unit='ms').strftime("%M:%S") for pos in values]

    # Define the y-axis settings
    figure.update_yaxes(gridwidth=0.03, 
                        title="# Bytes" if "byts" in feature else "# Packets", showgrid=True,
                        title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))
    
     # Define the x-axis settings
    figure.update_xaxes(gridwidth=0.03, 
                        title="Time (minutes:seconds)", showgrid=True, 
                        tickvals=values, ticktext=labels, 
                        title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))   
    
    figure.update_layout(showlegend=False)

    return figure


def connection_id_discrete_fourier(frame: pandas.DataFrame, connection_id: str, feature: str):

    #################################################################
    # Generate a copy of the original pandas DataFrame according to 
    # the "connection_id" that has been selected by the user.
    #################################################################
    data = frame.loc[frame["connection_id"] == connection_id].copy()


    #################################################################
    # Generate a discrete signal to be further converted into the FFT
    #################################################################
    x = []
    y = []

    for _, record in data.iterrows():

        xs = record["unix_ts_millis"]
        xe = record["unix_te_millis"]
        ys = record[feature]
        ye = record[feature]

        x.append(xs)
        #x.append(xe)
        y.append(ys)
        #y.append(ye)


    interpolator = scipy.interpolate.interp1d(x, y, kind='linear', fill_value="extrapolate")

    x_uniform = numpy.linspace(numpy.min(x), numpy.max(x), num=len(x)*1)
    y_uniform = interpolator(x_uniform)
    xvalues = x_uniform
    yvalues = y_uniform

    # Perform FFT
    fft_y = numpy.fft.fft(yvalues)
    fft_x = numpy.fft.fftfreq(len(yvalues), (xvalues[1] - xvalues[0]) / 1000)

    # Calculate the magnitude of the FFT values
    magnitude = numpy.abs(fft_y)

    # Create Plotly figure
    figure = plotly.graph_objects.Figure()
        
    figure.add_trace(plotly.graph_objects.Scatter(x=fft_x[:len(fft_x)//2],
                                                  y=magnitude[:len(magnitude)//2],
                                                  mode='lines',
                                                  line=dict(color=get_line_color(feature), width=2)))

    # Define the y-axis settings
    figure.update_yaxes(gridwidth=0.03, 
                        title="Magnitude", showgrid=True,
                        title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))
    
     # Define the x-axis settings
    figure.update_xaxes(gridwidth=0.03, 
                        title="Frequency (Hz)", showgrid=True, 
                        title_font=dict(family="Courier New"), tickfont=dict(family="Courier New"))   

    return figure