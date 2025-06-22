import pandas as pd
from pathlib import Path
import os
from datetime import datetime, date
dir = 'C://HKBingoTracker'
playerList = []
row1 = range(1, 6)
row2 = range(6, 11)
row3 = range(11, 16)
row4 = range(16, 21)
row5 = range(21, 26)
column1 = range(1, 23, 5)
column2 = range(2, 24, 5)
column3 = range(3, 25, 5)
column4 = range(4, 26, 5)
column5 = range(5, 27, 5)
tlbr = range(1, 26, 6)
bltr = range(5, 22, 4)
#victory conditions


overall = pd.DataFrame(columns = ["name", "FirstBlood", "GoalsMarked", "GoalsLost", "WinsByLine", "LossesByLine", "WinsByMajority", "LossesByMajority", "WinLoss", "Comeback", "Choke", "TimePlayed", "AvgTTFG"])
for file in Path(dir).rglob('*.csv'):
    df = pd.read_csv(file, sep = ',', header=None, skiprows=1)
    starttime = pd.read_csv(file, nrows=1, header=None)
    starttimestring = starttime.iloc[0][0]
    start = datetime.strptime(starttimestring.strip(), '%H:%M:%S').time()
    df.columns = ['Time', 'Player', 'Goal', 'Position']
    names = list(df['Player'].unique())
    if len(names) == 1:
            print(f"Match corresponding to file {file} only has one player marking goals. Please type the other player's name.")
            otherplayer = input()
            names.append(otherplayer) #if loser of match doesnt hit a single goal
     #now we also want to find who won the match
    player1 = names[0]  
    player2 = names[1]
    def score(x): #score for a given square
        if x in df['Position'].values:
            if df.loc[(df['Position'] == x), 'Player'].iloc[0] == player1:
                   return(1)
            if df.loc[(df['Position'] == x), 'Player'].iloc[0] == player2:
                   return(-1)
        else:
             return(0)
    def linescore(line):
            value = 0
            for x in line:
                value = value + score(x)
            return(int(value))
    lines = [row1, row2, row3, row4, row5, column1, column2, column3, column4, column5, tlbr, bltr]
    linescores = []
    for any in lines:
         linescores.append(linescore(any))
    winner = []
    majoritywinner = []
    comeback = 0
    choke = 0
    goalsmarked = len(df['Position'])
    if 5 in linescores:
         winner = player1
    if -5 in linescores:
         winner = player2
    if -5 not in linescores and 5 not in linescores:
        majorityscore = 0
        for x in range(1, 26):
              majorityscore += score(x)
        if majorityscore > 0:
            majoritywinner = player1
        if majorityscore < 0:
            majoritywinner = player2

    for name in names:
        if name not in playerList:
           playerList.append(name)
        #contributes to playerList
    firstBlood = df['Player'][0] #first to mark a goal
    endTime = datetime.strptime(df['Time'].iloc[-1].strip(), '%H:%M:%S').time()
    timePlayed = datetime.combine(date.min, endTime) - datetime.combine(date.min, start)
    for name in names:
        if name == otherplayer:
            hits = 0    
        else: 
            hits = int(df['Player'].value_counts().get(name))
        goalsLost = goalsmarked - hits
        if name == otherplayer:
             firstMarkTime = None
        else:
             mymarks = df.loc[df['Player']==name]
             firstMarkstamp = datetime.strptime(df['Time'][0].strip(), '%H:%M:%S').time()
             firstMarkTime = (datetime.combine(date.min, firstMarkstamp) - datetime.combine(date.min, start)).total_seconds()
        if winner == name or majoritywinner == name:
             winloss = 1
        else:
             winloss = -1
        if winloss == 1 & goalsLost > hits:
             comeback = 1
        else:
             comeback = 0
        if winloss == -1 & hits > goalsLost:
             choke = 1
        else:
             choke = 0
        newrow = pd.DataFrame([[name, int(firstBlood == name), hits, goalsLost, int(winner == name), int(winner != name and winner in names), int(majoritywinner == name), int(majoritywinner != name and majoritywinner in names),
                                 winloss, comeback, choke, timePlayed, firstMarkTime]], 
                              columns=["name", "FirstBlood", "GoalsMarked", "GoalsLost", "WinsByLine", "LossesByLine", "WinsByMajority", "LossesByMajority", "WinLoss", "Comeback", "Choke", "TimePlayed", "FirstMarkTime"])
        overall = pd.concat([overall, newrow], ignore_index=True) #one row per player per match
              #end loop

grouped = overall.groupby("name").sum()
matchesplayed = []
for user in playerList:
     games = int(overall['name'].value_counts().get(user))
     matchesplayed.append(games)

grouped['Matches Played'] = matchesplayed
grouped['GoalsPerGame'] = grouped['GoalsMarked'] / grouped['Matches Played']
grouped['K/D'] = grouped['GoalsMarked'] / grouped['GoalsLost'].replace(0, 1)
grouped['Time To First Goal'] = pd.to_timedelta(grouped['FirstMarkTime']/grouped['Matches Played'], unit='s')
grouped['Time To First Goal'] = grouped['Time To First Goal'].apply(lambda x: f"{int(x.total_seconds() // 60):02d}:{int(x.total_seconds() % 60):02d}")

print(grouped)
print("Save file?")
answer = input()
if answer == "yes":
     grouped.to_csv('statsheet.csv', index=True)
