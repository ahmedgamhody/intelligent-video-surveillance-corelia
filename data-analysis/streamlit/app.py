import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import ast
from datetime import datetime
import io
from connect_db import load_data
from anomaly_detection import *


# ---- Helper Functions ----
def convert_box_str_to_list(box_str):
    """Convert string representation of box to list."""
    if isinstance(box_str, str):
        try:
            return ast.literal_eval(box_str)
        except:
            return [0, 0, 0, 0]
    return box_str

# ---- Page Configuration ----
st.set_page_config(page_title="IVS Dashboard", layout="wide")
st.title("📊 Surveillance Dashboard")
st.markdown("---")

# ---- Load Data ----
df = load_data()

if df is None:
    exit()

# ---- Sidebar Filters ----
st.sidebar.header("🔎 Filters")

# Timestamp Filter
min_ts = df['timestamp'].min()
max_ts = df['timestamp'].max()
start_date, end_date = st.sidebar.date_input(
    "Select Timestamp Range",
    [min_ts.date(), max_ts.date()],
    min_value=min_ts.date(),
    max_value=max_ts.date()
)
start_dt = pd.to_datetime(start_date).tz_localize("UTC")
end_dt = pd.to_datetime(end_date).tz_localize("UTC") + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

# Dropdown Filters
channels = st.sidebar.multiselect("Select Channel Name", df['channel_name'].unique(), default=list(df['channel_name'].unique()))
sources = st.sidebar.multiselect("Select Source Name", df['source_name'].unique(), default=list(df['source_name'].unique()))
classes = st.sidebar.multiselect("Select Object Class", sorted(df['object_class'].unique()), default=list(df['object_class'].unique()))

# ---- Apply Filters ----
filtered_df = df[
    (df['timestamp'] >= start_dt) &
    (df['timestamp'] <= end_dt) &
    (df['channel_name'].isin(channels)) &
    (df['source_name'].isin(sources)) &
    (df['object_class'].isin(classes))
]

if filtered_df.empty:
    st.warning("No data matches the selected filters!")
    st.stop()

# ---- Summary Metrics ----
st.subheader("📈 Summary Metrics")
col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, _ = st.columns(4)

col1.metric("Total Detections", len(filtered_df))
col2.metric("Total Processed Frames", filtered_df[['timestamp', 'channel_name', 'source_name']].drop_duplicates().shape[0])
col3.metric("Total Number of Channels", filtered_df['channel_name'].nunique())
col4.metric("Total Number of Sources", filtered_df['source_name'].nunique())
col5.metric("Total Tracked Objects", filtered_df[['channel_name', 'source_name', 'object_id']].drop_duplicates().shape[0])
col6.metric("Count of Unique Classes", filtered_df['object_class'].nunique())
col7.metric("Average Object Confidence", f"{int(filtered_df['object_conf'].mean()*100)}%")

# Line separator
st.markdown("---")

# ---- Run Anomaly Detection ----
with st.spinner("Running anomaly detection..."):
    # Process data through anomaly detection pipeline
    analyzed_df = analyze_data(filtered_df)
    
    # Get anomaly summary
    anomaly_summary = get_anomaly_summary(analyzed_df)
    
    # Get anomaly details
    anomaly_details = get_anomaly_details(analyzed_df)

# ---- Anomaly Detection Section ----
st.subheader("🔍 Anomaly Detection")

# Create anomaly metrics
anomaly_col1, anomaly_col2, anomaly_col3 = st.columns(3)

anomaly_col1.metric("Duration Anomalies", anomaly_summary['duration_anomaly_count'])
anomaly_col2.metric("Object Count Anomalies", anomaly_summary['count_anomaly_count'])
anomaly_col3.metric("Density Anomalies", anomaly_summary['density_anomaly_count'])

# Create collapsible section for detailed anomalies
with st.expander(f"🚨 View All Anomalies ({anomaly_summary['total_anomaly_count']})"):
    # Tabs for different anomaly types
    anomaly_tabs = st.tabs(["All Anomalies", "Duration Anomalies", "Count Anomalies", "Density Anomalies"])
    
    with anomaly_tabs[0]:
        st.subheader("All Detected Anomalies")
        
        if anomaly_summary['total_anomaly_count'] > 0:
            # Display table with all anomalies
            all_anomalies = anomaly_details
            st.dataframe(all_anomalies.sort_values(['timestamp', 'channel_name', 'source_name']), use_container_width=True)
            
            # Group anomalies by channel and source
            st.subheader("Anomalies by Channel and Source")
            anomaly_counts = all_anomalies.groupby(['channel_name', 'source_name', 'anomaly_type']).size().reset_index(name='count')
            
            # Plot anomaly counts
            fig = px.bar(anomaly_counts, 
                         x='channel_name', 
                         y='count', 
                         color='anomaly_type',
                         barmode='group',
                         title='Anomaly Distribution by Channel and Type',
                         labels={'count': 'Number of Anomalies', 'channel_name': 'Channel Name'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No anomalies detected in the filtered data.")
    
    with anomaly_tabs[1]:
        st.subheader("Duration Anomalies")
        
        if anomaly_summary['duration_anomaly_count'] > 0:
            duration_anomalies = anomaly_summary['duration_anomalies']
            
            # Display duration anomalies table
            st.dataframe(duration_anomalies[['channel_name', 'source_name', 'timestamp', 
                                           'object_class', 'object_id', 'duration']], 
                        use_container_width=True)
            
            # Plot duration anomalies by object class
            st.subheader("Duration Anomalies by Object Class")
            fig = px.box(duration_anomalies, 
                        x='object_class', 
                        y='duration',
                        color='channel_name',
                        title='Duration Anomalies Distribution by Object Class',
                        labels={'duration': 'Duration (seconds)', 'object_class': 'Object Class'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No duration anomalies detected in the filtered data.")
    
    with anomaly_tabs[2]:
        st.subheader("Object Count Anomalies")
        
        if anomaly_summary['count_anomaly_count'] > 0:
            count_anomalies = anomaly_summary['count_anomalies']
            
            # Display count anomalies table
            st.dataframe(count_anomalies[['channel_name', 'source_name', 'timestamp', 
                                         'object_count', 'count_z_score']], 
                        use_container_width=True)
            
            # Plot count anomalies over time
            st.subheader("Object Count Anomalies Over Time")
            fig = px.scatter(count_anomalies, 
                           x='timestamp', 
                           y='object_count',
                           color='channel_name',
                           size='count_z_score',
                           hover_data=['count_z_score'],
                           title='Object Count Anomalies Over Time',
                           labels={'object_count': 'Object Count', 'timestamp': 'Timestamp'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No object count anomalies detected in the filtered data.")
    
    with anomaly_tabs[3]:
        st.subheader("Density Anomalies")
        
        if anomaly_summary['density_anomaly_count'] > 0:
            density_anomalies = anomaly_summary['density_anomalies']
            
            # Display density anomalies table
            st.dataframe(density_anomalies[['channel_name', 'source_name', 'timestamp', 
                                          'object_id', 'density_score', 'density_z_score']], 
                        use_container_width=True)
            
            # Plot density anomalies over time
            st.subheader("Density Anomalies Over Time")
            density_by_time = density_anomalies.groupby(['timestamp', 'channel_name']).size().reset_index(name='anomaly_count')
            
            fig = px.line(density_by_time, 
                         x='timestamp', 
                         y='anomaly_count',
                         color='channel_name',
                         title='Density Anomalies Over Time',
                         labels={'anomaly_count': 'Number of Density Anomalies', 'timestamp': 'Timestamp'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No density anomalies detected in the filtered data.")

# ---- Visualization Section ----
st.markdown("---")
st.subheader("📈 Anomaly Visualizations")

# Generate matplotlib visualizations
fig = visualize_results(analyzed_df, return_figures=True)
st.pyplot(fig)

# ---- Object Distribution Section ----
st.markdown("---")
st.subheader("📊 Object Distribution Analysis")

# Create tabs for different distribution analyses
dist_tabs = st.tabs(["Objects by Class", "Objects by Channel", "Objects by Time"])

with dist_tabs[0]:
    # Object class distribution
    class_counts = filtered_df['object_class'].value_counts().reset_index()
    class_counts.columns = ['Object Class', 'Count']
    
    fig = px.pie(class_counts, values='Count', names='Object Class', 
                 title='Distribution of Object Classes')
    st.plotly_chart(fig, use_container_width=True)

with dist_tabs[1]:
    # Objects by channel
    channel_counts = filtered_df.groupby(['channel_name', 'object_class']).size().reset_index(name='count')
    
    fig = px.bar(channel_counts, x='channel_name', y='count', color='object_class',
                title='Object Distribution by Channel and Class',
                labels={'count': 'Number of Detections', 'channel_name': 'Channel Name'})
    st.plotly_chart(fig, use_container_width=True)

with dist_tabs[2]:
    # Objects over time
    time_counts = filtered_df.groupby([pd.Grouper(key='timestamp', freq='1h'), 'object_class']).size().reset_index(name='count')
    
    fig = px.line(time_counts, x='timestamp', y='count', color='object_class',
                 title='Object Detection Over Time',
                 labels={'count': 'Number of Detections', 'timestamp': 'Time'})
    st.plotly_chart(fig, use_container_width=True)


# ---- Calculations ----
# Create two new dataframes as per requirements

# 1. Objects by timestamp
objects_by_timestamp = filtered_df.groupby(['timestamp', 'object_class']).size().reset_index(name='counts')

# 2. Unique objects occurrence
unique_objects_occurrence = filtered_df.groupby(['channel_name', 'source_name', 'object_class'])['object_id'].nunique().reset_index(name='unique_objects')

# Sum by class (total unique objects by class)
class_totals = unique_objects_occurrence.groupby('object_class')['unique_objects'].sum().reset_index(name='total_unique_objects')
class_totals = class_totals.sort_values('total_unique_objects', ascending=False)

# ---- Visualizations ----
st.subheader("🎯 Object Class Distribution")

# Class distribution plots (bar and pie chart) with 2:1 width ratio
col1, col2 = st.columns([2, 1])

with col1:
    # Change color palette to "viridis"
    fig_bar = px.bar(
        class_totals,
        x='object_class',
        y='total_unique_objects',
        title='Unique Objects by Class (Descending Order)',
        labels={'total_unique_objects': 'Count', 'object_class': 'Object Class'},
        color='object_class',
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig_bar.update_layout(xaxis_title="Object Class", yaxis_title="Count")
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    fig_pie = px.pie(
        class_totals,
        values='total_unique_objects',
        names='object_class',
        title='Class Distribution (%)',
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)

# Line separator
st.markdown("---")

# ---- Time Series Analysis ----
st.subheader("⏱️ Temporal Analysis")

# Object Detections Time Series Graph with class tabs
all_classes = sorted(filtered_df['object_class'].unique())
time_series_data = objects_by_timestamp.copy()

# Create time series plot
time_series_fig = px.line(
    time_series_data, 
    x='timestamp', 
    y='counts', 
    color='object_class',
    title='Object Detections Over Time',
    labels={'counts': 'Number of Detections', 'timestamp': 'Time'}
)
time_series_fig.update_layout(
    xaxis_title="Timestamp",
    yaxis_title="Detection Count"
)
st.plotly_chart(time_series_fig, use_container_width=True)

# Line separator
st.markdown("---")

# ---- Temporal Trends Distribution ----
st.subheader("📅 Temporal Trends Distribution")

# Create tabs for different time granularities
trend_tabs = st.tabs(["Daily (Hours)", "Weekly (Days)", "Monthly (Days)", "Yearly (Months)"])

# Create a copy of the dataframe with datetime components
time_df = filtered_df.copy()
time_df['hour'] = time_df['timestamp'].dt.hour
time_df['day_of_week'] = time_df['timestamp'].dt.day_name()
time_df['day_of_month'] = time_df['timestamp'].dt.day
time_df['month'] = time_df['timestamp'].dt.month_name()

# Order for days of week
days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Function to get top classes and aggregate others
def get_top_classes_data(df, time_col, time_values, class_col='object_class', n_top=4):
    # Get counts by time and class
    counts = df.groupby([time_col, class_col]).size().reset_index(name='count')
    
    # Get top classes by total count
    top_classes = counts.groupby(class_col)['count'].sum().nlargest(n_top).index.tolist()
    
    # Mark other classes
    counts['class_category'] = counts[class_col].apply(lambda x: x if x in top_classes else 'Others')
    
    # Aggregate others
    agg_counts = counts.groupby([time_col, 'class_category']).sum().reset_index()
    
    # Ensure all time values are present
    result = []
    for tv in time_values:
        for cls in top_classes + ['Others']:
            match = agg_counts[(agg_counts[time_col] == tv) & (agg_counts['class_category'] == cls)]
            if match.empty:
                result.append({'time': tv, 'class': cls, 'count': 0})
            else:
                result.append({'time': tv, 'class': cls, 'count': match.iloc[0]['count']})
    
    return pd.DataFrame(result)

# Daily (Hours) tab
with trend_tabs[0]:
    hours = list(range(24))
    hour_data = get_top_classes_data(time_df, 'hour', hours)
    
    hour_fig = px.bar(
        hour_data, 
        x='time', 
        y='count', 
        color='class',
        barmode='group',
        title='Object Detections by Hour of Day',
        labels={'time': 'Hour of Day (0-23)', 'count': 'Count', 'class': 'Object Class'}
    )
    hour_fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(24)),
            title="Hour of Day"
        ),
        yaxis_title="Detection Count"
    )
    st.plotly_chart(hour_fig, use_container_width=True)

# Weekly (Days) tab
with trend_tabs[1]:
    days_data = get_top_classes_data(time_df, 'day_of_week', days_order)
    
    # Map for correct ordering
    day_order_map = {day: i for i, day in enumerate(days_order)}
    days_data['day_order'] = days_data['time'].map(day_order_map)
    days_data = days_data.sort_values('day_order')
    
    day_fig = px.bar(
        days_data, 
        x='time', 
        y='count', 
        color='class',
        barmode='group',
        title='Object Detections by Day of Week',
        labels={'time': 'Day of Week', 'count': 'Count', 'class': 'Object Class'},
        category_orders={"time": days_order}
    )
    day_fig.update_layout(
        xaxis_title="Day of Week",
        yaxis_title="Detection Count"
    )
    st.plotly_chart(day_fig, use_container_width=True)

# Monthly (Days) tab
with trend_tabs[2]:
    days_of_month = list(range(1, 32))
    month_days_data = get_top_classes_data(time_df, 'day_of_month', days_of_month)
    
    month_day_fig = px.bar(
        month_days_data, 
        x='time', 
        y='count', 
        color='class',
        barmode='group',
        title='Object Detections by Day of Month',
        labels={'time': 'Day of Month', 'count': 'Count', 'class': 'Object Class'}
    )
    month_day_fig.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=list(range(1, 32)),
            title="Day of Month"
        ),
        yaxis_title="Detection Count"
    )
    st.plotly_chart(month_day_fig, use_container_width=True)

# Yearly (Months) tab
with trend_tabs[3]:
    months_order = ["January", "February", "March", "April", "May", "June", 
                    "July", "August", "September", "October", "November", "December"]
    year_data = get_top_classes_data(time_df, 'month', months_order)
    
    # Map for correct ordering
    month_order_map = {month: i for i, month in enumerate(months_order)}
    year_data['month_order'] = year_data['time'].map(month_order_map)
    year_data = year_data.sort_values('month_order')
    
    year_fig = px.bar(
        year_data, 
        x='time', 
        y='count', 
        color='class',
        barmode='group',
        title='Object Detections by Month',
        labels={'time': 'Month', 'count': 'Count', 'class': 'Object Class'},
        category_orders={"time": months_order}
    )
    year_fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Detection Count"
    )
    st.plotly_chart(year_fig, use_container_width=True)

# Line separator
st.markdown("---")

# ---- Spatial Analysis (Heatmap) ----
st.subheader("🗺️ Spatial Distribution (Bounding Box Heatmap)")

# Extract bounding box coordinates
def extract_box_centers(df):
    centers = []
    for _, row in df.iterrows():
        box = row['object_box']
        if isinstance(box, list) and len(box) == 4:
            x_center = (box[0] + box[2]) / 2
            y_center = (box[1] + box[3]) / 2
            centers.append((x_center, y_center))
        else:
            centers.append((320, 320))  # Default center if box is invalid
    
    return centers

# Create tabs for classes
all_classes = ["All Classes"] + sorted(filtered_df['object_class'].unique())
class_tabs = st.tabs(all_classes)

for idx, tab_class in enumerate(all_classes):
    with class_tabs[idx]:
        # Filter data for selected class
        if tab_class == "All Classes":
            heatmap_df = filtered_df
        else:
            heatmap_df = filtered_df[filtered_df['object_class'] == tab_class]
        
        # Extract box centers
        box_centers = extract_box_centers(heatmap_df)
        x_coords = [center[0] for center in box_centers]
        y_coords = [center[1] for center in box_centers]
        
        # Create heatmap using matplotlib and seaborn with smaller size and font
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.set_facecolor('white')
        
        # Only create heatmap if we have data
        if len(x_coords) > 1:
            sns.kdeplot(
                x=x_coords, 
                y=y_coords, 
                cmap="viridis", 
                fill=True, 
                alpha=0.7,
                ax=ax
            )
        
        ax.set_xlim(0, 640)
        ax.set_ylim(0, 640)
        ax.invert_yaxis()
        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top')
        ax.set_xlabel('X Coordinate', fontsize=9)  # Smaller font
        ax.set_ylabel('Y Coordinate', fontsize=9)  # Smaller font
        ax.tick_params(axis='both', which='major', labelsize=8)  # Smaller tick labels
        
        st.pyplot(fig)

# Line separator
st.markdown("---")

# ---- Classes by Channel and Source ----
st.subheader("📡 Classes Count by Channel and Source")

# Add "All Channels" option
all_channel_data = {}
for obj_class in filtered_df['object_class'].unique():
    class_count = filtered_df[filtered_df['object_class'] == obj_class].shape[0]
    all_channel_data[obj_class] = class_count

all_channel_df = pd.DataFrame(list(all_channel_data.items()), columns=['object_class', 'count'])
all_channel_df = all_channel_df.sort_values('count', ascending=False)

# Create tabs for channels with "All Channels" as first tab
channel_list = ["All Channels"] + sorted(filtered_df['channel_name'].unique())
channel_tabs = st.tabs(channel_list)

# All Channels tab
with channel_tabs[0]:
    # All Sources tab
    all_sources_fig = px.bar(
        all_channel_df,
        x='object_class',
        y='count',
        color='object_class',
        title=f'Object Class Distribution for All Channels',
        labels={'count': 'Count', 'object_class': 'Object Class'},
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    all_sources_fig.update_layout(
        xaxis_title="Object Class",
        yaxis_title="Count"
    )

    # Create tabs for each source
    source_list = ["All Sources"] + sorted(filtered_df['source_name'].unique())
    source_tabs = st.tabs(source_list)
    
    # All Sources tab
    with source_tabs[0]:
        st.plotly_chart(all_sources_fig, use_container_width=True)
    
    # Individual sources tabs
    for i, source in enumerate(sorted(filtered_df['source_name'].unique())):
        with source_tabs[i+1]:  # +1 because "All Sources" is first
            source_df = filtered_df[filtered_df['source_name'] == source]
            
            # Count objects by class
            class_counts = source_df['object_class'].value_counts().reset_index()
            class_counts.columns = ['object_class', 'count']
            
            # Create bar chart
            fig = px.bar(
                class_counts,
                x='object_class',
                y='count',
                color='object_class',
                title=f'Object Class Distribution for All Channels - {source}',
                labels={'count': 'Count', 'object_class': 'Object Class'},
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig.update_layout(
                xaxis_title="Object Class",
                yaxis_title="Count"
            )
            st.plotly_chart(fig, use_container_width=True)

# For each channel, create nested tabs for sources
for i, channel in enumerate(sorted(filtered_df['channel_name'].unique())):
    with channel_tabs[i+1]:  # +1 because "All Channels" is first
        channel_df = filtered_df[filtered_df['channel_name'] == channel]
        
        # Create "All Sources" data for this channel
        channel_all_sources = channel_df['object_class'].value_counts().reset_index()
        channel_all_sources.columns = ['object_class', 'count']
        
        # Create tabs for sources with "All Sources" as first tab
        source_list = ["All Sources"] + sorted(channel_df['source_name'].unique())
        source_tabs = st.tabs(source_list)
        
        # All Sources tab for this channel
        with source_tabs[0]:
            fig = px.bar(
                channel_all_sources,
                x='object_class',
                y='count',
                color='object_class',
                title=f'Object Class Distribution for {channel} - All Sources',
                labels={'count': 'Count', 'object_class': 'Object Class'},
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig.update_layout(
                xaxis_title="Object Class",
                yaxis_title="Count"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # For each source, show class distribution
        for j, source in enumerate(sorted(channel_df['source_name'].unique())):
            with source_tabs[j+1]:  # +1 because "All Sources" is first
                source_df = channel_df[channel_df['source_name'] == source]
                
                # Count objects by class
                class_counts = source_df['object_class'].value_counts().reset_index()
                class_counts.columns = ['object_class', 'count']
                
                # Create bar chart
                fig = px.bar(
                    class_counts,
                    x='object_class',
                    y='count',
                    color='object_class',
                    title=f'Object Class Distribution for {channel} - {source}',
                    labels={'count': 'Count', 'object_class': 'Object Class'},
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                fig.update_layout(
                    xaxis_title="Object Class",
                    yaxis_title="Count"
                )
                st.plotly_chart(fig, use_container_width=True)

# Line separator
st.markdown("---")

# ---- Confidence Analysis ----
st.subheader("🎯 Confidence Analysis by Class")

# Create 2 columns for bar chart and box plot
conf_col1, conf_col2 = st.columns(2)

# Calculate average confidence by class
avg_conf = filtered_df.groupby('object_class')['object_conf'].mean().reset_index()
avg_conf = avg_conf.sort_values('object_conf', ascending=False)

# Bar chart in column 1
with conf_col1:
    bar_fig = px.bar(
        avg_conf,
        x='object_class',
        y='object_conf',
        color='object_class',
        title='Average Confidence by Class',
        labels={'object_conf': 'Average Confidence', 'object_class': 'Object Class'}
    )
    bar_fig.update_layout(
        xaxis_title="Object Class",
        yaxis_title="Average Confidence",
        yaxis=dict(tickformat='.0%')
    )
    st.plotly_chart(bar_fig, use_container_width=True)

# Box plot in column 2
with conf_col2:
    box_fig = px.box(
        filtered_df,
        x='object_class',
        y='object_conf',
        color='object_class',
        title='Confidence Distribution by Class',
        labels={'object_conf': 'Confidence', 'object_class': 'Object Class'}
    )
    box_fig.update_layout(
        xaxis_title="Object Class",
        yaxis_title="Confidence",
        yaxis=dict(tickformat='.0%')
    )
    st.plotly_chart(box_fig, use_container_width=True)

# Line separator
st.markdown("---")

# ---- NEW ANALYSIS AND VISUALIZATIONS ----

# 1. Object Detection Rate Analysis
st.markdown("### 📊 Object Detection Rate Analysis")
col1, col2 = st.columns(2)

# Calculate detection rates
time_diff = filtered_df['timestamp'].max() - filtered_df['timestamp'].min()
total_hours = time_diff.total_seconds() / 3600

# Detection rate by class (objects per hour)
detection_rate = filtered_df.groupby('object_class').size().reset_index(name='count')
detection_rate['rate_per_hour'] = detection_rate['count'] / total_hours

with col1:
    rate_fig = px.bar(
        detection_rate.sort_values('rate_per_hour', ascending=False),
        x='object_class',
        y='rate_per_hour',
        color='object_class',
        title='Detection Rate by Class (Objects/Hour)',
        labels={'rate_per_hour': 'Detections/Hour', 'object_class': 'Object Class'}
    )
    rate_fig.update_layout(
        xaxis_title="Object Class",
        yaxis_title="Detections per Hour"
    )
    st.plotly_chart(rate_fig, use_container_width=True)

# 2. Channel-Source Heatmap analysis
with col2:
    # Create a crosstab of sources and channels
    cross_data = pd.crosstab(
        filtered_df['source_name'], 
        filtered_df['channel_name'],
        values=filtered_df['object_id'], 
        aggfunc='count',
        normalize=False
    ).fillna(0)
    
    # Create heatmap
    fig = px.imshow(
        cross_data,
        labels=dict(x="Channel", y="Source", color="Detection Count"),
        title="Detection Density by Channel and Source",
        color_continuous_scale="Viridis",
        aspect="auto"
    )
    fig.update_layout(
        xaxis_title="Channel",
        yaxis_title="Source"
    )
    st.plotly_chart(fig, use_container_width=True)

# 3. Object Co-occurrence Analysis
st.markdown("### 🤝 Object Co-occurrence Analysis")

# Create co-occurrence matrix
def create_cooccurrence_matrix(df):
    # Get unique timestamps, channels, and sources
    timestamps = df['timestamp'].dt.floor('1min').unique()
    channels = df['channel_name'].unique()
    sources = df['source_name'].unique()
    
    # Dictionary to store co-occurrences
    cooccurrence = {}
    classes = sorted(df['object_class'].unique())
    
    # Initialize the matrix
    for c1 in classes:
        cooccurrence[c1] = {}
        for c2 in classes:
            cooccurrence[c1][c2] = 0
    
    # Count co-occurrences
    for ts in timestamps:
        for ch in channels:
            for src in sources:
                # Get classes present in this timestamp-channel-source combination
                present_classes = df[
                    (df['timestamp'].dt.floor('1min') == ts) & 
                    (df['channel_name'] == ch) & 
                    (df['source_name'] == src)
                ]['object_class'].unique()
                
                # Update co-occurrence matrix
                for i, c1 in enumerate(present_classes):
                    for c2 in present_classes[i:]:  # include self-occurrence
                        cooccurrence[c1][c2] += 1
                        if c1 != c2:
                            cooccurrence[c2][c1] += 1
    
    # Convert to dataframe
    cooccurrence_df = pd.DataFrame(cooccurrence)
    
    return cooccurrence_df

# Create and display co-occurrence matrix
cooccurrence_matrix = create_cooccurrence_matrix(filtered_df)

# Create heatmap of co-occurrence
fig = px.imshow(
    cooccurrence_matrix,
    labels=dict(x="Object Class", y="Object Class", color="Co-occurrence Count"),
    title="Object Class Co-occurrence Matrix",
    color_continuous_scale="Viridis"
)
st.plotly_chart(fig, use_container_width=True)

# 4. Object Size Analysis
st.markdown("### 📏 Object Size Analysis")

# Calculate object sizes
def calculate_object_sizes(df):
    sizes = []
    for _, row in df.iterrows():
        box = row['object_box']
        if isinstance(box, list) and len(box) == 4:
            width = abs(box[2] - box[0])
            height = abs(box[3] - box[1])
            area = width * height
            sizes.append({
                'object_class': row['object_class'],
                'width': width,
                'height': height,
                'area': area
            })
    
    return pd.DataFrame(sizes)

# Calculate sizes
size_df = calculate_object_sizes(filtered_df)

if not size_df.empty:
    # Create size visualization tabs
    size_tabs = st.tabs(["Area Distribution", "Width vs Height"])
    
    with size_tabs[0]:
        # Create violin plot of area by class
        area_fig = px.violin(
            size_df,
            x='object_class',
            y='area',
            color='object_class',
            box=True,
            title="Object Area Distribution by Class",
            labels={'area': 'Area (pixels²)', 'object_class': 'Object Class'}
        )
        area_fig.update_layout(
            xaxis_title="Object Class",
            yaxis_title="Area (pixels²)"
        )
        st.plotly_chart(area_fig, use_container_width=True)
    
    with size_tabs[1]:
        # Create scatter plot of width vs height
        scatter_fig = px.scatter(
            size_df,
            x='width',
            y='height',
            color='object_class',
            opacity=0.7,
            title="Object Width vs Height by Class",
            labels={'width': 'Width (pixels)', 'height': 'Height (pixels)', 'object_class': 'Object Class'}
        )
        scatter_fig.update_layout(
            xaxis_title="Width (pixels)",
            yaxis_title="Height (pixels)"
        )
        st.plotly_chart(scatter_fig, use_container_width=True)

# Line separator
st.markdown("---")

# ---- Raw Data Table (optional) ----
if st.checkbox("Show Raw Data"):
    st.subheader("Raw Data Tables")
    
    # Create tabs for different dataframes
    raw_data_tabs = st.tabs(["Filtered DataFrame", "Objects by Timestamp", "Unique Objects Occurrence"])
    
    # Filtered DataFrame
    with raw_data_tabs[0]:
        st.dataframe(filtered_df)
    
    # Objects by Timestamp
    with raw_data_tabs[1]:
        st.dataframe(objects_by_timestamp)
    
    # Unique Objects Occurrence
    with raw_data_tabs[2]:
        st.dataframe(unique_objects_occurrence)

# ---- Download data ----
def to_excel(dfs_dict):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')

    for sheet_name, df in dfs_dict.items():
        for col in df.select_dtypes(include=['datetimetz']).columns:
            df[col] = df[col].dt.tz_localize(None)
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    writer.close()
    return output.getvalue()


st.download_button(
    label="Download All Data as Excel",
    data=to_excel({
        'Filtered_Data': filtered_df,
        'Objects_by_Timestamp': objects_by_timestamp,
        'Unique_Objects_Occurrence': unique_objects_occurrence
    }),
    file_name=f"surveillance_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

# streamlit run app.py --server.port 4567