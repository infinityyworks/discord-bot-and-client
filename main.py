import threading
import asyncio
import discord
from discord.ext import commands
import random
from dotenv import load_dotenv
import os

# read answers.txt and load the responses to the $eightball command
fhandler = open('answers.txt','r')
responses = fhandler.readlines()
fhandler.close()

# configure gateway intents
intents = discord.Intents.all()
intents.typing = True
intents.presences = False

# create client object, with $ as the command prefix
client = commands.Bot(intents=intents,command_prefix='$')

def all():
	# print a hierarchy tree of all servers, channels and members
	for guild in client.guilds:
		print(guild.name+':')
		for channel in guild.text_channels:
			print(' '+channel.name)
		print()
		for member in guild.members:
			print(' '+member.name)
		print('\n\n')

def getGuilds():
	# return a list of every server the bot belongs to
	return [g for g in client.guilds]

def getChannels(guild):
	# return a list of every channel in a given server
	return [channel for channel in guild.text_channels]

def getMembers(guild):
	# return a list of every member in a given server
	return [member for member in guild.members]

def getPrivateChannels():
	# return a list of the bot's DM channels
	return [c for c in client.private_channels]


chid = 0	# current channel ID
current_guild = 0	# current server ID

# CLI thread loop
def m():
	while True:
		# reads stdin
		cmd = input()

		# ignore empty input
		if cmd == '':
			continue
			
		# prints the hierarchal list of all servers and associated channels and members
		if cmd == '.all':
			all()

		# prints all text channels in the current server
		if cmd == '.channels':
			for i in current_guild.text_channels:
				print(i.name)
			print()

		# prints all members in the current server
		if cmd == '.members':
			for i in current_guild.members:
				print(i.name)
			print()

		# prints all servers that the bot belongs to
		if cmd == '.servers':
			for i in client.guilds:
				print(i.name)
			print()

		# prints all the bot's DM channels
		if cmd == '.dms':
			for i in client.private_channels:
				print(i)
			print()
			
		# clears the terminal screen
		if cmd == '.clear':
			os.system('clear')

		# safely closes the client
		if cmd == '.quit':
			asyncio.run_coroutine_threadsafe(client.close(), loop)
			return
			
		# selects a target server by exact matching name
		if cmd == '.select server':
			print('---')
			server = input()
			for g in getGuilds():
				if g.name == server:
					current_guild = g
					client.get_guild(g.id)
					print('Entered server \"'+server+'\"')
					
		# selects a channel in the current server by exact matching name
		if cmd == '.select channel':
			print('---')
			global c
			c = input()
			async def enter_channel():
				for i in getChannels(current_guild):
					if i.name == c:
						global chid
						chid = i.id
						channel = client.get_channel(chid)
						print('Entered channel \"'+c+'\"'+'\n')

						# prints the last 50 messages upon entering a channel
						messages = [message async for message in channel.history(limit=50)]
						messages = messages[::-1]
						for msg in messages:
							print(f'{msg.author}\n', msg.content)
							print()
			asyncio.run_coroutine_threadsafe(enter_channel(),loop)

		# repeatedly pings a user, with an optional attached message to each ping
		if cmd == '.ping':
			print('---')
			target = discord.utils.get(client.get_all_members(), name=input('Username:  '))
			message = input('Message:  ')
			nping = int(input('Number of pings:  '))
			async def ping():
				channel = client.get_channel(chid)
				for i in range(nping):
					await channel.send(f'<@{target.id}> {message}')
				print(f'Successfully pinged {target} {nping} times with message \"{message}\"')
				print()
			asyncio.run_coroutine_threadsafe(ping(), loop)

		# repeatedly sends a message (split into 2000 character chunks)
		if cmd == '.spam':
			print('---')
			message = input('Message:  ')
			n = int(input('Number of messages:  '))
			async def spam():
				channel = client.get_channel(chid)
				payload = ''
				for i in range(n):
					payload += (message+'\n')

				# accounting for Discord's 2000 character limit
				if len(payload) > 2000:
					for chunk in [payload[i:i+2000] for i in range(0, len(payload), 2000)]:
						await channel.send(chunk)
				else:
					await channel.send(payload)
				print(f'Successfully sent message \"{message}\" {n} times')
				print()
			asyncio.run_coroutine_threadsafe(spam(), loop)
			
		# inputs which don't start with . are sent as messages in the current channel
		elif cmd[0] != '.':
			channel = client.get_channel(chid)
			asyncio.run_coroutine_threadsafe(channel.send(cmd),loop)
				

# Event handlers

# triggered when the client fully initialises
@client.event
async def on_ready():
	# store main asyncio loop
	global loop
	loop = asyncio.get_running_loop()

	# print confirmation message
	print('logged in as {0.user}'.format(client))

	# set bot activity status to make it appear as "Playing with the API"
	game=discord.Game('with the API')
	await client.change_presence(status=discord.Status.online,activity=game)


# triggers when a message is sent in any server
@client.event
async def on_message(message):
	# if message starts with $, process it as a user command
	if message.content[0] == '$':
		await client.process_commands(message)

	# check if message was sent in the channel selected by the CLI
	current_channel = client.get_channel(chid)
	if message.channel == current_channel:
		# ignore own messages
		if message.author == client.user:
			return
		# stream messages from the selected channel into the terminal
		print(f'{message.author}\n', message.content)
		print()
	else:
		return


# Bot commands

# replies to user with "@user Hello World!"
@client.command()
async def pingself(ctx):
	await ctx.send(f'<@{ctx.author.id}> Hello world!', reference=ctx.message)


# sends a random float between 0 and 1
@client.command()
async def randfloat(ctx):
	await ctx.send(str(random.random()))


# ambiguously responds to the user's question, similar to the 8ball toy
@client.command()
async def eightball(ctx,question):
	# ensures the same user can't keep asking the same question over and over for a different answer
	random.seed(0)
	random.seed(question+str(ctx.author.id))
	await ctx.send(random.choice(responses), reference=ctx.message)

# retreives the last n entries in the server's audit log, where 0 < n < 21
@client.command()
async def audit(ctx,lim):
	lim = int(lim)
	if lim > 20 or lim < 1:
		await ctx.send('enter a range between 1 and 20', reference=ctx.message)
		return
		
	log = ''
	async for entry in ctx.guild.audit_logs(limit = lim):
		if entry.user == entry.target:
			log += (('Automod did '+str(entry.action)[15:]+' to {0.target}'.format(entry))+'\n\n')
		else:
			log += (('{0.user} did '.format(entry)+str(entry.action)[15:]+' to {0.target}'.format(entry))+'\n\n')

	# account for Discord's 2000 character limit
	if len(log) < 2000:
		await ctx.send(log)
	else:
		for chunk in [log[i:i+2000] for i in range(0, len(log), 2000)]:
			await ctx.send(chunk)

# start the CLI thread in the background
t = threading.Thread(target=m)
t.start()

# load secrets from .env file
load_dotenv()
# connect client to Discord using API key
client.run(os.getenv('TOKEN'))
