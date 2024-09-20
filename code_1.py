import pandas as pd
import os
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import operator as op
import plotly.express as px
from mlxtend.frequent_patterns import apriori, association_rules
import locale

#upload CSV file
file_path = 'C:\capstoneproject\groceries_shopping.csv'

# Read the CSV file
df = pd.read_csv(file_path)

# Display the first few rows of the DataFrame
print(df.head())

# To check the data types
df.info()

# Checking for the missing values
nan_values = df.isna().sum()
nan_values

# there are missing values
df = df.dropna(subset=['memberID','itemName'])

# Converting Date column into correct datatype which is datetime
df.Date = pd.to_datetime(df.Date)
df.memberID = df['memberID'].astype('str')
df.info()  # They are in correct datatype now

#create new column to calculate total price
df['totalPrice'] = df['quantity'] * df['price']

# Display the first few rows to verify the new column
df.head()

#Calculate the Sales Weekly
Sales_weekly = df.resample('w', on='Date').size()
fig = px.line(df, x=Sales_weekly.index, y=Sales_weekly,
              labels={'y': 'Number of Sales',
                     'x': 'Date'})
fig.update_layout(title_text='Number of Sales Weekly',
                  title_x=0.5, title_font=dict(size=18)) 
fig.show()

#Show the number of unique customer weekly
Unique_customer_weekly = df.resample('w', on='Date').memberID.nunique()
fig = px.line(Unique_customer_weekly, x=Unique_customer_weekly.index, y=Unique_customer_weekly,
              labels={'y': 'Number of Customers'})
fig.update_layout(title_text='Number of Customers Weekly',
                  title_x=0.5, title_font=dict(size=18))
fig.show()

#Calculate number of sales per customer
Sales_per_Customer = Sales_weekly / Unique_customer_weekly
fig = px.line(Sales_per_Customer, x=Sales_per_Customer.index, y=Sales_per_Customer,
              labels={'y': 'Sales per Customer Ratio'})
fig.update_layout(title_text='Sales per Customer Weekly',
                  title_x=0.5, title_font=dict(size=18))
fig.update_yaxes(rangemode="tozero")
fig.show()

#Frequency_of_items = df.groupby(pd.Grouper(key='itemName')).size().reset_index(name='count')
Frequency_of_items = df.groupby('itemName')['quantity'].sum().reset_index(name='quantitySold')

#Top 20% item sold calculation. Use the Pareto rules
threshold = Frequency_of_items['quantitySold'].quantile(0.80)

# Filter the DataFrame to include only items above this threshold
top_items = Frequency_of_items[Frequency_of_items['quantitySold'] >= threshold]

fig = px.treemap(top_items, path=['itemName'], values='quantitySold')
fig.update_layout(title_text='Frequency of the Items Sold',
                  title_x=0.5, title_font=dict(size=18)
                  )
fig.update_traces(textinfo="label+value")
fig.show()

# Sort the DataFrame by quantitySold in descending order
top_items = top_items.sort_values(by='quantitySold', ascending=False)

# Select the top 10 items
top20_items = top_items.head(10)

# Create the treemap with the top 10 items
fig = px.treemap(top20_items, path=['itemName'], values='quantitySold')
fig.update_layout(title_text='Top 10 Items Sold',
                  title_x=0.5, title_font=dict(size=18))
fig.update_traces(textinfo="label+value")
fig.show()

user_item = df.groupby(pd.Grouper(key='memberID')).size().reset_index(name='count')
fig = px.bar(user_item.head(25), x='memberID', y='count',
             labels={'y': 'Number of Sales',
                     'count': 'Number of Items Bought'},
             color='count')
fig.update_layout(title_text='Top 20 Customers regarding Number of Items Bought',
                  title_x=0.5, title_font=dict(size=18))
fig.update_traces(marker=dict(line=dict(color='#000000', width=1)))
fig.show()

# Define the order of the days
days_order = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']

# Group by day of the week and count the items
day = df.groupby(df['Date'].dt.strftime('%A'))['itemName'].count()

# Convert the index to a categorical type with the specified order
day.index = pd.Categorical(day.index, categories=days_order, ordered=True)

# Sort the values by the categorical index
day = day.sort_index()

fig = px.bar(day, x=day.index, y=day, color=day,
             labels={'y': 'Number of Sales',
                     'Date': 'Week Days'})
fig.update_layout(title_text='Number of Sales per Discrete Week Days',
                  title_x=0.5, title_font=dict(size=18))
fig.update_traces(marker=dict(line=dict(color='#000000', width=1)))
fig.show()

#create market basket analysis
baskets = df.groupby(['memberID', 'itemName'])['itemName'].count().unstack().fillna(0).reset_index()
baskets.head()

# Let's check the most sold -item which is whole milk- has the same number of sales as we discussed above in the treemap.
baskets['whole milk'].sum()

# Encoding the items that sold more than 1
def one_hot_encoder(k):
    if k <= 0:
        return 0
    if k >= 1:
        return 1
baskets_final = baskets.iloc[:, 1:baskets.shape[1]].applymap(one_hot_encoder)
baskets_final.head()

# Finding the most frequent items sold together
frequent_itemsets = apriori(baskets_final, min_support=0.025, use_colnames=True, max_len=3).sort_values(by='support')
frequent_itemsets.head(25)

# Creating association rules for indicating astecedent and consequent items
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1).sort_values('lift', ascending=False)
rules = rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
rules.head(25)

# This step, we will do the customer segmentation using RFM (recency, frequency, monetary) analysis

# Finding last purchase date of each customer - Customer Recency
Recency = df.groupby(by='memberID')['Date'].max().reset_index()
Recency.columns = ['memberID', 'LastDate']
Recency.head()

# Finding last date for our dataset
last_date_dataset = Recency['LastDate'].max()
last_date_dataset

# Calculating Recency by subtracting (last transaction date of dataset) and (last purchase date of each customer)
Recency['Recency'] = Recency['LastDate'].apply(lambda x: (last_date_dataset - x).days)
Recency.head()

#Recency Distribution of the Customers
fig = px.histogram(Recency, x='Recency', opacity=0.85, marginal='box')
fig.update_traces(marker=dict(line=dict(color='#000000', width=1)))
fig.update_layout(title_text='Recency Distribution of the Customers',
                  title_x=0.5, title_font=dict(size=20))
fig.show()

# Frequency of the customer visits
Frequency = df.drop_duplicates(['Date', 'memberID']).groupby(by=['memberID'])['Date'].count().reset_index()
Frequency.columns = ['memberID', 'Visit_Frequency']
Frequency.head()

#Visit Frequency Distribution of the Customers
fig = px.histogram(Frequency, x='Visit_Frequency', opacity=0.85, marginal='box')
fig.update_traces(marker=dict(line=dict(color='#000000', width=1)))
fig.update_layout(title_text='Visit Frequency Distribution of the Customers',
                  title_x=0.5, title_font=dict(size=20))
fig.show()

# Group by memberID and sum totalPrice
Monetary = df.groupby(by="memberID")['totalPrice'].sum().reset_index()
Monetary.columns = ['memberID', 'Monetary']

# Set locale to Indonesian
locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')

# Format the monetary values as Rupiah currency
Monetary['Monetary'] = Monetary['Monetary'].apply(lambda x: locale.currency(x, grouping=True))

Monetary.head() 

#'Monetary Distribution of the Customers
fig = px.histogram(Monetary, x='Monetary', opacity=0.85, marginal='box',
                   labels={'itemName': 'Monetary'})
fig.update_traces(marker=dict(line=dict(color='#000000', width=1)))
fig.update_layout(title_text='Monetary Distribution of the Customers',
                  title_x=0.5, title_font=dict(size=20))
fig.show()
# Combining all scores into one DataFrame
RFM = pd.concat([Recency['memberID'], Recency['Recency'], Frequency['Visit_Frequency'], Monetary['Monetary']], axis=1)
RFM.head()

# RFM scoring
# 5-5 score = the best customers
RFM['Recency_quartile'] = pd.qcut(RFM['Recency'], 5, [5, 4, 3, 2, 1])
RFM['Frequency_quartile'] = pd.qcut(RFM['Visit_Frequency'], 5, [1, 2, 3, 4, 5])

RFM['RF_Score'] = RFM['Recency_quartile'].astype(str) + RFM['Frequency_quartile'].astype(str)
RFM.head()

segt_map = {  # Segmentation Map [Ref]
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at risk',
    r'[1-2]5': 'can\'t loose',
    r'3[1-2]': 'about to sleep',
    r'33': 'need attention',
    r'[3-4][4-5]': 'loyal customers',
    r'41': 'promising',
    r'51': 'new customers',
    r'[4-5][2-3]': 'potential loyalists',
    r'5[4-5]': 'champions'
}

RFM['RF_Segment'] = RFM['RF_Score'].replace(segt_map, regex=True)
RFM.head()

x = RFM.RF_Segment.value_counts()
fig = px.treemap(x, path=[x.index], values=x)
fig.update_layout(title_text='Distribution of the RFM Segments', title_x=0.5,
                  title_font=dict(size=20))
fig.update_traces(textinfo="label+value+percent root")
fig.show()

fig = px.scatter(RFM, x="Visit_Frequency", y="Recency", color='RF_Segment',
                 labels={"math score": "Math Score",
                         "writing score": "Writing Score"})
fig.update_layout(title_text='Relationship between Visit_Frequency and Recency',
                  title_x=0.5, title_font=dict(size=20))
fig.show()
