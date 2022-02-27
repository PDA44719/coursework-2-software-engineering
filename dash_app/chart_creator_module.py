import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import math
import copy


class ChartCreator:
    """
    A class that creates the different figures that will be displayed on the dashboard.

    Arguments
    ---------
    dataset_path : str
        The path to the file containing the dataset (prepared_dataset.xlsx).

    Attributes
    ----------
    __df_file : str
        The dataset path introduced when creating the class.
    __df : pandas.core.frame.DataFrame
        The dataframe obtained by reading the dataset file.
    __genres_list : list
        A list containing each individual genre on __df['Genres'].
    __distributors_list : list
        A list containing each distribution company on __df['Distributor'].
    __genres_df : pandas.core.frame.DataFrame
        A dataframe containing information about each individual genre that appears on __genres_list.
    __dist_df : pandas.core.frame.DataFrame
        A dataframe containing information about each distribution company that appears on __distributors_list.
    __preferred_genres : list
        A list containing the preferred genres of the user. In this case, the preferred genres defined in persona.png
        will be utilized.
    __fig1, __fig2, __fig3, __fig4 : plotly.graph_objs._figure.Figure
        Different options for the Mean Revenue vs Genre bar chart (i.e., graph 1).
    __fig5, __fig6 : plotly.graph_objs._figure.Figure
        Different options for the Overall Revenue vs Genre bar plot (i.e., graph 1).
    __fig7, __fig8, __fig9 : plotly.graph_objs._figure.Figure
        Different options for the Runtime histograms (i.e., graph 2).
    __fig10 : plotly.graph_objs._figure.Figure
        Revenue before, during and after lockdown Area plot (i.e., graph 3).
    __fig11 : plotly.graph_objs._figure.Figure
        Revenue by distribution company Treemap (i.e., graph 4).
    __fig12, __fig13 : plotly.graph_objs._figure.Figure
        Different options for the Distribution Company vs Mean Revenue bar plot (i.e., graph 4).

    Methods
    -------
    __create_df
        Read prepared_dataset.xlsx and convert to a dataframe.
    __create_specialized_df
        Generate a dataframe containing information (overall, mean, standard deviation and standard error) about each
        element in a categorical column in __df (e.g., Genres, Distributors) with regards to different numerical
        variables (e.g., Revenue, Rating).
    --extract_sms
        Create a list containing information (overall, mean and standard deviation) about each element in a categorical
        column in __df (e.g., Genres, Distributors) with regards to different numerical variables (e.g., Revenue,
        Rating).
    __produce_color_lists
        Produce a couple of lists comprised of the colors for the bars of a bar chart. One of the lists will be
        monochromatic and the other will have a different color for the bars representing the preferred user genres.
    __create_barchart
        Create a vertical bar chart figure for a specific set of data.
    __create_horizontal_barchart
        Produce a horizontal bar chart for the Distributor vs Mean Revenue relationship.
    __add_labels
        Add the labels and any other additional options to one or more figures.
    __create_graph1_figs_mean_revenue
        Generate __fig1, __fig2, __fig3 and __fig4.
    __create_graph1_figs_overall_revenue
        Produce __fig5 and __fig6.
    __create_graph2_figs
        Create __fig7, __fig8 and __fig9.
    __create_graph3_fig
        Generate __fig10.
    __create_graph4_figs
        Create __fig11, __fig12 and __fig13.
    fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, fig11, fig12, fig13
        Getter methods to obtain the private figures.


    """

    def __init__(self, dataset_path):
        """Create an instance of the class"""
        self.__df_file = dataset_path
        self.__df = self.__create_df()

        # Get the each genre without repetition. As the Genres column contains lists, a list of lists must be converted
        # to a simple list before using set()
        self.__genres_list = list(set([genre for column_data in self.__df['Genres'] for genre in column_data]))

        # Get a list of distributors without repetition
        self.__distributors_list = list(set([element for element in self.__df['Distributor']]))

        self.__genres_df = self.__create_specialized_df('Genres', self.__genres_list, ['Revenue'])
        self.__dist_df = self.__create_specialized_df('Distributor', self.__distributors_list, ['Revenue'])
        self.__preferred_genres = ['History', 'Romance', 'Action']  # Taken from persona.png
        self.__fig1, self.__fig2, self.__fig3, self.__fig4 = self.__create_graph1_figs_mean_revenue()
        self.__fig5, self.__fig6 = self.__create_graph1_figs_overall_revenue()
        self.__fig7, self.__fig8, self.__fig9 = self.__create_graph2_figs()
        self.__fig10 = self.__create_graph3_fig()
        self.__fig11, self.__fig12, self.__fig13 = self.__create_graph4_figs()

    def __create_df(self):
        """Create a pandas dataframe containing the information from prepared_dataset.xlsx"""
        df = pd.read_excel(self.__df_file, engine='openpyxl')
        df.drop(['Unnamed: 0'], axis=1, inplace=True)  # Drop the unnamed column that is generated when reading the file
        df['Genres'] = df['Genres'].apply(eval)  # Convert the genres column to list (it is in string format initially)
        df.drop_duplicates(subset=['Film'], inplace=True)
        return df

    def __create_specialized_df(self, column, column_elements, list_of_variables):
        """
        Produce a dataframe containing information (Overall, Mean, Standard deviation and Standard error) about each
        element in a categorical column in __df (e.g., Genres, Distributors) with regards to different numerical
        variables (e.g., Revenue, Rating).

        Arguments
        ---------
        column : str
            The name of the categorical column whose information we want extracted.
        column_elements : list
            The individual categorical elements that appear in column.
        list_of_variables : list
            The names of the numerical columns we want the information (overall, mean, standard deviation and standard
            error) to be calculated about (e.g., Revenue, Rating).

        Returns
        -------
        pandas.core.frame.DataFrame
            The dataframe that was created.

        """
        info = self.__extract_sms(column, column_elements, list_of_variables)
        dataframe_columns = [column]  # Initialize the names of the columns that will appear on the dataframe

        # Include the additional column names
        for variable in list_of_variables:
            dataframe_columns.extend([variable, f'Mean {variable}', f'SD {variable}'])
        dataframe_columns.append('Number of Movies')

        specialized_df = pd.DataFrame(info, columns=dataframe_columns)  # Create the dataframe

        # Include additional columns containing the Standard Error of the variables
        # (the formula is SE = SD / sqrt(n of samples))
        for variable in list_of_variables:
            specialized_df[f'Standard Error ({variable})'] = specialized_df.apply(
                lambda x: round(x[f'SD {variable}'] / math.sqrt(x['Number of Movies']), 2), axis=1)

        return specialized_df

    def __extract_sms(self, column, column_elements, list_of_variables):
        """
        Extract information (Summation, Mean and Standard deviation) about each element in a categorical column in __df
        (e.g., Genres, Distributors) with regards to different numerical variables (e.g., Revenue, Rating). This method
        will be used inside __create_specialized_df to extract the information that will be later introduced into a
        dataframe.

        Arguments
        ---------
        column : str
            The name of the categorical column whose information we want extracted.
        column_elements : list
            The individual categorical elements that appear in column.
        list_of_variables : list
            The names of the numerical columns we want the information (overall, mean, standard deviation and standard
            error) to be calculated about (e.g., Revenue, Rating).

        Returns
        -------
        list
            A list containing the extracted information.

        """
        output_list = []
        for element in column_elements:  # Go through each element in the column
            output_list.append([element])
            for variable in list_of_variables:
                values = []  # Initialize a list containing the values of the numerical column (for each column element)

                # Go through each row and append the numerical value if element appears in the row
                for index, row in self.__df.iterrows():
                    if element in row[column]:
                        values.append(row[variable])

                output_list[-1].append(sum(values))  # Append the summation value
                output_list[-1].append(sum(values) / len(values))  # Append the mean value
                output_list[-1].append(np.std(values))  # Append the standard deviation value

            output_list[-1].append(len(values))  # Append the number of movies that contained element

        return output_list

    def __produce_color_lists(self, base_color, secondary_color):
        """
        Create a couple of lists comprised of the colors for the bars of a bar chart. One of the lists will be
        monochromatic and the other will have a different color for the bars representing the preferred user genres.

        Arguments
        ---------
        base_color : str
            A string representing the base color for the bars.
        secondary_color : str
            A string representing the color that will be used for the preferred genre bars.

        Returns
        -------
        monochromatic_list : list
            A list containing the base color for each of the bars.
        pg_highlighted : list
            A list containing the secondary colors for the preferred genres and the base colors for the rest.

        """
        monochromatic_list = [base_color] * len(self.__genres_df.index)  # Base color for each genre
        pg_highlighted = copy.copy(monochromatic_list)
        genres_list = self.__genres_df['Genres'].tolist()

        # Find the position of the bars that contain the preferred genres
        preferred_genres_pos = []
        for i in range(len(genres_list)):
            if genres_list[i] in self.__preferred_genres:
                preferred_genres_pos.append(i)

        # Change the color of the preferred genres bars to the secondary color
        for genre_pos, color in zip(preferred_genres_pos, pg_highlighted):
            pg_highlighted[genre_pos] = secondary_color

        return monochromatic_list, pg_highlighted

    @staticmethod
    def __create_barchart(data_x, data_y, bar_colors, customdata, hovertemplate, error=None):
        """
        Produce a bar chart figure for a specific set of data.

        Arguments
        ---------
        data_x : pandas.core.series.Series
            Pandas column that contains the x data.
        data_y : pandas.core.series.Series
            Pandas column that contains the y data.
        bar_colors : list
            A list containing the colors for the bars.
        customdata : numpy.ndarray
            An array containing the data that will be displayed when hovering over each bar.
        hovertemplate : str
            A string containing the format in which the information will be displayed when hovering over a bar.
        error : pandas.core.series.Series
            The pandas column that has the standard error that will be included in the chart. Default is none, which
            means no error bars will be shown.

        Returns
        -------
        plotly.graph_objs._figure.Figure
            The bar chart created with the arguments provided.

        """
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=data_x,
            y=data_y,
            customdata=customdata,
            marker_color=bar_colors,
            hovertemplate=hovertemplate,
            error_y=dict(type='data', array=error),
            name=''
        ))
        fig.update_layout(template='plotly_white')

        return fig

    def __create_horizontal_barchart(self, error=None):
        """
        Generate a horizontal bar plot to explain the Distributor vs Mean Revenue relationship.

        Arguments
        ---------
        error : pandas.core.series.Series
            The dataframe column that contains the standard error information. It is none by default, which means the
            error bars are not included.

        Returns
        -------
        plotly.graph_objs._figure.Figure
            The created figure.

        """
        fig = go.Figure(layout=go.Layout(bargap=0.3))
        fig.add_trace(go.Bar(
            y=self.__dist_df['Distributor'], x=self.__dist_df['Mean Revenue'], marker_color='lightslategray',
            error_x=dict(type='data', array=error), orientation='h'))
        fig.update_xaxes(type='log')
        fig.update_yaxes(tickfont_size=9)
        fig.update_layout(template='plotly_white')
        return fig

    @staticmethod
    def __add_labels(figures, titles, xlabels, ylabels, additional_options=None):
        """
        Add the labels and any other additional options required to one or more figures.

        Arguments
        ---------
        figures : list
            A list containing the different figures (plotly.graph_objs._figure.Figure) to be updated.
        titles : list
            The titles of each of the figures.
        xlabels : list
            The x label of each of the figures.
        ylabels : list
            The y label of each of the figures.
        additional_options : dict
            Any other additional options required by the figures. These options must be accepted by the
            figure.update_layout() method.

        """
        for i in range(len(figures)):  # Go through each of the figures
            figures[i].update_layout(
                title_text=titles[i],
                title_x=0.5,  # Center the title
                xaxis_title_text=xlabels[i],
                yaxis_title_text=ylabels[i]
            )
            figures[i].update_layout(additional_options)

    def __create_graph1_figs_mean_revenue(self):
        """
        Create the four different figures that showcase the Mean Revenue vs Genre relationship.

        Returns
        -------
        fig1 : plotly.graph_objs._figure.Figure
            Mean Revenue vs Genre bar plot (monochromatic and no error bars).
        fig2 : plotly.graph_objs._figure.Figure
            Mean Revenue vs Genre bar plot (preferred genres highlighted and error bars).
        fig3 : plotly.graph_objs._figure.Figure
            Mean Revenue vs Genre bar plot (preferred genres highlighted and no error bars).
        fig4 : plotly.graph_objs._figure.Figure
            Mean Revenue vs Genre bar plot (monochromatic and error bars).

        """
        self.__genres_df.sort_values(by=['Mean Revenue'], inplace=True)
        monochromatic_list, pg_highlighted = self.__produce_color_lists('lightslategray', 'crimson')

        # Introduce custom_df and hovertemplate (they will be used to define the hover value of the figures)
        custom_df = np.stack((self.__genres_df['Mean Revenue'], self.__genres_df['Number of Movies']), axis=-1)
        hovertemplate = 'Mean Revenue: %{customdata[0]:.0f} (USD) <br><b>Number of Movies: %{customdata[1]:.0f}'

        # Create the four different figures
        fig1 = self.__create_barchart(self.__genres_df['Genres'], self.__genres_df['Mean Revenue'],
                                      monochromatic_list, custom_df, hovertemplate)
        fig2 = self.__create_barchart(self.__genres_df['Genres'], self.__genres_df['Mean Revenue'],
                                      pg_highlighted, custom_df, hovertemplate,
                                      self.__genres_df['Standard Error (Revenue)'])
        fig3 = self.__create_barchart(self.__genres_df['Genres'], self.__genres_df['Mean Revenue'],
                                      pg_highlighted, custom_df, hovertemplate)
        fig4 = self.__create_barchart(self.__genres_df['Genres'], self.__genres_df['Mean Revenue'],
                                      monochromatic_list, custom_df, hovertemplate,
                                      self.__genres_df['Standard Error (Revenue)'])

        # Include the labels for the figures
        titles = ['Average Revenue for Movies Containing Elements of Each Main Genre'] * 4
        xlabels = [None] * 4
        ylabels = ['Revenue ($)'] * 4
        self.__add_labels([fig1, fig2, fig3, fig4], titles, xlabels, ylabels)

        return fig1, fig2, fig3, fig4

    def __create_graph1_figs_overall_revenue(self):
        """
        Create the two figures that describe the Overall Revenue vs Genre relationship.

        Returns
        -------
        fig5 : plotly.graph_objs._figure.Figure
            Overall Revenue vs Genre bar plot (monochromatic).
        fig6 : plotly.graph_objs._figure.Figure
            Overall Revenue vs Genre bar plot (preferred genres highlighted).

        """
        self.__genres_df.sort_values(by=['Revenue'], inplace=True)
        monochromatic_list, pg_highlighted = self.__produce_color_lists('lightslategray', 'crimson')

        # Introduce custom_df and hovertemplate (they will be used to define the hover value of the figures)
        custom_df = np.stack((self.__genres_df['Revenue'], self.__genres_df['Number of Movies']), axis=-1)
        hovertemplate = 'Overall Revenue: %{customdata[0]:.0f} (USD) <br><b>Number of Movies: %{customdata[1]:.0f}'

        # Create both figures
        fig5 = self.__create_barchart(self.__genres_df['Genres'], self.__genres_df['Revenue'],
                                      monochromatic_list, custom_df, hovertemplate)
        fig6 = self.__create_barchart(self.__genres_df['Genres'], self.__genres_df['Revenue'],
                                      pg_highlighted, custom_df, hovertemplate)

        # Include the labels for the figures
        titles = ['Overall Revenue for Movies Containing Elements of Each Main Genre'] * 2
        xlabels = [None] * 2
        ylabels = ['Revenue ($)'] * 2
        self.__add_labels([fig5, fig6], titles, xlabels, ylabels)

        return fig5, fig6

    def __create_graph2_figs(self):
        """
        Create the four figures that display the information about runtime.

        Returns
        -------
        fig7 : plotly.graph_objs._figure.Figure
            Overall Revenue vs Runtime histogram.
        fig8 : plotly.graph_objs._figure.Figure
            Average Revenue vs Runtime histogram.
        fig9 : plotly.graph_objs._figure.Figure
            Count vs Runtime Histogram.

        """
        # Create the figures
        fig7 = px.histogram(self.__df, x='Runtime', y='Revenue', log_y=True, nbins=8,
                            color_discrete_sequence=['lightslategray'], template='plotly_white')
        fig8 = px.histogram(self.__df, x='Runtime', y='Revenue', histfunc='avg', log_y=True, nbins=8,
                            color_discrete_sequence=['lightslategray'], template='plotly_white')
        fig9 = px.histogram(self.__df, x='Runtime', nbins=8, color_discrete_sequence=['lightslategray'],
                            template='plotly_white')

        # Include the labels. Spacing between the bars has been included
        titles = ['Overall Revenue per Runtime', 'Mean Revenue per Runtime', 'Movies per Runtime']
        xlabels = ['Runtime (minutes)'] * 3
        ylabels = ['Revenue ($)', 'Revenue ($)', 'Number of Movies']
        self.__add_labels([fig7, fig8, fig9], titles, xlabels, ylabels, {'bargap': 0.02})

        return fig7, fig8, fig9

    def __create_graph3_fig(self):
        """Produce the Revenue vs Date Area plot figure"""

        # Get each date in the Release Date column of self.__df
        dates = []
        for index, row in self.__df.iterrows():
            if row['Release Date'] not in dates:  # If the date has not already been included
                dates.append(row['Release Date'])

        # Get the summation of revenues of movies that came out on each date in dates
        revenue = []
        for date in dates:
            revenue.append(sum([row['Revenue'] for index, row in self.__df.iterrows() if date == row['Release Date']]))

        # Define the figure
        layout = go.Layout(template='plotly_white')
        fig10 = go.Figure(layout=layout)
        fig10.add_trace(
            go.Scatter(x=dates, y=revenue, fill='tonexty'))

        # Add a green region (pre-lockdown)
        fig10.add_vrect(
            x0="2018-01-01", x1="2020-03-15",
            fillcolor="rgb(0,255,0)", opacity=0.2,
            layer="below", line_width=0,
            annotation_text='Pre-Lockdown', annotation_position='top left', annotation_font_color='grey'
        )

        # Add a red region (lockdown)
        fig10.add_vrect(
            x0="2020-03-15", x1="2020-07-15",
            fillcolor="rgb(255,0,0)", opacity=0.2,
            layer="below", line_width=0,
            annotation_text='Lockdown', annotation_position='top left', annotation_font_color='grey'
        ),

        # Add a yellow region (post-lockdown)
        fig10.add_vrect(
            x0="2020-07-15", x1="2021-10-21",
            fillcolor="rgb(255,153,0)", opacity=0.2,
            layer="below", line_width=0,
            annotation_text='Post-Lockdown', annotation_position='top right', annotation_font_color='grey'
        )

        fig10.update_yaxes(range=[0, 2.9 * math.pow(10, 9)])  # Select the y range

        # Include the labels. The x unified hovermode means a vertical line will be used to hover over the chart
        self.__add_labels([fig10], ['Revenue of Top Movies per Release Date'], [None],
                                   ['Revenue ($)'], {'hovermode': 'x unified'})

        return fig10

    def __create_graph4_figs(self):
        """
        Produce the three figures that describe the relationship between Distributor and Revenue.

        Returns
        -------
        fig11 :  plotly.graph_objs._figure.Figure
            A treemap containing the Overall Revenue for each of the different Distributors.
        fig12 : plotly.graph_objs._figure.Figure
            A horizontal bar chart that showcases Distributor vs Mean Revenue (error bars included).
        fig13 : plotly.graph_objs._figure.Figure
            A horizontal bar chart that showcases Distributor vs Mean Revenue (no error bars).

        """
        # Define the figures
        fig11 = px.treemap(self.__dist_df, path=[px.Constant("Distribution Companies"), 'Distributor'],
                           values='Revenue',
                           color='Number of Movies',  # Add a color scale for the number of movies
                           color_continuous_scale='RdBu',
                           color_continuous_midpoint=np.average(self.__dist_df['Number of Movies'],
                                                                weights=self.__dist_df['Revenue']))
        self.__dist_df.sort_values(by=['Mean Revenue'], inplace=True)  # Sort by ascending Mean Revenue
        fig12 = self.__create_horizontal_barchart(self.__dist_df['Standard Error (Revenue)'])
        fig13 = self.__create_horizontal_barchart()

        # Include the labels
        titles = ['Distributor Revenue', 'Mean Distributor Revenue', 'Mean Distributor Revenue']
        xlabels = [None, 'Revenue ($)', 'Revenue ($)']
        ylabels = [None] * 3
        self.__add_labels([fig11, fig12, fig13], titles, xlabels, ylabels)

        return fig11, fig12, fig13

    @property
    def fig1(self):
        """Getter method to obtain __fig1"""
        return self.__fig1

    @property
    def fig2(self):
        """Getter method to obtain __fig2"""
        return self.__fig2

    @property
    def fig3(self):
        """Getter method to obtain __fig3"""
        return self.__fig3

    @property
    def fig4(self):
        """Getter method to obtain __fig4"""
        return self.__fig4

    @property
    def fig5(self):
        """Getter method to obtain __fig5"""
        return self.__fig5

    @property
    def fig6(self):
        """Getter method to obtain __fig6"""
        return self.__fig6

    @property
    def fig7(self):
        """Getter method to obtain __fig7"""
        return self.__fig7

    @property
    def fig8(self):
        """Getter method to obtain __fig8"""
        return self.__fig8

    @property
    def fig9(self):
        """Getter method to obtain __fig9"""
        return self.__fig9

    @property
    def fig10(self):
        """Getter method to obtain __fig10"""
        return self.__fig10

    @property
    def fig11(self):
        """Getter method to obtain __fig11"""
        return self.__fig11

    @property
    def fig12(self):
        """Getter method to obtain __fig12"""
        return self.__fig12

    @property
    def fig13(self):
        """Getter method to obtain __fig13"""
        return self.__fig13
