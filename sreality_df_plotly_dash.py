#%%
import pandas as pd
import webbrowser
import base64
from threading import Timer
import numpy as np
import dash_bootstrap_components as dbc
from dash import html
from dash import dcc
import plotly.express as px
from dash.dependencies import Input, Output
from jupyter_dash import JupyterDash
from dash_table import DataTable
import plotly.figure_factory as ff
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import math
from plotly.graph_objs import Heatmap
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
 

# Helping Functions
def astype_inplace(df, dct):
    """
    Allows to change Dataframe Column Datatype inplace.
    """
    df[list(dct.keys())] = df.astype(dct)[list(dct.keys())]


def open_browser():
    """
    Helping Function to Open Browser automatically, when script with App is run.
    """
    webbrowser.open("http://127.0.0.1:8050/")


# DataFrame Processing
def clean_property_df(df):
    """
    Cleaning DataFrame for Dashboard.
    """
    # Choose Columns to Analyze
    columns = [
        "Building",
        "Property_status",
        "Ownership",
        "Property_location",
        "Floor",
        "Water",
        "Heating",
        "Waste",
        "Electricity",
        "Barrier-free_access",
        "Elevator",
        "Energy_Efficiency_Rating",
        "Furnished",
        "Gas",
        "Loft",
        "Flat_type",
        "Ceiling_height",
        "Status",
        "Usable_area",
        "Floorage",
        "Built-up_area",
        "Balcony",
        "Cellar",
        "Garden_area",
        "Terrace",
        "Garage",
        "Parking",
        "Loggia",
        "Reconstruction_year",
        "Candy shop",
        "Movies",
        "Playground",
        "Small shop",
        "Pub",
        "Theater",
        "Vet office",
        "Tram",
        "Restaurant",
        "Shop",
        "Post Office",
        "School",
        "Drugstore",
        "Bus Public Transport",
        "ATM",
        "Metro",
        "Medic",
        "Sports",
        "Kindergarten",
        "Train",
        "Natural attraction",
        "Total_price",
        "Annuity",
        "Move-in_date",
        "Acquisition_of_title",
        "Address",
        "Image",
        "Property_Link",
        "Property_Type",
        "Advertising_Type",
        "Reload_Date_Time",
        "Order_ID",
    ]

    # Some property kinds, like Apartments or Houses dont have all columns specified, so we need to use
    # reindex, so the columns that are not in df, will be appear there, but will be filled by None
    df_preselected = df.reindex(columns=columns)

    ### "Price" --> Make "Price" Column from "Total_price" Column containing other text
    df_preselected[["Price", "to_remove"]] = (
        df_preselected["Total_price"].astype(str).str.split("CZK", expand=True)
    )
    df_preselected["Price"] = df_preselected["Price"].astype(str).str.replace(" ", "")
    df_preselected.drop(["to_remove", "Total_price"], axis=1, inplace=True)

    ### "Address" - Rename and split into parts
    df_preselected.rename(columns={"Address": "Address_Full"}, inplace=True)
    df_preselected[["Address", "Districts_Processing"]] = (
        df_preselected["Address_Full"].astype(str).str.split(",", expand=True)
    )
    df_preselected["Administrative_District"] = (
        df_preselected["Districts_Processing"]
        .astype(str)
        .str.split("-", expand=True)[0]
    )
    df_preselected["Municipal_District"] = (
        df_preselected["Districts_Processing"]
        .astype(str)
        .str.split("-", expand=True)[1]
    )
    df_preselected["Administrative_District"] = (
        df_preselected["Administrative_District"].astype(str).str.strip()
    )
    df_preselected["Municipal_District"] = (
        df_preselected["Municipal_District"].astype(str).str.strip()
    )
    df_preselected.drop(["Districts_Processing"], axis=1, inplace=True)

    ### Floor - Separate Floor, Floors Total and Floors Underground
    df_preselected["Floor"] = (
        df_preselected["Floor"].astype(str).str.replace("ground ", "0. ")
    )
    df_preselected.rename(columns={"Floor": "Floor_Full"}, inplace=True)
    # Making Floor_Underground Column
    df_preselected[["Floor", "Floor_Processing"]] = (
        df_preselected["Floor_Full"].astype(str).str.split(". floor", expand=True)
    )
    df_preselected[["Floor_Total_Processing", "Floor_Underground"]] = (
        df_preselected["Floor_Processing"]
        .astype(str)
        .str.split(" including ", expand=True)
    )
    df_preselected["Floor_Underground"] = np.where(
        (df_preselected["Floor_Underground"].notnull()),
        df_preselected["Floor_Underground"].str[0],
        df_preselected["Floor_Underground"],
    )

    # Making Floor_Total Column
    df_preselected[["Floor_Total_Processing_2", "Floor_Total"]] = (
        df_preselected["Floor_Total_Processing"]
        .astype(str)
        .str.split(" of total ", expand=True)
    )

    #  Dropping Processing Columns
    df_preselected.drop(["Floor_Processing"], axis=1, inplace=True)
    df_preselected.drop(["Floor_Full"], axis=1, inplace=True)
    df_preselected.drop(["Floor_Total_Processing"], axis=1, inplace=True)
    df_preselected.drop(["Floor_Total_Processing_2"], axis=1, inplace=True)

    ### Remove m2 / m
    df_preselected["Usable_area"] = (
        df_preselected["Usable_area"].astype(str).str.replace("m2", "")
    )
    df_preselected["Floorage"] = (
        df_preselected["Floorage"].astype(str).str.replace("m2", "")
    )
    df_preselected["Balcony"] = (
        df_preselected["Balcony"].astype(str).str.replace("m2", "")
    )
    df_preselected["Cellar"] = (
        df_preselected["Cellar"].astype(str).str.replace("m2", "")
    )
    df_preselected["Terrace"] = (
        df_preselected["Terrace"].astype(str).str.replace("m2", "")
    )
    df_preselected["Loggia"] = (
        df_preselected["Loggia"].astype(str).str.replace("m2", "")
    )
    df_preselected["Garden_area"] = (
        df_preselected["Garden_area"].astype(str).str.replace("m2", "")
    )
    df_preselected["Ceiling_height"] = (
        df_preselected["Ceiling_height"].astype(str).str.replace(" m", "")
    )
    df_preselected["Built-up_area"] = (
        df_preselected["Built-up_area"].astype(str).str.replace("m2", "")
    )

    # Annuity
    df_preselected["Annuity"] = (
        df_preselected["Annuity"].astype(str).str.replace(" Kc", "")
    )

    ### Convert to float
    astype_inplace(df_preselected, {"Price": float})
    astype_inplace(df_preselected, {"Floor": int})
    astype_inplace(df_preselected, {"Floor_Total": float})
    astype_inplace(df_preselected, {"Floor_Underground": float})
    astype_inplace(df_preselected, {"Usable_area": float})
    astype_inplace(df_preselected, {"Floorage": float})
    astype_inplace(df_preselected, {"Balcony": float})
    astype_inplace(df_preselected, {"Cellar": float})
    astype_inplace(df_preselected, {"Terrace": float})
    astype_inplace(df_preselected, {"Garage": float})
    astype_inplace(df_preselected, {"Parking": float})
    astype_inplace(df_preselected, {"Loggia": float})
    astype_inplace(df_preselected, {"Candy shop": float})
    astype_inplace(df_preselected, {"Movies": float})
    astype_inplace(df_preselected, {"Playground": float})
    astype_inplace(df_preselected, {"Small shop": float})
    astype_inplace(df_preselected, {"Pub": float})
    astype_inplace(df_preselected, {"Theater": float})
    astype_inplace(df_preselected, {"Vet office": float})
    astype_inplace(df_preselected, {"Tram": float})
    astype_inplace(df_preselected, {"Restaurant": float})
    astype_inplace(df_preselected, {"Shop": float})
    astype_inplace(df_preselected, {"Post Office": float})
    astype_inplace(df_preselected, {"School": float})
    astype_inplace(df_preselected, {"Drugstore": float})
    astype_inplace(df_preselected, {"Bus Public Transport": float})
    astype_inplace(df_preselected, {"ATM": float})
    astype_inplace(df_preselected, {"Metro": float})
    astype_inplace(df_preselected, {"Medic": float})
    astype_inplace(df_preselected, {"Sports": float})
    astype_inplace(df_preselected, {"Kindergarten": float})
    astype_inplace(df_preselected, {"Train": float})
    astype_inplace(df_preselected, {"Natural attraction": float})
    astype_inplace(df_preselected, {"Annuity": float})
    astype_inplace(df_preselected, {"Garden_area": float})
    astype_inplace(df_preselected, {"Ceiling_height": float})
    astype_inplace(df_preselected, {"Built-up_area": float})

    # Convert to Date
    df_preselected["Reconstruction_year"] = pd.to_datetime(
        df["Reconstruction_year"]
    ).dt.date
    df_preselected["Reload_Date"] = pd.to_datetime(df["Reload_Date_Time"]).dt.date
    df_preselected["Reload_Time"] = pd.to_datetime(df["Reload_Date_Time"]).dt.time

    # Replace all NaN values by 0
    df_preselected = df_preselected.fillna(0)

    return df_preselected


# Configuration
def prepare_column_names_and_aggr_functions():
    """
    This is the configuration function for the Dashboard. You can use it, but dont have to.
    It is also possible to prepare all the variables outside of the function.
    List of variable has to remain the same.
    Each variable contain a subset of column/columns from the DataFrame.
    This way we can specify which columns go to which axis on charts.
    Additionaly you specify which column contains:
        ID
        Link
        Reload Date
        Image
    More additionaly, we specify aggregation functions to be used on Y Columns (Numerical)

    Rearrange columns names as needed. Or can use everything, so just store original df in each variable, like this:
        x_columns = property_data_dataframe_cleaned.columns

    Be careful that i some cases variable is expected to be a string with only one column, not a list.

    To display all columns on its own line, in '' and with comma, can use this loop:
        for i in property_data_dataframe_cleaned.columns:
            print(f"'{i}',")
    """
    x_columns = [
        "Property_Type",
        "Administrative_District",
        "Municipal_District",
        "Building",
        "Property_status",
        "Furnished",
        "Reconstruction_year",
        "Energy_Efficiency_Rating",
        "Flat_type",
        "Floor",
        "Floor_Total",
        "Floorage",
        "Balcony",
        "Cellar",
        "Garden_area",
        "Terrace",
        "Garage",
        "Parking",
        "Loggia",
        "Metro",
        "Tram",
        "Bus Public Transport",
        "Train",
        "Natural attraction",
        "Medic",
        "Playground",
        "Kindergarten",
        "School",
    ]

    # Columns of the Numerical X Variables of the Property
    y_columns = [
        "Price",
        "Balcony",
        "Cellar",
        "Garden_area",
        "Terrace",
        "Garage",
        "Parking",
        "Loggia",
        "Metro",
        "Tram",
        "Bus Public Transport",
        "Train",
        "Natural attraction",
        "Medic",
        "Playground",
        "Kindergarten",
        "School",
        "Floor",
        "Floor_Total",
        "Floorage",
        "Annuity",
    ]

    # Columns of the Numerical X Variables of the Distances from Property
    table_columns = [
        "Price",
        "Property_Type",
        "Administrative_District",
        "Municipal_District",
        "Building",
        "Property_status",
        "Furnished",
        "Reconstruction_year",
        "Energy_Efficiency_Rating",
        "Flat_type",
        "Floor",
        "Floor_Total",
        "Floorage",
        "Balcony",
        "Cellar",
        "Garden_area",
        "Terrace",
        "Garage",
        "Parking",
        "Loggia",
        "Metro",
        "Tram",
        "Bus Public Transport",
        "Train",
        "Natural attraction",
        "Medic",
        "Playground",
        "Kindergarten",
        "School",
        "Ownership",
        "Property_location",
        "Water",
        "Heating",
        "Waste",
        "Electricity",
        "Barrier-free_access",
        "Elevator",
        "Gas",
        "Loft",
        "Ceiling_height",
        "Status",
        "Usable_area",
        "Floorage",
        "Built-up_area",
        "Candy shop",
        "Movies",
        "Playground",
        "Small shop",
        "Pub",
        "Theater",
        "Vet office",
        "Restaurant",
        "Shop",
        "Post Office",
        "Drugstore",
        "ATM",
        "Sports",
        "Annuity",
        "Move-in_date",
        "Acquisition_of_title",
        "Property_Link",
        "Advertising_Type",
        "Address",
    ]

    # Link to return on click, dont use  [],
    # put something else, if there is no link in the data, doesnt metter what, otherwise chart wont work.
    link_column = "Property_Link"  # Link to return on click, dont use  []

    corr_columns = y_columns

    pca_color_columns = x_columns

    pca_features = y_columns

    reload_date_column = "Reload_Date"

    id_column = "Order_ID"

    image_column = "Image"

    aggr_functions = ["avg", "sum", "count", "min", "max"]

    return (
        x_columns,
        y_columns,
        table_columns,
        corr_columns,
        link_column,
        pca_color_columns,
        pca_features,
        reload_date_column,
        id_column,
        image_column,
        aggr_functions,
    )


def dashboard(
    df,
    initial_image,
    dash_title,
    dash_subtitle_1,
    dash_subtitle_2,
    x_columns,
    y_columns,
    table_columns,
    link_column,
    corr_columns,
    pca_color_columns,
    pca_features,
    reload_date_column,
    id_column,
    image_column,
    aggr_functions,
    footer_text,
):
    """
    Function will prepare the Dashboard itself.
    It Returns the Dash (or JupyterDash) object that can be started to startup the server.
    The App is then accessed in the web browser.
    """

    ##################################################################################
    ##################################### SETUP  #####################################
    ##################################################################################

    # Correlogram
    corr = df[corr_columns].corr().round(2)
    corr_sub_selection = math.floor(len(corr.columns) / 2)

    # Subset of Features
    pca_features_sub_selection = math.floor(len(pca_features) / 1)

    # for PCA
    df_pca = df[pca_features]

    # for Image
    image_filename = initial_image
    try:
        encoded_image = base64.b64encode(open(image_filename, "rb").read()).decode(
            "ascii"
        )
    except FileNotFoundError:
        encoded_image = ""

    # app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    app = JupyterDash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        # For Mobile
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
        ],
    )

    ##################################################################################
    ##################################### CARDS ######################################
    ##################################################################################

    # TITLE
    title = dbc.Card(
        dbc.CardBody(
            [
                html.H2(
                    id="title",
                    className="card-text",
                    children=dash_title,
                    style={"textAlign": "center", "font-family": "Helvetica"},
                ),
            ]
        ),
        color="primary",
        style={"text-align": "center", "margin-top": "10px"},
        inverse=True,
    )

    # SUBTITLE 1
    subtitle_1 = dbc.Card(
        dbc.CardBody(
            [
                html.H3(
                    id="subtitle_1",
                    className="card-text",
                    children=dash_subtitle_1,
                    style={"textAlign": "center", "font-family": "Helvetica"},
                ),
            ]
        ),
        color="secondary",
        style={"text-align": "center"},
        inverse=True,
    )

    # SUBTITLE 1
    subtitle_2 = dbc.Card(
        dbc.CardBody(
            [
                html.H3(
                    id="subtitle_2",
                    className="card-text",
                    children=dash_subtitle_2,
                    style={
                        "textAlign": "center",
                        "font-family": "Helvetica",
                        "margin-bottom": "-10px",
                        "margin-top": "-10px",
                    },
                ),
            ]
        ),
        color="secondary",
        style={"text-align": "center"},
        inverse=True,
    )

    # UPPER CARDs
    upper_cards = dbc.CardDeck(
        [
            dbc.Card(
                [
                    dbc.CardHeader(
                        id="upper_card_6_header",
                        style={
                            "text-align": "center",
                            "color": "#FFFFFF",
                            "background": "#0DA550",
                            "height": "5vh",
                            "display": "flex",
                            "justify-content": "center",
                            "align-items": "center",
                            "font-size": "large",
                        },
                    ),
                    dbc.CardBody(
                        [
                            html.H3(
                                id="upper_card_6_text",
                                className="card-text",
                                style={
                                    "text-align": "center",
                                    "color": "#1E1E1E",
                                    "background": "#F8F9FA",
                                },
                            )
                        ]
                    ),
                ],
                color="light",
                style={"text-align": "center"},
            ),
            dbc.Card(
                [
                    dbc.CardHeader(
                        id="upper_card_1_header",
                        style={
                            "text-align": "center",
                            "color": "#FFFFFF",
                            "background": "#0DA550",
                            "height": "5vh",
                            "display": "flex",
                            "justify-content": "center",
                            "align-items": "center",
                            "font-size": "large",
                        },
                    ),
                    dbc.CardBody(
                        [
                            html.H3(
                                id="upper_card_1_text",
                                className="card-text",
                                style={
                                    "text-align": "center",
                                    "color": "#1E1E1E",
                                    "background": "#F8F9FA",
                                },
                            )
                        ]
                    ),
                ],
                color="light",
                style={"text-align": "center"},
            ),
            dbc.Card(
                [
                    dbc.CardHeader(
                        id="upper_card_2_header",
                        style={
                            "text-align": "center",
                            "color": "#FFFFFF",
                            "background": "#0DA550",
                            "height": "5vh",
                            "display": "flex",
                            "justify-content": "center",
                            "align-items": "center",
                            "font-size": "large",
                        },
                    ),
                    dbc.CardBody(
                        [
                            html.H3(
                                id="upper_card_2_text",
                                className="card-text",
                                style={
                                    "text-align": "center",
                                    "color": "#1E1E1E",
                                    "background": "#F8F9FA",
                                },
                            )
                        ]
                    ),
                ],
                color="light",
                style={"text-align": "center"},
            ),
            dbc.Card(
                [
                    dbc.CardHeader(
                        id="upper_card_3_header",
                        style={
                            "text-align": "center",
                            "color": "#FFFFFF",
                            "background": "#0DA550",
                            "height": "5vh",
                            "display": "flex",
                            "justify-content": "center",
                            "align-items": "center",
                            "font-size": "large",
                        },
                    ),
                    dbc.CardBody(
                        [
                            html.H3(
                                id="upper_card_3_text",
                                className="card-text",
                                style={
                                    "text-align": "center",
                                    "color": "#1E1E1E",
                                    "background": "#F8F9FA",
                                },
                            )
                        ]
                    ),
                ],
                color="light",
                style={"text-align": "center"},
            ),
            dbc.Card(
                [
                    dbc.CardHeader(
                        id="upper_card_4_header",
                        style={
                            "text-align": "center",
                            "color": "#FFFFFF",
                            "background": "#0DA550",
                            "height": "5vh",
                            "display": "flex",
                            "justify-content": "center",
                            "align-items": "center",
                            "font-size": "large",
                        },
                    ),
                    dbc.CardBody(
                        [
                            html.H3(
                                id="upper_card_4_text",
                                className="card-text",
                                style={
                                    "text-align": "center",
                                    "color": "#1E1E1E",
                                    "background": "#F8F9FA",
                                },
                            )
                        ]
                    ),
                ],
                color="light",
                style={"text-align": "center"},
            ),
            dbc.Card(
                [
                    dbc.CardHeader(
                        id="upper_card_5_header",
                        style={
                            "text-align": "center",
                            "color": "#FFFFFF",
                            "background": "#0DA550",
                            "height": "5vh",
                            "display": "flex",
                            "justify-content": "center",
                            "align-items": "center",
                            "font-size": "large",
                        },
                    ),
                    dbc.CardBody(
                        [
                            html.H3(
                                id="upper_card_5_text",
                                className="card-text",
                                style={
                                    "text-align": "center",
                                    "color": "#1E1E1E",
                                    "background": "#F8F9FA",
                                },
                            )
                        ]
                    ),
                ],
                color="light",
                style={"text-align": "center"},
            ),
        ]
    )

    # IMAGEs
    card_image = dbc.Card(
        [
            html.Img(
                id="property_image",
                # src="https://i.ibb.co/hdkDtKz/1324224673-1.png",
                src="data:image/png;base64,{}".format(encoded_image),
                title="Image",
                alt="",
                style={"width": "100%", "height": "30vh", "object-fit": "scale-down"},
            ),
            dbc.Button(
                id="open_link",
                children="Open",
                href="/",
                target="blank",
                color="primary",
                block=True,
            ),
        ],
        color="light",  # https://bootswatch.com/default/ - more card colors
        outline=False,  # True to remove the block colors from the background and header
    )

    # CHOICEs
    card_choice_1 = (
        dbc.Card(
            [
                dbc.Label("Choose X"),
                dbc.RadioItems(
                    id="card_choice_1",
                    options=[
                        {"label": i.replace("_", " "), "value": i}
                        for i in df[x_columns]
                    ],
                    value=x_columns[0],
                    style={"color": "#000000"},
                    labelStyle={
                        "color": "#000000",
                        "vertical-align": "middle",
                        "margin-left": "5px",
                        "margin-top": "-3px",
                        "margin-right": "10px",
                        "display": "block",
                    },
                    inline=False,
                ),
            ],
            body=True,
            color="light",
        ),
    )

    card_choice_2 = (
        dbc.Card(
            [
                dbc.Label("Choose Y"),
                dbc.RadioItems(
                    id="card_choice_2",
                    options=[
                        {"label": i.replace("_", " "), "value": i}
                        for i in df[y_columns]
                    ],
                    value=y_columns[0],
                    style={"color": "#000000"},
                    labelStyle={
                        "color": "#000000",
                        "vertical-align": "middle",
                        "margin-left": "5px",
                        "margin-top": "-3px",
                        "margin-right": "10px",
                        "display": "block",
                    },
                    inline=False,
                ),
            ],
            body=True,
            color="light",
        ),
    )

    card_choice_3 = dbc.Card(
        [
            dbc.Label("Choose Aggregation Function"),
            dbc.RadioItems(
                id="card_choice_3",
                options=[
                    {"label": i.replace("_", " "), "value": i} for i in aggr_functions
                ],
                value=aggr_functions[0],
                labelStyle={
                    "color": "#000000",
                    "vertical-align": "middle",
                    "margin-left": "5px",
                    "margin-top": "-3px",
                    "margin-right": "10px",
                    "display": "block",
                },
                inline=False,
            ),
        ],
        body=True,
        color="light",
    )

    # Scatter PLOTS + Image
    card_graph_1 = dbc.Card(
        dcc.Graph(id="card_graph_1", figure={}, style={"height": "30vh"}),
        body=True,
        color="light",
    )

    # TABLEs
    table = DataTable(
        id="datatable-interactivity",
        columns=[
            {"name": i, "id": i, "deletable": True, "selectable": True}
            for i in df[table_columns]
        ],
        data=df.to_dict("records"),
        # editable=True,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        # column_selectable="single",
        # row_selectable="multi",
        # row_deletable=True,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=10,  # rows per page
        style_table={"overflowX": "auto"},  # make it scrollable to the side
        ### Tooltip on hover
        tooltip_header={
            i: i for i in df[table_columns]
        },  # Adding tooltips when hovering over the header
        tooltip_delay=0,
        tooltip_duration=None,
    )

    # Histogram
    card_graph_2 = dbc.Card(
        dcc.Graph(id="card_graph_2", figure={}, style={"height": "50vh"}),
        body=True,
        color="light",
    )

    # Checklist + Correlation Matrix
    card_choice_4 = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.P(
                                dbc.Checklist(
                                    id="card_choice_4",
                                    options=[
                                        {"label": i, "value": i} for i in corr.columns
                                    ],
                                    value=corr.columns[0:corr_sub_selection],
                                    labelStyle={"display": "inline-block"},
                                    inline=True,
                                    style={"height": "5vh"},
                                ),
                            ),
                            html.P(
                                dcc.Graph(
                                    id="card_graph_3",
                                    figure={},
                                    style={"height": "40vh"},
                                )
                            ),
                        ]
                    ),
                ]
            ),
        ],
        body=True,
        color="light",
    )

    # Checklists + Scatter, Size and Color
    card_choice_5_6 = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.P(
                                # Size
                                # dbc.Label("Choose Size"),
                                dbc.RadioItems(
                                    id="card_choice_9",
                                    options=[
                                        {"label": "With Size", "value": "With Size"},
                                        {
                                            "label": "Without Size",
                                            "value": "Without Size",
                                        },
                                    ],
                                    value="With Size",
                                    labelStyle={"display": "inline-block"},
                                    inline=True
                                    # style={'height':'2vh'}
                                ),
                            ),
                            html.P(
                                dbc.RadioItems(
                                    id="card_choice_5",
                                    options=[
                                        {"label": i, "value": i} for i in df[y_columns]
                                    ],
                                    value=df[y_columns].columns[1],
                                    labelStyle={"display": "inline-block"},
                                    inline=True,
                                    style={"margin-top": "-10px"},
                                ),
                            ),
                        ],
                        style={"display": "block"},
                    ),
                    # Color
                    html.Div(
                        [
                            html.P(
                                dbc.RadioItems(
                                    id="card_choice_10",
                                    options=[
                                        {"label": "With Color", "value": "With Color"},
                                        {
                                            "label": "Without Color",
                                            "value": "Without Color",
                                        },
                                    ],
                                    value="With Color",
                                    labelStyle={"display": "inline-block"},
                                    inline=True,
                                ),
                            ),
                            html.P(
                                dbc.RadioItems(
                                    id="card_choice_6",
                                    options=[
                                        {"label": i, "value": i} for i in df[x_columns]
                                    ],
                                    value=df[x_columns].columns[1],
                                    labelStyle={"display": "inline-block"},
                                    inline=True,
                                    style={"margin-top": "-10px"},
                                ),
                            ),
                        ],
                        style={"display": "block"},
                    ),
                    html.Div(
                        dcc.Graph(id="card_graph_4", figure={}),
                    ),
                ]  # , style={'height':'40vh'}
            ),
        ]
    )

    # Checklists + PCA
    card_choice_7_8 = dbc.Card(
        [
            dbc.CardBody(
                [
                    # Features (Numerical)
                    html.Div(
                        [
                            html.P(
                                dbc.Label("Choose Features"),
                            ),
                            html.P(
                                dbc.Checklist(
                                    id="card_choice_7",
                                    options=[
                                        {"label": i, "value": i} for i in df_pca.columns
                                    ],
                                    value=df_pca.columns[
                                        0:pca_features_sub_selection
                                    ].tolist(),
                                    labelStyle={"display": "inline-block"},
                                    inline=True,
                                    style={"margin-top": "-20px"},
                                ),
                            ),
                        ],
                        style={"display": "block"},
                    ),
                    # Color (Categorical)
                    html.Div(
                        [
                            html.P(
                                dbc.Label("Choose Color"),
                            ),
                            html.P(
                                dbc.RadioItems(
                                    id="card_choice_8",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in df[pca_color_columns]
                                    ],
                                    value=df[pca_color_columns].columns[0],
                                    labelStyle={"display": "inline-block"},
                                    inline=True,
                                    style={"margin-top": "-20px"},
                                ),
                            ),
                        ],
                        style={"display": "block"},
                    ),
                    html.Div(
                        dcc.Graph(id="card_graph_5", figure={}),
                    ),
                ]  # , style={'height':'45vh'}
            ),
        ]
    )

    # FOOTER
    footer = dbc.Card(
        dbc.CardBody(
            [
                html.H6(
                    id="footer",
                    className="card-text",
                    children=footer_text,
                    style={"textAlign": "right", "font-family": "Helvetica"},
                ),
            ]
        ),
        color="dark",
        style={"text-align": "center", "margin-top": "10px"},
        inverse=True,
    )

    # # DEBUG
    # test_1 = dbc.Card(
    #     html.Div([
    #         html.Pre(id='test_1', style={'paddingTop':25})
    #     ], style={'width':'30%', 'display':'inline-block', 'verticalAlign':'top'})
    #     ,body=True, color="light",
    # )

    # DEBUG
    # test_2 = html.H1(id='test_2', style={'paddingTop':25})

    ##################################################################################
    ##################################### LAYOUT  ####################################
    ##################################################################################

    # app.layout = html.Div([
    app.layout = dbc.Container(
        [
            # Row 1
            dbc.Row(
                [
                    dbc.Col(
                        # TITLE
                        dbc.Row(
                            [dbc.Col(title, xs=12, sm=12, md=12, lg=12, xl=12)],
                            justify="center",
                            style={"margin-bottom": "5px"},
                        ),  # justify="start", "center", "end", "between", "around"
                        xs=12,
                        sm=12,
                        md=12,
                        lg=12,
                        xl=12,
                        style={"height": "100%"},
                    )
                ],
                justify="start",
                form=True,
                style={"margin-bottom": "5px"},
            ),
            # Row 2
            dbc.Row(
                [
                    # Col 1
                    dbc.Col(
                        [
                            (
                                # card_choice_1
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            card_choice_1,
                                            xs=12,
                                            sm=12,
                                            md=12,
                                            lg=12,
                                            xl=12,
                                        )
                                    ],
                                    justify="center",
                                    style={"margin-bottom": "5px"},
                                    form=True,
                                )  # justify="start", "center", "end", "between", "around"
                            ),
                            (
                                # card_choice_2
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            card_choice_2,
                                            xs=12,
                                            sm=12,
                                            md=12,
                                            lg=12,
                                            xl=12,
                                            style={"height": "100%"},
                                        )
                                    ],
                                    justify="center",
                                    style={"margin-bottom": "5px"},
                                    form=True,
                                )  # justify="start", "center", "end", "between", "around"
                            ),
                            (
                                # card_choice_3
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            card_choice_3,
                                            xs=12,
                                            sm=12,
                                            md=12,
                                            lg=12,
                                            xl=12,
                                            style={"height": "100%"},
                                        )
                                    ],
                                    justify="center",
                                    style={"margin-bottom": "5px"},
                                    form=True,
                                )  # justify="start", "center", "end", "between", "around"
                            ),
                        ],
                        xs=1,
                        sm=1,
                        md=1,
                        lg=1,
                        xl=1,
                        style={"height": "100%"},
                    ),
                    # Col 2
                    dbc.Col(
                        [
                            (
                                # Subtitle 1
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            subtitle_1,
                                            xs=12,
                                            sm=12,
                                            md=12,
                                            lg=12,
                                            xl=12,
                                            style={"height": "100%"},
                                        )
                                    ],
                                    justify="center",
                                    style={"margin-bottom": "5px"},
                                    form=True,
                                )
                            ),
                            (
                                # Upper Cards
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            upper_cards,
                                            xs=12,
                                            sm=12,
                                            md=12,
                                            lg=11,
                                            xl=11,
                                            style={"height": "100%"},
                                        )
                                    ],
                                    justify="center",
                                    style={"margin-bottom": "5px"},
                                    form=True,
                                )
                            ),
                            (
                                # Graph / Image / Link
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            card_graph_1,
                                            xs=12,
                                            sm=12,
                                            md=12,
                                            lg=6,
                                            xl=6,
                                            style={"height": "100%"},
                                        ),
                                        dbc.Col(
                                            card_image,
                                            xs=12,
                                            sm=12,
                                            md=12,
                                            lg=6,
                                            xl=6,
                                            style={"height": "100%"},
                                        ),
                                    ],
                                    justify="center",
                                    style={
                                        "margin-bottom": "5px",
                                        "margin-right": "5px",
                                    },
                                    form=True,
                                )
                            ),
                            (
                                # Table
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            table,
                                            xs=12,
                                            sm=12,
                                            md=12,
                                            lg=12,
                                            xl=12,
                                            style={"height": "100%"},
                                        )
                                    ],
                                    justify="center",
                                    style={"margin-bottom": "0px"},
                                    form=True,
                                )
                            ),
                            (
                                # Subtitle 2
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            subtitle_2,
                                            xs=12,
                                            sm=12,
                                            md=12,
                                            lg=12,
                                            xl=12,
                                            style={"height": "100%"},
                                        )
                                    ],
                                    justify="center",
                                    style={"margin-bottom": "5px"},
                                    form=True,
                                )
                            ),
                            (
                                # Graphs
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            card_graph_2,
                                            xs=12,
                                            sm=12,
                                            md=12,
                                            lg=6,
                                            xl=6,
                                            style={"height": "100%"},
                                        ),
                                        dbc.Col(
                                            card_choice_4,
                                            xs=12,
                                            sm=12,
                                            md=12,
                                            lg=6,
                                            xl=6,
                                            style={"height": "100%"},
                                        ),
                                    ],
                                    justify="center",
                                    style={"margin-bottom": "5px"},
                                    form=True,
                                )
                            ),
                            (
                                # Graphs
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            card_choice_5_6,
                                            xs=12,
                                            sm=12,
                                            md=12,
                                            lg=6,
                                            xl=6,
                                            style={"height": "100%"},
                                        ),
                                        dbc.Col(
                                            card_choice_7_8,
                                            xs=12,
                                            sm=12,
                                            md=12,
                                            lg=6,
                                            xl=6,
                                            style={"height": "100%"},
                                        ),
                                    ],
                                    justify="center",
                                    style={"margin-bottom": "0px"},
                                    form=True,
                                )
                            ),
                        ],
                        xs=11,
                        sm=11,
                        md=11,
                        lg=11,
                        xl=11,
                        style={"height": "100%"},
                    ),
                ],
                justify="start",
                form=True,
                style={"margin-bottom": "0px"},
            ),
            # Row 3
            dbc.Row(
                [
                    dbc.Col(
                        # FOOTER
                        dbc.Row(
                            [dbc.Col(footer, xs=12, sm=12, md=12, lg=12, xl=12)],
                            justify="end",
                            style={"margin-bottom": "5px"},
                        ),  # justify="start", "center", "end", "between", "around"
                        xs=12,
                        sm=12,
                        md=12,
                        lg=12,
                        xl=12,
                        style={"height": "100%"},
                    )
                ],
                justify="end",
                form=True,
                style={"margin-bottom": "5px"},
            ),
        ],
        style={"height": "100vh"},
        fluid=True,
    )

    ##################################################################################
    ##################################### CALLBACKS ##################################
    ##################################################################################

    ### Upper Card 1 ###
    # Text
    @app.callback(
        Output("upper_card_1_header", "children"), Input("card_choice_1", "value")
    )
    def upper_card_1_header(card_choice_1):
        return f"Number of Records"

    # Number
    @app.callback(
        Output("upper_card_1_text", "children"),
        Input("datatable-interactivity", "derived_virtual_data"),
        Input("datatable-interactivity", "derived_virtual_selected_rows"),
    )
    def upper_card_1_text_count(rows, derived_virtual_selected_rows):
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        dff = df if rows is None else pd.DataFrame(rows)

        info = len(dff.index)
        info_formatted = "{:,}".format(info).replace(",", " ")

        return info_formatted

    ### Upper Card 2 ###
    # Text
    @app.callback(
        Output("upper_card_2_header", "children"), Input("card_choice_2", "value")
    )
    def upper_card_2_header(card_choice_2):
        return f"Average of {card_choice_2}"

    # Number
    @app.callback(
        Output("upper_card_2_text", "children"),
        Input("datatable-interactivity", "derived_virtual_data"),
        Input("datatable-interactivity", "derived_virtual_selected_rows"),
        Input("card_choice_2", "value"),
    )
    def upper_card_2_text(rows, derived_virtual_selected_rows, card_choice_2):
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        dff = df if rows is None else pd.DataFrame(rows)

        info = dff[card_choice_2].mean().round(1)
        info_formatted = "{:,}".format(info).replace(",", " ")

        return info_formatted

    ### Upper Card 3 ###
    # Text
    @app.callback(
        Output("upper_card_3_header", "children"), Input("card_choice_2", "value")
    )
    def upper_card_3_header(card_choice_2):
        return f"Sum of {card_choice_2}"

    # Number
    @app.callback(
        Output("upper_card_3_text", "children"),
        Input("datatable-interactivity", "derived_virtual_data"),
        Input("datatable-interactivity", "derived_virtual_selected_rows"),
        Input("card_choice_2", "value"),
    )
    def upper_card_3_text(rows, derived_virtual_selected_rows, card_choice_2):
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        dff = df if rows is None else pd.DataFrame(rows)

        info = dff[card_choice_2].sum().round(1)
        info_formatted = "{:,}".format(info).replace(",", " ")

        return info_formatted

    ### Upper Card 4 ###
    # Text
    @app.callback(
        Output("upper_card_4_header", "children"), Input("card_choice_2", "value")
    )
    def upper_card_4_header(card_choice_2):
        return f"Min of {card_choice_2}"

    # Number
    @app.callback(
        Output("upper_card_4_text", "children"),
        Input("datatable-interactivity", "derived_virtual_data"),
        Input("datatable-interactivity", "derived_virtual_selected_rows"),
        Input("card_choice_2", "value"),
    )
    def upper_card_4_text(rows, derived_virtual_selected_rows, card_choice_2):
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        dff = df if rows is None else pd.DataFrame(rows)

        info = dff[card_choice_2].min().round(1)
        info_formatted = "{:,}".format(info).replace(",", " ")

        return info_formatted

    ### Upper Card 5 ###
    # Text
    @app.callback(
        Output("upper_card_5_header", "children"), Input("card_choice_2", "value")
    )
    def upper_card_5_header(card_choice_2):
        return f"Max of {card_choice_2}"

    # Number
    @app.callback(
        Output("upper_card_5_text", "children"),
        Input("datatable-interactivity", "derived_virtual_data"),
        Input("datatable-interactivity", "derived_virtual_selected_rows"),
        Input("card_choice_2", "value"),
    )
    def upper_card_5_text(rows, derived_virtual_selected_rows, card_choice_2):
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        dff = df if rows is None else pd.DataFrame(rows)

        info = dff[card_choice_2].max().round(1)
        info_formatted = "{:,}".format(info).replace(",", " ")

        return info_formatted

    ### Upper Card 6 ###
    # Text
    @app.callback(
        Output("upper_card_6_header", "children"), Input("card_choice_1", "value")
    )
    def upper_card_1_header(card_choice_1):
        return f"Reload Date"

    # Number
    @app.callback(
        Output("upper_card_6_text", "children"),
        Input("datatable-interactivity", "derived_virtual_data"),
        Input("datatable-interactivity", "derived_virtual_selected_rows"),
    )
    def upper_card_1_text_count(rows, derived_virtual_selected_rows):
        try:
            date = df[reload_date_column].max()
        except KeyError:
            date = ""

        return date

    ### Image ###
    @app.callback(
        Output("property_image", "src"),
        Input("datatable-interactivity", "derived_virtual_data"),
        Input("datatable-interactivity", "derived_virtual_selected_rows"),
        Input("card_graph_1", "clickData"),
    )
    def callback_image(rows, derived_virtual_selected_rows, clickData):
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        dff = df if rows is None else pd.DataFrame(rows)

        # return json.dumps(clickData, indent=2)
        prop_link = clickData["points"][0]["customdata"][0]
        img = dff[dff[link_column] == prop_link][image_column]
        return img

    ### Link ###
    @app.callback(Output("open_link", "href"), [Input("card_graph_1", "clickData")])
    def callback_link(clickData):
        prop_link = clickData["points"][0]["customdata"][0]
        if prop_link is None:
            return ""
        else:
            return prop_link

    ### Table ###
    @app.callback(
        Output("datatable-interactivity", "style_data_conditional"),
        Input("datatable-interactivity", "selected_columns"),
    )
    def update_styles(selected_columns):
        return [
            {"if": {"column_id": i}, "background_color": "#D2F3FF"}
            for i in selected_columns
        ]

    ### Chart 1 ###
    @app.callback(
        Output("card_graph_1", "figure"),
        Input("datatable-interactivity", "derived_virtual_data"),
        Input("datatable-interactivity", "derived_virtual_selected_rows"),
        Input("card_choice_1", "value"),
        Input("card_choice_2", "value"),
    )
    def update_chart_1(
        rows, derived_virtual_selected_rows, card_choice_1, card_choice_2
    ):
        card_choice_1_presentation = card_choice_1.replace("_", " ")
        card_choice_2_presentation = card_choice_2.replace("_", " ")

        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        dff = df if rows is None else pd.DataFrame(rows)

        fig = px.strip(
            dff,
            x=card_choice_1,
            y=card_choice_2,
            custom_data=[link_column],
            hover_data=[card_choice_2],
            title=(f"{card_choice_2_presentation} by {card_choice_1_presentation}"),
            labels={
                card_choice_1: card_choice_1_presentation,
                card_choice_2: card_choice_2_presentation,
            },
        )
        fig.layout.plot_bgcolor = "#FFFFFF"
        fig.layout.paper_bgcolor = "#FFFFFF"
        fig.update_xaxes(categoryorder="category ascending")
        return fig

    ### Chart 2 ###
    @app.callback(
        Output("card_graph_2", "figure"),
        Input("datatable-interactivity", "derived_virtual_data"),
        Input("datatable-interactivity", "derived_virtual_selected_rows"),
        Input("card_choice_1", "value"),
        Input("card_choice_2", "value"),
        Input("card_choice_3", "value"),
    )
    def update_chart_2(
        rows, derived_virtual_selected_rows, card_choice_1, card_choice_2, card_choice_3
    ):
        card_choice_1_presentation = card_choice_1.replace("_", " ")
        card_choice_2_presentation = card_choice_2.replace("_", " ")

        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        dff = df if rows is None else pd.DataFrame(rows)

        fig = px.histogram(
            dff,
            x=card_choice_1,
            y=card_choice_2,
            histfunc=card_choice_3,
            title=(
                f"{card_choice_3} of {card_choice_2_presentation} by {card_choice_1_presentation}"
            ),
            labels={
                card_choice_1: card_choice_1_presentation,
                card_choice_2: card_choice_2_presentation,
            },
        )
        fig.update_xaxes(categoryorder="category ascending")
        return fig

    ### Chart 3 ###
    @app.callback(
        Output("card_graph_3", "figure"),
        Input("datatable-interactivity", "derived_virtual_data"),
        Input("datatable-interactivity", "derived_virtual_selected_rows"),
        Input("card_choice_4", "value"),
    )
    def filter_heatmap(rows, derived_virtual_selected_rows, cols):

        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        dff = df if rows is None else pd.DataFrame(rows)

        # Correlogram
        corr = dff[corr_columns].corr().round(2)
        corr_sub_selection = math.floor(len(corr.columns) / 2)

        sub_corr = corr[cols].loc[cols]

        fig = ff.create_annotated_heatmap(
            z=sub_corr.values,
            x=sub_corr.columns.tolist(),
            y=sub_corr.columns.tolist(),
            # colorscale=col4,
            colorscale="RdBu",
            reversescale=True,
            showscale=True,
            zmin=-1,
            zmax=1,
            font_colors=["#3c3636", "#3c3636"]
            # annotation_text='Correlation Matrix'
            # title = 'Correlation Matrix'
        )

        fig.layout.plot_bgcolor = "#F8F9FA"
        fig.layout.paper_bgcolor = "#F8F9FA"

        fig["layout"]["title"] = "Correlation Matrix"
        fig["layout"]["yaxis"]["autorange"] = "reversed"
        return fig

    ### Chart 4 ###
    @app.callback(
        Output("card_graph_4", "figure"),
        Input("datatable-interactivity", "derived_virtual_data"),
        Input("datatable-interactivity", "derived_virtual_selected_rows"),
        Input("card_choice_1", "value"),
        Input("card_choice_2", "value"),
        Input("card_choice_5", "value"),
        Input("card_choice_6", "value"),
        Input("card_choice_9", "value"),
        Input("card_choice_10", "value"),
    )
    def update_chart_4(
        rows,
        derived_virtual_selected_rows,
        card_choice_1,
        card_choice_2,
        card_choice_5,
        card_choice_6,
        card_choice_9,
        card_choice_10,
    ):
        card_choice_1_presentation = card_choice_1.replace("_", " ")
        card_choice_2_presentation = card_choice_2.replace("_", " ")

        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        dff = df if rows is None else pd.DataFrame(rows)

        if card_choice_9 == "With Size":
            size_selection = card_choice_5
        else:
            size_selection = None

        if card_choice_10 == "With Color":
            color_selection = card_choice_6
        else:
            color_selection = None

        fig = px.scatter(
            dff,
            x=card_choice_1,
            y=card_choice_2,
            size=size_selection,
            color=color_selection,
            title=(f"{card_choice_2_presentation} by {card_choice_1_presentation}"),
            labels={
                card_choice_1: card_choice_1_presentation,
                card_choice_2: card_choice_2_presentation,
            },
        )

        fig.update_layout(
            xaxis=dict(categoryorder="category ascending"),
            yaxis=dict(categoryorder="category ascending"),
        )

        return fig

    ### Chart 5 ###
    @app.callback(
        Output("card_graph_5", "figure"),
        Input("datatable-interactivity", "derived_virtual_data"),
        Input("datatable-interactivity", "derived_virtual_selected_rows"),
        Input("card_choice_7", "value"),
        Input("card_choice_8", "value"),
    )
    def pca(rows, derived_virtual_selected_rows, card_choice_7, card_choice_8):

        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        dff = df if rows is None else pd.DataFrame(rows)

        df_X = dff[card_choice_7]

        # Scale
        scaler = StandardScaler()
        scaler.fit(df_X)
        scaled_data = scaler.transform(df_X)

        # Fit
        pca = PCA(n_components=2)
        components = pca.fit_transform(scaled_data)

        # Loadings
        loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

        # Graph
        fig = px.scatter(
            components,
            x=0,
            y=1,
            color=dff[card_choice_8],
            labels={
                "0": f"PC 0 ({pca.explained_variance_ratio_[0].round(4)*100}%)",
                "1": f"PC 1 ({pca.explained_variance_ratio_[1].round(4)*100}%)",
            },
            title="PCA"
            # hover_data=dff['Price']
        )

        for i, feature in enumerate(card_choice_7):
            fig.add_shape(type="line", x0=0, y0=0, x1=loadings[i, 0], y1=loadings[i, 1])
            fig.add_annotation(
                x=loadings[i, 0],
                y=loadings[i, 1],
                ax=0,
                ay=0,
                xanchor="center",
                yanchor="bottom",
                text=feature,
            )

        return fig

    ##################################################################################
    ##################################### RETURN #####################################
    ##################################################################################

    return app


if __name__ == "__main__":
    # # Load Back the Property Data (in List of Dicts)
    import pickle

    with open("property_data_list_of_dicts.pkl", "rb") as b:
        property_data_list_of_dicts = pickle.load(b)

    # Remove None values in a List - those Property that had some error in processing
    property_data_list_of_dicts_cleaned = []
    for i in property_data_list_of_dicts:
        if i != None:
            property_data_list_of_dicts_cleaned.append(i)

    # Make DataFrame
    property_data_dataframe = pd.DataFrame(property_data_list_of_dicts_cleaned)

    # Process DataFrame
    property_data_dataframe_cleaned = clean_property_df(property_data_dataframe)

    # Prepare column names for parts in the Dashboard (X variables, Y variable, Table) +
    # Prepare list of aggregation functions
    (
        x_columns,
        y_columns,
        table_columns,
        corr_columns,
        link_column,
        pca_color_columns,
        pca_features,
        reload_date_column,
        id_column,
        image_column,
        aggr_functions,
    ) = prepare_column_names_and_aggr_functions()

    # Start Dash App
    Timer(1, open_browser).start()
    my_app = dashboard(
        property_data_dataframe_cleaned,
        "no_prop_selected.png",
        "Sreality Analyzer",
        "Exploration",
        "Analysis",
        x_columns,
        y_columns,
        table_columns,
        link_column,
        corr_columns,
        pca_color_columns,
        pca_features,
        reload_date_column,
        id_column,
        image_column,
        aggr_functions,
        "Copyright. Data: https://www.sreality.cz/; Dashboard: michael.miscanuk@gmail.com",
    )
    my_app.run_server(debug=False)
    # my_app.run_server(mode='inline') # to open in the Jupyter output
