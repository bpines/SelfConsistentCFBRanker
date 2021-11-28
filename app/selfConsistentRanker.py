#! /usr/bin/python3.9
import pandas as pd
import pickle
import os

from app.functions import (
    general as gen,
)

import numpy as np
import csv
# import sys


db = "ncaafb"
# gen.dbInit(db)
d= pd.read_pickle(db+".p")
# pickle.dump(d, open(os.path.join(db + ".p"), "wb"))
#
# nTeamDetails = len(sys.argv) - 1
# if nTeamDetails > 0:
#     teamDetails = sys.argv[1:nTeamDetails+1]


seasonFile = 'app/data/2021season.csv'
teamsFile  = 'app/data/2021fbs.csv'
extendedPrint = True

maxIts = 10000
tol = 1e-14
maxWeek = 14
maxWeekRemaining = 16

rankstrings = [('(' + str(i+1) + ') ') for i in range(25)]
nameSwaps = [['Central Florida','UCF'],['Pittsburgh','Pitt'],['Alabama-Birmingham','UAB'],['Texas-San Antonio','UTSA'],
             ['Texas-El Paso','UTEP'],['Southern Methodist','SMU'],['Brigham Young','BYU'],['Mississippi','Ole Miss'],
             ['Louisiana State','LSU'],['Southern California','USC']]
season = []
with open(seasonFile, newline='') as csvfile:
    gameData = csv.reader(csvfile, delimiter=',')
    header = next(gameData, None)  # skip the header
    wIndex = header.index('Winner')
    lIndex = header.index('Loser')
    for game in gameData:
        name1 = game[wIndex]
        name2 = game[lIndex]
        for rank in rankstrings:
            name1 = name1.replace(rank,'')
            name2 = name2.replace(rank,'')
        for swap in nameSwaps:
            if name1 == swap[0]:
                name1 = swap[1]
            if name2 == swap[0]:
                name2 = swap[1]
        season.append([int(game[1]),name1,name2])

teams = []
with open(teamsFile, newline='') as csvfile:
    teamData = csv.reader(csvfile, delimiter=',')
    next(teamData, None)  # skip the header
    next(teamData, None)  # skip the header
    for team in teamData:
        teams.append(team[1])
maxNameLength = max([len(team) for team in teams])

nTeam = len(teams)
winLossMatrix = [[ [] for i in range(nTeam+1)] for j in range(nTeam+1)]
remainingSchedule = [[ [] for i in range(nTeam+1)] for j in range(nTeam+1)]
teams.append('Non-FBS')

gamesPlayed = np.zeros(nTeam+1)
gamesRemaining = np.zeros(nTeam+1)
ws = np.zeros(nTeam+1)
ls = np.zeros(nTeam+1)
for game in season:
    try:
        winner = teams.index(game[1])
    except ValueError:
        winner = nTeam
    try:
        loser  = teams.index(game[2])
    except ValueError:
        loser = nTeam
    if int(game[0]) <= maxWeek:
        winLossMatrix[winner][loser].append(1)
        winLossMatrix[loser][winner].append(-1)
        gamesPlayed[winner] += 1
        gamesPlayed[loser]  += 1
        ws[winner] += 1
        ls[loser]  += 1
    elif int(game[0]) <= maxWeekRemaining:
        remainingSchedule[winner][loser].append(1)
        remainingSchedule[loser][winner].append(1)
        gamesRemaining[winner] += 1
        gamesRemaining[loser]  += 1

naw = ws - ls
newNAW = np.copy(naw[0:-1])
for j in range(maxIts):
    naw[nTeam] = min(newNAW) - 1
    nawScale = max(np.abs(newNAW))
    for i in range(nTeam):
        newNAW[i] = 0
        for k in range(nTeam+1):
            for l in range(len(winLossMatrix[i][k])):
                newNAW[i] = newNAW[i] + winLossMatrix[i][k][l]*np.exp(winLossMatrix[i][k][l]*naw[k]/nawScale)
    maxDiff = np.amax(np.abs(newNAW-naw[0:nTeam]))
    naw[:-1] = np.copy(newNAW)
    iterations = j + 1
    if maxDiff < tol:
        break

ncs = np.zeros(nTeam)
for i in range(nTeam):
    for k in range(nTeam+1):
        for l in range(len(winLossMatrix[i][k])):
            ncs[i] = ncs[i] + np.exp(naw[k]/nawScale)

nawScale = max(np.abs(newNAW))
aaw = naw / np.amax([gamesPlayed,np.ones(nTeam+1)],axis=0)
nrs = np.zeros(nTeam)
for i in range(nTeam):
    for k in range(nTeam+1):
        for l in range(len(remainingSchedule[i][k])):
            nrs[i] = nrs[i] + remainingSchedule[i][k][l]*np.exp(naw[k]/nawScale)

ranks    = list(reversed(np.argsort(naw)))
aawranks = list(reversed(np.argsort(aaw)))
ncsranks = list(reversed(np.argsort(ncs)))
nrsranks = list(reversed(np.argsort(nrs)))

# Formatting
fnd = 3         # float number of decimals (choose odd)
ffw = fnd + 4   # float full width, :{ffw}.{fnd}f
ifw = 4         # integer full width, :{ifw}d
tlp = ' '*int((fnd+3)/2)    # padding around 3-letter strings
tbs = '-'*int(ffw+2)        # table border segment


ncs = np.append(ncs,[0]) #NCS and NRS for Non FBS
nrs = np.append(nrs,[0])
df = pd.DataFrame([],columns=["Team","NAW","AAW","NCS","NRS","Record"])
for i in ranks:
    team = teams[ranks[i]]
    tNaw = naw[ranks[i]]
    tAaw = aaw[ranks[i]]
    tNcs = ncs[ranks[i]]
    tNrs = nrs[ranks[i]]
    record = str(int(ws[ranks[i]]))+" - "+str(int(ls[ranks[i]]))
    r0 = pd.Series([team,tNaw,tAaw,tNcs,tNrs,record],index=df.columns)
    df = df.append(r0,ignore_index=True)
df = df.sort_values(["NAW"],ascending=False).reset_index(drop=True)
df.insert(0,"Rank",range(1,len(df)+1))
d["analysis"]["teamRankings"] = df
pickle.dump(d, open(os.path.join(db + ".p"), "wb"))

d["analysis"]["byTeam"]=dict()
for team in teams:
    v = dict()
    v["team"] = team
    v["wording"] = "this is the page for "+team
    d["analysis"]["byTeam"][team] =v

d["analysis"]["week"] = str(13)
teams.sort()
d["data"]["teams"]= teams
pickle.dump(d, open(os.path.join(db + ".p"), "wb"))


print()
if nTeamDetails == 0:
    print(f'Ranks to week {maxWeek} after {iterations} iterations:')
    print()
    print(f'| Rank | {"Team":{maxNameLength}} |{tlp}NAW{tlp}|{f"{tlp}AAW{tlp}|{tlp}NCS{tlp}|{tlp}NRS{tlp}| Record  |" if extendedPrint else ""}')
    print(f'|------|{"-"*(maxNameLength+2)}|{tbs}|{f"{tbs}|{tbs}|{tbs}|---------|" if extendedPrint else ""}')
    for i in range(nTeam):
        print(f'| {i+1:{ifw}} | {teams[ranks[i]]:{maxNameLength}} | {naw[ranks[i]]:{ffw}.{fnd}f} | {f"{aaw[ranks[i]]:{ffw}.{fnd}f} | {ncs[ranks[i]]:{ffw}.{fnd}f} | {nrs[ranks[i]]:{ffw}.{fnd}f} | {int(ws[ranks[i]]):2d} - {int(ls[ranks[i]]):2d} |" if extendedPrint else ""}')
else:
    for team in teamDetails:
        if team in teams:
            i = teams.index(team)
            if gamesPlayed[i] > 0:
                print(f'{team} ({int(ws[i])} - {int(ls[i])})')
                print(f'|       |{tlp}NAW{tlp}|{tlp}AAW{tlp}|{tlp}NCS{tlp}|{tlp}NRS{tlp}|')
                print(f'|-------|{tbs}|{tbs}|{tbs}|{tbs}|')
                print(f'| Value | {naw[i]:{ffw}.{fnd}f} | {aaw[i]:{ffw}.{fnd}f} | {ncs[i]:{ffw}.{fnd}f} | {nrs[i]:{ffw}.{fnd}f} |')
                print(f'| Rank  | {ranks.index(i)+1:{ffw}d} | {aawranks.index(i)+1:{ffw}d} | {ncsranks.index(i)+1:{ffw}d} | {nrsranks.index(i)+1:{ffw}d} |')
                print()
                print(f'|{" Played":{maxNameLength+5}}| Outcome    |{tlp[1:]}Change{tlp[1:]}|')
                print(f'|{"-"*(maxNameLength+5)}|------------|-{tbs}|')
                for k in range(nTeam+1):
                    for l in range(len(winLossMatrix[i][k])):
                        print(f'|{ranks.index(k)+1:4} {teams[k]:{maxNameLength}}|{" Win        " if winLossMatrix[i][k][l]==1 else " Loss       "}| {"+" if winLossMatrix[i][k][l]==1 else "-"}{np.exp(winLossMatrix[i][k][l]*naw[k]/nawScale):{ffw}.{fnd}f} |')
                print()
            if gamesRemaining[i] > 0:
                print(f'|{" Remaining":{maxNameLength+5}}|{tlp[1:]}If Win{tlp[1:]}|{tlp[1:]}If Loss{tlp[2:]}|')
                print(f'|{"-"*(maxNameLength+5)}|-{tbs}|-{tbs}|')
                for k in range(nTeam+1):
                    for l in range(len(remainingSchedule[i][k])):
                        print(f'|{ranks.index(k)+1:{ifw}} {teams[k]:{maxNameLength}}| +{np.exp(naw[k]/nawScale):{ffw}.{fnd}f} | -{np.exp(-naw[k]/nawScale):{ffw}.{fnd}f} |')
                print()
