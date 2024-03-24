import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.stats import linregress
import numpy as np

# Set page configuration
st.set_page_config(page_title="Data Visualization App", layout="wide")

# Initialize session state
if "data" not in st.session_state:
    st.session_state.data = None

# Page 1: CSV Upload and Data Overview
def page1():
    st.title("Data Visualization App")
    st.subheader("CSV Upload")

    # CSV file upload
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        # Read CSV data
        data = pd.read_csv(uploaded_file)
        st.success("CSV file uploaded successfully!")

        # Data overview
        st.subheader("Data Overview")
        st.write(f"Total Rows: {data.shape[0]}")
        st.write(f"Total Columns: {data.shape[1]}")
        
        # Column list
        st.subheader("Column List")
        columns = data.columns.tolist()
        selected_columns = st.multiselect("Select columns to display", columns)
        
        # Interactive table generation
        if selected_columns:
            num_rows = st.number_input("Number of rows to display", min_value=1, value=10)
            st.dataframe(data[selected_columns].head(num_rows))
        
        # Button to proceed to the next page
        if st.button("Click to Export Data to Page 2: Chart Generation"):
            st.session_state.data = data
            st.experimental_rerun()

# Page 2: Dynamic Chart Generation
def page2():
    st.title("Data Visualization App")
    st.subheader("Dynamic Chart Generation")
    

    if st.session_state.data is not None:
        data = st.session_state.data
        # Adding a new column "Number/Duration"
        data['X-Axis'] = range(len(data))
        columns = data.columns.tolist()

        # Configure charts
        num_charts = st.number_input("Number of charts to generate", min_value=1, max_value=10, value=1)

        for i in range(num_charts):
            st.subheader(f"Chart {i+1}")

            col1, col2 = st.columns([1, 3])  # Swapped the order of columns

            with col1:
                chart_type = st.selectbox(f"Select chart type for Chart {i+1}", ["Line", "Bar", "Scatter"])
                # Setting "Number/Duration" as default X-axis
                x_column = st.selectbox(f"Select X-axis column for Chart {i+1}", columns, index=columns.index("X-Axis"))
                y_columns = st.multiselect(f"Select Y-axis column(s) for Chart {i+1}", columns)
                secondary_y = st.checkbox(f"Add secondary Y-axis for Chart {i+1}")
                
                if x_column and y_columns:
                    x_min = data[x_column].min()
                    x_max = data[x_column].max()
                    x_start, x_end = st.slider(f"Select X-axis range for Chart {i+1}", min_value=x_min, max_value=x_max, value=(x_min, x_max))
                
                trendline = st.checkbox(f"Add trendline for Chart {i+1}")
                if trendline:
                    trendline_type = st.selectbox(f"Select trendline type for Chart {i+1}", ["Linear", "Average"])
                    

            with col2:
                if x_column and y_columns:
                    filtered_data = data[(data[x_column] >= x_start) & (data[x_column] <= x_end)]
                    
                    if chart_type == "Line":
                        fig = px.line(filtered_data, x=x_column, y=y_columns)
                    elif chart_type == "Bar":
                        fig = px.bar(filtered_data, x=x_column, y=y_columns)
                    else:
                        fig = px.scatter(filtered_data, x=x_column, y=y_columns)
                    
                    if secondary_y and len(y_columns) > 1:
                        fig.update_layout(yaxis2=dict(title=y_columns[1], side="right", overlaying="y"))
                        fig.update_traces(yaxis="y2", selector=dict(name=y_columns[1]))

                    if trendline:
                        for y_column in y_columns:
                            if trendline_type == "Linear":
                                slope, intercept, r_value, _, _ = linregress(filtered_data[x_column], filtered_data[y_column])
                                fig.add_shape(type="line", x0=x_start, y0=slope*x_start+intercept,
                                              x1=x_end, y1=slope*x_end+intercept,
                                              line=dict(color="red", width=2, dash="dash"))
                                st.write(f"Linear Trendline for {y_column}: y = {slope:.2f}x + {intercept:.2f}, R-value: {r_value:.2f}")
                            elif trendline_type == "Average":
                                avg_y_value = filtered_data[y_column].mean()
                                fig.add_hline(y=avg_y_value, line_dash="dot", annotation_text=f"Avg {y_column} = {avg_y_value:.2f}", annotation_position="bottom right")
                                st.write(f"Average Trendline for {y_column}")

                    fig.update_layout(title=f"Chart {i+1}", xaxis_title=x_column, yaxis_title="Value")
                    st.plotly_chart(fig, use_container_width=True)

                    st.write(f"Chart {i+1} Summary:")
                    st.write(f"X-axis Start: {x_start}")
                    st.write(f"X-axis End: {x_end}")
                    for y_column in y_columns:
                        st.write(f"Average of {y_column}: {filtered_data[y_column].mean():.2f}")
                        st.write(f"Standard Deviation of {y_column}: {filtered_data[y_column].std():.2f}")

                else:
                    st.warning("Please select X-axis and Y-axis columns to generate the chart.")

# App navigation
page = st.sidebar.radio("Select a page", ["CSV Upload", "Chart Generation"])

if page == "CSV Upload":
    page1()
else:
    page2()
