# Written in Python 3.7.1

import asyncio
import discord
import time
import datetime
import traceback
import os
import subprocess

from config import *
from user import *
from website import *

client = discord.Client()

config = Config()
P = config.prefix

loading_embed = discord.Embed()
loading_embed.set_image(url='https://i.ibb.co/Y49LpjD/Please-Stand-By.gif')
loading_embed.set_author(name='Loading...', icon_url='https://www.playstation.com/en-gb/1.36.45/etc/designs/pdc/clientlibs_base/images/nav/avatar-default-2x.png')

@client.event
async def on_message(message):
    if message.author == client.user:
        return # Ensuring the bot won't respond to himself

    if message.author.bot:
        return # Ensuring the bot won't respond to other bots

    if message.content.lower() == P+'help' or message.content.lower() == P+'h':
        embed = discord.Embed(title='Source code', url='https://github.com/liav22/PSBot', colour=0x1e90ff)
        embed.add_field(name='Information:', value="""
            Command list: `{p}help` | Shortcut `~h`
            Changelog: `{p}changelog` | Shortcut `{p}log`""".format(p=P), inline=False)
        embed.add_field(name='General Commands:', value="""
            Search profile: `{p}user PSN` | Shortcut: `{p}u`
            Search prices: `{p}price Game` | Shortcut: `{p}p`
            Search trophies: `{p}trophy Game` | Shortcut: `{p}t`
            Search scores: `{p}meta Game` | Shortcut: `{p}m`
            Search length: `{p}hltb Game` | Shortcut `{p}h`
            Search deals: `{p}deals` | Press ▶ to skip slide
            Search news: `{p}news`""".format(p=P), inline=False)
        embed.add_field(name='User Specific Commands:', value="""
            Registration: `{p}register PSN`
            Show my profile: `{p}u`
            Unregister: `{p}unregister`
            Update my profile: `{p}update`
            My last platinum: `{p}mlp`""".format(p=P), inline=False)
        embed.set_author(name='Playstation Network Bot', icon_url='https://www.playstation.com/en-gb/1.36.45/etc/designs/pdc/clientlibs_base/images/nav/avatar-default-2x.png')
        embed.set_footer(text='© Made by Liav22')
        await message.channel.send(embed=embed)

    if message.content.lower() == P+'changelog' or message.content.lower() == P+'log':
        embed = discord.Embed(colour=0x1e90ff)
        embed.add_field(name='Changes:', value="""
            - New command: `{p}news`""".format(p=P), inline=False)
        embed.set_author(name='Update 21/07/2020', url='https://github.com/liav22/PSBot/commit/b5d147f47d5b67376857a76680da1ccb0d4a22b3', icon_url='https://www.playstation.com/en-gb/1.36.45/etc/designs/pdc/clientlibs_base/images/nav/avatar-default-2x.png')
        embed.set_footer(text='© Made by Liav22')
        await message.channel.send(embed=embed)

    if message.content.lower().startswith(P+'register '):
        try: 
            if message.guild is None:
                raise CommandUnusable()
        except CommandUnusable:
            await error_message(message.channel, 'This command is only useable in servers.', 'Try using this in a server where the bot is present.')
            return

        if search_user(message.author.id, message.guild.id) == False:
            register_new_user(message.author.id,message.content[10::], message.guild.id)
            await message.channel.send(f'<@{message.author.id}> registered successfully.')

        else:
            await error_message(message.channel, 'User already registered.', 'Try `~u` or `~unregister`')

    if message.content.lower() == P+'register':
        await error_message(message.channel, 'No username inserted.', 'Try `~register [USERNAME]`')

    if message.content.lower() == P+'unregister':
        try: 
            if message.guild is None:
                raise CommandUnusable()
        except CommandUnusable:
            await error_message(message.channel, 'This command is only useable in servers.', 'Try using this in a server where the bot is present.')
            return

        if search_user(message.author.id, message.guild.id) == True:
            remove_user(message.author.id, message.guild.id)
            await message.channel.send(f'<@{message.author.id}> removed successfully.')
        else:
            await error_message(message.channel, 'User not registered.', 'Use `~register [USERNAME]`', '004')

    if message.content.lower() == (P+'u'):
        t0 = time.time()
        try: 
            if message.guild is None:
                raise CommandUnusable()
        except CommandUnusable:
            await error_message(message.channel, 'This command is only useable in servers.', 'Try using this in a server where the bot is present.')
            return

        msg = await message.channel.send(embed=loading_embed)

        if search_user(message.author.id, message.guild.id) == True:
            try:
                url = 'https://psnprofiles.com/' + lookup_user(message.author.id, message.guild.id)
                soup = get_any_webpage(url)
                a = UserInfo(soup)
                embed = discord.Embed(description=a.description(), colour=0x4BA0FF)
                embed.set_author(name=a.name() + "'s Profile", url=url, icon_url=a.icon())
                embed.set_image(url=a.card())
                t1 = time.time()
                embed.set_footer(text=f'by PSNProfiles.com | Load time: {str(t1-t0)[0:4]} seconds')
                await msg.edit(embed=embed)

            except AttributeError:
                await error_message(message.channel, 'User not found on PSNProfiles.', 'Use `~unregister` and `~register [USERNAME]` again.', msg)

        else:
            await error_message(message.channel, 'User not registered.', 'Use `~register [USERNAME]`')

    if message.content.lower() == (P+'mlp') and "@" not in message.content or message.content.lower() == (P+'mylastplatinum') and "@" not in message.content:
        t0 = time.time()
        try: 
            if message.guild is None:
                raise CommandUnusable()
        except CommandUnusable:
            await error_message(message.channel, 'This command is only useable in servers.', 'Try using this in a server where the bot is present.')
            return

        msg = await message.channel.send(embed=loading_embed)

        try:
            if search_user(message.author.id, message.guild.id) == True:
                user = lookup_user(message.author.id, message.guild.id)
                soup = get_any_webpage(f'https://psnprofiles.com/{user}')

                if soup.find(text='Latest Platinum') == None:
                    raise NoResultsFound()

                a = PlatinumInfo(soup)
                embed = discord.Embed(title = a.game() + ' • ' + a.rarity(),description=a.description(), color=0x057fcc)
                embed.set_author(name=a.name() + "'s last Platinum Trophy", url=a.url(), icon_url='https://psnprofiles.com/lib/img/icons/40-platinum.png')
                embed.set_thumbnail(url=a.image())
                t1 = time.time()
                embed.set_footer(text=f'by PSNProfiles.com | Load time: {str(t1-t0)[0:4]} seconds')
                await msg.edit(embed=embed)

            elif search_user(message.author.id, message.guild.id) == False:
                await error_message(message.channel, 'User not registered.', 'Use `~register [USERNAME]`')

        except NoResultsFound:
            await error_message_edit(message.channel, "User doesn't have any Platinum trophy!", 'Try getting some trophies scrub', msg)

        except AttributeError:
            traceback.print_exc()
            await error_message(message.channel, "Unknown Error.", "Inform the bot's developer.")

    if message.content.lower().startswith(P+'mlp') and "@" in message.content:
        t0 = time.time()
        user = message.mentions[0].id

        try: 
            if message.guild is None:
                raise CommandUnusable()
        except CommandUnusable:
            await error_message(message.channel, 'This command is only useable in servers.', 'Try using this in a server where the bot is present.')
            return

        msg = await message.channel.send(embed=loading_embed)

        try:
            if search_user(user, message.guild.id) == True:
                user = lookup_user(user, message.guild.id)
                soup = get_any_webpage(f'https://psnprofiles.com/{user}')

                if soup.find(text='Latest Platinum') == None:
                    raise NoResultsFound()

                a = PlatinumInfo(soup)
                embed = discord.Embed(title = a.game() + ' • ' + a.rarity(),description=a.description(), color=0x057fcc)
                embed.set_author(name=a.name() + "'s last Platinum Trophy", url=a.url(), icon_url='https://psnprofiles.com/lib/img/icons/40-platinum.png')
                embed.set_thumbnail(url=a.image())
                t1 = time.time()
                embed.set_footer(text=f'by PSNProfiles.com | Load time: {str(t1-t0)[0:4]} seconds')
                await msg.edit(embed=embed)

            elif search_user(user, message.guild.id) == False:
                await error_message_edit(message.channel, 'User not registered.', 'Use `~register [USERNAME]`', msg)

        except NoResultsFound:
            await error_message_edit(message.channel, "User doesn't have any Platinum trophy!", 'Try getting some trophies scrub', msg)

        except AttributeError:
            traceback.print_exc()
            await error_message_edit(message.channel, "Unknown Error.", "Inform the bot's developer.", msg)

    if message.content.lower() == (P+'update'):
        try: 
            if message.guild is None:
                raise CommandUnusable()
        except CommandUnusable:
            await error_message(message.channel, 'This command is only useable in servers.', 'Try using this in a server where the bot is present.')
            return

        if search_user(message.author.id, message.guild.id) == True:
                user = lookup_user(message.author.id, message.guild.id)
                embed = discord.Embed(title='Click here to update your profile!', url=f'https://psnprofiles.com/?psnId={user}', colour=0x1e90ff)
                embed.set_author(name=f'Welcome back, {user}', icon_url='https://www.playstation.com/en-gb/1.36.45/etc/designs/pdc/clientlibs_base/images/nav/avatar-default-2x.png')
                await message.channel.send(embed=embed)

        elif search_user(message.author.id, message.guild.id) == False:
                await error_message(message.channel, 'User not registered.', 'Use `~register [USERNAME]`')

    if message.content.lower().startswith(P+'u') and '@' in message.content:
        t0 = time.time()
        user = message.mentions[0].id
        msg = await message.channel.send(embed=loading_embed)
        try: 
            if message.guild is None:
                raise CommandUnusable()
        except CommandUnusable:
            await error_message_edit(message.channel, 'This command is only useable in servers.', 'Try using this in a server where the bot is present.', msg)
            return

        if search_user(user, message.guild.id) == True:
            try:
                url = 'https://psnprofiles.com/' + lookup_user(user, message.guild.id)
                soup = get_any_webpage(url)
                a = UserInfo(soup)
                embed = discord.Embed(description=a.description(), colour=0x4BA0FF)
                embed.set_author(name=a.name() + "'s Profile", url=url, icon_url=a.icon())
                embed.set_image(url=a.card())
                t1 = time.time()
                embed.set_footer(text=f'by PSNProfiles.com | Load time: {str(t1-t0)[0:4]} seconds')
                await msg.edit(embed=embed)

            except AttributeError:
                await error_message_edit(message.channel, 'User not found on PSNProfiles.', 'Use `~unregister` and `~register [USERNAME]` again.', msg)
                
        if search_user(user, message.guild.id) == False:
                await error_message_edit(message.channel, 'User not registered.', 'Use `~register [USERNAME]`', msg)

    if message.content.lower().startswith(P+'u ') and '@' not in message.content or message.content.lower().startswith(P+'user ') and '@' not in message.content:
        if message.content.lower().startswith(P+'u '):
            url = 'https://psnprofiles.com/' + message.content[3::]
        if message.content.lower().startswith(P+'user '):
            url = 'https://psnprofiles.com/' + message.content[6::]
        soup = get_any_webpage(url)

        msg = await message.channel.send(embed=loading_embed)

        try:
            a = UserInfo(soup)
            embed = discord.Embed(description=a.description(), colour=0x4BA0FF)
            embed.set_author(name=a.name() + "'s Profile", url=url, icon_url=a.icon())
            embed.set_image(url=a.card())
            embed.set_footer(text='by PSNProfiles.com')
            await msg.edit(embed=embed)

        except AttributeError:
            traceback.print_exc()
            await error_message_edit(message.channel, 'User not found on PSNProfiles.', 'Check if you typed the name correctly.', msg)

    if message.content.lower().startswith(P+'trophy ') or message.content.lower().startswith(P+'t '):
        t0 = time.time()
        if message.content.lower().startswith(P+'t '):
            game = message.content[3::]
        if message.content.lower().startswith(P+'trophy '):
            game = message.content[8::]

        msg = await message.channel.send(embed=loading_embed)

        try:
            soup = get_web_page_google(game, ' Trophies • PSNProfiles.com')

            if soup == None:
                raise NoResultsFound(game)

            if 'Trophy List' not in str(soup.find('meta', {'name':'Description'})):
                raise NoResultsFound(game)

            a = TrophiesInfo(soup)
            embed = discord.Embed(title=a.trophies()+a.comp(), description=a.guide(), colour=0x4BA0FF)
            embed.set_author(name=a.name(), url=a.url(), icon_url='https://psnprofiles.com/lib/img/icons/logo-round-160px.png')
            embed.set_image(url=a.image())
            t1 = time.time()
            embed.set_footer(text=f'by PSNProfiles.com | Load time: {str(t1-t0)[0:4]} seconds')
            await msg.edit(embed=embed)

        except NoResultsFound:
            print(f'[{datetime.datetime.now()}] User {message.author.id} searched the following with no results: {game}')
            await error_message_with_url_edit(message.channel, 'Game not found.', 'Press the link to search manually.', f"https://psnprofiles.com/search/games?q={game.replace(' ','+')}", msg)

        except (urllib.error.HTTPError, urllib.error.URLError, discord.errors.HTTPException):
            traceback.print_exc()
            await error_message_edit(message.channel, f"HTTP Error. Why would you even search for {game}?", 'Search for an actual game.', msg)

        except (AttributeError, UnicodeEncodeError):
            traceback.print_exc()
            await error_message_edit(message.channel, "Unknown Error.", "Inform the bot's developer.", msg)

    if message.content.lower().startswith(P+'price ') or message.content.lower().startswith(P+'p '):
        t0 = time.time()
        if message.content.lower().startswith(P+'p '):
            game = message.content[3::]
        if message.content.lower().startswith(P+'price '):
            game = message.content[7::]

        msg = await message.channel.send(embed=loading_embed)

        try:
            soup = get_web_page_google('site:psprices.com/region-us ps4 ', game)

            if soup == None:
                raise NoResultsFound(game)

            if soup.find('div', {'class':'game-card--meta'}).span['content'] not in ('PS4', 'PS3', 'PSVita'):
                raise NoResultsFound(game)

            if 'Price change history' not in str(soup.find('div', {'id':'price_history'})):
                raise NoResultsFound(game)

            a = PriceInfo(soup)
            embed = discord.Embed(title='Current Price: ' + a.price() + a.plus_price(), description='Lowest Price: ' + a.lowest_price(), url=a.page_url(), colour=0x2200FF)
            embed.set_author(name=a.title(), url=a.store_url(), icon_url='https://psprices.com/staticfiles/i/content__game_card__price_plus.bccff0c297cd.png')
            embed.set_thumbnail(url=a.image())
            t1 = time.time()
            embed.set_footer(text=f'by PSprices.com | Load time: {str(t1-t0)[0:4]} seconds')
            await msg.edit(embed=embed)

        except NoResultsFound:
            print(f'[{datetime.datetime.now()}] User {message.author.id} searched the following with no results: {game}')
            await error_message_with_url_edit(message.channel, 'Game not found!', 'Press the link to search manually.', f"https://psprices.com/region-us/search/?q={game.replace(' ','+')}&dlc=show&platform=PS4", msg)

        except (urllib.error.HTTPError, urllib.error.URLError, discord.errors.HTTPException):
            traceback.print_exc()
            await error_message_edit(message.channel, f"HTTP Error. Why would you even search for {game}?", 'Search for an actual game.', msg)

        except AttributeError:
            traceback.print_exc()
            await error_message_edit(message.channel, "Unknown Error.", "Inform the bot's developer.", msg)

    if message.content.lower().startswith(P+'meta ') or message.content.lower().startswith(P+'m '):
        t0 = time.time()
        if message.content.lower().startswith(P+'m '):
            game = message.content[3::]
        if message.content.lower().startswith(P+'meta '):
            game = message.content[6::]

        msg = await message.channel.send(embed=loading_embed)

        try:
            soup = get_web_page_google(game, ' game Reviews - Metacritic')

            if soup == None:
                raise NoResultsFound(game)

            if 'Metacritic Game Reviews' not in str(soup):
                raise NoResultsFound(game)

            a = MetaInfo(soup)
            embed = discord.Embed(title='Metascore: ' + a.score(),description='by ' + a.critics(), colour=a.color())
            embed.add_field(name=a.best_review_author(), value=a.best_review_body(), inline=False)
            embed.add_field(name=a.worst_review_author(), value=a.worst_review_body(), inline=False)
            embed.set_author(name=a.title(), url=a.url(), icon_url='https://i.imgur.com/jpgFaHq.png')
            embed.set_thumbnail(url=a.image())
            t1 = time.time()
            embed.set_footer(text=f'by Metacritic.com | Load time: {str(t1-t0)[0:4]} seconds')
            await msg.edit(embed=embed)

        except NoResultsFound:
            print(f'[{datetime.datetime.now()}] User {message.author.id} searched the following with no results: {game}')
            await error_message_with_url_edit(message.channel, 'Game not found.', 'Press the link to search manually.', f"https://www.metacritic.com/search/game/{game.replace(' ','+')}/results", msg)

        except (urllib.error.HTTPError, urllib.error.URLError, discord.errors.HTTPException):
            traceback.print_exc()
            await error_message_edit(message.channel, f"HTTP Error. Why would you even search for {game}?", 'Search for an actual game.', msg)

        except AttributeError:
            traceback.print_exc()
            await error_message_edit(message.channel, "Unknown Error.", "Inform the bot's developer.", msg)

    if message.content.lower().startswith(P+'hltb ') or message.content.lower().startswith(P+'h '):
        t0 = time.time()
        if message.content.lower().startswith(P+'h '):
            game = message.content[3::]
        if message.content.lower().startswith(P+'hltb '):
            game = message.content[6::]

        msg = await message.channel.send(embed=loading_embed)

        try:
            soup = get_web_page_google('site:howlongtobeat.com ', game)

            if soup == None:
                raise NoResultsFound(game)

            if 'How long is' not in str(soup.title):
                raise NoResultsFound(game)

            a = HowLongInfo(soup)
            embed = discord.Embed(description=a.times(), colour=0x328ED)
            embed.set_author(name=a.title(), url=a.url(), icon_url='https://i.imgur.com/WjDVkDF.jpg')
            embed.set_thumbnail(url=a.image())
            t1 = time.time()
            embed.set_footer(text=f'by HowLongToBeat.com | Load time: {str(t1-t0)[0:4]} seconds')
            await msg.edit(embed=embed)

        except NoResultsFound:
            print(f'[{datetime.datetime.now()}] User {message.author.id} searched the following with no results: {game}')
            await error_message_with_url_edit(message.channel, 'Game not found.', 'Press the link to search manually.', 'https://howlongtobeat.com/', msg)

        except (urllib.error.HTTPError, urllib.error.URLError, discord.errors.HTTPException):
            traceback.print_exc()
            await error_message_edit(message.channel, f"HTTP Error. Why would you even search for {game}?", 'Search for an actual game.', msg)

        except AttributeError:
            traceback.print_exc()
            await error_message_edit(message.channel, "Unknown Error.", "Inform the bot's developer.", msg)

    if message.content.lower() == (P+'deals'):
        try:
            if message.guild is None:
                raise CommandUnusable(game)

        except:
            await error_message(message.channel, 'This command is only useable in servers.', 'Try using this in a server where the bot is present.')
            return

        soup = get_any_webpage('https://store.playstation.com/en-us/home/games')
        a = PSStoreInfo(soup)
        num = 0
        embed = discord.Embed(colour=0x1e90ff)
        embed.set_author(name='Current Featured Deals', url=a.url(num), icon_url='https://i.imgur.com/ivD9PE0.png')
        embed.set_image(url=a.image(num))
        embed.set_footer(text='by PlayStation Store')
        msg = await message.channel.send(embed=embed)
        await msg.add_reaction('▶')

        def check_reaction(reaction, user):
            return user == message.author and str(reaction.emoji) == '▶'

        while num < a.slides_count():
            await msg.add_reaction('▶')
            try:
                reaction, user = await client.wait_for('reaction_add', timeout=10.0, check=check_reaction)

            except asyncio.TimeoutError:
                await msg.clear_reactions()
                break
            else:
                num += 1
                embed = discord.Embed(colour=0x1e90ff)
                embed.set_author(name='Current Featured Deals', url=a.url(num), icon_url='https://i.imgur.com/ivD9PE0.png')
                embed.set_image(url=a.image(num))
                embed.set_footer(text='by PlayStation Store')
                await msg.edit(embed=embed)
                await msg.remove_reaction('▶', message.author)

        if num == a.slides_count():
            await msg.clear_reactions()
            await msg.add_reaction('<:reggie:449983603871580171>')
                

    if message.content.lower() == (P+'news'):
        t0 = time.time()
        msg = await message.channel.send(embed=loading_embed)

        try:
            soup = get_any_webpage('https://www.playstationtrophies.org/archive/gaming-news/1/')

        except rllib.error.URLError:
            await error_message_edit(message.channel, 'PlayStationTrophies.org is not responding.', 'Try again in a few minutes.', msg)

        a = PSNews(soup)
        embed = discord.Embed(description=a.all_news(), colour=0x1e90ff)
        embed.set_author(name='Latest PlayStation News', icon_url='https://i.imgur.com/ZOEtCfF.png')
        t1 = time.time()
        embed.set_footer(text=f'by PlayStationTrophies.com | Load time: {str(t1-t0)[0:4]} seconds')
        await msg.edit(embed=embed)

    if message.content.lower() == P+'restart' and message.author.id == int(config.owner):
        print(f'[{datetime.datetime.now()}] Initiating full restart as requested by bot owner...\n')
        if os.path.isfile("updater.bat"):
            subprocess.Popen('updater.bat').wait()
        os.execl(sys.executable, sys.executable, *sys.argv)

async def error_message(channel, error, solution):
    embed = discord.Embed(title=error, description='SOLUTION: '+solution)
    embed.set_author(name='Error', icon_url='https://www.playstation.com/en-gb/1.36.45/etc/designs/pdc/clientlibs_base/images/nav/avatar-default-2x.png')
    await channel.send(embed=embed)

async def error_message_edit(channel, error, solution, msg):
    embed = discord.Embed(title=error, description='SOLUTION: '+solution)
    embed.set_author(name='Error', icon_url='https://www.playstation.com/en-gb/1.36.45/etc/designs/pdc/clientlibs_base/images/nav/avatar-default-2x.png')
    await msg.edit(embed=embed)

async def error_message_with_url_edit(channel, error, solution, url, msg):
    embed = discord.Embed(title=error, description='SOLUTION: '+solution, url=url)
    embed.set_author(name='Error', icon_url='https://www.playstation.com/en-gb/1.36.45/etc/designs/pdc/clientlibs_base/images/nav/avatar-default-2x.png')
    await msg.edit(embed=embed)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=config.status, type=0))
    print('Logged in as {0.user}'.format(client))
    print(client.user.id)
    print('------')

if __name__ == "__main__":
    while True:
        try:
            """Since discord.py 1.0, this should also be able to handle connetion interruptions and automatically reconnect"""
            client.loop.run_until_complete(client.start(config.token))

        except BaseException:
            """In case there's no connection upon initial launch"""
            traceback.print_exc()
            print(f'[{datetime.datetime.now()}] Login failed, attempting to reconnect in 60 seconds...\n')
            time.sleep(60)
            continue
