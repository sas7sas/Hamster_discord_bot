import discord
from discord.ext import commands
from discord import utils
import data
import json
import requests
client = commands.Bot(command_prefix = data.PREFIX)
client.remove_command ('help')

@client.event
async def on_ready():
    print ('Бот активирован.')
    await client.change_presence (status = discord.Status.online, activity = discord.Game(name = 'Visual Studio Code'))

@client.event
async def on_command_error(ctx, error):
    pass

@client.event
async def on_member_join(member):
    emb=discord.Embed(title = "присоединился к серверу", color=0xfffffe)
    emb.set_author(name = member.name, icon_url= member.avatar_url)
    emb.add_field (name = 'привет :wave:', value = '{}'.format(member.mention))
    channel = client.get_channel(data.ENTER_EXIT_CHANNEL)
    await channel.send (embed = emb)
    role = discord.utils.get(member.guild.roles, id=data.autoRoleId)
    await member.add_roles(role)

@client.event
async def on_member_remove(member):
    emb=discord.Embed(title = "покинул сервер", color=0x000001)
    emb.set_author(name = member.name, icon_url= member.avatar_url)
    emb.add_field (name = 'пока :wave:', value = '{}'.format(member.mention))
    channel = client.get_channel(data.ENTER_EXIT_CHANNEL)
    await channel.send (embed = emb)

@client.event
async def on_raw_reaction_add(payload):
    if payload.message_id == data.POST_ID:
        channel = client.get_channel(payload.channel_id) # получаем объект канала
        message = await channel.fetch_message(payload.message_id) # получаем объект сообщения
        member = utils.get(message.guild.members, id=payload.user_id) # получаем объект пользователя, который поставил реакцию
        try:
            emoji = str(payload.emoji) # эмодзи, который выбрал юзер
            role = utils.get(message.guild.roles, id=data.ROLES[emoji]) # объект выбранной роли (если есть)
            if(len([i for i in member.roles if i.id not in data.EXCROLES]) <= data.MAX_ROLES_PER_USER):
                await member.add_roles(role)
            else:
                await message.remove_reaction(payload.emoji, member)
        except Exception as e:
            print(repr(e))

@client.event
async def on_message(message):
    if message.channel == client.get_channel(data.SUGGESTIONS_CHANNEL):
        await message.add_reaction('✅')
        await message.add_reaction('⛔')
    if message.channel == client.get_channel(data.GREETER_CHANNEL):
        await message.add_reaction('✅')
    await client.process_commands(message)

# clear mess

@client.command(pass_context = True)
@commands.has_permissions(kick_members = True)

async def очистить(ctx, amount: int):
    await ctx.channel.purge(limit = amount)

@очистить.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.purge(limit = 1)
        message = await ctx.send('Ошибка! Недостаточно прав...')
        await message.delete(delay = 3)

# Kick

@client.command(pass_context = True)
@commands.has_permissions(kick_members = True)

async def кик(ctx, member: discord.Member, *, reason = None):
    emb = discord.Embed (title = 'Kick :wave:', colour = discord.Color.red())
    await ctx.channel.purge(limit = 1)
    await member.kick(reason = reason)
    emb.set_author (name = member.name, icon_url = member.avatar_url)
    emb.add_field (name = 'Kicked user', value = '{}'.format(member.mention))
    emb.set_footer (text = 'Kicked by: {}'.format (ctx.author.name), icon_url = ctx.author.avatar_url)
    channel = client.get_channel(data.LOG_CHANNEL)
    await channel.send (embed = emb)

@кик.error
async def kick_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.channel.purge(limit = 1)
        message = await ctx.send('Ошибка! Участник не найден...')
        await message.delete(delay = 3)
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.purge(limit = 1)
        message = await ctx.send('Ошибка! Недостаточно прав...')
        await message.delete(delay = 3)

# Ban

@client.command(pass_context = True)
@commands.has_permissions(kick_members = True)

async def бан(ctx, member: discord.Member, *, reason = None):
    emb = discord.Embed (title = 'Ban :lock:', colour = discord.Color.dark_red())
    await ctx.channel.purge(limit = 1)
    await member.ban(reason = reason)
    emb.set_author (name = member.name, icon_url = member.avatar_url)
    emb.add_field (name = 'Banned user', value = '{}'.format(member.mention))
    emb.set_footer (text = 'Banned by: {}'.format (ctx.author.name), icon_url = ctx.author.avatar_url)
    channel = client.get_channel(data.LOG_CHANNEL)
    await channel.send (embed = emb)

@бан.error
async def ban_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.channel.purge(limit = 1)
        message = await ctx.send('Ошибка! Участник не найден...')
        await message.delete(delay = 3)
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.purge(limit = 1)
        message = await ctx.send('Ошибка! Недостаточно прав...')
        await message.delete(delay = 3)

# mute

@client.command()
@commands.has_permissions(kick_members = True)

async def мут(ctx, member: discord.Member):
    emb = discord.Embed (title = 'Mute :mute:', colour = discord.Color.gold())
    await ctx.channel.purge(limit = 1)
    mute_role = discord.utils.get(ctx.message.guild.roles, name = 'MUTED')
    await member.add_roles (mute_role)
    emb.set_author (name = member.name, icon_url = member.avatar_url)
    emb.add_field (name = 'Muted user', value = '{}'.format(member.mention))
    emb.set_footer (text = 'Muted by: {}'.format (ctx.author.name), icon_url = ctx.author.avatar_url)
    channel = client.get_channel(data.LOG_CHANNEL)
    await channel.send (embed = emb)

@мут.error
async def mute_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.channel.purge(limit = 1)
        message = await ctx.send('Ошибка! Участник не найден...')
        await message.delete(delay = 3)
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.purge(limit = 1)
        message = await ctx.send('Ошибка! Недостаточно прав...')
        await message.delete(delay = 3)

# unmute

@client.command()
@commands.has_permissions(kick_members = True)

async def размут(ctx, member: discord.Member):
    emb = discord.Embed (title = 'Unmute :speaker:', colour = discord.Color.green())
    await ctx.channel.purge(limit = 1)
    mute_role = discord.utils.get(ctx.message.guild.roles, name = 'MUTED')
    await member.remove_roles (mute_role)
    emb.set_author (name = member.name, icon_url = member.avatar_url)
    emb.add_field (name = 'Unmuted user', value = '{}'.format(member.mention))
    emb.set_footer (text = 'Unmuted by: {}'.format (ctx.author.name), icon_url = ctx.author.avatar_url)
    channel = client.get_channel(data.LOG_CHANNEL)
    await channel.send (embed = emb)

@размут.error
async def unmute_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.channel.purge(limit = 1)
        message = await ctx.send('Ошибка! Участник не найден...')
        await message.delete(delay = 3)
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.purge(limit = 1)
        message = await ctx.send('Ошибка! Недостаточно прав...')
        await message.delete(delay = 3)

#bot_say_in

@client.command()
@commands.has_permissions(kick_members = True)

async def транс(ctx, kanal, *, arg):
    await client.get_channel(int(kanal)).send (arg)
    await ctx.channel.purge(limit = 1)

@транс.error
async def sayin_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.channel.purge(limit = 1)
        message = await ctx.send('Ошибка! Канал не найден...')
        await message.delete(delay = 3)
    if isinstance(error, commands.MissingPermissions):
        await ctx.channel.purge(limit = 1)
        message = await ctx.send('Ошибка! Недостаточно прав...')
        await message.delete(delay = 3)

# help

@client.command(pass_context = True)

async def помощь(ctx):
    emb = discord.Embed (title = 'Навигация по командам:')
    emb.add_field(name ='{}помощь_развлечения'.format(data.PREFIX), value = 'Раздел "Развлечения"', inline=False)
    emb.add_field(name ='{}помощь_модерация'.format(data.PREFIX), value = 'Раздел "Модерация"', inline=False)
    await ctx.send ( embed = emb )

# help_mod

@client.command(pass_context = True)
@commands.has_permissions(kick_members = True)

async def помощь_модерация(ctx):
    emb = discord.Embed (title = 'Навигация по командам:')
    emb.add_field(name ='{}очистить <кол-во сообщений>'.format(data.PREFIX), value = 'Очистка чата', inline=False)
    emb.add_field(name ='{}бан <участник>'.format(data.PREFIX), value = 'Бан участника', inline=False)
    emb.add_field(name ='{}кик <участник>'.format(data.PREFIX), value = 'Кик участника', inline=False)
    emb.add_field(name ='{}мут <участник>'.format(data.PREFIX), value = 'Мут участника', inline=False)
    emb.add_field(name ='{}размут <участник>'.format(data.PREFIX), value = 'Размут участника', inline=False)
    emb.add_field(name ='{}транс <id канала> <сообщение>'.format(data.PREFIX), value = 'Сообщение от имени бота', inline=False)
    await ctx.send ( embed = emb )

# help_fun

@client.command(pass_context = True)

async def помощь_развлечения(ctx):
    emb = discord.Embed (title = 'Навигация по командам:')
    emb.add_field(name ='{}лис'.format(data.PREFIX), value = 'Пикча с лисой', inline=False)
    emb.add_field(name ='{}кот'.format(data.PREFIX), value = 'Пикча с котом', inline=False)
    emb.add_field(name ='{}пес'.format(data.PREFIX), value = 'Пикча с псом', inline=False)
    emb.add_field(name ='{}скажи <сообщение>'.format(data.PREFIX), value = 'Сообщение от имени бота', inline=False)
    await ctx.send ( embed = emb )

@client.command()

async def скажи(ctx, *, arg):
    await ctx.send (arg)

@client.command()
async def лис(ctx):
    response = requests.get('https://some-random-api.ml/img/fox') # Get-запрос
    json_data = json.loads(response.text) # Извлекаем JSON
    embed = discord.Embed(color = 0xff9900, title = 'Лиса') # Создание Embed'a
    embed.set_image(url = json_data['link']) # Устанавливаем картинку Embed'a
    await ctx.send(embed = embed) # Отправляем Embed

@client.command()
async def кот(ctx):
    response = requests.get('https://some-random-api.ml/img/cat')
    json_data = json.loads(response.text)
    embed = discord.Embed(color = 0xff9900, title = 'Кот')
    embed.set_image(url = json_data['link'])
    await ctx.send(embed = embed)

@client.command()
async def пес(ctx):
    response = requests.get('https://some-random-api.ml/img/dog')
    json_data = json.loads(response.text)
    embed = discord.Embed(color = 0xff9900, title = 'Пес')
    embed.set_image(url = json_data['link'])
    await ctx.send(embed = embed)

# Connect
client.run(data.TOKEN)