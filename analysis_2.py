import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import re


file_names = ['github_timeline_data000000000000.csv', 'github_timeline_data000000000001.csv',
              'github_timeline_data000000000002.csv', 'github_timeline_data000000000003.csv',
              'github_timeline_data000000000004.csv', 'github_timeline_data000000000005.csv',
              'github_timeline_data000000000006.csv', 'github_timeline_data000000000007.csv']
df_list = []
for file in file_names: #reading csv files
    df_temp = pd.read_csv(file, usecols=['repository_url', 'repository_description', 'repository_created_at',
                                         'actor_attributes_type', 'repository_watchers', 'actor', 'type'])
    df_list.append(df_temp)

df = pd.concat(df_list, axis=0, ignore_index=True) #concatenated dataframe.

df6 = df[['repository_url', 'type']]
df6 = df6.groupby('repository_url').count() #obtaining # of events for each repository, to judge popularity.
df6.sort_values('type', ascending=False, inplace=True)
popular_repos = df6.iloc[0:10].index.tolist() #Top 10 popular repos based of # of events occured.
print('Part 2a)')
print('Top 10 popular repos are', popular_repos)

df6 = df[['repository_url', 'repository_watchers', 'actor_attributes_type', 'actor', 'type']]
df6 = df6.loc[df6['repository_url'].isin(popular_repos)] #Here, we are only concerned with the popular repos
# obtained above in part a
df7 = df6.groupby('repository_url', as_index=False)['repository_watchers'].max() #no. of watchers for each repo by picking max value.
df8 = df6.loc[(df6['actor_attributes_type'] == 'User') & (df6['type'] != "WatchEvent")] #Here, concerned with only actors
# who are Users(to calculate contributors) and events other than 'WatchEvent'.
df8 = df8[['repository_url', 'actor']].drop_duplicates()#dropping repeated contributors, since a user has to be counted only once.
df8 = df8.groupby('repository_url', as_index=False)['actor'].count() #obtaining contributors for each repository.
df8.rename(columns={'actor': 'contributors'}, inplace=True)

merged_df = pd.merge(df7, df8, how='left', left_on='repository_url', right_on='repository_url').fillna(0) #merging to
# get both contributors and watchers for each repository in to a single dataframe.
merged_df.plot.scatter(x='contributors', y='repository_watchers', c=np.arange(0, 10), colormap='hsv')
plt.title('2b) Contributors vs Watchers for top 10 repos')
plt.show()


df = df[['repository_url', 'repository_description', 'repository_created_at']].dropna().drop_duplicates('repository_url')
#dropping duplicates above, to eliminate repeated repositories, here we need unique repo values.
df['security_related'] = df['repository_description'].str.contains('security') #adding new boolean column 'security_related',
#to specify if the description has the keyword 'security' in it or not (True/False).
security_repos_count = df['security_related'].sum() #adding boolean values of 'security_related' column to get # of security repos.
total_repos = df['security_related'].count() #total # of repos in the dataframe.
print('Part 2c)')
print('# of security repos:', security_repos_count)
print('Total # of repos:', total_repos)
print('Percentage of security repos:', security_repos_count*100/total_repos)

df = df[df['security_related']] #selecting only security related repos.
df['repository_created_at'] = pd.to_datetime(df['repository_created_at']) #pandas timestamp.
start_date = pd.to_datetime('1-1-2012')
df['created_in_timewindow'] = df['repository_created_at'] >= start_date #new boolean colunm to specify if repo is
# created in the time window of 2012 or not (True/False).
num_repos = df['created_in_timewindow'].sum() #adding boolean column values to get # of repos created in the time window
print('# of security repos created in the time window:', num_repos)
