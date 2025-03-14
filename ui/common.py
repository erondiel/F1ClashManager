import streamlit as st
import pandas as pd
import altair as alt

def create_stats_display(stats_dict, title="Stats", show_total=True):
    """
    Create a consistent display for stats dictionaries
    
    Parameters:
    -----------
    stats_dict : dict
        Dictionary containing stat names and values
    title : str
        Title to display above the stats
    show_total : bool
        Whether to show the total value of all stats
    
    Returns:
    --------
    None
    """
    if not stats_dict:
        st.warning("No stats available")
        return
    
    st.subheader(title)
    
    # Create a DataFrame for the stats
    stats_df = pd.DataFrame({
        "Stat": list(stats_dict.keys()),
        "Value": list(stats_dict.values())
    })
    
    # Sort by value (descending)
    stats_df = stats_df.sort_values(by="Value", ascending=False)
    
    # Create a bar chart
    chart = alt.Chart(stats_df).mark_bar().encode(
        x=alt.X('Value:Q', title='Value'),
        y=alt.Y('Stat:N', title=None, sort='-x'),
        color=alt.Color('Stat:N', legend=None)
    ).properties(
        height=len(stats_dict) * 40  # Adjust height based on number of stats
    )
    
    st.altair_chart(chart, use_container_width=True)
    
    # Show the data table
    st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    # Show total if requested
    if show_total:
        total = sum(stats_dict.values())
        st.info(f"Total Value: {total:.1f}")

def create_filter_sidebar(filter_options, title="Filters"):
    """
    Create a consistent sidebar filter section
    
    Parameters:
    -----------
    filter_options : dict
        Dictionary with filter names as keys and lists of options as values
    title : str
        Title to display above the filters
    
    Returns:
    --------
    dict
        Dictionary with filter names as keys and selected values as values
    """
    st.sidebar.subheader(title)
    
    selected_values = {}
    
    for filter_name, options in filter_options.items():
        # Add "All" option if not already present
        if "All" not in options:
            options = ["All"] + options
        
        # Create a unique key for each filter
        key = f"filter_{filter_name.lower().replace(' ', '_')}"
        
        # Create the selectbox
        selected = st.sidebar.selectbox(
            f"Filter by {filter_name}",
            options,
            key=key
        )
        
        selected_values[filter_name] = selected
    
    return selected_values

def create_comparison_chart(df, x_column, y_column, title=None, color_column=None):
    """
    Create a scatter plot for comparing two metrics
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing the data
    x_column : str
        Column name for the x-axis
    y_column : str
        Column name for the y-axis
    title : str, optional
        Title for the chart
    color_column : str, optional
        Column name to use for coloring points
    
    Returns:
    --------
    None
    """
    if title:
        st.subheader(title)
    
    if color_column:
        chart = alt.Chart(df).mark_circle(size=60).encode(
            x=alt.X(f'{x_column}:Q', title=x_column),
            y=alt.Y(f'{y_column}:Q', title=y_column),
            color=alt.Color(f'{color_column}:N', legend=alt.Legend(title=color_column)),
            tooltip=[col for col in df.columns]
        ).interactive()
    else:
        chart = alt.Chart(df).mark_circle(size=60).encode(
            x=alt.X(f'{x_column}:Q', title=x_column),
            y=alt.Y(f'{y_column}:Q', title=y_column),
            tooltip=[col for col in df.columns]
        ).interactive()
    
    st.altair_chart(chart, use_container_width=True)

def create_tabs_for_focus_areas(focus_areas, display_function):
    """
    Create tabs for different focus areas and display content using the provided function
    
    Parameters:
    -----------
    focus_areas : list
        List of focus area names
    display_function : function
        Function to call for each tab, will be passed the focus area name
    
    Returns:
    --------
    None
    """
    tabs = st.tabs(focus_areas)
    
    for i, tab in enumerate(tabs):
        with tab:
            display_function(focus_areas[i])

def format_stat_value(value, precision=1):
    """
    Format a stat value with consistent precision
    
    Parameters:
    -----------
    value : float or int
        The value to format
    precision : int
        Number of decimal places to show
    
    Returns:
    --------
    str
        Formatted value
    """
    try:
        return f"{float(value):.{precision}f}"
    except (ValueError, TypeError):
        return str(value)

def create_two_column_metrics(metrics_dict, title=None):
    """
    Display metrics in a two-column layout
    
    Parameters:
    -----------
    metrics_dict : dict
        Dictionary with metric names as keys and values as values
    title : str, optional
        Title to display above the metrics
    
    Returns:
    --------
    None
    """
    if title:
        st.subheader(title)
    
    # Create columns in pairs
    metrics = list(metrics_dict.items())
    for i in range(0, len(metrics), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            if i < len(metrics):
                name, value = metrics[i]
                st.metric(label=name, value=format_stat_value(value))
        
        with col2:
            if i + 1 < len(metrics):
                name, value = metrics[i + 1]
                st.metric(label=name, value=format_stat_value(value))

def create_success_error_message(success, success_msg, error_msg):
    """
    Display either a success or error message based on a condition
    
    Parameters:
    -----------
    success : bool
        Whether the operation was successful
    success_msg : str
        Message to display on success
    error_msg : str
        Message to display on error
    
    Returns:
    --------
    None
    """
    if success:
        st.success(success_msg)
    else:
        st.error(error_msg) 