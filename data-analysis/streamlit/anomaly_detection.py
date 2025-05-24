import pandas as pd
import numpy as np
from collections import defaultdict
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from shapely.geometry import box

def process_data(df, channel_filter=None, source_filter=None):
    """
    Filter dataframe by channel_name and source_name and calculate object durations
    
    Args:
        df: Input dataframe with columns [timestamp, channel_name, source_name, 
                                         object_class, object_id, object_conf, object_box]
        channel_filter: Optional filter for channel_name
        source_filter: Optional filter for source_name
        
    Returns:
        Filtered dataframe with additional duration column
    """
    # Apply filters if provided
    filtered_df = df.copy()
    if channel_filter:
        filtered_df = filtered_df[filtered_df['channel_name'] == channel_filter]
    if source_filter:
        filtered_df = filtered_df[filtered_df['source_name'] == source_filter]
    
    # Ensure timestamp is in datetime format
    filtered_df['timestamp'] = pd.to_datetime(filtered_df['timestamp'])
    
    # Sort by object_id and timestamp
    filtered_df = filtered_df.sort_values(['object_id', 'timestamp'])
    
    # Calculate first appearance time for each object_id
    first_appearances = filtered_df.groupby('object_id')['timestamp'].first().reset_index()
    first_appearances.columns = ['object_id', 'first_appearance']
    
    # Calculate last appearance time for each object_id
    last_appearances = filtered_df.groupby('object_id')['timestamp'].last().reset_index()
    last_appearances.columns = ['object_id', 'last_appearance']
    
    # Merge first and last appearances
    object_durations = pd.merge(first_appearances, last_appearances, on='object_id')
    
    # Calculate duration in seconds
    object_durations['duration'] = (object_durations['last_appearance'] - 
                                   object_durations['first_appearance']).dt.total_seconds()
    
    # Merge durations back to filtered_df
    result_df = pd.merge(filtered_df, object_durations[['object_id', 'duration']], on='object_id')
    
    return result_df

def detect_duration_anomalies(df):
    """
    Detect anomalies in object durations using Isolation Forest (non-trainable usage)
    
    Args:
        df: Processed dataframe with duration column
    
    Returns:
        DataFrame with anomaly scores for durations
    """
    # Group by object_class and detect anomalies within each class
    classes = df['object_class'].unique()
    results = []
    
    for obj_class in classes:
        class_df = df[df['object_class'] == obj_class].copy()
        
        # Skip if too few samples
        if len(class_df) < 5:
            class_df['duration_anomaly_score'] = 0
            results.append(class_df)
            continue
        
        # Get unique duration values per object_id (to avoid duplicates)
        unique_durations = class_df.drop_duplicates('object_id')[['object_id', 'duration']]
        
        # Apply Isolation Forest - used in non-trainable manner with fixed parameters
        clf = IsolationForest(contamination=0.1, random_state=42)
        durations = unique_durations['duration'].values.reshape(-1, 1)
        scores = clf.fit_predict(durations)
        
        # Convert predictions to anomaly scores (-1 for anomalies, 1 for normal)
        unique_durations['duration_anomaly_score'] = scores
        
        # Map scores back to the original dataframe
        anomaly_mapping = unique_durations.set_index('object_id')['duration_anomaly_score'].to_dict()
        class_df['duration_anomaly_score'] = class_df['object_id'].map(anomaly_mapping)
        
        results.append(class_df)
    
    return pd.concat(results)

def detect_object_count_anomalies(df):
    """
    Detect anomalies in the number of objects per timestamp using Z-score method
    
    Args:
        df: Processed dataframe
    
    Returns:
        DataFrame with anomaly scores for object counts
    """
    # Count objects per timestamp
    counts = df.groupby(['timestamp']).size().reset_index(name='object_count')
    
    # Calculate z-scores for object counts
    mean_count = counts['object_count'].mean()
    std_count = counts['object_count'].std()
    
    if std_count == 0:  # Handle case with no variation
        counts['count_z_score'] = 0
    else:
        counts['count_z_score'] = abs((counts['object_count'] - mean_count) / std_count)
    
    # Flag anomalies where z-score exceeds threshold (e.g., 2.5)
    threshold = 2.5
    counts['is_count_anomaly'] = counts['count_z_score'] > threshold
    
    # Merge back to original dataframe
    result = pd.merge(df, counts[['timestamp', 'object_count', 'count_z_score', 'is_count_anomaly']], 
                     on='timestamp', how='left')
    
    return result

def detect_density_anomalies(df):
    """
    Detect anomalies in object density using DBSCAN clustering
    
    Args:
        df: Processed dataframe with object_box column containing bounding box coordinates
    
    Returns:
        DataFrame with density anomaly scores
    """
    results = []
    
    # Process each timestamp separately
    for timestamp, group in df.groupby('timestamp'):
        # Skip if too few objects
        if len(group) < 3:
            group['density_score'] = 0
            group['is_density_anomaly'] = False
            results.append(group)
            continue
        
        # Extract box centers and create intersection matrix
        centers = []
        boxes = []
        
        for _, row in group.iterrows():
            # Parse bounding box coordinates (assuming format: x1,y1,x2,y2)
            try:
                # Handle different possible formats of object_box
                if isinstance(row['object_box'], str):
                    coords = [float(x) for x in row['object_box'].strip('[]()').split(',')]
                elif isinstance(row['object_box'], list):
                    coords = row['object_box']
                else:
                    # Skip invalid boxes
                    continue
                
                x1, y1, x2, y2 = coords
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                centers.append([center_x, center_y])
                
                # Create box object for intersection calculation
                boxes.append(box(x1, y1, x2, y2))
            except (ValueError, IndexError):
                # Skip invalid format
                continue
        
        if not centers:
            group['density_score'] = 0
            group['is_density_anomaly'] = False
            results.append(group)
            continue
        
        # Calculate intersection matrix
        n_boxes = len(boxes)
        intersection_count = np.zeros(n_boxes)
        
        for i in range(n_boxes):
            for j in range(i+1, n_boxes):
                if boxes[i].intersects(boxes[j]):
                    intersection_count[i] += 1
                    intersection_count[j] += 1
        
        # Apply DBSCAN to find density-based clusters (non-trainable, parameter-based)
        if len(centers) >= 2:  # Need at least 2 points for DBSCAN
            # Convert to numpy array
            centers_array = np.array(centers)
            
            # Apply DBSCAN with fixed parameters (non-trainable approach)
            clustering = DBSCAN(eps=50, min_samples=2).fit(centers_array)
            
            # Get cluster labels (-1 is for noise points)
            labels = clustering.labels_
            
            # Calculate density score based on cluster membership and intersection count
            density_scores = defaultdict(float)
            
            # Assign density scores
            for i, (label, intersect_count) in enumerate(zip(labels, intersection_count)):
                if label == -1:  # Noise points
                    density_scores[i] = 0.0
                else:
                    # Density score combines cluster membership and intersection count
                    cluster_size = np.sum(labels == label)
                    density_scores[i] = (intersect_count + 1) * (cluster_size / len(labels))
        else:
            # Not enough points for clustering
            density_scores = {0: 0.0}
        
        # Map density scores back to the dataframe
        density_score_list = []
        for i in range(len(group)):
            if i < len(density_scores):
                density_score_list.append(density_scores[i])
            else:
                density_score_list.append(0.0)
        
        group_copy = group.copy()
        group_copy['density_score'] = density_score_list
        
        # Determine anomalies
        if len(group_copy) > 0 and group_copy['density_score'].std() > 0:
            # Use z-score for density anomaly detection
            mean_density = group_copy['density_score'].mean()
            std_density = group_copy['density_score'].std()
            group_copy['density_z_score'] = abs((group_copy['density_score'] - mean_density) / std_density)
            group_copy['is_density_anomaly'] = group_copy['density_z_score'] > 2.0
        else:
            group_copy['density_z_score'] = 0
            group_copy['is_density_anomaly'] = False
        
        results.append(group_copy)
    
    return pd.concat(results) if results else pd.DataFrame()

def analyze_data(df, channel_filter=None, source_filter=None):
    """
    Complete analysis pipeline
    """
    # Process and filter data
    processed_df = process_data(df, channel_filter, source_filter)
    
    # Apply all three anomaly detection methods
    result = processed_df.copy()
    
    # 1. Duration anomalies
    result = detect_duration_anomalies(result)
    
    # 2. Object count anomalies
    result = detect_object_count_anomalies(result)
    
    # 3. Density anomalies
    result = detect_density_anomalies(result)
    
    return result

def visualize_results(df, return_figures=False):
    """
    Visualize anomaly detection results
    
    Args:
        df: Dataframe with anomaly detection results
        return_figures: If True, return the figure objects instead of displaying them
        
    Returns:
        If return_figures is True, returns a list of figure objects
    """
    # Create a figure with subplots
    fig, axes = plt.subplots(3, 1, figsize=(12, 15))
    
    # 1. Duration anomalies by object class
    duration_data = df.drop_duplicates('object_id')[['object_class', 'duration', 'duration_anomaly_score']]
    anomalies = duration_data[duration_data['duration_anomaly_score'] == -1]
    normal = duration_data[duration_data['duration_anomaly_score'] == 1]
    
    for obj_class in duration_data['object_class'].unique():
        class_normal = normal[normal['object_class'] == obj_class]
        class_anomalies = anomalies[anomalies['object_class'] == obj_class]
        
        axes[0].scatter(class_normal['object_class'], class_normal['duration'], 
                       color='blue', alpha=0.5, label='Normal' if obj_class == duration_data['object_class'].unique()[0] else "")
        axes[0].scatter(class_anomalies['object_class'], class_anomalies['duration'], 
                       color='red', marker='x', s=100, label='Anomaly' if obj_class == duration_data['object_class'].unique()[0] else "")
    
    axes[0].set_title('Object Duration Anomalies by Class')
    axes[0].set_xlabel('Object Class')
    axes[0].set_ylabel('Duration (seconds)')
    axes[0].legend()
    
    # 2. Object count anomalies by timestamp
    count_data = df[['timestamp', 'object_count', 'is_count_anomaly']].drop_duplicates('timestamp')
    count_data = count_data.sort_values('timestamp')
    
    normal_counts = count_data[~count_data['is_count_anomaly']]
    anomaly_counts = count_data[count_data['is_count_anomaly']]
    
    axes[1].plot(normal_counts['timestamp'], normal_counts['object_count'], 'b-', label='Normal')
    axes[1].scatter(anomaly_counts['timestamp'], anomaly_counts['object_count'], 
                   color='red', marker='x', s=100, label='Anomaly')
    axes[1].set_title('Object Count Anomalies by Timestamp')
    axes[1].set_xlabel('Timestamp')
    axes[1].set_ylabel('Object Count')
    axes[1].legend()
    plt.xticks(rotation=45)
    
    # 3. Density anomalies
    density_data = df[['timestamp', 'object_id', 'density_score', 'is_density_anomaly']]
    
    # Get average density score per timestamp
    avg_density = density_data.groupby('timestamp')['density_score'].mean().reset_index()
    avg_density = avg_density.sort_values('timestamp')
    
    axes[2].plot(avg_density['timestamp'], avg_density['density_score'], 'g-', label='Avg Density')
    
    # Plot density anomalies
    for timestamp, group in df[df['is_density_anomaly']].groupby('timestamp'):
        if len(group) > 0:
            axes[2].axvline(x=timestamp, color='red', linestyle='--', alpha=0.3)
    
    anomaly_timestamps = df[df['is_density_anomaly']]['timestamp'].unique()
    if len(anomaly_timestamps) > 0:
        axes[2].scatter([anomaly_timestamps[0]], [0], color='red', marker='x', s=100, label='Density Anomaly')
    
    axes[2].set_title('Object Density Anomalies by Timestamp')
    axes[2].set_xlabel('Timestamp')
    axes[2].set_ylabel('Average Density Score')
    axes[2].legend()
    
    plt.tight_layout()
    
    if return_figures:
        return fig
    else:
        plt.show()

def get_anomaly_summary(df):
    """
    Get summary statistics about anomalies
    
    Args:
        df: Dataframe with anomaly detection results
        
    Returns:
        Dictionary with anomaly summary statistics
    """
    # Duration anomalies
    duration_anomalies = df[df['duration_anomaly_score'] == -1].drop_duplicates('object_id')
    
    # Count anomalies 
    count_anomalies = df[df['is_count_anomaly']].drop_duplicates('timestamp')
    
    # Density anomalies
    density_anomalies = df[df['is_density_anomaly']].drop_duplicates(['timestamp', 'object_id'])
    
    return {
        'duration_anomaly_count': len(duration_anomalies),
        'count_anomaly_count': len(count_anomalies),
        'density_anomaly_count': len(density_anomalies),
        'total_anomaly_count': len(duration_anomalies) + len(count_anomalies) + len(density_anomalies),
        'duration_anomalies': duration_anomalies,
        'count_anomalies': count_anomalies,
        'density_anomalies': density_anomalies
    }

def get_anomaly_details(df):
    """
    Get detailed information about anomalies
    
    Args:
        df: Dataframe with anomaly detection results
        
    Returns:
        DataFrame with detailed anomaly information
    """
    # Duration anomalies
    duration_anomalies = df[df['duration_anomaly_score'] == -1].drop_duplicates('object_id')
    if not duration_anomalies.empty:
        duration_anomalies = duration_anomalies[['channel_name', 'source_name', 'timestamp', 'object_class', 'object_id', 'duration']]
        duration_anomalies['anomaly_type'] = 'Duration'
    else:
        duration_anomalies = pd.DataFrame(columns=['channel_name', 'source_name', 'timestamp', 'object_class', 'object_id', 'duration', 'anomaly_type'])
    
    # Count anomalies
    count_anomalies = df[df['is_count_anomaly']].drop_duplicates('timestamp')
    if not count_anomalies.empty:
        count_anomalies = count_anomalies[['channel_name', 'source_name', 'timestamp', 'object_count', 'count_z_score']]
        count_anomalies['anomaly_type'] = 'Object Count'
        # Rename columns to match
        count_anomalies = count_anomalies.rename(columns={
            'object_count': 'value',
            'count_z_score': 'score'
        })
    else:
        count_anomalies = pd.DataFrame(columns=['channel_name', 'source_name', 'timestamp', 'value', 'score', 'anomaly_type'])
    
    # Density anomalies
    density_anomalies = df[df['is_density_anomaly']].drop_duplicates(['timestamp', 'object_id'])
    if not density_anomalies.empty:
        density_anomalies = density_anomalies[['channel_name', 'source_name', 'timestamp', 'object_id', 'density_score', 'density_z_score']]
        density_anomalies['anomaly_type'] = 'Density'
        # Rename columns to match
        density_anomalies = density_anomalies.rename(columns={
            'density_score': 'value',
            'density_z_score': 'score'
        })
    else:
        density_anomalies = pd.DataFrame(columns=['channel_name', 'source_name', 'timestamp', 'object_id', 'value', 'score', 'anomaly_type'])
    
    # Combine all anomalies
    all_anomalies = pd.concat([
        duration_anomalies[['channel_name', 'source_name', 'timestamp', 'anomaly_type']],
        count_anomalies[['channel_name', 'source_name', 'timestamp', 'anomaly_type']],
        density_anomalies[['channel_name', 'source_name', 'timestamp', 'anomaly_type']]
    ])
    
    return all_anomalies
