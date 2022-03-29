import csv
import discord
import io
import os

intents = discord.Intents(members=True, messages=True, guilds=True)

client = discord.Client(intents=intents)
client_token = os.environ["CLIENT_TOKEN"]

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))
	
@client.event
async def on_message(message):
	if message.author == client.user:
		return
	
	if message.content.startswith('$assigngroups'):
		if len(message.attachments) == 1 and message.attachments[0].url.endswith('.csv'):
			channels = message.channel_mentions
			# Strip all existing group roles, then assign roles according to the provided csv
			await strip_group_roles(message)
			await csv_assign_group_roles(message, channels)
		else:
			await message.channel.send('`Error: $assigngroups expects one .csv file attached`')
	
	if message.content.startswith('$removegroups'):
		await strip_group_roles(message)


async def csv_assign_group_roles(message, channels):
	csv_bytes = await message.attachments[0].read()
	with io.StringIO(csv_bytes.decode('utf-8')) as f:
		reader = csv.reader(f)
		
		failed_usernames = []
		forbidden_channel_map = {}
		# csv reader reads in rows, but we copy and paste groups into columns
		for column in zip(*reader):
			print(column)
			# First element in column is group/role name - get corresponding Discord role
			group_name = column[0]
			group_role = discord.utils.get(message.guild.roles, name=group_name)
			if not group_role:
				print('Corresponding role not found for {}'.format(group_name))
				continue
			msg_lines = ['<@&{}>'.format(group_role.id)]
			for username in column[1:9]:
				if username:
					name_and_discrim = username.split('#')
					name = name_and_discrim[0]
					if len(name_and_discrim) > 1:
						discrim = name_and_discrim[1]
						user = discord.utils.get(message.guild.members, name=name, discriminator=discrim)
					else:
						user = discord.utils.get(message.guild.members, name=name)
					if not user:
						failed_usernames.append(username)
						print('Corresponding user not found for {}'.format(username))
						continue
					# Add group_role to the user
					await user.add_roles(group_role)
					msg_lines.append(' - {}'.format(username))
			# Send message containing the group assignments
			group_msg = '\n'.join(msg_lines)
			for channel in channels:
				try:
					await channel.send(group_msg)
				except discord.errors.Forbidden:
					if channel.name not in forbidden_channel_map:
						forbidden_channel_map[channel.name] = True
						await message.channel.send('`Error: I do not have the required permissions in {}`'.format(channel.name))
	
	# Send completion msg
	completion_msg = 'Group assignments complete!'
	if failed_usernames:
		completion_msg = 'The following users were not found: {}\n'.format(', '.join(failed_usernames)) + completion_msg
	print(completion_msg)
	await message.channel.send('`{}`'.format(completion_msg))


async def strip_group_roles(message):
	# Strip all "Group X" roles from all users assigned during preivous rounds
	for user in message.guild.members:
		user_group_roles = [role for role in user.roles if role.name.startswith('Group')]
		if user_group_roles:
			await user.remove_roles(*user_group_roles)
	
	completion_msg = 'All group rules successfully stripped from users'
	print(completion_msg)
	await message.channel.send('`{}`'.format(completion_msg))

client.run(client_token)
