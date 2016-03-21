from clean_logs import clean_data
import pandas as pd


#Import raw data and clean up into a usable dataframe
data = pd.read_csv('mill_logs_2015.csv')
unit_indices = {}
data, unit_indices = clean_data(data)


