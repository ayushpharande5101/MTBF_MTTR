import pyodbc
import streamlit as st
import plotly.express as px
import pandas as pd
from PIL import Image
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Dashboard", layout='wide')

def display_image(image_path, height, width):
    img = Image.open(image_path)
    img.thumbnail((width, height))
    st.image(img, use_column_width=False)


with st.container(border=True):
    dash_logo = "CTPL2.png"  # image change needed
    display_image(dash_logo, height=100, width=100)
    left_column, middle_column, right_column = st.columns(3)
    with left_column:
        selected_date = st.date_input(label='Date:: From:')
    with middle_column:
        select_date = st.date_input(label='To:')
    with right_column:
        pass


def connection(sql):  # sql server connection changes needed

    connection = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                                'Server= AYUSHP-DELL\\SQLEXPRESS03;'
                                'Trusted_Connection=yes;')

    cursor = connection.cursor()
    cursor.execute(sql)
    return cursor

menu = ["MTTR and MTBF", "OEE"]
options = st.sidebar.radio("View", menu)

sql1 = "SELECT MTTR, MTBF, DATETIME,OVERALL_OEE FROM MTBF_MTTR.dbo.DATA_INSERT "
curs = connection(sql1)
# Fetch all rows and create a DataFrame
rows = curs.fetchall()
columns = [column[0] for column in curs.description]
df = pd.DataFrame.from_records(rows, columns=columns)
# Close cursor and connection
curs.close()

# Create a bar chart using Plotly Express
MTTR_MTBF = px.bar(df, x='DATETIME', y=['MTTR', 'MTBF'], barmode='group', width=1000,
                   color_discrete_map={'MTTR': 'blue', 'MTBF': 'green'})
# Display the Plotly chart in Streamlit


# Execute SQL query and fetch data

sql2 = "SELECT TOTAL_UPTIME, TOTAL_DOWNTIME, DATETIME, TOTAL_FAILURES FROM MTBF_MTTR.dbo.DATA_INSERT "
cur = connection(sql2)

# Fetch all rows and create a DataFrame
rows = cur.fetchall()
columns = [column[0] for column in cur.description]
ds = pd.DataFrame.from_records(rows, columns=columns)
# Close cursor and connection
cur.close()

# fig2 = px.line(ds, x='DATETIME',y=['TOTAL_UPTIME','TOTAL_DOWNTIME'])


Uptime_Downtime= px.pie(ds, names=['Total_uptime', 'Total_downtime'],
              title='Pie Chart of Total_uptime and Total_downtime', hole=0.7)
Uptime_Downtime.update_layout(width=630, height=500)

Failure = px.scatter(ds, x='DATETIME', y='TOTAL_FAILURES', title='Scatter chart of No of Failures')
Failure.update_layout(width=720, height=500)

sql3 = "SELECT  AVAILABILITY, PERFORMANCE, QUALITY,DATETIME FROM MTBF_MTTR.dbo.DATA_UPDATE "
cur2 = connection(sql3)
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
    title={'text': "OEE"},
    gauge={'axis': {'range': [None, 100]},
           'bar': {'color': "#0f4587"},
           'steps': [
               {'range': [0, 100], 'color': "#aabfe3"}],
           # Replace with your data
           }
))
OEE.update_layout(height=500, title='Gauge chart of Overall OEE')
Availability = go.Figure(go.Indicator(
    mode="gauge+number",
    value=dd['AVAILABILITY'].mean(),  # Replace with your data
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Availability"},
    gauge={'axis': {'range': [None, 100]},
           'bar': {'color': "#186318"},
           'steps': [
               {'range': [0, 100], 'color': "#7b8c7b"}],
           'threshold': {
               'line': {'color': "#186318", 'width': 4},
               'thickness': 0.75,
               'value': dd['AVAILABILITY'].mean()}  # Replace with your data
           }
))
Availability.update_layout(height=350, width=415, title='Gauge chart of Availability')
sql4 = "SELECT TOTAL_PRODUCTION_TIME,TOTAL_UPTIME,TOTAL_DOWNTIME, GOOD_PIECES, REJECTED_PIECES, TOTAL_FAILURES FROM MTBF_MTTR.dbo.DATA_INSERT"
cur3 = connection(sql4)
rows = cur3.fetchall()
columns = [column[0] for column in cur3.description]
da = pd.DataFrame.from_records(rows, columns=columns)
cur3.close()

values = ['TOTAL_PRODUCTION_TIME', 'TOTAL_UPTIME', 'TOTAL_DOWNTIME']
dta = make_subplots(rows=1, cols=len(values), shared_yaxes=True)
# Create a bar chart for each value and add it to the subplot
for i, value in enumerate(values):
    dta.add_trace(px.bar(da, y=value, barmode='group').data[0], row=1, col=i + 1)

# Customize the appearance of the plot

dta.update_layout(height=350, width=350, margin=dict(l=50, r=50))

performance = go.Figure(go.Indicator(
    mode="gauge+number",
    value=dd['PERFORMANCE'].mean(),  # Replace with your data
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Performance"},
    gauge={'axis': {'range': [None, 100]},
           'bar': {'color': "#071fb8"},
           'steps': [
               {'range': [0, 100], 'color': "#667691"}],
           'threshold': {
               'line': {'color': "#071fb8", 'width': 4},
               'thickness': 0.75,
               'value': dd['PERFORMANCE'].mean()}  # Replace with your data
           }
))
performance.update_layout(height=350, width=415, title='Gauge chart of Performance')
values1 = ['TOTAL_PRODUCTION_TIME', 'TOTAL_UPTIME',]
# performance.update_layout(paper_bgcolor='#203b38')
dta2 = make_subplots(rows=1, cols=len(values1), shared_yaxes=True, shared_xaxes=True)
# colors = ['blue', 'blue', 'red']
# Create a bar chart for each value and add it to the subplot
for i, value in enumerate(values1):
    dta2.add_trace(px.bar(da, y=value, barmode='group').data[0], row=1, col=i + 1)

# Customize the appearance of the plot

dta2.update_layout(height=350, width=350, margin=dict(l=50, r=50))

Quality = go.Figure(go.Indicator(
    mode="gauge+number",
    value=dd['QUALITY'].mean(),
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Quality"},
    gauge={'axis': {'range': [None, 100]},
           'bar': {'color': "#a84e03"},
           'steps': [
               {'range': [0, 100], 'color': "#917766"}],
           'threshold': {
               'line': {'color': "#a84e03", 'width': 4},
               'thickness': 0.75,
               'value': dd['QUALITY'].mean()}  # Replace with your data
           }
))
Quality.update_layout(height=350, width=415, title='Gauge chart of Quality')
values2 = ['GOOD_PIECES', 'REJECTED_PIECES']
# Quality.update_layout(paper_bgcolor='#3b3020')
dta3 = make_subplots(rows=1, cols=len(values2), shared_yaxes=True)
# Create a bar chart for each value and add it to the subplot
for i, value in enumerate(values2):
    dta3.add_trace(px.bar(da, y=value, barmode='group').data[0], row=1, col=i + 1)

# Customize the appearance of the plot
dta3.update_layout(height=350, width=350)

if options == "MTTR and MTBF":
    with st.container(border=True):  # Display the charts inside the container
        st.plotly_chart(MTTR_MTBF, use_container_width=True)
    left_column, right_column = st.columns(2)
    # Display pie chart and
    with left_column:
        with st.container(border=True):  # Display the charts inside the container
            st.plotly_chart(Uptime_Downtime)
    with right_column:
        with st.container(border=True):  # Display the charts inside the container
            st.plotly_chart(Failure, use_container_width=True)

elif options == "OEE":
    with st.container(border=True):  # Display the charts inside the container
        st.plotly_chart(OEE)
    left_column, middle, right_column = st.columns(3)
    # Display performance, availability, and quality side by side
    with left_column:
        with st.container(border=True):  # Display the charts inside the container
            st.plotly_chart(Availability)
            st.plotly_chart(dta)
    with middle:
        with st.container(border=True):  # Display the charts inside the container
            st.plotly_chart(performance)
            st.plotly_chart(dta2)
    with right_column:
        with st.container(border=True):  # Display the charts inside the container
            st.plotly_chart(Quality)
            st.plotly_chart(dta3)