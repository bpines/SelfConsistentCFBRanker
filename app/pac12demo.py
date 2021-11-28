#! /usr/bin/python3.9
import numpy as np

maxIts = 1000
tol = 1e-10
teamNames = ['Arizona', 'Arizona State', 'California', 'Colorado', 'Oregon', 'Oregon State', 'Stanford', 'UCLA', 'USC', 'Utah', 'Washington', 'Washington State']
nTeam = len(teamNames)
winLossMatrix = np.zeros([nTeam,nTeam])

# By week, each pair is [winner,loser]
season = [
         [],
         [[2,10],[8,6]],
         [],
         [[8,9],[4,6],[3,1],[7,11]],
         [[1,2],[10,8],[6,5],[9,11],[0,7]],
         [[0,3],[4,2],[5,7],[6,10]],
         [[4,3],[1,11],[9,5],[10,0]],
         [[7,6],[5,2],[4,10],[9,1],[11,3],[8,0]],
         [[8,3],[6,0],[7,1],[9,2],[4,11]],
         [[9,10],[5,0],[4,8],[7,3]],
         [[10,5],[3,6],[8,1],[2,11]],
         [[11,6],[5,1],[9,7],[4,0],[8,2]],
         [[8,7],[2,6],[1,4],[11,5],[3,10],[9,0]],
         [[10,11],[4,5],[9,3],[1,0],[2,7]],
         [[4,9]]
         ]
for week in season:
    for game in week:
        if (winLossMatrix[game[0],game[1]] != 0) or (winLossMatrix[game[1],game[0]] != 0):
            print('Repeat match of ' + teamNames[game[0]] + ' and ' + teamNames[game[1]])
        winLossMatrix[game[0],game[1]] = 1
        winLossMatrix[game[1],game[0]] = -1

strength = np.ones(nTeam)
newStrength = np.ones(nTeam)
for j in range(maxIts):
    strengthSum = sum(np.abs(strength))
    for i in range(nTeam):
        newStrength[i] = sum(winLossMatrix[i]*np.exp(winLossMatrix[i]*strength/strengthSum))
    maxDiff = np.amax(np.abs(newStrength-strength))
    strength = np.copy(newStrength)
    # print(maxDiff)
    # print(newStrength)
    if maxDiff < tol:
        break

ranks = list(reversed(np.argsort(strength)))
print('Ranks:')
for i in range(nTeam):
    print(str(i+1) + ' ' + teamNames[ranks[i]] + ' ' + str(strength[ranks[i]]))
