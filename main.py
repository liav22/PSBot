# Written in Python 3.7.1

import asyncio
import discord
import time
import datetime
import traceback
import os

from config import *
from user import *
from website import *

client = discord.Client()

config = Config()
P = config.prefix

@client.event
async def on_message(message):
    if message.author == client.user:
        return # Ensuring the bot won't respond to himself

    if message.author.bot:
        return # Ensuring the bot won't respond to other bots

    if message.content.lower() == P+'help' or message.content.lower() == P+'h':
        embed = discord.Embed(title='Source code', url='https://github.com/liav22/PSBot', colour=0x1e90ff, provider='me')
        embed.add_field(name='General Commands:', value="""
            Search Profile: `{p}user PSN` | Shortcut: `{p}u`
            Search Prices: `{p}price Game` | Shortcut: `{p}p`
            Search Trophies: `{p}trophy Game` | Shortcut: `{p}t`
            Search Scores: `{p}meta Game` | Shortcut: `{p}m`
            Search Length: `{p}hltb Game` | Shortcut `{p}h`""".format(p=P), inline=False)
        embed.add_field(name='User Specific Commands:', value="""
            Registration: `{p}register PSN`
            Show My Profile: `{p}u`
            Unregister: `{p}unregister`
            My Last Platinum: `{p}mlp`""".format(p=P), inline=False)
        embed.set_author(name='Playstation Network Bot', icon_url='https://www.playstation.com/en-gb/1.36.45/etc/designs/pdc/clientlibs_base/images/nav/avatar-default-2x.png')
        embed.set_footer(text='© Made by Liav22')
        await message.channel.send(embed=embed)

    if message.content.lower().startswith(P+'register '):

        if message.guild is None:
            await error_message(message.channel, 'Registration is only possible on servers.', 'Try using on a server where the bot is present.', '001')

        if search_user(message.author.id, message.guild.id) == False:
            register_new_user(message.author.id,message.content[10::], message.guild.id)
            await message.channel.send(f'<@{message.author.id}> registered successfully.')

        else:
            await error_message(message.channel, 'User already registered.', 'Try `~u` or `~register`', '002')

    if message.content.lower() == P+'register':
        await error_message(message.channel, 'No username inserted.', 'Try `~register [USERNAME]`', '003')

    if message.content.lower() == P+'unregister':
        if search_user(message.author.id, message.guild.id) == True:
            remove_user(message.author.id, message.guild.id)
            await message.channel.send(f'<@{message.author.id}> removed successfully.')
        else:
            await error_message(message.channel, 'User not registered.', 'Use `~register [USERNAME]`', '004')

    if message.content.lower() == (P+'u'):
        if search_user(message.author.id, message.guild.id) == True:
            try:
                url = 'https://psnprofiles.com/' + lookup_user(message.author.id, message.guild.id)
                soup = get_any_webpage(url)
                a = UserInfo(soup)
                embed = discord.Embed(description=a.description(), colour=0x4BA0FF)
                embed.set_author(name=a.name() + "'s Profile", url=url, icon_url=a.icon())
                embed.set_image(url=a.card())
                embed.set_footer(text='by PSNProfiles.com')
                await message.channel.send(embed=embed)

            except AttributeError:
                await error_message(message.channel, 'User not found on PSNProfiles.', 'Use `~unregister` and `~register [USERNAME]` again.', '005')

        else:
            await error_message(message.channel, 'User not registered.', 'Use `~register [USERNAME]`', '006')

    if message.content.lower() == (P+'mlp') or message.content.lower() == (P+'mylastplatinum'):
        try:
            if search_user(message.author.id, message.guild.id) == True:
                user = lookup_user(message.author.id, message.guild.id)
                url_temp = f'https://psnprofiles.com/{user}/log?type=platinum'
                soup_temp = get_any_webpage(url_temp)

                if 'No trophies to show' in str(soup_temp.find('div',{'class':'box'})):
                    await error_message(message.channel, "User doesn't have any Platinum trophy!", 'Try getting some trophies scrub', '000')

                game = soup_temp.find('img', {'class':'game'})['title']
                url = f'https://psnprofiles.com/{user}'
                soup = get_any_webpage(url)

                a = PlatinumInfo(soup, game)
                embed = discord.Embed(title = a.game() + ' • ' + a.rarity(),description=a.description(), color=0x057fcc)
                embed.set_author(name=a.name() + "'s last Platinum Trophy", url=url, icon_url='https://psnprofiles.com/lib/img/icons/40-platinum.png')
                embed.set_thumbnail(url=a.image())
                embed.set_footer(text='by PSNProfiles.com')
                await message.channel.send(embed=embed)

            elif search_user(message.author.id, message.guild.id) == False:
                await error_message(message.channel, 'User not registered.', 'Use `~register [USERNAME]`', '006')

        except AttributeError:
            traceback.print_exc()
            await error_message(message.channel, "Unknown Error.", "Inform the bot's developer.", '007')

    if message.content.lower().startswith(P+'u ') or message.content.lower().startswith(P+'user '):
        if message.content.lower().startswith(P+'u '):
            url = 'https://psnprofiles.com/' + message.content[3::]
        if message.content.lower().startswith(P+'user '):
            url = 'https://psnprofiles.com/' + message.content[6::]
        soup = get_any_webpage(url)

        try:
            a = UserInfo(soup)
            embed = discord.Embed(description=a.description(), colour=0x4BA0FF)
            embed.set_author(name=a.name() + "'s Profile", url=url, icon_url=a.icon())
            embed.set_image(url=a.card())
            embed.set_footer(text='by PSNProfiles.com')
            await message.channel.send(embed=embed)

        except AttributeError:
            traceback.print_exc()
            await error_message(message.channel, 'User not found on PSNProfiles.', 'Check if you typed the name correctly.', '005')

    if message.content.lower().startswith(P+'trophy ') or message.content.lower().startswith(P+'t '):
        if message.content.lower().startswith(P+'t '):
            game = message.content[3::]
        if message.content.lower().startswith(P+'trophy '):
            game = message.content[8::]

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
            embed.set_footer(text='by PSNProfiles.com')
            await message.channel.send(embed=embed)

        except NoResultsFound:
            print(f'[{datetime.datetime.now()}] User {message.author.id} searched the following with no results: {game}')
            await error_message_with_url(message.channel, 'Game not found.', 'Press the link to search manually.', f"https://psnprofiles.com/search/games?q={game.replace(' ','+')}", '009')

        except urllib.error.HTTPError:
            traceback.print_exc()
            await error_message_with_url(message.channel, 'Google or PSNProfiles are not cooperating.', 'Press the link to search manually.', f"https://psnprofiles.com/search/games?q={game.replace(' ','+')}", '008')

        except AttributeError:
            traceback.print_exc()
            await error_message(message.channel, "Unknown Error.", "Inform the bot's developer.", '007')

    if message.content.lower().startswith(P+'price ') or message.content.lower().startswith(P+'p '):
        if message.content.lower().startswith(P+'p '):
            game = message.content[3::]
        if message.content.lower().startswith(P+'price '):
            game = message.content[7::]

        try:
            soup = get_web_page_google('site:psprices.com ps4 ', game)

            if soup == None:
                raise NoResultsFound(game)

            if 'Price change history' not in str(soup.find('div', {'id':'price_history'})):
                raise NoResultsFound(game)

            a = PriceInfo(soup)
            embed = discord.Embed(title='Current Price: ' + a.price() + a.plus_price(), description='Lowest Price: ' + a.lowest_price(), url=a.page_url(), colour=0x2200FF)
            embed.set_author(name=a.title(), url=a.store_url(), icon_url='https://psprices.com/staticfiles/i/content__game_card__price_plus.bccff0c297cd.png')
            embed.set_thumbnail(url=a.image())
            embed.set_footer(text='by PSprices.com')
            await message.channel.send(embed=embed)

        except NoResultsFound:
            print(f'[{datetime.datetime.now()}] User {message.author.id} searched the following with no results: {game}')
            await error_message_with_url(message.channel, 'Game not found!', 'Press the link to search manually.', f"https://psprices.com/region-us/search/?q={game.replace(' ','+')}&dlc=show&platform=PS4", '010')

        except urllib.error.HTTPError:
            traceback.print_exc()
            await error_message_with_url(message.channel, 'Google or PSPrices are not cooperating.', 'Press the link to search manually.', f"https://psprices.com/region-us/search/?q={game.replace(' ','+')}&dlc=show&platform=PS4", '008')

        except AttributeError:
            traceback.print_exc()
            await error_message(message.channel, "Unknown Error.", "Inform the bot's developer.", '007')

    if message.content.lower().startswith(P+'meta ') or message.content.lower().startswith(P+'m '):
        if message.content.lower().startswith(P+'m '):
            game = message.content[3::]
        if message.content.lower().startswith(P+'meta '):
            game = message.content[6::]

        try:
            soup = get_web_page_google('site:metacritic.com/game ', game)

            if soup == None:
                raise NoResultsFound(game)

            if 'Critic Reviews' not in str(soup.find('div', {'class':'content_nav'}).a):
                raise NoResultsFound(game)

            a = MetaInfo(soup)
            embed = discord.Embed(title='Metascore: ' + a.score(),description='by ' + a.critics(), colour=a.color())
            embed.add_field(name=a.best_review_author(), value=a.best_review_body(), inline=False)
            embed.add_field(name=a.worst_review_author(), value=a.worst_review_body(), inline=False)
            embed.set_author(name=a.title(), url=a.url(), icon_url='https://i.imgur.com/jpgFaHq.png')
            embed.set_thumbnail(url=a.image())
            embed.set_footer(text='by Metacritic.com')
            await message.channel.send(embed=embed)

        except NoResultsFound:
            print(f'[{datetime.datetime.now()}] User {message.author.id} searched the following with no results: {game}')
            await error_message_with_url(message.channel, 'Game not found.', 'Press the link to search manually.', f"https://www.metacritic.com/search/game/{game.replace(' ','+')}/results", '011')

        except urllib.error.HTTPError:
            traceback.print_exc()
            await error_message_with_url(message.channel, 'Google or Metacritic are not cooperating.', 'Press the link to search manually.', f"https://www.metacritic.com/search/game/{game.replace(' ','+')}/results", '008')

        except AttributeError:
            traceback.print_exc()
            await error_message(message.channel, "Unknown Error.", "Inform the bot's developer.", '007')

    if message.content.lower().startswith(P+'hltb ') or message.content.lower().startswith(P+'h '):
        if message.content.lower().startswith(P+'h '):
            game = message.content[3::]
        if message.content.lower().startswith(P+'hltb '):
            game = message.content[6::]

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
            embed.set_footer(text='by HowLongToBeat.com')
            await message.channel.send(embed=embed)

        except NoResultsFound:
            print(f'[{datetime.datetime.now()}] User {message.author.id} searched the following with no results: {game}')
            await error_message_with_url(message.channel, 'Game not found.', 'Press the link to search manually.', 'https://howlongtobeat.com/', '012')

        except urllib.error.HTTPError:
            traceback.print_exc()
            await error_message_with_url(message.channel, 'Google or HowLongToBeat are not cooperating.', 'Press the link to search manually.', f"https://www.metacritic.com/search/game/{game.replace(' ','+')}/results", '008')

        except AttributeError:
            traceback.print_exc()
            await error_message(message.channel, "Unknown Error.", "Inform the bot's developer.", '007')

    if message.content.lower() == P+'restart' and message.author.id == int(config.owner):
        print(f'[{datetime.datetime.now()}] Initiating full restart as requested by bot owner...\n')
        os.execl(sys.executable, sys.executable, *sys.argv)

@client.event
async def error_message(channel, error, solution, code):
    embed = discord.Embed(title=error, description='SOLUTION: '+solution)
    embed.set_author(name='RIP', icon_url='https://i.imgur.com/gs99PYz.png')
    embed.set_footer(text='Error code: '+code)
    await channel.send(embed=embed)

async def error_message_with_url(channel, error, solution, url, code):
    embed = discord.Embed(title=error, description='SOLUTION: '+solution, url=url)
    embed.set_author(name='RIP', icon_url='https://i.imgur.com/gs99PYz.png')
    embed.set_footer(text='Error code: '+code)    
    await channel.send(embed=embed)

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
            print(f'[{datetime.datetime.now()}] Login failed, attempting to reconnect in 60 seconds...\n')
            time.sleep(60)
            continue
