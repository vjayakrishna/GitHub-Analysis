import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d as m3d
import re


def get_country(location):
    '''Determines the country of a given location.
    Assigns USA if location has one the us states or cities.
    Assigns other countries if the location has the country as a substring in it.'''
    country = ''
    us_states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                 "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                 "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                 "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                 "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
                 "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
                 "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois",
                 "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
                 "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
                 "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
                 "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
                 "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
                 "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"]
    us_cities = ["Chicago", "San Francisco", "Seattle"]
    countries = ['UK', 'Canada', 'Germany', 'France', 'Japan', 'China', 'Australia', 'Sweden', 'Russia', 'Brazil', 'Switzerland',
                 'Singapore', 'Netherlands', 'Sri Lanka', 'India', 'Italy', 'Norway', 'Poland', 'Austria', 'Mexico', 'Denmark']
    uk_locations = ['United Kingdom', 'London', 'England'] #Assigns country as UK for these locations
    expr = "|".join(us_states + us_cities) #regex to match us locations
    expr += "|USA|U.S."
    match = re.compile(expr)
    expr2 = "|".join(countries) #regex to match other countries
    match2 = re.compile(expr2)
    expr3 = "|".join(uk_locations) #regex to match few uk locations
    match3 = re.compile(expr3)

    if match.search(location) is not None: #if location has one of us states or cities
        country = 'USA'
    elif match2.search(location) is not None: #if location has one of the country names
        country = match2.search(location).group(0) #assigning the matched country name.
    elif match3.search(location) is not None: #if location has one of the uk locations
        country = 'UK'
    else: #if location is not matched with any of the above searches, assigning it as it is.
        country = location
    return country


file_names = ['github_timeline_data000000000000.csv', 'github_timeline_data000000000001.csv',
              'github_timeline_data000000000002.csv', 'github_timeline_data000000000003.csv',
              'github_timeline_data000000000004.csv', 'github_timeline_data000000000005.csv',
              'github_timeline_data000000000006.csv', 'github_timeline_data000000000007.csv']
df_list = [] #list of pandas dataframes
for file in file_names: #reading the csv files in to pandas dataframes one by one.
    df_temp = pd.read_csv(file, usecols=['repository_url', 'repository_owner',
                                         'repository_language', 'actor',
                                         'actor_attributes_location'])
    df_list.append(df_temp)

df = pd.concat(df_list, axis=0, ignore_index=True) #concatenating all the above dataframes to one big dataframe.
#print(df.head())


df1 = df[['repository_url', 'repository_language']].dropna().drop_duplicates() #dropping NaN and duplicate values
df1 = df1.groupby(['repository_language']).count() #obtaining repo count for each programming language.
df1.rename(columns={'repository_url': 'repo_count'}, inplace=True)
df1.sort_values('repo_count', ascending=False, inplace=True)
df1 = df1.iloc[0:10]
top_languages = df1.index.tolist() #top 10 popular programming languages based on # of repos
#print(df1.head())

df1['repo_count'].plot.bar(rot=0)
plt.title('1a) Top 10 programming languages used')
plt.ylabel('# of repositories')
plt.show()


#Below, I am using dataframes df2, df3 to obtain repo owner's location.
df2 = df[['repository_url', 'repository_owner', 'repository_language']].dropna().drop_duplicates('repository_url')
df3 = df[['actor', 'actor_attributes_location']].dropna().drop_duplicates('actor') #dropping repeated actor values
merged_df = pd.merge(df2, df3, how='inner', left_on='repository_owner', right_on='actor')\
            .drop(['actor', 'repository_owner'], axis=1) #merging df2, df3 to find the repo location
# based on owner's location(who is actor at some point).
merged_df['COUNTRY'] = merged_df['actor_attributes_location'].apply(get_country) #assigning country based on the location.
merged_df.drop('actor_attributes_location', inplace=True, axis=1)
df4 = merged_df.groupby('COUNTRY').count() #obtaining repo count for each country.
df4.rename(columns={'repository_url': 'repo_count'}, inplace=True)
df4.sort_values('repo_count', ascending=False, inplace=True)
df4 = df4.iloc[0:10]
top_contries = df4.index.tolist() #top 10 most productive countries based on the number of repositories
print('Part 1b)')
print('Top 10 productive countries are ', top_contries)

# df4['repo_count'].plot.bar(rot=0)
# plt.title('1b) Top 10 productive countries')
# plt.ylabel('# of repositories')
# plt.show()

#for each of the above obtained countries, have to calculate relative popularity of languages (for popular languages from part a).
#So, I am only selecting the rows related to top_countries and top_languages below, as we are only concerned with these rows.
df5 = merged_df.loc[merged_df['COUNTRY'].isin(top_contries) & (merged_df['repository_language'].isin(top_languages))]
#Next, I am constructing a pivot table with top countries as index and popular languages as columns. For each country,
#the corresponding row has the repo_count for each of the popular languages (like C, C++, Java etc.,)
df5 = df5.pivot_table('repository_url', index='COUNTRY', columns='repository_language', aggfunc='count', margins=True)
df5 = df5.div(df5['All'], axis=0) #Normalizing the table values by dividing with margin column ('All') of pivot table,
#to obtain relative popularity.
df5.drop('All', inplace=True) #dropping margins
df5.drop('All', axis=1, inplace=True)
#print(df5)

fig = plt.figure()
ax1 = fig.add_subplot(111, projection='3d') #3d bar plot with top countries on x-axis and top languages on y-axis and
#relative popularity of languages per country on z-axis.
for i in range(0, 10): #for each country, drawing the bar plot separately.
    x = np.full(10, i) #same values of x for a country.
    y = np.arange(0, 10) #10 languages on y-axis for each country.
    z = df5.iloc[i] #Normalized row values of pivot table (df5) that represent relative popularity of 10 languages for each country.
    ax1.bar3d(x, y, 0, 0.5, 0.5, z) #bar plot for each country
ax1.set_xlabel('Country')
ax1.set_ylabel('Programming lanuage')
ax1.set_zlabel('Relative popularity of languages')
ax1.set_xticks(np.arange(0.25, 10))
ax1.set_xticklabels(df5.index.tolist())
ax1.set_yticks(np.arange(0.25, 10))
ax1.set_yticklabels(df5.columns.tolist())
plt.show()

