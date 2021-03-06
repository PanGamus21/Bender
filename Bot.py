﻿import discord
import json
import os
from discord.ext import commands

TOKEN = str(os.environ.get('TOKEN')) 
bot = commands.Bot(command_prefix='b.')
games = {}

@bot.event
async def on_ready():
    print('bot started')

@bot.event
async def on_member_join(member):
    await bot.send_message(member, 'Приветствую на сервере {}! Я покажу с чего начать. Сначала заходи в канал <#493139750211813377> и читай его полностью. Затем просто будь активным и получай новый уровень, тем самым получая новый возможности.\nЖелаю хорошо провести время!'.format(member.server.name
))
    with open('users.json', 'r') as f:
        users = json.load(f)
    
    await update_data(users, member)
    
    with open('users.json', 'w') as f:
        json.dump(users, f)


@bot.event
async def on_message(message):
    BadWords = open('badwords.txt', encoding='windows-1251')
    author = message.author
    content = str(message.content)
    channel = message.channel
    print('{}: {} from {}'.format(author, content, channel))
    for i in BadWords:
        if content.lower().find(i[:-1]) != -1:
            print('finding {} result: {}'.format(i[:-1], content.lower().find(i[:-1])))
            await bot.send_message(channel, 'Без мата :ok_hand:')
            await bot.delete_message(message)
            break
    with open('users.json', 'r') as f:
        users = json.load(f)
    
    await update_data(users, message.author)
    await add_experience(users, message.author, 5, 'give', channel)
    
    with open('users.json', 'w') as f:
        json.dump(users, f)

    await bot.process_commands(message)

async def update_data(users, user):
    if not user.id in users:
        users[user.id] = {}
        users[user.id]['experience'] = 0
        users[user.id]['level'] = 1
        users[user.id]['warn'] = 0
        
async def add_experience(users, user, exp, mode, channel):
    if mode.lower() == 'give':
        users[user.id]['experience'] += exp
    elif mode.lower() == 'set':
        users[user.id]['experience'] = exp
    experience = users[user.id]['experience']
    lvl_start = users[user.id]['level']
    lvl_end = int(experience ** (1/4))
    if lvl_start < lvl_end:
        await bot.send_message(channel, "{}, Твой уровень повышен: {}!".format(user.mention, lvl_end))
        users[user.id]['level'] = lvl_end
    
async def level_up(users, user):
    users[user.id]['experience'] = (users[user.id]['level'] + 1) ** 4
    await add_experience(users, user, 0)
    
 
@bot.command(pass_context = True)
async def find(ctx, game):
    print('Finding match')
    channel = ctx.message.channel
    author = ctx.message.author
    if game in games and games[game] != set():
        games[game].add(author)
        if len(games[game]) >= 2:
            await bot.send_message(channel, 'Подбор завершен с результатом:```\nИгра: {}\nИгроки: {}, {}```'.format(game, games[game].pop(), games[game].pop()))
    else:
        games[game] = set([author])
        await bot.send_message(channel, 'Подбор начался')
        
@bot.command(pass_context = True)
async def level(ctx, name=''):
    channel = ctx.message.channel
    members = ctx.message.server.members
    member = ctx.message.author
    author = ctx.message.author
    for i in members:
        if i.mention == name:
            member = i
            break    
    with open('users.json', 'r') as f:
        users = json.load(f)
    embed = discord.Embed(
        colour = discord.Colour.blue()
    )
    if author.id == '498163342079426570':
        await bot.say(users[member.id]['level'])
    else:
        embed.set_author(name=member.name, icon_url=member.avatar_url)
        embed.add_field(name='Уровень',value=users[member.id]['level'])
        embed.add_field(name='Опыт',value=str(users[member.id]['experience'])+' / '+ str((users[member.id]['level']+1) ** 4)) 
        await bot.say(embed=embed)
    with open('users.json', 'w') as f:
        json.dump(users, f)  

@bot.command(pass_context = True)
async def give(ctx, giving='', name='', item='0'):
    channel = ctx.message.channel
    while giving == '':
        await bot.send_message(channel, 'Укажите что хотите выдать')
        msg = await bot.wait_for_message(author=ctx.message.author)
        giving = msg.content
    while name == '':
        await bot.send_message(channel, 'Укажите кому хотите выдать')
        msg = await bot.wait_for_message(author=ctx.message.author)
        name = msg.content
    members = ctx.message.server.members
    member = ctx.message.author
    for i in members:
        if i.mention == name:
            member = i
            break
    if giving.lower() == 'level':
        with open('users.json', 'r') as f:
            users = json.load(f)
    
        await update_data(users, member)
        await add_experience(users, member, int(item) ** 4, 'set', channel)
    
        with open('users.json', 'w') as f:
            json.dump(users, f)
    elif giving.lower() == 'hello':
        await on_member_join(member)

@bot.command(pass_context = True)
@commands.has_role('Тестер ботов')
async def id (ctx, name=''):
    channel = ctx.message.channel
    members = ctx.message.server.members
    member = ctx.message.author
    for i in members:
        if i.mention == name:
            member = i
            break    
    if name == '':
        await bot.send_message(channel, channel.id)
    else:
        await bot.send_message(channel, member.id)
        
@bot.command(pass_context=True)
async def warn(ctx, name):
    members = ctx.message.server.members
    member = ctx.message.author
    for i in members:
        if i.mention == name:
            member = i
            break
    if member == ctx.message.author:
        bot.say('Пользователь {} не найдей'.format(name))
        return 
    with open('users.json', 'r') as f:
            users = json.load(f)
    await update_data(users, ctx.message.author)
    users[member.id]['warn'] += 1
    if users[member.id]['warn'] >= 3:
        bot.ban(member, delete_message_days=1)
    
    with open('users.json', 'w') as f:
            json.dump(users, f)
bot.run(TOKEN)
