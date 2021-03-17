import discord
import json
from discord.ext import commands
from kbbi import KBBI
from kbbi import AutentikasiKBBI

bot = commands.Bot(command_prefix='b!')
auth = AutentikasiKBBI("","")

@bot.event
async def on_ready():
    print("bot siap mengontol")

@bot.command()
async def tes(message):
    await message.send(f'{message.author.mention}\'s id: `{message.author.id}`') 

@bot.command()
async def plei(message):
    #main = True
    host = message.author.mention
    await message.send(host+ ' memulai permainan, ketik `join` untuk ikutan')
    teks = 'Players:\n'
    teksobj = await message.send(teks)
#   print(message.message.id)
    await main(message, host, teks, teksobj)

async def main(message,host,teks,teksobj):
    players = []
    players.append(message.author.name)
    newteks = await addPlayer(players,teks)
    await teksobj.edit(content=newteks)
    while True:
        msg = await bot.wait_for('message')
        if msg.content == 'join':
            player = msg.author.name
            exist = False
            for name in players:
                if player == name:
                    exist = True
                    break
            if exist == False:
                players.append(msg.author.name)
                newteks = await addPlayer(players,teks)
                await teksobj.edit(content=newteks)
        
        if msg.author.mention == host:
            if msg.content == 'start':
                if len(players) >= 2:
                    break
                else:
                    await message.send('Permainan membutuhkan minimal 2 orang')
            elif msg.content == 'melok':
                players.append(str(bot.user))
                newteks = await addPlayer(players,teks)
                await teksobj.edit(content=newteks)
    
    input = 'lontong'
    kata = KBBI(input, auth)
    katajson = kata.serialisasi()
    entri = katajson['entri'][0]['nama']
    await message.send('**'+entri+'**')
    await message.send(kata.__str__(contoh=False))
    split = entri.split('.')
    next = split[len(split)-1]
    await message.send('Lanjutkan kata dengan awalan **'+next+'**')

    while True:
        try:
            wait = await bot.wait_for('message')
            print('tes')
            check = await checkWord(next,wait.content)
            print(check)
            if check == True:
                input = wait.content
                kata = KBBI(input, auth)
                katajson = kata.serialisasi()
                entri = katajson['entri'][0]['nama']
                await message.send('**'+entri+'**')
                await message.send(kata.__str__(contoh=False))
                # print(entri)
                # print(kata.__str__(contoh=False))
                #print(kata.serialisasi())
                split = entri.split('.')
                next = split[len(split)-1]
                await message.send('Lanjutkan kata dengan awalan **'+next+'**')

        except:
            print('kata tidak ditemukan')

async def addPlayer(players,teks):
    newteks = teks
    co = 1
    for player in players:
        newteks += str(str(co) +'. '+player+'\n')
        co += 1
    return newteks

async def checkWord(next,word):
    print('next:' +next)
    word = word.lower()
    word = word[:len(next)]
    print('word:'+word)
    if word == next:
        print('masuk true')
        return True
    else:
        return False 

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