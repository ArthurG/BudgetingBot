from sheetFunctions import *

import discord
from discord.ext import commands, tasks
import json
import datetime
import asyncio


valid_extensions = ['png', 'jpg', 'jpeg', 'gif']

with open('config.txt') as json_file:
	data = json.load(json_file)
	
	prefix = data['prefix']
	description = data['description']
	token = data['token']
	botActivity = data['botActivity']
	colour = int(data['color'])
	timeout = float(data['timeout'])


bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix), description=description)
bot.remove_command('help')


@bot.event
async def on_ready():
	print(f"BudgetingBot by HerbeMalveillante")
	print("Logged in successfully !")
	print(f"Bot username : {bot.user.name}")
	print(f"Bot id : {bot.user.id}")
	await bot.change_presence(activity = discord.Game(name=botActivity))
	print("-----------")
	

@bot.event
async def on_message(message):
	try :
		amount = float(message.content)
		print(f"The message has been detected as a valid amount : {amount}")
		
		# everything happens here.
		
		expense = Expense(message.channel.name, amount, amount)
		
		embed = discord.Embed(title=":dollar: expense added !", description = f"Click on the reaction within {timeout}s to cancel :put_litter_in_its_place:", colour=colour, timestamp=datetime.datetime.utcnow())
		embed.add_field(name="Expense details :", value=f"""Id : `{expense.id}`
		Category : `{expense.category}`
		Spent Amount : `{expense.amount}`
		Expense Time : `{expense.time}`
		Billable Amount : `{expense.billable}`
		""", inline = False)
		embed.set_thumbnail(url=bot.user.avatar_url)
		embed.set_footer(text=bot.user.name + " - requested by "+str(message.author), icon_url=message.author.avatar_url)

		messageSent = await message.channel.send(embed=embed)
		addExpense(expense)
		
		await messageSent.add_reaction("🚮")
		
		Expense.isLastSaved = False
		Expense.lastExpense = expense
		
		def check(r,u):
			checkBool = u.id == message.author.id and (not u.bot) and r.message.id == messageSent.id and str(r.emoji) == "🚮"
			return checkBool
		try :
			reaction, user = await bot.wait_for('reaction_add', check=check, timeout=timeout)
			
		except asyncio.TimeoutError:
			log(f"The delay to delete the expense of ID {expense.id} has expired.")
			if not Expense.isLastSaved :
				await message.channel.send(f"Hey {message.author.mention}, you did not upload the receipt for the last expense ! Please post a picture in this channel to save it as the receipt.")
			return
		else : 
			if str(reaction.emoji == "🚮"):
				delExpense(expense.id)
					
				embed = discord.Embed(title=":put_litter_in_its_place: Entry deleted !", description = f"entry id : {expense.id}")
				embed.set_thumbnail(url=bot.user.avatar_url)
				embed.set_footer(text=bot.user.name + " - requested by "+str(message.author), icon_url=message.author.avatar_url)
				await message.channel.send(embed=embed)
		
		
		
		

		
	except ValueError :
		print("The message has been detected not being a valid amount.")

		if len(message.attachments) > 0:
			receiptFile = message.attachments[0]
			ext = receiptFile.url.split(".")[-1]
			lastTime = Expense.lastExpense.time
			await message.attachments[0].save(f"receipts/{lastTime}.{ext}")
			await message.channel.send(f"Receipt detected and saved in `receipts/{lastTime}.{ext}`")
			
			Expense.isLastSaved = True
		
	
	
	await bot.process_commands(message)
	


@bot.command(name='ping', aliases=["p", "pong", "pingpong"])
async def ping(ctx):
	"""
	a simple ping command used to check if the bot is online
	"""
	embed = discord.Embed(title="PONG :ping_pong: ", description="I'm online ! :signal_strength:", colour=colour, timestamp=datetime.datetime.utcnow())
	embed.set_thumbnail(url=bot.user.avatar_url)
	embed.set_footer(text=bot.user.name + ' - requested by ' + str(ctx.author), icon_url=ctx.author.avatar_url)

	await ctx.send(embed=embed)
	log(f"{str(ctx.author)} pinged the bot.")



bot.run(token)
