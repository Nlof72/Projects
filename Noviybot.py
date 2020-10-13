import discord
from discord.ext import commands
from discord.utils import get
from config import settings
from tabulate import tabulate
import json
import sqlite3
import random
import datetime


random.seed()
conn = sqlite3.connect("Discord.db") # или :memory:
cursor = conn.cursor()

'''cursor.execute("""CREATE TABLE users 
( id int, nickname	text, mention text, money int, rep_rank text, lvl int, xp int)
""")'''

cursor.execute("SELECT * FROM users")
print(tabulate(cursor.fetchall()))


bot = commands.Bot(command_prefix = settings['prefix'])



@bot.event
async def on_ready():
    print("Bot Has been runned")#сообщение о готовности
    for guild in bot.guilds:#т.к. бот для одного сервера, то и цикл выводит один сервер
        print(guild.id)#вывод id сервера
        global  serv
        serv=guild#без понятия зачем это
        for member in guild.members:#цикл, обрабатывающий список участников
            cursor.execute(f"SELECT id FROM users where id={member.id}")#проверка, существует ли участник в БД
            if cursor.fetchone()==None:#Если не существует
                cursor.execute(f"INSERT INTO users VALUES ({member.id}, '{member.name}', '<@{member.id}>', 500, 'S', 0, 0)")#вводит все данные об участнике в БД
            else:#если существует
                pass
            conn.commit()#применение изменений в БД
    global chan
    chan_id = guild.text_channels[0].id
    chan = guild.get_channel(chan_id)



@bot.event
async def on_member_join(member):
    cursor.execute(f"SELECT id FROM users where id={member.id}")#все также, существует ли участник в БД
    if cursor.fetchone()==None:#Если не существует
        cursor.execute(f"INSERT INTO users VALUES ({member.id}, '{member.name}', '<@{member.id}>', 500, 'S',0,0)")#вводит все данные об участнике в БД
    else:#Если существует
        pass
    conn.commit()#применение изменений в БД


'''@bot.event
async def on_message(message):
    print(message)''' #Работет на сообщения боту (содержимое брать из dmChannel)




@bot.event
async def on_voice_state_update(member, before, after):
    global aa
    if before.channel == None:
        print(member.id)
        aa = int(datetime.timedelta(seconds=datetime.datetime.now().second, minutes=datetime.datetime.now().minute, hours=datetime.datetime.now().hour).seconds)
        #print(datetime.timedelta(seconds=datetime.datetime.now().second, minutes=datetime.datetime.now().minute, hours=datetime.datetime.now().hour).seconds)
    if after.channel == None:
        b = int(datetime.timedelta(seconds=datetime.datetime.now().second, minutes=datetime.datetime.now().minute, hours=datetime.datetime.now().hour).seconds)
        #print(datetime.timedelta(seconds=datetime.datetime.now().second, minutes=datetime.datetime.now().minute, hours=datetime.datetime.now().hour).seconds)
        if aa == 0:
            b = 0
        #print(b-aa)
        for row in cursor.execute(f"SELECT xp,lvl,money FROM users where id={member.id}"):
            expi = row[0] + (b - aa)
            cursor.execute(f'UPDATE users SET xp={expi} where id={member.id}')
            lvch = expi / (((row[1] + 1) * 1000))
            #print(int(lvch))
            lv = int(lvch)
            if row[1] < lv:  # если текущий уровень меньше уровня, который был рассчитан формулой выше,...
                await chan.send(f'Новый уровень!')  # то появляется уведомление...
                bal = row[2] + (1000 * lv)
                cursor.execute(
                    f'UPDATE users SET lvl={lv}, money={bal} where id={member.id}')  # и участник получает деньги
        conn.commit()  # применение изменений в БД



@bot.command(aliases=['inf'])
async def stat(ctx):  # команда _account (где "_", ваш префикс указаный в начале)
    table = [["nickname", "money", "lvl", "xp", "rank"]]
    for row in cursor.execute(f"SELECT nickname,money,lvl,xp,rep_rank FROM users where id={ctx.author.id}"):
        table.append([row[0], row[1], row[2], row[3], row[4]])
        await ctx.send(f">\n{tabulate(table)}")


@bot.command(aliases=['hi', 'h'])
async def hello(ctx):
    author = ctx.message.author
    await ctx.send(f'Дорроу, {author.mention}!')

@bot.command()
async def game(ctx): #Старт игры в секретный гитлер нужна проверка на админа(добавить)
    global start
    start = True
    global prez_list
    prez_list = []
    words = ['Либ', 'фаш', 'Гит']
    player_sp = []
    a = ctx.message.content
    hitisfash = False
    count = int(a[a.find(' ') + 1:len(a)])
    pres = random.randint(0, count-1)
    print(pres)
    if count < 7:
        fash = 1
        lib = count - fash+1
        hitisfash = True
    elif (count > 6) and (count < 9):
        fash = 2
        lib = count - fash + 1
    else:
        fash = 3
        lib = count - fash + 1
    if count == 2:
        fash =0
        lib = count - fash
    try:
        cursor.execute("""CREATE TABLE secret 
            ( id int, nickname	text, mention text, role text, live int, president int, chancellor int, number int) 
            """)
    except Exception:
        cursor.execute("""DROP TABLE secret 
            """)
        conn.commit()
        cursor.execute("""CREATE TABLE secret 
                    ( id int, nickname	text, mention text, role text, live int, president int, chancellor int, number int) 
                    """)  # Роли распределяются от 0 до 2, где 0 либерал, 1 фаш, 2 секретный'''


    #>>> # Six roulette wheel spins (weighted sampling with replacement)
    #>>> choices(['red', 'black', 'green'], [18, 18, 2], k=6)
    #['red', 'green', 'black', 'black', 'red', 'black']
    #Переделать с использованием этого ^

    #Добавить поля в бд с презедентом, канцлером, живой

    schet = 0
    for ro in serv.roles:
        if ro.name == 'Игрок':
            for player in ro.members:
                secret_word = random.choice(words)
                if secret_word == 'Гит':
                    words.remove('Гит')
                if secret_word == 'фаш':
                    fash -= 1
                if secret_word == 'Либ':
                    lib -= 1
                if fash == 0:
                    words.remove('фаш')
                    fash = -1
                if lib == 0:
                    words.remove('Либ')
                    lib = -1
                cursor.execute(
                    f"INSERT INTO secret VALUES ({player.id}, '{player.name}', '@{player.id}', '{secret_word}', {1}, {-1}, {-1}, {schet})")  # вводит все данные об участнике в БД
                await player.send(f"{secret_word}")
                player_sp.append(player.name)
                if schet == pres:
                    await player.send("Ну шо, ты презедент, подравляю, выбирай канцлера!")
                    cursor.execute(
                        f'UPDATE secret SET president={1}')
                    prez_list.append(player.name)
                schet +=1
                #Написать роль в лс
            fash_sp = [["Ник", "Роль"]]
            for row in cursor.execute("SELECT id, nickname, role FROM secret"):
                if (row[2] == 'фаш') or (row[2] == 'Гит'):
                    fash_sp.append([row[1], row[2]])
            k = 1
            for player in ro.members:
                try:
                    if player.name in fash_sp[k][0]:
                        if hitisfash:
                            await player.send(f"Список союзников\n {tabulate(fash_sp)}")
                        elif fash_sp[k][1] == 'Гит':
                            continue
                        else:
                            await player.send(f"Список союзников\n {tabulate(fash_sp)}")
                except:
                    print("Недостаточно игроков!!!!")
                k += 1
            global rolegame
            rolegame = ro
            conn.commit()
            cursor.execute("SELECT id, nickname, role FROM secret")
            print(tabulate(cursor.fetchall()))
            print(player_sp)
            print(tabulate(fash_sp))
            print(prez_list)
    #await guild.members[0].send('hi')  работает
    #await chan.send(':red_square:')
    #await chan.send(':blue_square:')

@bot.command()
async def chancellor(ctx):
    try:
        if start:
            global chancellor_list
            chancellor_list = []
            a = ctx.message.content
            b = ctx.message.author.name
            print(b)
            chancellor = a[a.find(' ') + 1:len(a)]
            if b in prez_list:
                if chancellor not in prez_list:
                    cursor.execute(f"UPDATE secret SET chancellor={1} where nickname='{chancellor}'")
                    chancellor_list.append(b)
                    await chan.send(f"У нас новый канцлер, поздравляем {chancellor} c победой на выборах!!!")
                else:
                    await chan.send(f"Ты являешься президентом или канцлером уже {chancellor}!!!!!! ")
            else:
                await chan.send(f"Ты не являешся президентом {b}!!!")
    except:
        await ctx.send('Игра не началась!')


@bot.command()
async def change(ctx):
    a = ctx.message.content
    zvanie = a[a.find(' ')+1:len(a)]
    cursor.execute(
        f'UPDATE users SET rep_rank="{zvanie}" where id={ctx.author.id}')
    conn.commit()
    print(a[a.find(' ')+1:len(a)])

@bot.command(aliases = ['j'])
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.send(f"Бот присоединился к каналу -> {channel}")


@bot.command(aliases = ['q'])
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)
    await ctx.send('<Честь имею>')
    if voice and voice.is_connected():
        await voice.disconnect()
    else:
        voice = await channel.connect()
        await ctx.send(f"Бот уехал отсюда -> {channel}")


bot.run(settings['token'])