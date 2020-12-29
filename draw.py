import os
import sqlite3
import time

def awardUser(user):
    if len(user) == 0:
        return False
    if user[0] == '@':
        user = user[1:]
    user = user.lower()

    conn = None
    try:
        conn = sqlite3.connect('Data/draw.db')
    except Error as e:
        print(e)
        
    cur = conn.cursor()
    cur.execute("INSERT INTO Users(Name,Score) SELECT '" + user + "',0 WHERE NOT EXISTS(SELECT * FROM Users WHERE Name='" + user + "')")
    cur.execute("UPDATE Users SET Score=(SELECT Score+1 FROM Users WHERE Name='" + user + "') WHERE Name='" + user + "'")
    conn.commit()
    cur.execute("SELECT a.Score, (SELECT COUNT(*) FROM Users b WHERE a.Score <= b.Score ORDER BY b.Score DESC) FROM Users a WHERE a.Name='" + user + "'")

    rows = cur.fetchall()
    
    updateLeaderboardFile(user, rows[0])
    
    return rows[0][0]
    
def getScore(user):
    if len(user) == 0:
        return False
    if user[0] == '@':
        user = user[1:]
    user = user.lower()

    conn = None
    try:
        conn = sqlite3.connect('Data/draw.db')
    except Error as e:
        print(e)
        
    cur = conn.cursor()
    cur.execute("SELECT Score FROM Users WHERE Name='" + user + "'")

    rows = cur.fetchall()
    
    try:
        return rows[0][0]
    except:
        return 0
        
def getLeaderboard(limit, msgFmt=True):
    conn = None
    try:
        conn = sqlite3.connect('Data/draw.db')
    except Error as e:
        print(e)
        
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users ORDER BY Score DESC LIMIT " + str(limit))

    rows = cur.fetchall()
    
    board = []
    i = 0
    for row in rows:
        if msgFmt:
            board.append('@' + row[0] + ' (score: ' + str(row[1]) + ')\n')
        else:
            board.append('(' + str(row[1]) + ') ' + row[0] + '\n')
        i += 1
    return board
    
def updateLeaderboardFile(lastWinner=None, lastWinnerScore=None):
    top = getLeaderboard(5, False)
    
    topStr = "\n"
    i = 1
    for row in top:
        topStr += str(i) + ". " + row
        i = i+1
    if lastWinner != None and lastWinnerScore != None:
        topStr += "\n\n" + str(lastWinnerScore[1]) + ". " + "(" + str(lastWinnerScore[0]) + ") " + lastWinner
    
    f = open("Data/drawLeaderboard.txt", "w")
    f.write(topStr)
    f.close()

lastGet = None
async def gameMain(ctx):
    global lastGet

    commands = ctx.content.split(' ')
    if len(commands) > 2:
        if commands[1] == 'award':
            if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
                await ctx.send('User ' + commands[2] + ' won! Score: ' + str(awardUser(commands[2])))
            else:
                await ctx.send('Sorry @' + ctx.author.name + ', you can\'t do that :(')
    if len(commands) > 1:
        if commands[1] == 'score':
            user = commands[2] if len(commands) > 2 else ctx.author.name
            if user[0] != '@':
                user = '@' + user
            await ctx.send('User ' + user + '\'s current score: ' + str(getScore(user)))
        elif commands[1] == 'leaderboard':
            if lastGet == None or time.time()-lastGet > 45: # No spamming leaderboard! Time limit in seconds
                lastGet = time.time()
                
                limit = 5
                leaderboard = getLeaderboard(limit)
                await ctx.send('TOP ' + (str(len(leaderboard)) if len(leaderboard) < limit else str(limit)) + ':')
                i = 1
                for row in leaderboard:
                    await ctx.send(str(i) + '. ' + row)
                    i += 1
            else:
                await ctx.send('Hey, @' + ctx.author.name + ', look at leaderboard above! ;)')