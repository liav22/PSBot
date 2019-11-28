import asyncio
import discord
import time
import subprocess
import datetime
import traceback

from user_data import *
from website_data import *

TOKEN = open('token.txt', 'r').read() # DO NOT SHARE

P = '~' # Adjustable prefix for commands

client = discord.Client()

@client.event
async def on_message(message):
	if message.author == client.user:
		return # Ensuring the bot won't respond to himself

	if message.author.bot:
		return # Ensuring the bot won't respond to other bots

	if message.content == P+'help' or message.content == P+'h':
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
				soup = get_psn_profile_page(url)
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
		if search_user(message.author.id, message.guild.id) == True:
			url = 'https://psnprofiles.com/' + lookup_user(message.author.id, message.guild.id)
			soup = get_psn_profile_page(url)
			a = PlatinumInfo(soup)
			embed = discord.Embed(title = a.game() + ' • ' + a.rarity(),description=a.description(), color=0x057fcc)
			embed.set_author(name=a.name() + "'s last Platinum Trophy", url=url, icon_url='https://psnprofiles.com/lib/img/icons/40-platinum.png')
			embed.set_thumbnail(url=a.image())
			embed.set_footer(text='by PSNProfiles.com')
			await message.channel.send(embed=embed)

		else:
			await error_message(message.channel, 'User not registered.', 'Use `~register [USERNAME]`', '006')

	if message.content.lower().startswith(P+'u ') or message.content.lower().startswith(P+'user '):
		if message.content.lower().startswith(P+'u '):
			url = 'https://psnprofiles.com/' + message.content[3::]
		if message.content.lower().startswith(P+'user '):
			url = 'https://psnprofiles.com/' + message.content[6::]
		soup = get_psn_profile_page(url)
		a = UserInfo(soup)
		embed = discord.Embed(description=a.description(), colour=0x4BA0FF)
		embed.set_author(name=a.name() + "'s Profile", url=url, icon_url=a.icon())
		embed.set_image(url=a.card())
		embed.set_footer(text='by PSNProfiles.com')
		await message.channel.send(embed=embed)


	if message.content.lower().startswith(P+'trophy ') or message.content.lower().startswith(P+'t '):
		if message.content.lower().startswith(P+'t '):
			game = message.content[3::]
		if message.content.lower().startswith(P+'trophy '):
			game = message.content[8::]
		try:
			soup = get_web_page_google('site:psnprofiles.com ', game)
			a = TrophiesInfo(soup)
			embed = discord.Embed(title=a.trophies()+a.comp(), description=a.guide(), colour=0x4BA0FF)
			embed.set_author(name=a.name(), url=a.url(), icon_url='https://psnprofiles.com/lib/img/icons/logo-round-160px.png')
			embed.set_image(url=a.image())
			embed.set_footer(text='by PSNProfiles.com')
			await message.channel.send(embed=embed)

		except AttributeError:
			traceback.print_exc()
			await error_message_with_url(message.channel, 'Game not found.', 'Press the link to search manually.', f"https://psnprofiles.com/search/games?q={game.replace(' ','+')}", '009')

		except urllib.error.HTTPError:
			traceback.print_exc()
			await error_message_with_url(message.channel, 'Google or PSNProfiles are not cooperating.', 'Press the link to search manually.', f"https://psnprofiles.com/search/games?q={game.replace(' ','+')}", '008')

		except Exception:
			traceback.print_exc()
			await error_message(message.channel, "Unknown Error.", "Inform the bot's developer.", '007')

	if message.content.lower().startswith(P+'price ') or message.content.lower().startswith(P+'p '):
		if message.content.lower().startswith(P+'p '):
			game = message.content[3::]
		if message.content.lower().startswith(P+'price '):
			game = message.content[7::]

		try:
			soup = get_web_page_google('site:psprices.com ps4 ', game)
			a = PriceInfo(soup)
			embed = discord.Embed(title='Current Price: ' + a.price() + a.plus_price(), description='Lowest Price: ' + a.lowest_price(), url=a.page_url(), colour=0x2200FF)
			embed.set_author(name=a.title(), url=a.store_url(), icon_url='https://psprices.com/staticfiles/i/content__game_card__price_plus.bccff0c297cd.png')
			embed.set_thumbnail(url=a.image())
			embed.set_footer(text='by PSprices.com')
			await message.channel.send(embed=embed)

		except AttributeError:
			traceback.print_exc()
			await error_message_with_url(message.channel, 'Game not found.', 'Press the link to search manually.', f"https://psprices.com/region-us/search/?q={game.replace(' ','+')}&dlc=show&platform=PS4", '010')

		except urllib.error.HTTPError:
			traceback.print_exc()
			await error_message_with_url(message.channel, 'Google or PSPrices are not cooperating.', 'Press the link to search manually.', f"https://psprices.com/region-us/search/?q={game.replace(' ','+')}&dlc=show&platform=PS4", '008')

		except Exception:
			traceback.print_exc()
			await error_message(message.channel, "Unknown Error.", "Inform the bot's developer.", '007')

	if message.content.lower().startswith(P+'meta ') or message.content.lower().startswith(P+'m '):
		if message.content.lower().startswith(P+'m '):
			game = message.content[3::]
		if message.content.lower().startswith(P+'meta '):
			game = message.content[6::]

		try:
			soup = get_web_page_google('site:metacritic.com/game ', game)
			a = MetaInfo(soup)
			embed = discord.Embed(title='Metascore: ' + a.score(),description='by ' + a.critics(), colour=a.color())
			embed.add_field(name=a.best_review_author(), value=a.best_review_body(), inline=False)
			embed.add_field(name=a.worst_review_author(), value=a.worst_review_body(), inline=False)
			embed.set_author(name=a.title(), url=a.url(), icon_url='https://i.imgur.com/jpgFaHq.png')
			embed.set_thumbnail(url=a.image())
			embed.set_footer(text='by Metacritic.com')
			await message.channel.send(embed=embed)

		except AttributeError:
			traceback.print_exc()
			await error_message_with_url(message.channel, 'Game not found.', 'Press the link to search manually.', f"https://www.metacritic.com/search/game/{game.replace(' ','+')}/results", '011')

		except urllib.error.HTTPError:
			traceback.print_exc()
			await error_message_with_url(message.channel, 'Google or Metacritic are not cooperating.', 'Press the link to search manually.', f"https://www.metacritic.com/search/game/{game.replace(' ','+')}/results", '008')

		except Exception:
			traceback.print_exc()
			await error_message(message.channel, "Unknown Error.", "Inform the bot's developer.", '007')

	if message.content.lower().startswith(P+'hltb ') or message.content.lower().startswith(P+'h '):
		if message.content.lower().startswith(P+'h '):
			game = message.content[3::]
		if message.content.lower().startswith(P+'hltb '):
			game = message.content[6::]

		try:
			soup = get_web_page_google('site:howlongtobeat.com ', game)
			a = HowLongInfo(soup)
			embed = discord.Embed(description=a.times(), colour=0x328ED)
			embed.set_author(name=a.title(), url=a.url(), icon_url='https://i.imgur.com/WjDVkDF.jpg')
			embed.set_thumbnail(url=a.image())
			embed.set_footer(text='by HowLongToBeat.com')
			await message.channel.send(embed=embed)
			
		except AttributeError:
			traceback.print_exc()
			await error_message_with_url(message.channel, 'Game not found.', 'Press the link to search manually.', 'https://howlongtobeat.com/', '012')

		except Exception:
			traceback.print_exc()
			await error_message(message.channel, "Unknown Error: Google has either blocked us, or it's currently down.", "Wait an hour and try again or inform the bot's developer.", '008')

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
	await client.change_presence(activity=discord.Game(name="2.0 Now live", type=0))
	print('Logged in as {0.user}'.format(client))
	print(client.user.id)
	print('------')

client.run(TOKEN)