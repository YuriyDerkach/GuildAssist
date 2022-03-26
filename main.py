import discord
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption
import configs

bot = discord.Client()


class BotInstaller:

    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.guild_channels = {}
        self.guild_roles = {}

    async def bot_setup(self):
        pass


class AdminMenu:

    def __init__(self):
        self.admin_roles = {}
        self.menu_description = 'Add event - создать событие в указанном чате.'

    async def open_menu(self, msg):

        show_admin_menu = await msg.author.send(
            embed=discord.Embed(title='Admin menu:', description=self.menu_description),
            components=[
                [
                    Button(style=ButtonStyle.green, label='Add event'),
                    Button(style=ButtonStyle.red, label='Close')
                ]
            ]
        )
        response = await bot.wait_for('button_click')
        if response.component.label == 'Add event':
            await events.add_event(response)
        elif response.component.label == 'Close':
            await show_admin_menu.delete()


class Events:

    def __init__(self):
        self.event_names = ('HCE', 'Group dungeon', 'Static dungeon',)
        self.event_names_buttons = [Button(style=ButtonStyle.gray, label=name) for name in self.event_names]
        self.event_channels_buttons = []
        self.game_roles = ('Tank', 'Healer', 'Damage dealer',)
        self.event_members = {
            'Tanks': [],
            'Healers': [],
            'Damage dealers': []
        }
        self.event_description = 'Tanks:\n{}\n' \
                                 'Healers:\n{}\n' \
                                 'Damage dealers:\n{}'.format(
            self.event_members['Tanks'],
            self.event_members['Healers'],
            self.event_members['Damage dealers'],
        )

    async def add_event(self, msg):
        name_choice = await self.name_choice(msg)
        event_name = name_choice.component.label
        channel_choice = await self.channel_choice(name_choice)
        channel_name = channel_choice.component.label
        await bot_install.guild_channels[channel_name].send(content='@everyone')
        event_msg = await bot_install.guild_channels[channel_name].send(
            embed=discord.Embed(
                title=event_name,
                description=self.event_description
            ),
            components=[
                [
                    Button(style=ButtonStyle.blue, label=self.game_roles[0]),
                    Button(style=ButtonStyle.green, label=self.game_roles[1]),
                    Button(style=ButtonStyle.red, label=self.game_roles[2])
                ]
            ]
        )
        response = await bot.wait_for('button_click')
        await self.event_join(event_msg, response)

    async def name_choice(self, msg):
        await msg.respond(
            embed=discord.Embed(
                title='Событие',
                description='Выберите какое событие создать.'
            ),
            components=[
                self.event_names_buttons
            ]
        )
        return await bot.wait_for('button_click')

    async def channel_choice(self, msg):
        await msg.respond(
            embed=discord.Embed(
                title='Канал',
                description='Выберите канал, в котором отобразиться событие.'
            ),
            components=[
                self.event_channels_buttons
            ]
        )
        return await bot.wait_for('button_click')

    async def event_join(self, event_msg, response):
        if response.component.label == 'Tank':
            self.event_members['Tanks'].append(response.author.nick)
            event_msg.edit(
                embed=discord.Embed(
                    description=self.event_description
                )
            )
        elif response.component.label == 'Healer':
            self.event_members['Healers'].append(response.author.nick)
            event_msg.edit(
                embed=discord.Embed(
                    description=self.event_description
                )
            )
        elif response.component.label == 'Damage dealer':
            self.event_members['Damage dealers'].append(response.author.nick)
            event_msg.edit(
                embed=discord.Embed(
                    description=self.event_description
                )
            )


@bot.event
async def on_ready():
    DiscordComponents(bot)
    print('Bot connected')


@bot.event
async def on_message(message):
    if bot_install.guild_id == None:
        print('Installing bot')
        bot_install.guild_id = message.guild.id
        for channel in bot.get_guild(message.guild.id).channels:
            if isinstance(channel, discord.TextChannel):
                bot_install.guild_channels[channel.name] = channel
        for role in bot.get_guild(message.guild.id).roles:
            bot_install.guild_roles[role.name] = role
            if role.permissions.manage_messages:
                admin_menu.admin_roles[role.name] = role
        events.event_channels_buttons = \
            [Button(style=ButtonStyle.gray, label=channel) for channel in bot_install.guild_channels.keys()]

    if message.content == '!menu':
        if set(message.author.roles) & set(admin_menu.admin_roles.values()):
            print('i can admin')
            await message.delete()
            await admin_menu.open_menu(message)
        else:
            print('i cant admin')

    if message.content == '!test':
        await message.author.send(content='test')
        await message.delete()


if __name__ == '__main__':
    bot_install = BotInstaller(None)
    admin_menu = AdminMenu()
    events = Events()
    bot.run(configs.settings['token'])
