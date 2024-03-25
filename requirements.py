import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objs as go
from scipy.stats import linregress
from scipy.optimize import curve_fit
import plotly.graph_objects as go
import plotly.express as px
from sklearn.metrics import r2_score

# Set page configuration
st.set_page_config(page_title="Data Visualization App", layout="wide")
st.write("Antero Eng Tool")

# Custom CSS for bottom border
st.markdown(
    """
    <style>
    .chart-container {
        border-bottom: 2px solid #ccc;
        padding-bottom: 20px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize data variable
data = None

# CSV Upload and Dynamic Chart Generation
def main():
    global data

    st.title("Data Visualization and Analysis App")

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

        columns = data.columns.tolist()
        selected_columns = st.multiselect("Please choose the columns you wish to display in table format, or skip this section if you prefer not to generate a table.", columns)

        # Interactive table generation
        if selected_columns:
            num_rows = st.number_input("Number of rows to display", min_value=1, value=10)
            st.dataframe(data[selected_columns].head(num_rows))

        # Dynamic Chart Generation
        st.subheader("")
        st.subheader("")
        st.subheader("")
        st.subheader("Dynamic Chart Generation")

        # Adding a new column "Number/Duration"
        if data is not None:
            data['X-Axis'] = range(len(data))
            columns = data.columns.tolist()

            # Configure charts
            num_charts = st.number_input("Number of charts to generate", min_value=1, max_value=10, value=1)

            for i in range(num_charts):
                st.subheader(f"Chart {i+1}")

                col1, col_chart, col2 = st.columns([1, 3, 1])

                with col1:
                    chart_type = st.selectbox(f"Select chart type for Chart {i+1}", ["Line", "Bar", "Scatter"])
                    # Setting "Number/Duration" as default X-axis
                    st.write("Select columns for the X and Y axis")
                    st.write("Only columns in **'NUMBER'** format are valid; using columns with **date or text** formats will result in ERRORS.")
                    x_column = st.selectbox(f"Select X-axis column for Chart {i+1}", columns, index=columns.index("X-Axis"))
                    y_columns = st.multiselect(f"Select Y-axis column(s) for Chart {i+1}", columns)

                    if x_column and y_columns:
                        x_min = data[x_column].min()
                        x_max = data[x_column].max()

                        # Define a key for the start and end inputs
                        start_input_key = f"start_{i}"
                        end_input_key = f"end_{i}"

                        # Get the current values from the session state or set defaults
                        x_start = st.session_state.get(start_input_key, x_min)
                        x_end = st.session_state.get(end_input_key, x_max)

                        # Ensure synchronization between slider and input
                        if x_start > x_end:
                            x_start, x_end = x_end, x_start

                        # Update number input fields based on slider value
                        st.write("")
                        st.write("")
                        st.write(f"Select X-axis range using the following input fields")
                        col_start, col_end = st.columns([1.5, 1.5])
                        with col_start:
                            x_start = st.number_input(f"Enter X-axis start for Chart {i+1}", min_value=x_min, max_value=x_max, value=x_start)
                        with col_end:
                            x_end = st.number_input(f"Enter X-axis end for Chart {i+1}", min_value=x_min, max_value=x_max, value=x_end)

                    trendline = st.checkbox(f"Add trendline for Chart {i+1}")
                    if trendline:
                        col_a, col_b = st.columns([1.5, 1.5])
                        with col_a:
                            trendline_type = st.selectbox(f"Select trendline type", ["Linear", "Average", "Polynomial"])
                        with col_b:
                            if trendline_type == "Polynomial":
                                degrees = {}
                                for y_column in y_columns:
                                    degrees[y_column] = st.number_input(f"Degree for {y_column}", min_value=2, max_value=20, value=2)

                    with col_chart:
                        with st.container():
                            if x_column and y_columns:
                                filtered_data = data[(data[x_column] >= x_start) & (data[x_column] <= x_end)]

                                if chart_type == "Line":
                                    fig = px.line(filtered_data, x=x_column, y=y_columns)
                                elif chart_type == "Bar":
                                    fig = px.bar(filtered_data, x=x_column, y=y_columns)
                                else:
                                    fig = px.scatter(filtered_data, x=x_column, y=y_columns)

                                if trendline:
                                    for trace in fig.data:
                                        if trace.name in y_columns:
                                            color = trace.line.color if hasattr(trace.line, 'color') else trace.marker.color
                                            if trendline_type == "Linear":
                                                slope, intercept, _, _, _ = linregress(filtered_data[x_column], filtered_data[trace.name])
                                                fig.add_shape(type="line", x0=x_start, y0=slope*x_start+intercept,
                                                            x1=x_end, y1=slope*x_end+intercept,
                                                            line=dict(color=color, width=2, dash="dash"))
                                                y_predicted = slope * filtered_data[x_column] + intercept
                                                r_squared = r2_score(filtered_data[trace.name], y_predicted)
                                            elif trendline_type == "Average":
                                                avg_y_value = filtered_data[trace.name].mean()
                                                fig.add_hline(y=avg_y_value, line_dash="dash",
                                                            annotation_text=f"Avg {trace.name} = {avg_y_value:.5f}",
                                                            annotation_position="bottom right",
                                                            line=dict(color=color)) 
                                            elif trendline_type == "Polynomial":
                                                degree = degrees[trace.name]
                                                coeffs = np.polyfit(filtered_data[x_column], filtered_data[trace.name], degree)
                                                poly_function = np.poly1d(coeffs)
                                                equation = " + ".join(f"{coeffs[i]:.8f} * x^{degree-i}" for i in range(degree+1))
                                                x_values = np.linspace(x_start, x_end, 100)
                                                y_values = poly_function(x_values)
                                                r_squared = r2_score(filtered_data[trace.name], poly_function(filtered_data[x_column]))
                                                fig.add_trace(go.Scatter(x=x_values, y=y_values, line_dash="dash",
                                                                        name=f"Polynomial Trendline {degree} for {trace.name}",
                                                                        line=dict(color=color))) 

                                fig.update_layout(title=f"Chart {i+1}", xaxis_title=x_column, yaxis_title="Value", height=700) 
                                st.plotly_chart(fig, use_container_width=True)
                                st.markdown('<div class="chart-container"></div>', unsafe_allow_html=True)

                with col2:
                    st.write(f"**Chart {i+1} Summary:**")
                    st.write("")
                    st.write("")
                    
                    for y_column in y_columns:
                        st.write("• **Min of**", y_column + ":", f"{filtered_data[y_column].min():.5f}")
                        st.write("• **Max of**", y_column + ":", f"{filtered_data[y_column].max():.5f}")
                        st.write("• **Average of**", y_column + ":", f"{filtered_data[y_column].mean():.5f}")
                        st.write("• **Standard Deviation of**", y_column + ":", f"{filtered_data[y_column].std():.5f}")
                    if trendline:
                                for trace in fig.data:
                                    if trace.name in y_columns:
                                        if trendline_type == "Linear":
                                            st.write(f"• **Linear Trendline for {trace.name}:** y = {slope:.5f}x + {intercept:.5f}, R-squared: {r_squared:.5f}")
                                        elif trendline_type == "Polynomial":
                                            degree = degrees[trace.name]
                                            coeffs = np.polyfit(filtered_data[x_column], filtered_data[trace.name], degree)
                                            poly_function = np.poly1d(coeffs)
                                            equation = " + ".join(f"{coeffs[i]:.8f} * x^{degree-i}" for i in range(degree+1))
                                            x_values = np.linspace(x_start, x_end, 100)
                                            y_values = poly_function(x_values)
                                            r_squared = r2_score(filtered_data[trace.name], poly_function(filtered_data[x_column]))
                                            st.write(f"• **Polynomial Trendline {degree} for {trace.name}:** y = {equation}, R-squared: {r_squared:.5f}")    

# Run the app
if __name__ == "__main__":
    main()
