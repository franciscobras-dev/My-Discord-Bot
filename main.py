import discord
from discord.ext import commands
import os
import random
import requests
import json
import time
import spotipy
import spotipy.util as util
import youtube_dl
from googletrans import Translator
import subprocess
import openai
from typing import Union


openai.api_key = "yourapikey"

GIPHY_API_KEY = 'yourapikey'

TOKEN = 'yourapikey'
PREFIX = ';'
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix=';', intents=intents)

client = discord.Client(intents=intents)

bot.remove_command('help')

@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name}')
    print(f'With ID: {bot.user.id}')
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Game(name="Para o uso do bot só usar [;help]"))

@bot.command(name='help', help="Use este comando para ver a lista de comandos")
async def custom_help(ctx):

    command_list = sorted(bot.commands, key=lambda cmd: cmd.name)

    embed = discord.Embed(title="Bot Commands", description="Lista de comandos disponiveis", color=discord.Color.gold())

    for command in command_list:
        if not command.hidden:
            embed.add_field(name=command.name, value=command.help, inline=False)

    await ctx.send(embed=embed)

@bot.command(help=" Use este comando para encontrar a latência do bot")
async def ping(ctx):
    start_time = time.time()
    ping_msg = await ctx.send('Pinging...')
    end_time = time.time()
    ping = round((end_time - start_time) * 1000, 2)
    await ping_msg.edit(content=f'Pong! {ping}ms')
  
@bot.command(help=" Use este comando para banir um utilizador")
@commands.has_permissions(ban_members = True)
async def ban(ctx, member : discord.Member, *, reason = None):
    await member.ban(reason = reason)
    await ctx.send('O utilizador foi banido')

@bot.command(help=" Use este comando para desbanir um utilizador")
async def unban(ctx, id: int):
    user = await bot.fetch_user(id)
    await ctx.guild.unban(user)
    await ctx.send('O utilizador foi desbanido')

@bot.command(help=" Use este comando para apagar mensagens")
async def clear(ctx, amount=11):
  if (not ctx.author.guild_permissions.manage_messages):
    await ctx.send('Este comando necessita a permissão (Manage Messages)')
    return
  amount = amount+1
  if amount > 101:
    await ctx.send(' Não pode tentar apagar mais de 100 mensagens')
  else:
    await ctx.channel.purge(limit=amount)
    await ctx.send('Mensagens Apagadas!')

@bot.command(help=" Use este comando para bloquear um canal")
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,send_messages=False)
    await ctx.channel.purge(limit=1)
    await ctx.send('**O Canal foi bloqueado**')

@bot.command(help=" Use este comando para desbloquear um canal")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role,send_messages=True)
    await ctx.channel.purge(limit=1)
    await ctx.send('**O Canal foi desbloqueado**')

@bot.command(help="Use este comando para traduzir a sua mensagem")
async def translate(ctx, lang, *, thing):
    translator = Translator()
    translation = translator.translate(thing, dest=lang)
    await ctx.send(translation.text)

def read_quotes(file_name):
    with open(file_name, "r") as file:
        quotes = file.readlines()
    return quotes

@bot.command(help="Use este comando para enviar uma citação")
async def quote(ctx):  
    quotes = read_quotes("quotes.txt")
    await ctx.send(random.choice(quotes))

with open("bot_intro.txt", "r") as f:
    bot_intro = f.read()

@bot.command(help="Use este comando para falar com IA")
async def gpt(ctx, *, prompt: str):

    input_text = f"{bot_intro}\n\n{prompt}\n"
    

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=input_text,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    ).choices[0].text


    await ctx.send(response)

@bot.command(help="Use este comando para enviar um gif")
async def search_gif(ctx, *, query: str):

    response = requests.get(f'https://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q={query}&limit=1')
    data = response.json()


    if data['data']:

        gif_url = data['data'][0]['images']['original']['url']


        await ctx.send(gif_url)
    else:
        await ctx.send("Couldn't find a gif for that query. Please try again.")

@bot.command(help="Use este comando para obter informações de um utilizador")
async def userinfo(ctx, *, user: Union[discord.Member, int] = None):
    """
    Shows information about a specific user or the user who called the command if no user is provided.
    """
    if not user:

        user = ctx.author
    elif isinstance(user, int):

        try:
            user = await bot.fetch_user(user)
        except discord.errors.NotFound:
            await ctx.send(f"User with ID {user} not found.")
            return
    else:

        pass
    

    embed = discord.Embed(title=f"{user.display_name}'s Info", color=user.color)
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="Name", value=user.name)
    embed.add_field(name="Discriminator", value=user.discriminator)
    embed.add_field(name="ID", value=user.id)
    embed.add_field(name="Created at", value=user.created_at.strftime("%d/%m/%Y %H:%M:%S"))
    
    if isinstance(user, discord.Member):

        embed.add_field(name="Joined at", value=user.joined_at.strftime("%d/%m/%Y %H:%M:%S"))
        embed.add_field(name="Roles", value=', '.join([role.mention for role in user.roles if role != ctx.guild.default_role]))
    
    await ctx.send(embed=embed)


@bot.command(help="Use este comando para convidar um utilizador")
async def invite(ctx, user_id):

    user = await bot.fetch_user(user_id)
    

    invite = await ctx.channel.create_invite()
    

    await user.send(f'Aqui está o seu convite para o servidor: {invite}')

@bot.command(help="Use este comando para enviar o avatar de um utilizador")
async def avatar(ctx, *, member: Union[discord.Member, int] = None):
    if member is None:
        member = ctx.author
    if isinstance(member, int):
        user = await bot.fetch_user(member)
        await ctx.send(user.avatar.url)
    else:
        await ctx.send(member.avatar.url)




bot.run(TOKEN)