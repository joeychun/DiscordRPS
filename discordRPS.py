# Work with Python 3.6

# https://discord.com/api/oauth2/authorize?client_id=739069897606299648&permissions=1073883200&scope=bot

import discord, asyncio
from discord.ext import commands, tasks
from discord import Embed
from asyncio import sleep

### CLASSES

class Game:
    """
    Creates RPS Game object
    --------------------
    game_manager: GameManager object that manages this game
    host: User object that hosted the RPS
    opponent: User object that is assigned as the opponent of the RPS
    time: Integer time in seconds
    """

    def __init__(self, game_manager, host, opponent, time):
        self.game_manager = game_manager
        self.time = time
        self.id = 0

        self.host = host
        self.host_response = None
        self.host_counter = time

        self.opponent = opponent
        self.opponent_response = None
        self.opponent_counter = time

        self.host_msg = None
        self.opponent_msg = None
        self.server_msg = None

    def delete(self):
        self.game_manager.games.pop(self.id)


class GameManager:
    """
    Manages RPS Games
    --------------------
    games: Dictionary that has mappings of game_id(int) and Game(Game object)
    next_id: Integer that is the next_id available as the game_id


    METHODS
    --------------------
    increase_id(): Increases next_id by 1
    is_playing(user): Checks if the user is in a RPS game.
                      Returns a tuple of (1, "host") if the user is playing as a host, (1, "opponent") if the user is playing as an opponent, and (0, "nobody") if neither
    """
    def __init__(self):
        self.games = {}
        self.next_id = 0

    def increase_id(self):
        self.next_id += 1

    def create_game(self, host, opponent, time):
        game = Game(self, host, opponent, time)

        # Assign game_id
        game.id = self.next_id
        self.increase_id()

        self.games[game.id] = game

        return game

    def is_playing(self, user):
        for game_id in self.games.keys():
            game = self.games[game_id]
            if game.host == user:
                return 1
            elif game.opponent == user:
                return 1
        return 0



### GLOBAL VARS
"""
r   : rock option
s   : scissors option
p   : paper option
ff  : forfeit option
fft : forfeit from time limit
"""
char_to_full = {
    'r':"✊",
    's':"✌️",
    'p':"🖐️",
    'ff':"🏳️",
    'fft':"⏲️"
}

game_manager = GameManager()
bot = commands.Bot(command_prefix='!')



### FUNCTIONS

def rps_test(a, b):
    """
    When given available RSP responses('r','s','p','ff','fft') a and b, decides who is the winner.
    Returns 1 if a wins b, -1 if b wins a, and 0 if it is a tie.
    """
    if a[0] == b[0]:
        return 0
    if a == 'ff' or a == 'fft':
        return -1
    if b == 'ff' or b == 'fft':
        return 1

    if a == 'r':
        if b == 's':
            return 1
        elif b == 'p':
            return -1
    elif a == 's':
        if b == 'p':
            return 1
        elif b == 'r':
            return -1
    elif a == 'p':
        if b == 'r':
            return 1
        elif b == 's':
            return -1

# CHANGED
async def do_stuff_every_x_seconds(timeout, func, game, user_str):
    """
    Every x seconds, calls function func()
    user_str shows if the func() is about the host or opponent
    Modifies the messages when the counter becomes zero.
    """

    while True:
        # Every timeout seconds, calls func
        await asyncio.sleep(timeout)
        await func(game, user_str)

        if user_str == "host" and game.host_counter <= 0:
            # If there was no response before time reaches 0, give a response of 'fft'
            try:
                await game.host_msg.delete()

                game.host_response = 'fft'

                # Edit the server_msg, depending on if the other player gave his response
                embed=discord.Embed(title="Rock Paper Scissors!"+ "✊"+"✌️"+"🖐️", description="", color=0x00ff00)
                msg1 = 'Let a Rock-Paper-Scissors game start between {0.name} and {1.name}!'.format(game.host, game.opponent)
                msg2 = ''
                if game.opponent_response != None:
                    msg2 = '\nThe results are:'
                else:
                    msg2 = 'Waiting for response from {0.mention}... '.format(game.opponent)
                embed.add_field(name=msg1, value=msg2, inline=True)
                await game.server_msg.edit(embed=embed)

                if game.opponent_response != None:
                    # Edit the server_msg, when the other player has answered
                    embed=discord.Embed(title="Rock Paper Scissors!"+ "✊"+"✌️"+"🖐️", description="", color=0x00ff00)
                    msg1 = 'Let a Rock-Paper-Scissors game start between {0.name} and {1.name}!'.format(game.host, game.opponent)
                    msg2 = '\nThe results are:'

                    # The edited message will be decided depending on which player won
                    won = rps_test(game.host_response, game.opponent_response)
                    if won == 1:
                        msg2 += "\n\n{0}({2}) won {1}({3})!\n\nWinner: {0}\nLoser: {1}".format(game.host.mention, game.opponent.mention, char_to_full[game.host_response], char_to_full[game.opponent_response])
                    if won == 0:
                        msg2 += "\n\n{0}({2}) and {1}({3}) tied!\n\nIt's a tie!".format(game.host.mention, game.opponent.mention, char_to_full[game.host_response], char_to_full[game.opponent_response])
                    if won == -1:
                        msg2 += "\n\n{1}({3}) won {0}({2})!\n\nWinner: {1}\nLoser: {0}".format(game.host.mention, game.opponent.mention, char_to_full[game.host_response], char_to_full[game.opponent_response])

                    embed.add_field(name=msg1, value=msg2, inline=True)
                    await game.server_msg.edit(embed=embed)

                    game.host_response = None
                    game.opponent_response = None
                    game.delete()
            except Exception:
                pass
            break
        elif user_str == "opponent" and game.opponent_counter <= 0:
            # If there was no response before time reaches 0, give a response of 'fft'
            try:
                await game.opponent_msg.delete()

                game.opponent_response = 'fft'

                # Edit the server_msg, depending on if the other player gave his response
                embed=discord.Embed(title="Rock Paper Scissors!"+ "✊"+"✌️"+"🖐️", description="", color=0x00ff00)
                msg1 = 'Let a Rock-Paper-Scissors game start between {0.name} and {1.name}!'.format(game.host, game.opponent)
                msg2 = ''
                if game.host_response != None:
                    msg2 = '\nThe results are:'
                else:
                    msg2 = 'Waiting for response from {0.mention}... '.format(game.host)
                embed.add_field(name=msg1, value=msg2, inline=True)
                await game.server_msg.edit(embed=embed)

                if game.host_response != None:
                    # Edit the server_msg, when the other player has answered
                    embed=discord.Embed(title="Rock Paper Scissors!"+ "✊"+"✌️"+"🖐️", description="", color=0x00ff00)
                    msg1 = 'Let a Rock-Paper-Scissors game start between {0.name} and {1.name}!'.format(game.host, game.opponent)
                    msg2 = '\nThe results are:'

                    # The edited message will be decided depending on which player won
                    won = rps_test(game.opponent_response, game.host_response)
                    if won == 1:
                        msg2 += "\n\n{0}({2}) won {1}({3})!\n\nWinner: {0}\nLoser: {1}".format(game.opponent.mention, game.host.mention, char_to_full[game.opponent_response], char_to_full[game.host_response])
                    if won == 0:
                        msg2 += "\n\n{0}({2}) and {1}({3}) tied!\n\nIt's a tie!".format(game.host.mention, game.opponent.mention, char_to_full[game.host_response], char_to_full[game.opponent_response])
                    if won == -1:
                        msg2 += "\n\n{1}({3}) won {0}({2})!\n\nWinner: {1}\nLoser: {0}".format(game.opponent.mention, game.host.mention, char_to_full[game.opponent_response], char_to_full[game.host_response])

                    embed.add_field(name=msg1, value=msg2, inline=True)
                    await game.server_msg.edit(embed=embed)

                    game.host_response = None
                    game.opponent_response = None
                    game.delete()
            except Exception:
                pass
            break



# CHANGED
async def rps_msg_edit(game, user_str):
    if user_str == "host":
        game.host_counter -= 1
        msg = "What will you play against {0}?   **{1}**\n(Don't give your response before the Bot gives you all of the options)".format(game.opponent.name, game.host_counter)
        embed_host = discord.Embed(title="Rock Paper Scissors! " + "✊"+"✌️"+"🖐️", description=msg, color=0x00ff00)
        try:
            await game.host_msg.edit(embed=embed_host)
        except Exception:
           pass
    elif user_str == "opponent":
        game.opponent_counter -= 1
        msg = "What will you play against {0}?   **{1}**\n(Don't give your response before the Bot gives you all of the options)".format(game.host.name, game.opponent_counter)
        embed_opponent = discord.Embed(title="Rock Paper Scissors! " + "✊"+"✌️"+"🖐️", description=msg, color=0x00ff00)
        try:
            await game.opponent_msg.edit(embed=embed_opponent)
        except Exception:
            pass
    else:
        raise Exception('user_str was expected to be either "host" or "opponent", but it was neither')



### BOT COMMANDS

@bot.command()
async def hello(ctx):
    # we do not want the bot to reply to itself
    if ctx.author == bot.user:
        return

    msg = 'Hello {0.author.mention}'.format(ctx)
    await ctx.send(msg)
    msg = 'Hello {0.author}'.format(ctx)
    await ctx.send(msg)

@bot.command(pass_context=True, aliases=['rsp', 'prs', 'psr', 'srp', 'spr', 'play', 'game', 'battle'])
async def rps(ctx, mention1, s=10):
    if ctx.author == bot.user:
        return

    # Mapping user ids to Member objects, and getting opponent information
    id_to_member = {}
    for member in ctx.guild.members:
        id_to_member[str(member.id)] = member

    mention1_user_id = ""
    for c in mention1:
        if '0'<=c and c<='9':
            mention1_user_id += c


    host = ctx.author
    opponent = id_to_member[mention1_user_id]

    embed=discord.Embed(title="Rock Paper Scissors! " + "✊"+"✌️"+"🖐️", description="", color=0x00ff00)

    # Cases that will not start a RPS
    if not (10 <= s):
        msg1 = 'Sorry, the time you selected was too short'
        embed.add_field(name=msg1, value='The time limit can only be between 10 and 60', inline=True)
        await ctx.send(embed=embed)
        return
    if not (s <= 60):
        msg1 = 'Sorry, the time you selected was too long'
        embed.add_field(name=msg1, value='The time limit can only be between 10 and 60', inline=True)
        await ctx.send(embed=embed)
        return
    if host == opponent:
        msg1 = 'Sorry, you cannot battle yourself'
        embed.add_field(name=msg1, value='You can only battle other players', inline=True)
        await ctx.send(embed=embed)
        return
    if opponent.bot:
        msg1 = 'Sorry, you cannot battle a Bot'
        embed.add_field(name=msg1, value='You can only battle other players', inline=True)
        await ctx.send(embed=embed)
        return
    if game_manager.is_playing(host):
        msg1 = 'Sorry, you are currrently in another game'
        embed.add_field(name=msg1, value='You can only battle other players once you\'re done with your match', inline=True)
        await ctx.send(embed=embed)
        return
    if game_manager.is_playing(opponent):
        msg1 = 'Sorry, {0} is currrently in another game'.format(opponent.name)
        embed.add_field(name=msg1, value='You can only battle {0} when {0} is done with his/her match'.format(opponent.name), inline=True)
        await ctx.send(embed=embed)
        return

    game = game_manager.create_game(host, opponent, s)

    # Post embed server message
    msg1 = 'Let a Rock-Paper-Scissors game start between {0.name} and {1.name}!'.format(host, opponent)
    msg2 = 'Waiting for response from {0.mention}...\nWaiting for response from {1.mention}... '.format(host, opponent)
    embed.add_field(name=msg1, value=msg2, inline=True)
    game.server_msg = await ctx.send(embed=embed)

    msg = "What will you play against {0}?   **{1}**\n(Don't give your response before the Bot gives you all of the options)".format(opponent.name, s)
    embed_host = discord.Embed(title="Rock Paper Scissors! " + "✊"+"✌️"+"🖐️", description=msg, color=0x00ff00)
    game.host_msg = await host.send(embed=embed_host)
    await game.host_msg.add_reaction("✊")
    await game.host_msg.add_reaction("✌️")
    await game.host_msg.add_reaction("🖐️")
    await game.host_msg.add_reaction("🏳️")
    task = asyncio.create_task(do_stuff_every_x_seconds(1,rps_msg_edit,game,"host"))

    msg = "What will you play against {0}?   **{1}**\n(Don't give your response before the Bot gives you all of the options)".format(host.name, s)
    embed_opponent = discord.Embed(title="Rock Paper Scissors! " + "✊"+"✌️"+"🖐️", description=msg, color=0x00ff00)
    game.opponent_msg = await opponent.send(embed=embed_opponent)
    await game.opponent_msg.add_reaction("✊")
    await game.opponent_msg.add_reaction("✌️")
    await game.opponent_msg.add_reaction("🖐️")
    await game.opponent_msg.add_reaction("🏳️")
    task = asyncio.create_task(do_stuff_every_x_seconds(1,rps_msg_edit,game,"opponent"))


    @bot.event
    async def on_reaction_add(reaction, user):
        channel = reaction.message.channel
        message = reaction.message
        player_response = ''

        # Check for all of the reactions; look for a one that is not given by a bot
        for reaction in message.reactions:
            async for user in reaction.users():
                if user != bot.user:
                    if reaction.emoji == "✊":
                        player_response = 'r'
                        print("{0} chose {1}.".format(user.name, player_response))
                    elif reaction.emoji == "✌️":
                        player_response = 's'
                        print("{0} chose {1}.".format(user.name, player_response))
                    elif reaction.emoji == "🖐️":
                        player_response = 'p'
                        print("{0} chose {1}.".format(user.name, player_response))
                    elif reaction.emoji == "🏳️":
                        player_response = 'ff'
                        print("{0} chose {1}.".format(user.name, player_response))

                    if user == game.host:
                        game.host_response = player_response
                    elif user == game.opponent:
                        game.opponent_response = player_response

                    await message.delete()


                    if user == host:
                        # Edit the server_msg, depending on if the other player gave his response
                        embed=discord.Embed(title="Rock Paper Scissors!"+ "✊"+"✌️"+"🖐️", description="", color=0x00ff00)
                        msg1 = 'Let a Rock-Paper-Scissors game start between {0.name} and {1.name}!'.format(game.host, game.opponent)
                        msg2 = ''
                        if game.opponent_response != None:
                            msg2 = '\nThe results are:'
                        else:
                            msg2 = 'Waiting for response from {0.mention}... '.format(game.opponent)
                        embed.add_field(name=msg1, value=msg2, inline=True)
                        await game.server_msg.edit(embed=embed)

                        if game.opponent_response != None:
                            embed=discord.Embed(title="Rock Paper Scissors!"+ "✊"+"✌️"+"🖐️", description="", color=0x00ff00)
                            msg1 = 'Let a Rock-Paper-Scissors game start between {0.name} and {1.name}!'.format(game.host, game.opponent)
                            msg2 = '\nThe results are:'

                            # The edited message will be decided depending on which player won
                            won = rps_test(game.host_response, game.opponent_response)
                            if won == 1:
                                msg2 += "\n\n{0}({2}) won {1}({3})!\n\nWinner: {0}\nLoser: {1}".format(game.host.mention, game.opponent.mention, char_to_full[game.host_response], char_to_full[game.opponent_response])
                            if won == 0:
                                msg2 += "\n\n{0}({2}) and {1}({3}) tied!\n\nIt's a tie!".format(game.host.mention, game.opponent.mention, char_to_full[game.host_response], char_to_full[game.opponent_response])
                            if won == -1:
                                msg2 += "\n\n{1}({3}) won {0}({2})!\n\nWinner: {1}\nLoser: {0}".format(game.host.mention, game.opponent.mention, char_to_full[game.host_response], char_to_full[game.opponent_response])

                            embed.add_field(name=msg1, value=msg2, inline=True)
                            await game.server_msg.edit(embed=embed)

                            game.host_response = None
                            game.opponent_response = None
                            game.delete()

                    elif user == opponent:
                        # Edit the server_msg, depending on if the other player gave his response
                        embed=discord.Embed(title="Rock Paper Scissors!"+ "✊"+"✌️"+"🖐️", description="", color=0x00ff00)
                        msg1 = 'Let a Rock-Paper-Scissors game start between {0.name} and {1.name}!'.format(game.host, game.opponent)
                        msg2 = ''
                        if game.host_response != None:
                            msg2 = '\nThe results are:'
                        else:
                            msg2 = 'Waiting for response from {0.mention}... '.format(game.host)
                        embed.add_field(name=msg1, value=msg2, inline=True)
                        await game.server_msg.edit(embed=embed)

                        if game.host_response != None:
                            embed=discord.Embed(title="Rock Paper Scissors!"+ "✊"+"✌️"+"🖐️", description="", color=0x00ff00)
                            msg1 = 'Let a Rock-Paper-Scissors game start between {0.name} and {1.name}!'.format(game.host, game.opponent)
                            msg2 = '\nThe results are:'

                            # The edited message will be decided depending on which player won
                            won = rps_test(game.opponent_response, game.host_response)
                            if won == 1:
                                msg2 += "\n\n{0}({2}) won {1}({3})!\n\nWinner: {0}\nLoser: {1}".format(game.opponent.mention, game.host.mention, char_to_full[game.opponent_response], char_to_full[game.host_response])
                            if won == 0:
                                msg2 += "\n\n{0}({2}) and {1}({3}) tied!\n\nIt's a tie!".format(game.host.mention, game.opponent.mention, char_to_full[game.host_response], char_to_full[game.opponent_response])
                            if won == -1:
                                msg2 += "\n\n{1}({3}) won {0}({2})!\n\nWinner: {1}\nLoser: {0}".format(game.opponent.mention, game.host.mention, char_to_full[game.opponent_response], char_to_full[game.host_response])

                            embed.add_field(name=msg1, value=msg2, inline=True)
                            await game.server_msg.edit(embed=embed)

                            game.host_response = None
                            game.opponent_response = None
                            game.delete()

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

TOKEN = 'Private Information :)'
bot.run(TOKEN)
