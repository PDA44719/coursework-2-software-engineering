import dash
from dash import html
from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
from dash_app.chart_creator_module import ChartCreator
import collections

cc = ChartCreator('../dash_app/prepared_dataset.xlsx')  # Generate all the charts


def init_dashboard(flask_app):
    dash_app = dash.Dash(server=flask_app,
                         routes_pathname_prefix="/dash_app/",
                         external_stylesheets=[dbc.themes.LUX],
                         )

    # Define the layout of the main page of the app
    main_page_layout = html.Div([
        html.Br(),
        html.H1(children='Film Dashboard', style={'textAlign': 'center'}),
        html.Br(),
        html.Div(id='main_page_content'),

        # This row will contain the 4 image cards
        dbc.Row([
            dbc.Col([create_graph_card('../static/assets/graph1.png',
                                       "Discover how much revenue (overall and average) each main genre made",
                                       "Which Movie Genres are more Popular?", 'graph-page-1')], width=3),
            dbc.Col([create_graph_card('../static/assets/graph2.png',
                                       "Learn about the number of films, overall and average revenue for different lengths",
                                       "What are the Most Popular Runtimes?", 'graph-page-2')], width=3),
            dbc.Col([create_graph_card('../static/assets/graph3.png',
                                       "Understand the impact that COVID-19 has had on film revenue",
                                       "How much are Top Movies Making?", 'graph-page-3')], width=3),
            dbc.Col([create_graph_card('../static/assets/graph4.png',
                                       "Find out how much money distributors made overall and on average",
                                       "How much are Distributors Making?", 'graph-page-4')], width=3),
        ]),
    ])

    # Define the layout of the graph 1 page
    graph1_layout = html.Div([
        html.H1(children='Which Movie Genres are more Popular?', style={'textAlign': 'center'}),
        html.Div(),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='dropdown1',
                    options=[{'label': 'Mean Revenue', 'value': 'type1_1'},
                             {'label': 'Overall Revenue', 'value': 'type1_2'}],
                    value='type1_1',  # Initial value of the dropdown
                    className='dropdown_list',
                    clearable=False  # Do not allow the dropdown value to be None
                ),
            ], width={"size": 6, "offset": 3})
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([html.Br()], style={'height': '25vh'}),
                create_checklist_card('chck1', [{'label': 'Show Preferred Genres', 'value': 'SPG'},
                                                {'label': 'Show Error Bars', 'value': 'SEB'}])
            ], width={"size": 2, "offset": 1}),
            dbc.Col([dcc.Graph(figure=cc.fig1, id='graph_1', style={'height': '75vh'})], width=8)
        ]),
        dbc.Row([
            dbc.Col([dbc.Button("Go back to main page", color='primary', href='main-page')],
                    width={"size": 4, "offset": 8})
        ])
    ])

    # Define the layout of the graph 2 page
    graph2_layout = html.Div([
        html.H1(children='What are the Most Popular Runtimes?', style={'textAlign': 'center'}),
        html.Div(),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='dropdown2',
                    options=[{'label': 'Overall Revenue', 'value': 'type2_1'},
                             {'label': 'Mean Revenue', 'value': 'type2_2'},
                             {'label': 'Number of Movies', 'value': 'type2_3'}],
                    value='type2_1',  # Initial value of the dropdown
                    className='dropdown_list',
                    clearable=False  # Do not allow the dropdown value to be None
                ),
            ], width={"size": 6, "offset": 3})
        ]),
        dbc.Row([
            dbc.Col([dcc.Graph(figure=cc.fig7, id='graph_2', style={'height': '75vh'})], width={"size": 8, "offset": 2})
        ]),
        dbc.Row([
            dbc.Col([dbc.Button("Go back to main page", color='primary', href='main-page')],
                    width={"size": 4, "offset": 8})
        ])
    ])

    # Define the layout of the graph 3 page
    graph3_layout = html.Div([
        html.H1(children='How much are Top Movies Making?', style={'textAlign': 'center'}),
        html.Div(),
        dbc.Row([
            dbc.Col([dcc.Graph(figure=cc.fig10, style={'height': '75vh'})], width={"size": 8, "offset": 2})
        ]),
        dbc.Row([
            dbc.Col([dbc.Button("Go back to main page", color='primary', href='main-page')],
                    width={"size": 4, "offset": 8})
        ])
    ])

    # Depending on the dropdown option selected (type4_1 or type4_2) one of the rows within the graph 4 layout will be
    # different. Hence, define both rows
    type4_1_row = dbc.Row([dbc.Col([dcc.Graph(figure=cc.fig11, style={'height': '75vh'})],
                                   width={"size": 8, "offset": 2})], id='type4_1_layout')
    type4_2_row = dbc.Row([
        dbc.Col([
            html.Div([html.Br()], style={'height': '30vh'}),
            create_checklist_card('chck4', [{'label': 'Show Error Bars', 'value': 'SEB'}])
        ], width={"size": 2, "offset": 1}),
        dbc.Col([dcc.Graph(figure=cc.fig13, id='graph_4', style={'height': '75vh'})], width=8)
    ], id='type4_2_layout')

    # Define the layout of the graph 4 page
    graph4_layout = html.Div([
        html.H1(children='How much are Distributors Making?', style={'textAlign': 'center'}),
        html.Div(),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='dropdown4',
                    options=[{'label': 'Overall Revenue', 'value': 'type4_1'},
                             {'label': 'Mean Revenue', 'value': 'type4_2'}],
                    value='type4_1',  # Initial value of the dropdown
                    className='dropdown_list',
                    clearable=False  # Do not allow the dropdown value to be None
                ),
            ], width={"size": 6, "offset": 3})
        ]),
        # This is the row that will be modified depending on the value of the dropdown
        dbc.Row(children=type4_1_row, id='modifiable_row'),
        dbc.Row([
            dbc.Col([dbc.Button("Go back to main page", color='primary', href='main-page')],
                    width={"size": 4, "offset": 8})
        ])
    ])

    # This is necessary because there are callbacks for elements that do not initially appear on the app
    dash_app.config['suppress_callback_exceptions'] = True

    # Define the layout of the app
    dash_app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content', children=[graph1_layout])
    ])

    init_callbacks(dash_app, graph1_layout, graph2_layout, graph3_layout, graph4_layout, type4_1_row, type4_2_row, main_page_layout)

    return dash_app.server


def create_graph_card(image_source, description, question, button_url):
    """
    Create a card containing an image, a description, the question that the graph is trying to address and a button to
    go to the graph page.
    This function will be used to create the cards for the main page layout.


    Arguments
    ---------
    image_source : str
        The path to the image that will be displayed on the card.
    description : str
        A short description that provides some background for the graph.
    question : str
        The question that the graph is trying to answer.
    button_url : str
        The url that the button will redirect to when being pressed.

    Returns
    -------
    dash_bootstrap_components._components.Card.Card
        The generated card.

    """
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div([
                        html.H5(question, className="card-title"),
                        dbc.CardImg(src=image_source),
                        html.P(description, className="card-text"),
                        dbc.Button("See Graph", color="primary", href=button_url),
                    ])
                ]
            ),
        ],
    )

    return card


def create_checklist_card(checklist_id, checklist_options):
    """
    Create a card that contains different checklist options for a specific graph.

    Arguments
    ---------
    checklist_id : str
        The id of the checklist that will be included on the card.
    checklist_options : list
        A list of dictionaries containing the label and values of the checklist.

    Returns
    -------
    dash_bootstrap_components._components.Card.Card
        The created card.

    """
    card = dbc.Card(className="bg-dark text-light", children=[
        dbc.CardBody([
            html.H4('Options', className="card-title"),
            html.Br(),
            dcc.Checklist(id=checklist_id, options=checklist_options)
        ])
    ])

    return card


def init_callbacks(dash_app, graph1_layout, graph2_layout, graph3_layout, graph4_layout, type4_1_row, type4_2_row, main_page_layout):
    # Define a series of callbacks to allow the user to interact with the page
    @dash_app.callback(Output('page-content', 'children'),
                  Input('url', 'pathname'))
    def navigate_pages(pathname):
        """
        Navigate through the different pages of the app.

        Arguments
        ---------
        pathname : str
            The path to the specific page in the app to be displayed.

        Returns
        -------
        dash.html.Div.Div
            The layout of the page that will be displayed.

        """
        print(pathname)
        if pathname == '/dash_app/graph-page-1':
            return graph1_layout

        if pathname == '/dash_app/graph-page-2':
            return graph2_layout

        if pathname == '/dash_app/graph-page-3':
            return graph3_layout

        if pathname == '/dash_app/graph-page-4':
            return graph4_layout

        else:
            return main_page_layout


    @dash_app.callback(Output('graph_1', 'figure'),
                  Input('dropdown1', 'value'),
                  Input('chck1', 'value'))
    def modify_graph_1(dropdown_value, selected_chart_options):
        """
        Change graph_1 depending on the dropdown1 and chck1 options selected.

        Arguments
        ---------
        dropdown_value : str
            The selected dropdown value. Available options: Mean Revenue, Overall Revenue.
        selected_chart_options : str
            The selected checklist value. Available options: Show Preferred Genres, Show Error Bars (when Mean Revenue is
            chosen) and Show Error Bars (when Overall Genre Revenue is chosen).

        Returns
        -------
        plotly.graph_objs._figure.Figure
            The figure that corresponds to the chosen dropdown1 and chck1 options.

        """
        # If selected_chart_options is None, convert to an empty list to avoid exception 'NoneType' is not iterable
        if selected_chart_options is None:
            selected_chart_options = []

        # User has chosen Overall Revenue and Show Preferred Genres is not selected
        if dropdown_value == 'type1_2' and 'SPG' not in selected_chart_options:
            return cc.fig5

        # User has chosen Overall Revenue and Show Preferred Genres
        elif dropdown_value == 'type1_2':
            return cc.fig6

        # User has chosen Mean Revenue and Show Preferred Genres
        elif dropdown_value == 'type1_1' and selected_chart_options == ['SPG']:
            return cc.fig3

        # User has chosen Mean Revenue and Show Error Bars
        elif dropdown_value == 'type1_1' and selected_chart_options == ['SEB']:
            return cc.fig4

        # User has chosen Mean Revenue, Show Error Bars and Show Preferred Genres
        elif dropdown_value == 'type1_1' and collections.Counter(selected_chart_options) == collections.Counter(
                ['SEB', 'SPG']):
            return cc.fig2

        else:  # User has chosen Mean Revenue and no additional checklist options
            return cc.fig1


    @dash_app.callback(Output('graph_2', 'figure'),
                  [Input('dropdown2', 'value')])
    def modify_graph_2(value):
        """
        Change graph 2 depending on the value selected on the dropdown bar.

        Arguments
        ---------
        value : str
            The selected value of dropdown2.

        Returns
        -------
        plotly.graph_objs._figure.Figure
            The figure that corresponds to the selected dropdown option.

        """
        if value == 'type2_1':  # User has chosen Overall Revenue
            return cc.fig7
        elif value == 'type2_2':  # User has chosen Mean Revenue
            return cc.fig8
        else:  # User has chosen Number of Movies
            return cc.fig9


    @dash_app.callback(Output('chck1', 'options'),
                  Input('dropdown1', 'value'))
    def modify_checklist_1(dropdown_value):
        """
        Modify the options of chck1 depending on the dropdown1 value.

        Arguments
        ---------
        dropdown_value : str
            The dropdown1 value selected.

        Returns
        -------
        list
            The options to be displayed on the checklist card.

        """
        if dropdown_value == 'type1_1':  # User has chosen Mean Revenue
            return [{'label': 'Show Preferred Genres', 'value': 'SPG'},
                    {'label': 'Show Error Bars', 'value': 'SEB'}]
        else:  # User has chosen Overall Revenue
            return [{'label': 'Show Preferred Genres', 'value': 'SPG'}]


    @dash_app.callback(Output('modifiable_row', 'children'),
                  Input('dropdown4', 'value'))
    def modify_graph4_layout_row(dropdown_value):
        """
        Change modifiable_row depending on the value of dropdown4 selected.

        Arguments
        ---------
        dropdown_value : str
            The value chosen on dropdown4.

        Returns
        -------
        dash_bootstrap_components._components.Row.Row
            The layout of the modifiable row inside graph4_layout.

        """
        if dropdown_value == 'type4_1':  # User has chosen Overall Revenue
            return type4_1_row
        else:  # User has chosen Mean Revenue
            return type4_2_row


    @dash_app.callback(Output('graph_4', 'figure'),
                  Input('chck4', 'value'))
    def modify_graph_4(checklist_value):
        """
        Change graph_4 depending on the selected value of chck4.

        Arguments
        ---------
        checklist_value : str
            The chosen value on chck4 (available option: show error bars).

        Returns
        -------
        plotly.graph_objs._figure.Figure
            The figure that corresponds to the selected checklist option.

        """
        if checklist_value is None or checklist_value == []:  # User has not selected the Show Error Bars option
            return cc.fig13
        else:  # User has selected the Show Error Bars option
            return cc.fig12
