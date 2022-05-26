# This project will let you examine and analyze SReality using Plotly / Dash Dashboard.

# Setup

Install all libraries from requirements.txt

# RUN

Running sreality_df_plotly_dash.py (from terminal - .\sreality_df_plotly_dash.py) will start a server and open a browser window with the plotly dashboard.

# Filter Properties

To change filters to different property types - change defaults in the function get_property_links in sreality_scrape.py file - according to the function description.

# To Scrape the Property Data

Run sreality_main.py (from terminal - .\sreality_main.py)

# Plotly for Different Data

Plotly Dashboard (sreality_df_plotly_dash.py) can be used to any other table data - with some minor changes in the code - where you need to list a names of columns from YOUR data.

In the function clean_property_df() - columns variable - list all columns from your data that will be selected for analysis
In the function prepare_column_names_and_aggr_functions() change the names of YOUR columnms in the specified variables according to the variable name, for example variable "x_columns" - put here names of columns that can be chosen to appear on graphs on x axis, these are mainly dimensions or qualitative columns. "y_columns" - choose here names of YOUR columns that can be aggregated, or should appear on Y axis - those are mainly facts or quantitative columns
