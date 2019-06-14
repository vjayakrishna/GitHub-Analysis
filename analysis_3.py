import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as an
import re


def get_timeblock(colvalue):
    '''Determines the time block (1,2,3,4) of the given timestamp value based on its hour. Each day is divided into four
    6-hour blocks. Block 1: (0-6hr), Block 2: (6-12hr), Block3: (12-18hr), Block4: (18-24hr)'''
    hour_ofthe_day = colvalue.hour #hour value of the date
    block = 0
    if hour_ofthe_day < 6: #assigning block value based on the hour value.
        block = 1
    elif 6 <= hour_ofthe_day < 12:
        block = 2
    elif 12 <= hour_ofthe_day < 18:
        block = 3
    else:
        block = 4
    return block


def get_activity_type(oldvalue):
    '''Determines the activity type based on the inout value and categorises it into one of these 6 values.
    {Create, Fork, Delete, Commit, PullRequest, Other}'''
    categories = ['Create', 'Fork', 'Delete', 'Commit', 'PullRequest', 'Other']
    expr = "^"+"|".join(categories) #regex to search for the category type.
    p = re.compile(expr)
    if p.search(oldvalue) is not None:
        newvalue = p.search(oldvalue).group(0) #assigning the matched category.
    else:
        newvalue = 'Other' #If not matched, assign 'Other'
    return newvalue


def get_country2(location):
    '''Determines the country of the location as USA or Other. If location has one of us states or cities,
    it is marked as USA, else it is markes as Other'''
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
    expr = "|".join(us_states + us_cities) #regex to match us locations
    expr += "|USA|U.S."
    match = re.compile(expr)
    if match.search(location) is not None: #If location in us, assign 'USA'
        country = 'USA'
    else: #If no match found, assign 'Other'
        country = 'Other'
    return country


file_names = ['github_timeline_data000000000000.csv', 'github_timeline_data000000000001.csv',
              'github_timeline_data000000000002.csv', 'github_timeline_data000000000003.csv',
              'github_timeline_data000000000004.csv', 'github_timeline_data000000000005.csv',
              'github_timeline_data000000000006.csv', 'github_timeline_data000000000007.csv']
df_list = []
for file in file_names: #reading csv files
    df_temp = pd.read_csv(file, usecols=['repository_url', 'created_at', 'type', 'actor_attributes_location'])
    df_list.append(df_temp)
df = pd.concat(df_list, axis=0, ignore_index=True) #concatenated dataframe


df2 = df[['type', 'created_at', 'actor_attributes_location']]
df2['created_at'] = pd.to_datetime(df2['created_at']) #pandas timestamps
df2['timeblocks'] = df2['created_at'].apply(get_timeblock) #assigning timeblocks based on the timestamp
df3 = df2.groupby('timeblocks').count() #Counting # of events(/dev activities) for each timeblock
df3.rename(columns={'type': 'dev_activity'}, inplace=True)
#print(df3.head())

df3['dev_activity'].plot.bar(rot=0) #bar plot of development activities broken down by time blocks.
plt.title('3a) Development activity over time of the day')
plt.ylabel('# of activities')
plt.xticks([0, 1, 2, 3], ['12am-6am', '6am-12pm', '12pm-6pm', '6pm-12am'])
plt.show()


df2['activity_type'] = df2['type'].apply(get_activity_type) #categorizing activities into (Create, Delete, Fork, ...etc.,)
df4 = df2.pivot_table('created_at', index='timeblocks', columns='activity_type', aggfunc='count') # pivot table with
# timeblocks as index. For each of the timeblocks(1,2,3,4), the corr. row has # of events for different categories (Create, Delete, Fork, ...etc.,)
#print(df4)

df4[['Create', 'Fork', 'Delete', 'Commit', 'PullRequest', 'Other']].plot(kind='bar', stacked=True, rot=0) #stacked bar graph
# with different activity types.
plt.title('3b) Development activities over time of the day')
plt.ylabel('# of activities')
plt.xticks([0, 1, 2, 3], ['12am-6am', '6am-12pm', '12pm-6pm', '6pm-12am'])
plt.show()

df5 = df2.dropna() #dropping rows with no locations
df5['COUNTRY'] = df5['actor_attributes_location'].apply(get_country2) #assigning country
df5 = df5.pivot_table('created_at', index='timeblocks', columns='COUNTRY', aggfunc='count') #pivot table with timeblocks and countries.
# For each timeblock, the corr. row has # of events/activities for countries (USA, Other).
#print(df5)

df5[['USA', 'Other']].plot(kind='bar', stacked=True, rot=0) #stacked bar graph for dev activities analysed
# furthur by country (USA, Other)
plt.title('3c) Development activities in USA vs. rest of the world')
plt.ylabel('# of activities')
plt.xticks([0, 1, 2, 3], ['12am-6am', '6am-12pm', '12pm-6pm', '6pm-12am'])
plt.show()


daysoftheweek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
df6 = df2[['type', 'created_at']]
df6['dayofweek'] = df6['created_at'].dt.dayofweek #get day of the week based on the timestamp
df6['weekofyear'] = df6['created_at'].dt.weekofyear #get week of the year based on the timestamp
df7 = df6.groupby('dayofweek', as_index=False)['type'].count() #Obtaining # of activities for each day of the week.
df7.sort_values('type', ascending=False, inplace=True)
most_active_day = df7.iloc[0, 0] #Most active day based on the highest # of activities.
print('Part 3d)')
print('Most active development day of the week in the time window:', daysoftheweek[most_active_day])

df6 = df6.pivot_table('type', index='weekofyear', columns='dayofweek',aggfunc='count').fillna(0) #pivot table with
# weekofyear and dayofweek. For each weekofyear, corr. row in the pivot table has # of activities for all days of the
# week (Mon, Tue, Wed, Thu, Fri, Sat, Sun)
max_value = df6.max().max() #maximum # of activities in the pivot table. Needed for y limit below.
#print(df6)

fig = plt.figure()
plt.title('3d) Animation of development activities over weeks')
plt.xticks([0, 1, 2, 3, 4, 5, 6], ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
plt.xlabel('Day of the week')
plt.ylabel('# of activities')
plt.ylim(0, max_value+100)
xdata = np.arange(0, 7)
ydata = np.array(df6.iloc[0]) #first bar plot in the animation.
barplot = plt.bar(xdata, ydata, width=0.5, color="rmygbck")

def figinit():
    pass

def redraw(framenum):
    ydata = np.array(df6.iloc[framenum]) #next bar plot values.
    # Here, each row in df6 corresponds to a week in the year 2012.
    index = 0
    for bar in barplot:
        bar.set_height(ydata[index])
        index += 1
    return barplot,


anim = an.FuncAnimation(fig, redraw, frames=len(df6.index), interval=500, init_func=figinit, blit=False, repeat=False)
plt.show()

