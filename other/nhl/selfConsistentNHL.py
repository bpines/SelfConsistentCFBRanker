#! /usr/bin/python3.9
import numpy as np
import csv

seasonFile = '20182019nhlseason.csv'
teamsFile  = '20182019nhlteams.csv'

maxIts = 10000
tol = 1e-10
maxWeek = 100
outputPrecision = 8

season = []
with open(seasonFile, newline='') as csvfile:
    gameData = csv.reader(csvfile, delimiter=',')
    next(gameData, None)  # skip the header
    for game in gameData:
        name1  = game[1]
        score1 = game[2]
        name2  = game[3]
        score2 = game[4]
        if score1 > score2:
            season.append([0,name1,name2])
        elif score2 > score1:
            season.append([0,name2,name1])

teams = []
with open(teamsFile, newline='') as csvfile:
    teamData = csv.reader(csvfile, delimiter=',')
    next(teamData, None)  # skip the header
    for team in teamData:
        teams.append(team[1])
maxNameLength = max([len(team) for team in teams])

nTeam = len(teams)
winLossMatrix = [[ [] for i in range(nTeam)] for j in range(nTeam)]

for game in season:
    if int(game[0]) > maxWeek:
        break
    try:
        winner = teams.index(game[1])
    except ValueError:
        winner = nTeam
    try:
        loser  = teams.index(game[2])
    except ValueError:
        loser = nTeam
    winLossMatrix[winner][loser].append(1)
    winLossMatrix[loser][winner].append(-1)

strength = np.ones(nTeam)
newStrength = np.ones(nTeam)
for j in range(maxIts):
    strengthScale = max(np.abs(strength))
    for i in range(nTeam):
        newStrength[i] = 0
        for k in range(nTeam):
            for l in range(len(winLossMatrix[i][k])):
                newStrength[i] = newStrength[i] + winLossMatrix[i][k][l]*np.exp(winLossMatrix[i][k][l]*strength[k]/strengthScale)
    maxDiff = np.amax(np.abs(newStrength-strength))
    strength = np.copy(newStrength)
    iterations = j + 1
    if maxDiff < tol:
        break

ranks = list(reversed(np.argsort(strength)))
print(f'Ranks after {iterations} iterations:')
print(f'| Rank |{"Team":{maxNameLength}}| Strength |')
print(f'|------|{"-"*maxNameLength}|----------|')
for i in range(nTeam):
    print(f'|{i+1:6}|{teams[ranks[i]]:{maxNameLength}}|{strength[ranks[i]]:.{outputPrecision}f}|')
