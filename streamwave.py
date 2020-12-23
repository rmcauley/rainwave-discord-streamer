#Discord bot controls to connect to rainwave via selenium and start streaming music from the selenium browser to whatever discord
#channel the bot is in.
import os
from discord.ext import commands
from discord import FFmpegPCMAudio as ffmpeg
from dotenv import load_dotenv

#load environment variables. Discord Tokens should not be hard coded in
#The Discord Bot is already iinitialized on discord's side.
#DISCORD_TOKEN is how we control it specifically.
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#define bot command prefix
bot = commands.Bot(command_prefix='!') 

#show options
@bot.command(name='h')
async def show_help(ctx):
    await ctx.send(
            "Type !play to start playing music.\n"
            "Type !stop to stop the music.\n"
            "!play <channel> to specify a rainwave channel"
            )

#define action if input command is play
#TODO: allow users to change station without having to stop the music and start it again.
@bot.command(name='play')
async def start_playing(ctx, arg=""):
    if arg and isinstance(arg, str): #discord should pass arg as a string, but I'm paranoid.
        if arg.lower() == "chiptune":
            source = "http://allrelays.rainwave.cc/chiptune.mp3"
        elif arg.lower() == "ocr" or arg.lower() == "oc" or arg.lower() == "overclocked" or arg.lower() == "ocremix":
            source = "http://allrelays.rainwave.cc/ocremix.mp3"
        elif arg.lower() == "game":
            source = "http://allrelays.rainwave.cc/game.mp3"
        elif arg.lower() == "covers":
            source = "http://allrelays.rainwave.cc/covers.mp3"
        else:
            source = "http://allrelays.rainwave.cc/all.mp3"
    else:
        source = "http://allrelays.rainwave.cc/all.mp3"
    channel = ctx.author.voice.channel
    vc = await channel.connect()
    audio_source = ffmpeg(source)
    vc.play(audio_source)

#define action if input command is stop.
#Action should be to leave the voice channel altogether.
#TODO: This throws an error if the bot was playing music before leaving.
#      While this doesn't prevent it from playing music in the future, it should be cleaner.
@bot.command(name='stop')
async def stop_playing(ctx):
    for x in bot.voice_clients:
        if x.guild == ctx.message.guild: #in case of multiple servers running the bot
            return await x.disconnect()
    await ctx.send('Disconnecting!')

#Actually run the bot, now that we've set up the commands.
bot.run(TOKEN)
