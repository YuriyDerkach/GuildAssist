import discord
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption
import configs

bot = discord.Client()

class BotInstaller:
    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.channels_list = []
        self.setup_channel = None

    def channels_set(self):
        for channel in bot.get_guild(self.guild_id).channels:
            self.channels_list.append(channel)
            if channel.position == 1:
                self.setup_channel = channel

    async def setup(self):
        self.channels_set()
        await self.setup_channel.send('Hello, I am Guild Assistant Bot.\n'
                                      'Before you need to setup me.\n'
                                      'Write: .bot_setup ADMIN_MENU_CHAT EVENTS_CHAT'
                                      )

    async def bot_setup(self):
        pass

class AdminMenu:
    def __init__(self, admin_menu_chat):
        self.admin_menu_chat = admin_menu_chat

    async def open_menu(self):
        chnl_options = []
        for channel in bot_install.channels_list:
            if isinstance(channel, discord.TextChannel) and channel != self.admin_menu_chat:
                chnl_options.append(SelectOption(label=channel.name, value=channel.name))
        menu = await self.admin_menu_chat.send(
            embed=discord.Embed(title='Admin Menu:'),
            components=[
                Select(
                    placeholder='Edit admin menu chat',
                    options=chnl_options
                ),
                Button(style=ButtonStyle.red, label='Close menu')
            ]
        )
        response = await bot.wait_for('button_click')
        if response.channel == self.admin_menu_chat:
            if response.component.label == 'Close menu':
                await menu.delete()

class Events:
    def __init__(self, events_chat):
        self.events_chat = events_chat

@bot.event
async def on_ready():
    DiscordComponents(bot)

@bot.event
async def on_message(message):
    if message.content == '!start_bot':
        global bot_install
        bot_install = BotInstaller(message.guild.id)
        await bot_install.setup()

    if message.content.startswith('!bot_setup'):
        msg_list = message.content.split()
        for chnl in bot.get_guild(message.guild.id).channels:
            if msg_list[1] == chnl.name:
                admin_menu_chat = msg_list[1]
                await message.channel.send('You successfully set #{} as ADMIN_MENU_CHAT.'.format(admin_menu_chat))
                global admin_menu
                admin_menu = AdminMenu(chnl)
            elif msg_list[2] == chnl.name:
                events_chat = msg_list[2]
                await message.channel.send('You successfully set #{} as EVENTS_CHAT.'.format(events_chat))
                events = Events(chnl)
        await admin_menu.open_menu()

    if message.content == '!menu':
        print('done')
        if message.channel == admin_menu.admin_menu_chat:
            print('done')
            await admin_menu.open_menu()

bot.run(configs.settings['token'])
