import discord
import json
import random
from collections import deque
from discord.ext import commands
from kbbi import KBBI
from kbbi import AutentikasiKBBI
from kbbi import TidakDitemukan

bot = commands.Bot(command_prefix='b!')
auth = AutentikasiKBBI("")

@bot.event
async def on_ready():
    print("bot siap")

# @bot.command()
# async def tes(message):
#     await message.send(f'{message.author.mention}\'s id: `{message.author.id}`') 

@bot.command()
async def plei(message, highscore = 100, jumlah_roll = 5):
    host = message.author.mention
    await message.send(host+ ' memulai permainan, ketik `melok` untuk ikutan')
    teks = 'Players:\n'
    teksobj = await message.send(teks)
#   print(message.message.id)
    await main(message, host, teks, teksobj,highscore,jumlah_roll)

@bot.command()
async def ajak(message, friend= '@everyone'):
    await message.send(friend+' mari mengontol kita main gim sambung words')

async def main(message,host,teks,teksobj,highscore,jumlah_roll):
    score = highscore
    kataterpakai = []
    players = []
    roll = False

    player = Player(message.author.id, message.author.name)
    players.append(player)
    newteks = await addPlayer(teks,players)
    await teksobj.edit(content=newteks)

    while True:
        msg = await bot.wait_for('message')
        if msg.content == 'melok':
            id = msg.author.id
            exist = False
            for player in players:
                if player.id == id:
                    exist = True
                    break
            if exist == False:
                player = Player(msg.author.id,msg.author.name)
                players.append(player)
                newteks = await addPlayer(teks,players)
                await teksobj.edit(content=newteks)
        
        if msg.author.mention == host:
            if msg.content == 'start':
                if len(players) >= 2:
                    for player in players:
                        player.roll = jumlah_roll
                    break
                else:
                    await message.send('Permainan membutuhkan minimal 2 orang')
            
            elif msg.content == 'exit':
                await message.send('Game exit')
                exit
            elif msg.content == 'bot':
                split = str(bot.user).split('#')[0]
                player = Player(bot.user.id,split)
                players.append(player)
                newteks = await addPlayer(teks,players)
                await teksobj.edit(content=newteks)
    
    random.shuffle(players)

    teks_score = 'Scoreboard:\n'
    teks_score_obj = await message.send(teks_score)
    teks_score = await scoreBoard(teks_score,players)
    await teks_score_obj.edit(content=teks_score)
    
    input = await getRandomWord()
    kataterpakai.append(input)
    wait = await message.send(input)
    #before = input

    while True:
        try:
            kata = KBBI(wait.content, auth)
            break
        except:
            input = await getRandomWord()
            kataterpakai.append(input)
            wait = await message.send(input)
            #before = input
            kata = KBBI(wait.content, auth)

    katajson = kata.serialisasi()
    entri = katajson['entri'][0]['nama']
    tekskirim = "**"+entri+" - "+str(len(entri)-1)+"**\n"
    tekskirim += str(kata.__str__(contoh=False,terkait=False,fitur_pengguna=False)+'\n')
    #await message.send('**'+entri+' - '+str(len(entri)-1)+'**')
    #await message.send(kata.__str__(contoh=False,terkait=False,fitur_pengguna=False))

    if "." in entri:
        split = entri.split('.')
        next = split[len(split)-1]
    else:
        next = await makeSplit(entri.lower())

    tekskirim += "Lanjutkan kata dengan awalan **"+next+"**"
    await message.send(tekskirim)

    while True:
        wait = await bot.wait_for('message')
        if wait.author.id == players[0].id:
            check = await checkWord(next,wait.content,roll)
            if wait.content == 'roll':
                if players[0].roll > 0:
                    roll = True
                    randword = await getRandomWord()
                    wait = await message.send(randword)
                    check = await checkWord(next,wait.content,roll)
                else:
                    await message.send('Entek roll mu')
                    
            elif wait.content == 'nyerah':
                if wait.author.name == 'Renton':
                    wait = await message.send('YATIM KOK NYERAH AKWOAKWOAKWOAWKOK')
                else:
                    wait = await message.send(players[0].name+' nyerah anjing gublug')
                if type(players) == list:
                    players.pop(0)
                else:
                    players.popleft()
                if len(players) > 1:
                    continue
                else:
                    await message.send('Game selesai! '+players[0].name+' menang dengan point '+str(players[0].score))
                    break

            elif wait.content == 'exit':
                await message.send('Game exit')
                break
        else:
            check = False

        if check == True:
            try:
                if wait.content in kataterpakai:
                    await message.send('Kata sudah digunakan')
                else:
                    input = wait.content
                    #before = input
                    kata = KBBI(input, auth)
                    kataterpakai.append(input)
                    if roll == False:
                        players[0].addPoint(len(wait.content))
                        if players[0].score >= score:
                            await message.send('Game selesai! '+players[0].name+' menang dengan point '+str(players[0].score))
                            if type(players) == list:
                                players.pop(0)
                            else:
                                players.popleft()
                            kalah = ''
                            for player in players:
                                kalah += '@'+player.name+' , '
                            kalah += 'GOBLOG AWKOAKWOAKWOAKWOAKW'
                            await message.send(kalah)
                            break
                        players = deque(players)
                        players.rotate(1)
                    else:
                        players[0].useRoll()
                        roll = False

                    teks_score = 'Scoreboard:\n'
                    teks_score_obj = await message.send(teks_score)
                    teks_score = await scoreBoard(teks_score,players)
                    await teks_score_obj.edit(content=teks_score)

                    katajson = kata.serialisasi()
                    entri = katajson['entri'][0]['nama']
                    # await message.send('**'+entri+'**')
                    # await message.send(kata.__str__(contoh=False,terkait=False,fitur_pengguna=False))
                    # # print(entri)
                    # # print(kata.__str__(contoh=False))
                    # #print(kata.serialisasi())
                    # if "." in entri:
                    #     split = entri.split('.')
                    #     next = split[len(split)-1]
                    # else:
                    #     next = await makeSplit(entri.lower())
                    # await message.send('Lanjutkan kata dengan awalan **'+next+'**')

                    tekskirim = "**"+entri+" - "+str(len(entri)-1)+"**\n"
                    tekskirim += str(kata.__str__(contoh=False,terkait=False,fitur_pengguna=False)+'\n')
                    
                    if "." in entri:
                        split = entri.split('.')
                        next = split[len(split)-1]
                    else:
                        next = await makeSplit(entri.lower())

                    tekskirim += "Lanjutkan kata dengan awalan **"+next+"**"
                    await message.send(tekskirim)

            except TidakDitemukan as e:
                print(e)
                await message.send("Ngarang blok")

async def addPlayer(teks,players):
    newteks = teks
    co = 1
    for player in players:
        newteks += str(str(co) +'. '+player.name+'\n')
        co += 1
    return newteks

async def scoreBoard(teks_score,players):
    newteks = teks_score
    co = 1
    
    for player in players:
        if co == 1:
            newteks += str(str(co) + '. '+player.name+' ['+str(player.roll)+'] - '+str(player.score)+' <---\n')
        else:
            newteks += str(str(co) + '. '+player.name+' ['+str(player.roll)+'] - '+str(player.score)+'\n')
        co += 1
    newteks+= '---------------\n'
    return newteks

async def checkWord(next,word,roll):
    if roll == False:
        word = word.lower()
        word = word[:len(next)]
        if word == next:
            return True
        else:
            return False
    else:
        return True

async def makeSplit(entri):
    vocal = 0
    word = entri[::-1]
    next = ""
    for alphabet in word:
        if vocal < 2:
            if alphabet == 'a' or alphabet == 'i' or alphabet == 'u' or alphabet == 'e' or alphabet == 'o':
                if vocal < 1 :
                    next += alphabet
                vocal += 1
            else:
                next += alphabet
        else:
            break
    return next[::-1]

async def getRandomWord():
    file = open("words.txt", "r")
    words = file.readlines()
    pos = random.randint(0,10000)
    file.close()
    return words[pos]

class Player:
    id = ''
    name = ''
    score = 0
    roll = 5
    
    def __init__(self,id,name):
        self.id = id
        self.name = name
        self.roll = 5
        self.score = 0
    
    def useRoll(self):
        self.roll -= 1

    def addPoint(self,point):
        self.score += point

# class MyClient(discord.Client):
#     async def on_ready(self):
#         print('Logged on as', self.user)

#     async def on_message(self, message):
#         # don't respond to ourselves
#         if message.author == self.user:
#             return

#         else:
#             teks = 'id anda adalah ' + str(message.author.id)
#             await message.channel.send(teks)

# bot = MyClient()

bot.run('')