import discord
import json
import random
from collections import deque
from discord.ext import commands
from kbbi import KBBI
from kbbi import AutentikasiKBBI
from kbbi import TidakDitemukan

bot = commands.Bot(command_prefix='b!')
bot.remove_command("help")
try:
    auth = AutentikasiKBBI("")
except:
    auth = AutentikasiKBBI("")
file = open("words.txt", "r")
words = file.readlines()
file.close()

@bot.event
async def on_ready():
    print("bot siap")

@bot.command()
async def help(message):
    embed = discord.Embed(title="Salam Jastok", description="***Renton adalah kita***\nBerikut list command yang bisa dipakai dengan prefix **b!**", color=0xff0000)
    embed.add_field(name="b!help", value="kalo ga tau command ini mana bisa message ini muncul blok", inline=False)
    embed.add_field(name="b!plei <highscore> <roll>", value="Maen sambung words, ketik 'bot' kalo mau maen sama alonte", inline=False)
    embed.add_field(name="b!ajak <User>", value="Ajak teman-teman klean buat mengontol", inline=False)
    embed.set_footer(text="author: Alfonsus Enrico @2k21", icon_url="https://pbs.twimg.com/profile_images/976709320631971841/drjCPMfj_400x400.jpg")
    await message.send(embed = embed)

@bot.command()
async def plei(message, highscore = 100, jumlah_roll = 5):
    host = message.author.mention
    await message.send(host+ ' memulai permainan, ketik `melok` untuk ikutan')
    teks = 'Players:\n'
    teksobj = await message.send(teks)
    await main(message, host, teks, teksobj,highscore,jumlah_roll)

@bot.command()
async def ajak(message, friend= '@everyone'):
    await message.send(friend+' mari mengontol kita main gim sambung words')

async def main(message,host,teks,teksobj,highscore,jumlah_roll):
    score = highscore
    kataterpakai = []
    players = []
    bot_sama = False
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
    
    input = getRandomWord()
    wait = await message.send(input)

    while True:
        try:
            kata = KBBI(wait.content, auth)
            kataterpakai.append(input)
            break
        except:
            input = getRandomWord()
            kataterpakai.append(input)
            wait = await message.send(input)
            break
            # kata = KBBI(wait.content, auth)

    katajson = kata.serialisasi()
    entri = katajson['entri'][0]['nama']
    #await message.send('**'+entri+' - '+str(len(entri)-1)+'**')
    #await message.send(kata.__str__(contoh=False,terkait=False,fitur_pengguna=False))

    if "." in entri:
        split = entri.split('.')
        next = split[len(split)-1]
    else:
        next = await makeSplit(entri.lower())

    # tekskirim = "**"+entri+" - "+str(len(entri)-1)+"**\n"
    # tekskirim += str(kata.__str__(contoh=False,terkait=False,fitur_pengguna=False)+'\n')
    # tekskirim += "Lanjutkan kata dengan awalan **"+next+"**"

    embed = discord.Embed(title="**"+entri+" - "+str(len(entri)-1)+"**", color =0x0000ff)
    embed.add_field(name="Penjelasan:",value=str(kata.__str__(contoh=False,terkait=False,fitur_pengguna=False)),inline=False)
    embed.set_footer(text="Lanjutkan kata dengan awalan "+next+"")
    teks_score = await scoreBoard(players)

    teks_score_obj = await message.send(embed=teks_score)
    before = await message.send(embed=embed)

    while True:
        bot_words = []
        if players[0].id == bot.user.id:
            if bot_sama == True:
                wait = await message.send("roll")
                bot_sama = False
            else:
                for index, word in enumerate(words):
                    if next in word[:len(next)]:
                        bot_words.append(word)
                        try:
                            if words[index+1][:len(next)] != next:
                                break
                        except:
                            break   
                if len(bot_words) == 0:
                    wait = await message.send("roll")
                    # print('kata tidak ditemukan, kirim roll')
                else:
                    while True:
                        pos = random.randint(0,(len(bot_words)-1))
                        # print('pos: '+str(pos))
                        # print(str(bot_words))
                        # print('word[pos]: '+bot_words[pos])
                        try:
                            check = await checkWord(next,bot_words[pos],roll)
                            if check == True and bot_words[pos] not in kataterpakai:
                                wait = await message.send(bot_words[pos])
                                # print('kirim')
                                # print('pos: '+str(pos))
                                # print('word[pos]: '+bot_words[pos])
                                break
                        except Exception as e:
                            print('exception check: '+str(e))
                bot_words.clear()
        else:
            wait = await bot.wait_for('message')

        if wait.author.id == players[0].id:
            check = await checkWord(next,wait.content,roll)
            if wait.content == 'roll':
                if players[0].roll > 0:
                    roll = True
                    randword = getRandomWord()
                    while True:
                        try:
                            KBBI(randword,auth)
                            print('try: '+randword)
                            break
                        except Exception as e:
                            randword = getRandomWord()
                            print(randword)
                            break
                    wait = await message.send(randword)
                    check = await checkWord(next,wait.content,roll)                    
                else:
                    if wait.author.id == bot.user.id:
                        await message.send('nyerah')
                    await message.send('**Entek roll mu**')
                        
            elif wait.content == 'nyerah':
                if wait.author.name == 'Renton':
                    wait = await message.send('YATIM KOK NYERAH AKWOAKWOAKWOAWKOK')
                else:
                    wait = await message.send("**"+players[0].name+" nyerah anjing gublug**")
                if type(players) == list:
                    players.pop(0)
                else:
                    players.popleft()
                if len(players) > 1:
                    continue
                else:
                    await message.send("**Game selesai! "+players[0].name+" menang dengan point "+str(players[0].score)+"**")
                    break

            elif wait.content == 'exit':
                await message.send('Game exit')
                try:
                    await teks_score_obj.delete()
                    await before.delete()
                except:
                    pass
                break
        else:
            check == False
            pass

        if check == True:
            try:
                if wait.content in kataterpakai:
                    if wait.author.id == bot.user.id:
                        bot_sama = True
                    await message.send("**Kata sudah digunakan**")
                else:
                    input = wait.content
                    kata = KBBI(input, auth)
                    #print('Benar'+input+' - '+str(len(input)))                    
                    await teks_score_obj.delete()
                    await before.delete()
                    kataterpakai.append(input)
                    if roll == False:
                        players[0].addPoint(len(wait.content))
                        if players[0].score >= score:
                            await message.send("**Game selesai! "+players[0].name+" menang dengan point "+str(players[0].score)+"**")
                            if type(players) == list:
                                players.pop(0)
                            else:
                                players.popleft()
                            kalah = ''
                            for player in players:
                                kalah += '@'+player.name+' , '
                            kalah += "**GOBLOG AWKOAKWOAKWOAKWOAKW**"
                            await message.send(kalah)
                            break
                        players = deque(players)
                        players.rotate(1)
                    else:
                        players[0].useRoll()
                        roll = False

                    katajson = kata.serialisasi()
                    entri = katajson['entri'][0]['nama']

                    if "." in entri:
                        split = entri.split('.')
                        next = split[len(split)-1]
                    else:
                        next = await makeSplit(entri.lower())
                    
                    embed = discord.Embed(title="**"+entri+" - "+str(len(entri)-1)+"**", color =0x0000ff)
                    embed.add_field(name="Penjelasan:",value=str(kata.__str__(contoh=False,terkait=False,fitur_pengguna=False)),inline=False)
                    embed.set_footer(text="Lanjutkan kata dengan awalan "+next+"")
                    teks_score = await scoreBoard(players)

                    teks_score_obj = await message.send(embed=teks_score)
                    before = await message.send(embed = embed)

            except TidakDitemukan as e:
                print(e)
                await message.send("Ngarang blok, "+players[0].name+" -1 poin")
                players[0].wrong()

async def addPlayer(teks,players):
    newteks = teks
    co = 1
    for player in players:
        newteks += str(str(co) +'. '+player.name+'\n')
        co += 1
    return newteks

async def scoreBoard(players):
    teks_score = ''
    co = 1
    for player in players:
        if co == 1:
            teks_score += str(str(co) + '. '+player.name+' ['+str(player.roll)+'] - '+str(player.score)+' <---\n')
        else:
            teks_score += str(str(co) + '. '+player.name+' ['+str(player.roll)+'] - '+str(player.score)+'\n')
        co += 1

    embed = discord.Embed(title="Sambung Kata", author=str(bot.user).split('#')[0], icon=bot.user.avatar_url, color=0x0088ff)
    embed.add_field(name="Scoreboard:", value=teks_score, inline=False)
    return embed

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

def getRandomWord():
    pos = random.randint(0,(len(words)-1))
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

    def wrong(self):
        self.score -= 1
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