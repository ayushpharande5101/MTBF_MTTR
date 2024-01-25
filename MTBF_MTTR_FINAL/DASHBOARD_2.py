import numpy as np
import pyodbc
import streamlit as st
import pandas as pd
from PIL import Image
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Dashboard", layout='wide')

def display_image(image_path, height, width):
    img = Image.open(image_path)
    img.thumbnail((width, height))
    st.image(img, use_column_width=False)

def connection():  # sql server connection changes needed
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                          'Server= AYUSHP-DELL\\SQLEXPRESS03;'
                          'Trusted_Connection=yes;')

    cursor = conn.cursor()
    return cursor

def current_mode():
    sql1 = "SELECT MTTR, MTBF, DATETIME,OVERALL_OEE, TOTAL_FAILURES FROM MTBF_MTTR.dbo.DATA_UPDATE"
    curs = connection().execute(sql1)
    # Fetch all rows and create a DataFrame
    rows = curs.fetchall()
    columns = [column[0] for column in curs.description]
    df = pd.DataFrame.from_records(rows, columns=columns)
    # Close cursor and connection
    curs.close()

    MTTR_values = df['MTTR'].values
    MTBF_values = df['MTBF'].values
    MTTR = float(MTTR_values[0]) if len(MTTR_values) > 0 else 0
    MTBF = float(MTBF_values[0]) if len(MTBF_values) > 0 else 0

    # Create a bar chart using Plotly Express

    # Execute SQL query and fetch data

    sql2 = "SELECT TOTAL_UPTIME, TOTAL_DOWNTIME, DATETIME, TOTAL_FAILURES FROM MTBF_MTTR.dbo.DATA_UPDATE"
    cur = connection().execute(sql2)

    # Fetch all rows and create a DataFrame
    rows = cur.fetchall()
    columns = [column[0] for column in cur.description]
    ds = pd.DataFrame.from_records(rows, columns=columns)
    # Close cursor and connection
    cur.close()

    sql3 = "SELECT  AVAILABILITY, PERFORMANCE, QUALITY,DATETIME FROM MTBF_MTTR.dbo.DATA_UPDATE"
    cur2 = connection().execute(sql3)
    # Fetch all rows and create a DataFrame
    rows = cur2.fetchall()
    columns = [column[0] for column in cur2.description]
    dd = pd.DataFrame.from_records(rows, columns=columns)
    # Close cursor and connection
    cur2.close()

    OEE = go.Figure(go.Indicator(
        mode="gauge+number",
        value=df['OVERALL_OEE'].mean(),  # Replace with your data
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "OEE",
               'font': {'size': 60}},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "#204223"},
               'steps': [
                   {'range': [0, 100], 'color': "#c9dec8"}],

               # Replace with your data
               },
        number={'suffix': '%'}
    ))
    OEE.update_layout(width=500, font=dict(color="black"))

    # Create a line chart for the delta
    Availability = go.Figure(go.Indicator(
        mode="gauge+number",
        value=dd['AVAILABILITY'].mean(),  # Replace with your data
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Availability",
               'font': {'size': 50}},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "#204223"},
               'steps': [
                   {'range': [0, 100], 'color': "#c9dec8"}],
               'threshold': {
                   'line': {'color': "#204223", 'width': 4},
                   'thickness': 0.75,
                   'value': dd['AVAILABILITY'].mean()}  # Replace with your data
               },
        number={'suffix': '%'}
    ))
    Availability.update_layout(height=290, width=350, font=dict(color="black"), margin=dict(b=5, l=45, r=65))
    sql4 = "SELECT TOTAL_PIECES, GOOD_PIECES,IDEAL_RUN_RATE, REJECTED_PIECES, TOTAL_FAILURES,TOTAL_PRODUCTION_TIME, TOTAL_DOWNTIME FROM MTBF_MTTR.dbo.DATA_UPDATE "
    cur3 = connection().execute(sql4)
    rows = cur3.fetchall()
    columns = [column[0] for column in cur3.description]
    da = pd.DataFrame.from_records(rows, columns=columns)
    cur3.close()

    detail = make_subplots(rows=1, cols=3,
                           shared_yaxes=True)

    val = da['TOTAL_PRODUCTION_TIME']
    production_t = go.Bar(y=val, text=val, textposition='auto', marker=dict(color='#17b509'))
    detail.add_trace(production_t, row=1, col=1)

    # Add the second bar chart (Downtime)
    val1 = da['TOTAL_DOWNTIME']
    down_t = go.Bar(y=val1, text=val1, textposition='auto', marker=dict(color='#bd1919'))
    detail.add_trace(down_t, row=1, col=2)

    # Add the third bar chart (Total Failure)
    val2 = da['TOTAL_FAILURES']
    total_failure = go.Bar(y=val2, text=val2, textposition='auto', marker=dict(color='#e87e0c'))
    detail.add_trace(total_failure, row=1, col=3)

    # Update layout to customize the appearance
    detail.update_layout(height=305, width=250, showlegend=False, font=dict(color="black"))
    detail.update_xaxes(title_text='Total<br>Production<br>Time', row=1, col=1, title_font=dict(color='black'))
    detail.update_xaxes(title_text='DownTime', row=1, col=2, title_font=dict(color='black'))
    detail.update_xaxes(title_text='Total<br>Failure', row=1, col=3, title_font=dict(color='black'))

    dta = make_subplots(rows=1, cols=2, shared_yaxes=True)

    # Add the first bar chart (Total Production Time)
    val_t = da['TOTAL_PRODUCTION_TIME']
    operation_time = go.Bar(y=val_t, text=val_t, textposition='auto', marker=dict(color='#17b509'))
    dta.add_trace(operation_time, row=1, col=1)

    # Add the second bar chart (Downtime)
    val_d = da['TOTAL_DOWNTIME']
    down_time = go.Bar(y=val_d, text=val_d, textposition='auto', marker=dict(color='#bd1919'))
    dta.add_trace(down_time, row=1, col=2)

    # Update layout to customize the appearance
    dta.update_layout(height=250, width=170, showlegend=False, font=dict(color="black"))
    dta.update_xaxes(title_text='<span style="color:black;">Total<br>Production<br>Time</span>', row=1, col=1)
    dta.update_xaxes(title_text='<span style="color:black;">DownTime</span>', row=1, col=2)

    performance = go.Figure(go.Indicator(
        mode="gauge+number",
        value=dd['PERFORMANCE'].mean(),  # Replace with your data
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Performance",
               'font': {'size': 50}},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "#204223"},
               'steps': [
                   {'range': [0, 100], 'color': "#c9dec8"}],
               'threshold': {
                   'line': {'color': "#204223", 'width': 4},
                   'thickness': 0.75,
                   'value': dd['PERFORMANCE'].mean()}  # Replace with your data
               },
        number={'suffix': '%'}
    ))
    performance.update_layout(height=290, width=350, font=dict(color="black"), margin=dict(b=5, l=45, r=65))
    dta2 = make_subplots(rows=1, cols=3, shared_yaxes=True)

    # Add the first bar chart (Total Production Time)
    val_1 = da['TOTAL_PRODUCTION_TIME']
    operation_t = go.Bar(y=val_1, text=val_1, textposition='auto', marker=dict(color='#17b509'))
    dta2.add_trace(operation_t, row=1, col=1)

    # Add the second bar chart (Downtime)
    val_2 = da['TOTAL_PIECES']
    total_pieces = go.Bar(y=val_2, text=val_2, textposition='auto', marker=dict(color='#805238'))
    dta2.add_trace(total_pieces, row=1, col=2)

    val_3 = da['IDEAL_RUN_RATE']
    ideal_run_rate = go.Bar(y=val_3, text=val_3, textposition='auto', marker=dict(color='#e87e0c'))
    dta2.add_trace(ideal_run_rate, row=1, col=3)

    # Update layout to customize the appearance
    dta2.update_layout(height=250, width=209, showlegend=False, font=dict(color="black"))
    dta2.update_xaxes(title_text='Total<br>Production<br>Time', row=1, col=1, title_font=dict(color='black'))
    dta2.update_xaxes(title_text='Total pieces', row=1, col=2, title_font=dict(color='black'))
    dta2.update_xaxes(title_text='Ideal<br>Run<br>Rate', row=1, col=3, title_font=dict(color='black'))

    Quality = go.Figure(go.Indicator(
        mode="gauge+number",
        value=dd['QUALITY'].mean(),
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Quality",
               'font': {'size': 50}},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "#204223"},
               'steps': [
                   {'range': [0, 100], 'color': "#c9dec8"}],
               'threshold': {
                   'line': {'color': "#204223", 'width': 4},
                   'thickness': 0.75,
                   'value': dd['QUALITY'].mean()}  # Replace with your data
               },
        number={'suffix': '%'}
    ))
    Quality.update_layout(height=290, width=350, font=dict(color="black"), margin=dict(b=5, l=45, r=65))

    # Quality.update_layout(paper_bgcolor='#3b3020')
    dta3 = make_subplots(rows=1, cols=2, shared_yaxes=True)

    # Add the first bar chart (Total Production Time)
    value = da['GOOD_PIECES']
    Good_pieces = go.Bar(y=value, text=value, textposition='auto', marker=dict(color='#17b509'))
    dta3.add_trace(Good_pieces, row=1, col=1)

    # Add the second bar chart (Downtime)
    val = da['REJECTED_PIECES']
    Rejected_pieces = go.Bar(y=val, text=val, textposition='auto', marker=dict(color='#bd1919'))
    dta3.add_trace(Rejected_pieces, row=1, col=2)

    dta3.update_layout(height=250, width=150, showlegend=False, font=dict(color="black"))
    dta3.update_xaxes(title_text='Accepted<br>Pieces', row=1, col=1, title_font=dict(color='black'))
    dta3.update_xaxes(title_text='Rejected<br>Pieces', row=1, col=2, title_font=dict(color='black'))

    # Update layout to customize the appearance

    left_width = 4
    middle_width = 1.8
    right_width = 3.2

    # Create columns with specified widths
    left_side, middle_side, right_side = st.columns([left_width, middle_width, right_width])

    with left_side:
        with st.container(border=True):
            # Adjust the height of the chart to ensure proper visibility
            chart_height = 304  # Adjust as needed
            OEE.update_layout(height=chart_height, margin=dict(t=75, b=7, l=0, r=0))
            st.plotly_chart(OEE, use_container_width=True)

    with middle_side:
        with st.container(border=True):
            st.plotly_chart(detail)
    with right_side:
        with st.container(border=True):
            st.markdown(f'<p style="font-size:55px;">MTTR: {MTTR} min</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size:55px;">MTBF: {MTBF} min</p>', unsafe_allow_html=True)
    # Display the charts inside the container
    left_col, middle_col, right_col = st.columns(3)
    with left_col:
        with st.container(border=True):  # Display the charts inside the container
            gauge_w = 7
            bar_w = 4
            Gauge, bar = st.columns([gauge_w, bar_w])
            with Gauge:
                st.plotly_chart(Availability)
            with bar:
                st.plotly_chart(dta)
    with middle_col:
        with st.container(border=True):  # Display the charts inside the container
            gauge_w = 7
            bar_w = 5
            Gauge, bar = st.columns([gauge_w, bar_w])
            with Gauge:
                st.plotly_chart(performance, margin=dict(b=3, l=1, r=1))
            with bar:
                st.plotly_chart(dta2)
    with right_col:
        with st.container(border=True):
            gauge_w = 7
            bar_w = 4
            Gauge, bar = st.columns([gauge_w, bar_w])
            with Gauge:
                st.plotly_chart(Quality, margin=dict(b=3, l=1, r=1))
            with bar:
                st.plotly_chart(dta3)

def history_mode():
    global selected_date, select_date, s_option
    f_date = selected_date
    t_date = select_date
    shift = s_option
    shift_num = int(shift.replace('Shift ', ''))

    sql1 = "SELECT MTTR, MTBF, DATETIME,OVERALL_OEE, TOTAL_FAILURES FROM MTBF_MTTR.dbo.DATA_INSERT WHERE DATETIME BETWEEN ? AND ? AND SHIFT = ?"
    curs = connection().execute(sql1, (f_date, t_date, shift_num))
    # Fetch all rows and create a DataFrame
    rows = curs.fetchall()
    columns = [column[0] for column in curs.description]
    df = pd.DataFrame.from_records(rows, columns=columns)
    # Close cursor and connection
    curs.close()

    MTTR_values = df['MTTR'].values
    MTBF_values = df['MTBF'].values
    MTTR = float(MTTR_values[0]) if len(MTTR_values) > 0 else 0
    MTBF = float(MTBF_values[0]) if len(MTBF_values) > 0 else 0

    # Create a bar chart using Plotly Express

    # Execute SQL query and fetch data

    # fig2 = px.line(ds, x='DATETIME',y=['TOTAL_UPTIME','TOTAL_DOWNTIME'])

    sql2 = "SELECT  AVAILABILITY, PERFORMANCE, QUALITY,DATETIME FROM MTBF_MTTR.dbo.DATA_INSERT WHERE DATETIME BETWEEN ? AND ? AND SHIFT = ?"
    cur2 = connection().execute(sql2, (f_date, t_date, shift_num))
    # Fetch all rows and create a DataFrame
    rows = cur2.fetchall()
    columns = [column[0] for column in cur2.description]
    dd = pd.DataFrame.from_records(rows, columns=columns)
    # Close cursor and connection
    cur2.close()

    OEE = go.Figure(go.Indicator(
        mode="gauge+number",
        value=df['OVERALL_OEE'].mean(),  # Replace with your data
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "OEE",
               'font': {'size': 60}},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "#204223"},
               'steps': [
                   {'range': [0, 100], 'color': "#c9dec8"}],
               # Replace with your data
               },
        number={'suffix': '%'}
    ))
    OEE.update_layout(font=dict(color="black"))

    Availability = go.Figure(go.Indicator(
        mode="gauge+number",
        value=dd['AVAILABILITY'].mean(),  # Replace with your data
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Availability",
               'font': {'size': 50}},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "#204223"},
               'steps': [
                   {'range': [0, 100], 'color': "#c9dec8"}],
               'threshold': {
                   'line': {'color': "#204223", 'width': 4},
                   'thickness': 0.75,
                   'value': dd['AVAILABILITY'].mean()}  # Replace with your data
               },
        number={'suffix': '%'}
    ))
    Availability.update_layout(height=250, width=350, font=dict(color="black"), margin=dict(b=5, l=45, r=65))
    sql4 = "SELECT TOTAL_PIECES, GOOD_PIECES,IDEAL_RUN_RATE, REJECTED_PIECES, TOTAL_FAILURES,TOTAL_PRODUCTION_TIME, TOTAL_DOWNTIME FROM MTBF_MTTR.dbo.DATA_INSERT WHERE DATETIME BETWEEN ? AND ? AND SHIFT = ?"
    cur3 = connection().execute(sql4, (f_date, t_date, shift_num))
    rows = cur3.fetchall()
    columns = [column[0] for column in cur3.description]
    da = pd.DataFrame.from_records(rows, columns=columns)
    cur3.close()
    detail = make_subplots(rows=1, cols=3,
                           shared_yaxes=True)

    # Add the second bar chart (Downtime)
    val = da['TOTAL_PRODUCTION_TIME']
    production_t = go.Bar(y=val, text=val, textposition='auto', marker=dict(color='#17b509'))
    detail.add_trace(production_t, row=1, col=1)

    # Add the second bar chart (Downtime)
    val1 = da['TOTAL_DOWNTIME']
    down_t = go.Bar(y=val1, text=val1, textposition='auto', marker=dict(color='#bd1919'))
    detail.add_trace(down_t, row=1, col=2)

    # Add the third bar chart (Total Failure)
    val2 = da['TOTAL_FAILURES']
    total_failure = go.Bar(y=val2, text=val2, textposition='auto', marker=dict(color='#e87e0c'))
    detail.add_trace(total_failure, row=1, col=3)

    # Update layout to customize the appearance
    detail.update_layout(height=280, width=250, showlegend=False, font=dict(color="black"))
    detail.update_xaxes(title_text='Total<br>Production<br>Time', row=1, col=1, title_font=dict(color='black'))
    detail.update_xaxes(title_text='DownTime', row=1, col=2, title_font=dict(color='black'))
    detail.update_xaxes(title_text='Total<br>Failure', row=1, col=3, title_font=dict(color='black'))

    dta = make_subplots(rows=1, cols=2, shared_yaxes=True)

    # Add the first bar chart (Total Production Time)
    val_t = da['TOTAL_PRODUCTION_TIME']
    operation_time = go.Bar(y=val_t, text=val_t, textposition='auto', marker=dict(color='#17b509'))
    dta.add_trace(operation_time, row=1, col=1)

    # Add the second bar chart (Downtime)
    val_d = da['TOTAL_DOWNTIME']
    down_time = go.Bar(y=val_d, text=val_d, textposition='auto', marker=dict(color='#bd1919'))
    dta.add_trace(down_time, row=1, col=2)

    # Update layout to customize the appearance
    dta.update_layout(height=250, width=170, showlegend=False, font=dict(color="black"))
    dta.update_xaxes(title_text='<span style="color:black;">Total<br>Production<br>Time</span>', row=1, col=1)
    dta.update_xaxes(title_text='<span style="color:black;">DownTime</span>', row=1, col=2)

    performance = go.Figure(go.Indicator(
        mode="gauge+number",
        value=dd['PERFORMANCE'].mean(),  # Replace with your data
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Performance",
               'font': {'size': 50}},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "#204223"},
               'steps': [
                   {'range': [0, 100], 'color': "#c9dec8"}],
               'threshold': {
                   'line': {'color': "#204223", 'width': 4},
                   'thickness': 0.75,
                   'value': dd['PERFORMANCE'].mean()}  # Replace with your data
               },
        number={'suffix': '%'}
    ))
    performance.update_layout(height=250, width=350, font=dict(color="black"), margin=dict(b=5, l=45, r=65))
    dta2 = make_subplots(rows=1, cols=3, shared_yaxes=True)

    # Add the first bar chart (Total Production Time)
    val_1 = da['TOTAL_PRODUCTION_TIME']
    operation_t = go.Bar(y=val_1, text=val_1, textposition='auto', marker=dict(color='#17b509'))
    dta2.add_trace(operation_t, row=1, col=1)

    # Add the second bar chart (Downtime)
    val_2 = da['TOTAL_PIECES']
    total_pieces = go.Bar(y=val_2, text=val_2, textposition='auto', marker=dict(color='#805238'))
    dta2.add_trace(total_pieces, row=1, col=2)

    val_3 = da['IDEAL_RUN_RATE']
    ideal_run_rate = go.Bar(y=val_3, text=val_3, textposition='auto', marker=dict(color='#e87e0c'))
    dta2.add_trace(ideal_run_rate, row=1, col=3)

    # Update layout to customize the appearance
    dta2.update_layout(height=250, width=209, showlegend=False, font=dict(color="black"))
    dta2.update_xaxes(title_text='Total<br>Production<br>Time', row=1, col=1)
    dta2.update_xaxes(title_text='Total pieces', row=1, col=2)
    dta2.update_xaxes(title_text='Ideal<br>Run<br>Rate', row=1, col=3)

    Quality = go.Figure(go.Indicator(
        mode="gauge+number",
        value=dd['QUALITY'].mean(),
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Quality",
               'font': {'size': 50}},
        gauge={'axis': {'range': [None, 100]},
               'bar': {'color': "#204223"},
               'steps': [
                   {'range': [0, 100], 'color': "#c9dec8"}],
               'threshold': {
                   'line': {'color': "#204223", 'width': 4},
                   'thickness': 0.75,
                   'value': dd['QUALITY'].mean()}  # Replace with your data
               },
        number={'suffix': '%'}
    ))
    Quality.update_layout(height=250, width=350,
                          font=dict(color="black"), margin=dict(b=5, l=45, r=65))

    # Quality.update_layout(paper_bgcolor='#3b3020')
    dta3 = make_subplots(rows=1, cols=2, shared_yaxes=True)

    # Add the first bar chart (Total Production Time)
    value = da['GOOD_PIECES']
    Good_pieces = go.Bar(y=value, text=value, textposition='auto', marker=dict(color='#17b509'))
    dta3.add_trace(Good_pieces, row=1, col=1)

    # Add the second bar chart (Downtime)
    val = da['REJECTED_PIECES']
    Rejected_pieces = go.Bar(y=val, text=val, textposition='auto', marker=dict(color='#bd1919'))
    dta3.add_trace(Rejected_pieces, row=1, col=2)

    # Update layout to customize the appearance
    dta3.update_layout(height=250, width=150, showlegend=False, font=dict(color="black"))
    dta3.update_xaxes(title_text='Accepted<br>Pieces', row=1, col=1)
    dta3.update_xaxes(title_text='Rejected<br>Pieces', row=1, col=2)

    # Update layout to customize the appearance

    left_width = 4
    middle_width = 1.8
    right_width = 3.2

    # Create columns with specified widths
    left_side, middle_side, right_side = st.columns([left_width, middle_width, right_width])

    with left_side:
        with st.container(border=True):
            chart_height = 280  # Adjust as needed
            OEE.update_layout(height=chart_height, margin=dict(t=75, b=7, l=0, r=0))
            st.plotly_chart(OEE, use_container_width=True)
    with middle_side:
        with st.container(border=True):
            st.plotly_chart(detail)
    with right_side:
        with st.container(border=True):
            st.markdown(f'<p style="font-size:55px;">MTTR: {MTTR} min</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="font-size:55px;">MTBF: {MTBF} min</p>', unsafe_allow_html=True)
    # Display the charts inside the container
    left_col, middle_col, right_col = st.columns(3)
    with left_col:
        with st.container(border=True):  # Display the charts inside the container
            gauge_w = 7
            bar_w = 4
            Gauge, bar = st.columns([gauge_w, bar_w])
            with Gauge:
                st.plotly_chart(Availability)
            with bar:
                st.plotly_chart(dta)
    with middle_col:
        with st.container(border=True):  # Display the charts inside the container
            gauge_w = 7
            bar_w = 5
            Gauge, bar = st.columns([gauge_w, bar_w])
            with Gauge:
                st.plotly_chart(performance, margin=dict(b=3, l=1, r=1))
            with bar:
                st.plotly_chart(dta2)
    with right_col:
        with st.container(border=True):
            gauge_w = 7
            bar_w = 4
            Gauge, bar = st.columns([gauge_w, bar_w])
            with Gauge:
                st.plotly_chart(Quality, margin=dict(b=3, l=1, r=1))
            with bar:
                st.plotly_chart(dta3)


with st.container(border=True):
    left, middle, right = st.columns(3)
    with left:
        dash_logo = "CTPL2.png"  # need changes
        display_image(dash_logo, height=100, width=100)
    with middle:
        pass
    with right:
        options = ['current', 'history']

        # Display a dropdown list using the `selectbox` function
        selected_option = st.selectbox('dash:', options)
    l, w, r, = st.columns(3)
    if selected_option == "history":
        with l:
            selected_date = st.date_input(label='Date:: From:')
        with w:
            select_date = st.date_input(label='To:')
        with r:
            shift_option = ['1', '2', '3']
            s_option = st.selectbox('SHIFT:', shift_option)

if selected_option == "current":
    current_mode()
elif selected_option == "history":
    history_mode()

    # Display the charts inside the container
