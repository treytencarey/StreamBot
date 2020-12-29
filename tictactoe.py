from twitchio.ext import commands
import os
import pygame
import asyncio
from random import randrange
from time import sleep
import time
import sqlite3

def getScore(user):
    if len(user) == 0:
        return False
    if user[0] == '@':
        user = user[1:]
    user = user.lower()

    conn = None
    try:
        conn = sqlite3.connect('Data/tictactoe.db')
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
        conn = sqlite3.connect('Data/tictactoe.db')
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
            board.append('(' + str(row[1]) + ') ' + row[0])
        i += 1
    return board

tttRunning = False
gameDisplay = 0
turn = 0
user1Piece = ''
users = { 0: False, 1: False }
windowSize = { "w": 800, "h": 600 }
leaderboardWidth = 600
board = {}

def drawLeaderboard():
    global gameDisplay
    global windowSize
    global leaderboardWidth
    
    gameDisplay.fill(pygame.Color("black"), (windowSize["w"], 0, leaderboardWidth, windowSize["h"]))
    
    myfont = pygame.font.SysFont('Comic Sans MS', 30)
    
    txt = myfont.render("LEADERBOARD:", True, (0,255,0))
    txt_rect = txt.get_rect(center=(windowSize["w"]+leaderboardWidth/2,80))
    gameDisplay.blit(txt, txt_rect)
    i = 1
    for row in getLeaderboard(10, False):
        txt = myfont.render(str(i) + ". " + row, True, (0,255,0))
        txt_rect = txt.get_rect(center=(windowSize["w"]+leaderboardWidth/2,80+30*i))
        gameDisplay.blit(txt, txt_rect)
        i += 1

async def startGame(ctx, user1, user2):
    if user1.lower() == user2.lower():
        await ctx.send('@' + user1 + ", stop playing with yourself!!")
        return

    global users
    users = { 0: user1, 1: user2 }
    global board
    board = {}
    for i in range(0,9):
        board[i] = ''
    global turn
    turn = randrange(2)
    global user1Piece
    user1Piece = 'X' if randrange(2) == 0 else 'O'
    
    await ctx.send('@' + users[turn] + ", it's your turn! Say \"!ttt #\" (no quotes, where # is 1-9) to play, or type \"!ttt help\" for more info :)")
    
    pygame.init()
    
    global gameDisplay
    global windowSize
    gameDisplay = pygame.display.set_mode((windowSize["w"]+leaderboardWidth,windowSize["h"]))
    pygame.display.set_caption('Test')
    clock = pygame.time.Clock()
    
    # Vertical lines
    pygame.draw.rect(gameDisplay, (255,255,255), pygame.Rect(windowSize["w"]/3,0,2,windowSize["h"]))
    pygame.draw.rect(gameDisplay, (255,255,255), pygame.Rect(windowSize["w"]/3*2,0,2,windowSize["h"]))
    # Horizontal lines
    pygame.draw.rect(gameDisplay, (255,255,255), pygame.Rect(0,windowSize["h"]/3,windowSize["w"],2))
    pygame.draw.rect(gameDisplay, (255,255,255), pygame.Rect(0,windowSize["h"]/3*2,windowSize["w"],2))
    
    # Draw text on board
    pygame.font.init()
    myfont = pygame.font.SysFont('Comic Sans MS', 30)
    for x in range(0,3):
        for y in range(0,3):
            txt = myfont.render(str(x+y*3+1),False,(155,155,155))
            gameDisplay.blit(txt,(windowSize["w"]/3*x+windowSize["w"]/3/2,windowSize["h"]/3*y+windowSize["h"]/3/2))
            
    drawLeaderboard()
    
    global tttRunning
    tttRunning = True
    while tttRunning:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                tttRunning = False
            print(event)
        
        pygame.display.update()
        clock.tick(60)
        await asyncio.sleep(0.01)
        
    pygame.quit()
    
def awardUser(user):
    if len(user) == 0:
        return False
    if user[0] == '@':
        user = user[1:]
    user = user.lower()

    conn = None
    try:
        conn = sqlite3.connect('Data/tictactoe.db')
    except Error as e:
        print(e)
        
    cur = conn.cursor()
    cur.execute("INSERT INTO Users(Name,Score) SELECT '" + user + "',0 WHERE NOT EXISTS(SELECT * FROM Users WHERE Name='" + user + "')")
    cur.execute("UPDATE Users SET Score=(SELECT Score+1 FROM Users WHERE Name='" + user + "') WHERE Name='" + user + "'")
    conn.commit()
    cur.execute("SELECT a.Score, (SELECT COUNT(*) FROM Users b WHERE a.Score <= b.Score ORDER BY b.Score DESC) FROM Users a WHERE a.Name='" + user + "'")

    rows = cur.fetchall()
    
    return rows[0][0]
    
def checkWin():
    global board
    global users
    global user1Piece
    
    emptySpots = False
    for i in range(0,9):
        if board[i] == '':
            emptySpots = True
            break
    if emptySpots == False:
        return None
    
    # Check horizontal
    for y in range(0,3):
        if board[y*3+0] != '' and board[y*3+0] == board[y*3+1] and board[y*3+1] == board[y*3+2]:
            return users[0] if board[y*3+0] == 'X' and user1Piece == 'X' else users[1]
    # Check vertical
    for x in range(0,3):
        if board[x+0] != '' and board[x+0] == board[x+3] and board[x+3] == board[x+6]:
            return users[0] if board[x+0] == 'X' and user1Piece == 'X' else users[1]
    # Check diagonal
    if board[0] != '' and board[0] == board[4] and board[4] == board[8]:
        return users[0] if board[0] == 'X' and user1Piece == 'X' else users[1]
    if board[2] != '' and board[2] == board[4] and board[4] == board[6]:
        return users[0] if board[2] == 'X' and user1Piece == 'X' else users[1]
    
    return ''
    
async def placeAt(ctx, user, spot):
    global tttRunning
    if tttRunning == False:
        await ctx.send('@' + user + ", there's not a Tic-Tac-Toe game running!")
        return
        
    global user1Piece
    global users
    global turn
    if user.lower() != users[turn].lower():
        await ctx.send('@' + user + ", it's not your turn!")
        return
    if spot < 1 or spot > 9:
        await ctx.send('@' + user + ", that's not a valid spot, try again!")
        return
    
    piece = user1Piece if turn == 0 else 'X' if user1Piece == 'O' else 'O'
    global board
    if board[spot-1] != '':
        await ctx.send('@' + user + ", that spot is already taken! Please try again.")
        return
    board[spot-1] = piece
        
    global gameDisplay
    myfont = pygame.font.SysFont('Comic Sans MS', 240)
    
    txt = myfont.render(piece,False,(255 if piece == 'X' else 0,0,255 if piece == 'O' else 0))
    
    x = (spot-1)%3
    y = int((spot-1)/3)
    global windowSize
    gameDisplay.blit(txt,(windowSize["w"]/3*x+windowSize["w"]/3/2-80,windowSize["h"]/3*y+windowSize["h"]/3/2-180))
    
    turn = 0 if turn == 1 else 1
    winner = checkWin()
    if winner == None:
        myfont = pygame.font.SysFont('Comic Sans MS', 45)
        
        txt = myfont.render("NO WINNER :( TRY AGAIN", True, (0,255,0))
        txt_rect = txt.get_rect(center=(windowSize["w"]/2,windowSize["h"]/2))
        gameDisplay.blit(txt, txt_rect)
        
        pygame.display.update()
        clock = pygame.time.Clock()
        clock.tick(60)
        sleep(10)
    
        tttRunning = False
        pygame.quit()
    elif winner != '':
        myfont = pygame.font.SysFont('Comic Sans MS', 45)
        
        newScore = awardUser(winner)
        drawLeaderboard()
        
        txt = myfont.render("AND THE WINNER IS:", True, (0,255,0))
        txt_rect = txt.get_rect(center=(windowSize["w"]/2,windowSize["h"]/2))
        gameDisplay.blit(txt, txt_rect)
        await ctx.send('CONGRATS @' + winner + ", you won!")
        
        txt = myfont.render(winner + " (" + str(newScore) + ")!", True, (0,255,0))
        txt_rect = txt.get_rect(center=(windowSize["w"]/2,windowSize["h"]/2+50))
        gameDisplay.blit(txt, txt_rect)
        
        pygame.display.update()
        clock = pygame.time.Clock()
        clock.tick(60)
        sleep(10)
    
        tttRunning = False
        pygame.quit()
    else:
        await ctx.send('@' + users[turn] + ", it's your turn! (Type \"!ttt help\" if you need help playing)")

lastGet = None
lastGetLeaderboard = None
async def gameMain(ctx):
    global lastGet
    global lastGetLeaderboard

    commands = ctx.content.split(' ')
    if len(commands) > 1:
        if commands[1].find("start") == 0 and len(commands) > 2:
            # if ctx.author.name.lower() == os.environ['BOT_NICK'].lower():
                withUsers = [ commands[2], commands[3] if len(commands) > 3 else ctx.author.name ]
                if withUsers[0][0] == '@':
                    withUsers[0] = withUsers[0][1:]
                if withUsers[1][0] == '@':
                    withUsers[1] = withUsers[1][1:]
                await ctx.send('A Tic-Tac-Toe game has been started between users @' + withUsers[0] + ' and @' + withUsers[1] + '! Use command "!ttt help" to see available commands!')
                await startGame(ctx, withUsers[0], withUsers[1])
            # else:
            #     await ctx.send('Sorry @' + ctx.author.name + ', you can\'t do that :(')
        elif commands[1].isnumeric():
            await placeAt(ctx,ctx.author.name.lower(),int(commands[1]))
        elif commands[1].lower() == "help":
            if lastGet == None or time.time()-lastGet > 45: # No spamming help! Time limit in seconds
                lastGet = time.time()
                
                await ctx.send('@' + ctx.author.name + ' here are the TIC-TAC-TOE game commands:')
                await ctx.send('Say "!ttt start @user" to start a Tic-Tac-Toe match against a player (no quotes, where @user is a user\'s name).')
                await ctx.send('Say "!ttt #" to place a piece (no quotes, where # is 1-9 corresponding to the parts of the board).')
                await ctx.send('Say "!ttt leaderboard" to view the top 5 players (no quotes).')
                await ctx.send('Say "!ttt score @user" to view the score of a player (no quotes, where @user is a user\'s name or no name to view your own).')
            else:
                await ctx.send('Hey, @' + ctx.author.name + ', look at the commands in chat above!')
        elif commands[1].lower() == "leaderboard":
            if lastGetLeaderboard == None or time.time()-lastGetLeaderboard > 45: # No spamming help! Time limit in seconds
                lastGetLeaderboard = time.time()
                
                limit = 5
                leaderboard = getLeaderboard(limit)
                await ctx.send('TOP ' + (str(len(leaderboard)) if len(leaderboard) < limit else str(limit)) + ':')
                i = 1
                for row in leaderboard:
                    await ctx.send(str(i) + '. ' + row)
                    i += 1
            else:
                await ctx.send('Hey, @' + ctx.author.name + ', look at leaderboard above! ;)')
        elif commands[1] == 'score':
            user = commands[2] if len(commands) > 2 else ctx.author.name
            if user[0] != '@':
                user = '@' + user
            await ctx.send('User ' + user + '\'s current score: ' + str(getScore(user)))