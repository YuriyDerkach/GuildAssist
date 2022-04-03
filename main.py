import discord
from discord_components import DiscordComponents, Button, ButtonStyle, Select, SelectOption
import configs
import sqlite3 as sql

bot = discord.Client()


class BotInstaller:

    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.guild_channels = {}
        self.guild_roles = {}

    async def bot_setup(self):
        pass


class Menu:
    def __init__(self):
        # self.admin_roles = {}
        self.menu_description = 'Add event - создать событие в указанном чате.'
        self.event_titles = {
            'HCE': 'PvE',
            'Group dungeon': 'PvE',
            'Static dungeon': 'PvE',
            'Avalon': 'PvE',
            'World boss': 'PvE',
            'Open world': 'PvE',
            'Fraction': 'PvP',
            'Gank': 'PvP',
            'Hell gate': 'PvP',
            'Arena': 'PvP',
            'Transportation': 'Peaceful'
        }
        self.event_names_selections = [
            SelectOption(
                label=item[0],
                value=item[0],
                description=item[1]
            ) for item in self.event_titles.items()
        ]
        self.event_channels_selections = []

    async def open_menu(self, msg, author_nick):
        show_admin_menu = await msg.author.send(
            embed=discord.Embed(title='Admin menu:', description=self.menu_description),
            components=[
                [
                    Button(style=ButtonStyle.green, label='Add event'),
                    Button(style=ButtonStyle.red, label='Close')
                ]
            ]
        )
        await show_admin_menu.edit(components=[
            [
                Button(style=ButtonStyle.green, label='Add event', custom_id=str(show_admin_menu.id) + '_01')
            ]
        ])
        response = await bot.wait_for('button_click', check=lambda i: i.author == msg.author)
        while True:
            if response.component.label == 'Add event':
                await self.event_choice(msg, response, author_nick)

    async def event_choice(self, msg, response, author_nick):
        event_settings = {}
        menu_msg = await response.author.send(
            embed=discord.Embed(
                title='Добавление события',
                description='Выберите все настройки, представленные ниже для добавления события.'
            ),
            components=[]
        )
        await menu_msg.edit(
            components=[
                Select(
                    placeholder='Событие',
                    custom_id='00',
                    options=self.event_names_selections
                ),
                Button(label='Создать', style=ButtonStyle.green, custom_id='10', disabled=True)
            ]
        )
        event_settings['Leader'] = author_nick
        channels = sql_connection(f'SELECT channel_name FROM text_channels WHERE guild_id={msg.guild.id}')
        self.event_channels_selections = [
            SelectOption(
                label=name,
                value=name
            ) for name in channels
        ]
        interaction = await bot.wait_for('select_option', check=lambda i: i.author == msg.author)
        if interaction.custom_id == '00':
            event_settings['Name'] = interaction.values[0]
            event_settings['Type'] = self.event_titles[event_settings['Name']]
            await interaction.edit_origin(
                embed=discord.Embed(
                    title='Добавление события',
                    description=f"Выберите все настройки, представленные ниже для добавления события.\n\n"
                                f"Событие: {event_settings['Name']}\n"
                                f"Тип события: {event_settings['Type']}"
                ),
                components=[
                    Select(
                        placeholder='Канал',
                        custom_id='01',
                        options=self.event_channels_selections
                    ),
                    Button(label='Создать', style=ButtonStyle.green, custom_id='10', disabled=True)
                ]
            )
            interaction = await bot.wait_for('select_option', check=lambda i: i.author == msg.author)
            if interaction.custom_id == '01':
                event_settings['Channel'] = interaction.values[0]
                await interaction.edit_origin(
                    embed=discord.Embed(
                        title='Добавление события',
                        description=f"Выберите все настройки, представленные ниже для добавления события.\n\n"
                                    f"Событие: {event_settings['Name']}\n"
                                    f"Тип события: {event_settings['Type']}\n"
                                    f"Канал для отправки: {event_settings['Channel']}"
                    ),
                    components=[
                        Button(label='Создать', style=ButtonStyle.green, custom_id='10')
                    ]
                )
                response = await bot.wait_for('button_click', check=lambda i: i.author == msg.author)
                if response.custom_id == '10':
                    await menu_msg.delete()
                    await events.add_event(event_settings)


class AdminMenu(Menu):
    def __init__(self):
        super().__init__()
        self.admin_roles = {}


class Events:

    def __init__(self):
        self.game_roles = ('Tank', 'Healer', 'DPS',)

    async def add_event(self, event_settings):
        event_title = f"{event_settings['Name']} [{event_settings['Type']}]\n" \
                      f"Лидер: {event_settings['Leader']}\n" \
                      f"ID события:"
        event_members = {
            'Tanks': [],
            'Healers': [],
            'DPS': []
        }
        new_line = '\n'
        event_description = \
            '\n'.join([f'{key}:{new_line.join(event_members[key])}\n' for key in event_members])
        event_msg = await bot_install.guild_channels[event_settings['Channel']].send(
            embed=discord.Embed(
                title=event_title,
                description=event_description
            )
        )
        event_title += str(event_msg.id)
        sql_connection(f"INSERT INTO events VALUES"
                       f"({event_msg.id}, {event_msg.channel.id}, '{event_title}', "
                       f"{event_msg.guild.id}, '{''.join(event_members['Tanks'])}', "
                       f"'{''.join(event_members['Healers'])}', '{''.join(event_members['DPS'])}')")
        await event_msg.edit(
            embed=discord.Embed(
                title=event_title,
                description=event_description
            ),
            components=[
                [
                    Button(style=ButtonStyle.blue, label=self.game_roles[0], custom_id=str(event_msg.id) + '_00'),
                    Button(style=ButtonStyle.green, label=self.game_roles[1], custom_id=str(event_msg.id) + '_01'),
                    Button(style=ButtonStyle.red, label=self.game_roles[2], custom_id=str(event_msg.id) + '_02')
                ]
            ]
        )
        while True:
            response = await bot.wait_for('button_click')
            await self.event_join(response)

    async def event_join(self, response):
        new_line = '\n'
        event_title = sql_connection(f'SELECT event_title FROM events '
                                     f'WHERE event_msg_id={int(response.custom_id[:-3])}')[0]
        event_members = {
            'Tanks': sql_connection(f'SELECT tanks FROM events '
                                    f'WHERE event_msg_id={int(response.custom_id[:-3])}')[0].split(', '),
            'Healers': sql_connection(f'SELECT healers FROM events '
                                      f'WHERE event_msg_id={int(response.custom_id[:-3])}')[0].split(', '),
            'DPS': sql_connection(f'SELECT dps FROM events '
                                  f'WHERE event_msg_id={int(response.custom_id[:-3])}')[0].split(', ')
        }
        channel_id = sql_connection(f'SELECT event_channel_id FROM events '
                                    f'WHERE event_msg_id={int(response.custom_id[:-3])}')[0]
        channel = bot.get_channel(channel_id)
        event_msg = await channel.fetch_message(int(response.custom_id[:-3]))
        if response.component.label == 'Tank' and response.author.display_name not in event_members['Tanks']:
            if response.author.display_name in event_members['Healers']:
                event_members['Healers'].remove(response.author.display_name)
            elif response.author.display_name in event_members['DPS']:
                event_members['DPS'].remove(response.author.display_name)
            event_members['Tanks'].append(response.author.display_name)
            event_description = \
                '\n'.join([f'{key}:{new_line.join(event_members[key])}\n' for key in event_members])
            await event_msg.edit(
                embed=discord.Embed(
                    title=event_title,
                    description=event_description
                )
            )
        elif response.component.label == 'Healer' and response.author.display_name not in event_members['Healers']:
            if response.author.display_name in event_members['Tanks']:
                event_members['Tanks'].remove(response.author.display_name)
            elif response.author.display_name in event_members['DPS']:
                event_members['DPS'].remove(response.author.display_name)
            event_members['Healers'].append(response.author.display_name)
            event_description = \
                '\n'.join([f'{key}:{new_line.join(event_members[key])}\n' for key in event_members])
            await event_msg.edit(
                embed=discord.Embed(
                    title=event_title,
                    description=event_description
                )
            )
        elif response.component.label == 'DPS' and \
                response.author.display_name not in event_members['DPS']:
            if response.author.display_name in event_members['Tanks']:
                event_members['Tanks'].remove(response.author.display_name)
            elif response.author.display_name in event_members['Healers']:
                event_members['Healers'].remove(response.author.display_name)
            event_members['DPS'].append(response.author.display_name)
            event_description = \
                '\n'.join([f'{key}:{new_line.join(event_members[key])}\n' for key in event_members])
            await event_msg.edit(
                embed=discord.Embed(
                    title=event_title,
                    description=event_description
                )
            )
        sql_connection(
            f"UPDATE events SET tanks='{', '.join(event_members['Tanks'])}' "
            f"WHERE event_msg_id={int(response.custom_id[:-3])}"
        )
        sql_connection(
            f"UPDATE events SET healers='{', '.join(event_members['Healers'])}' "
            f"WHERE event_msg_id={int(response.custom_id[:-3])}"
        )
        sql_connection(
            f"UPDATE events SET dps='{', '.join(event_members['DPS'])}' "
            f"WHERE event_msg_id={int(response.custom_id[:-3])}"
        )


def sql_connection(sql_request):
    with sql.connect('bot.db') as db:
        cur = db.cursor()
        cur.execute(sql_request)
        if 'SELECT' in sql_request:
            fet = cur.fetchall()
        db.commit()
    if 'SELECT' in sql_request:
        result = [value[0] for value in fet]
        return result


@bot.event
async def on_ready():
    DiscordComponents(bot)
    print('Bot connected')


@bot.event
async def on_message(message):
    if bot_install.guild_id == None:
        print('Installing bot')
        bot_install.guild_id = message.guild.id
        if bot_install.guild_id not in sql_connection('SELECT guild_id FROM guilds'):
            sql_connection(f'INSERT INTO guilds VALUES({message.guild.id}, \'{message.guild.name}\')')
        for channel in message.guild.channels:
            if isinstance(channel, discord.TextChannel):
                bot_install.guild_channels[channel.name] = channel
                if channel.id not in sql_connection('SELECT channel_id FROM text_channels'):
                    sql_connection(f'INSERT INTO text_channels VALUES'
                                   f'({channel.id}, \'{channel.name}\', {message.guild.id})')
        for role in bot.get_guild(message.guild.id).roles:
            if role.id == message.guild.id:
                continue
            bot_install.guild_roles[role.name] = role
            if role.permissions.manage_messages:
                admin_menu.admin_roles[role.name] = role
                if role.name not in sql_connection('SELECT role_name FROM guild_roles'):
                    sql_connection(f'INSERT INTO guild_roles VALUES'
                                   f'({role.id}, \'{role.name}\', 1, {message.guild.id})')
            if role.name not in sql_connection('SELECT role_name FROM guild_roles'):
                sql_connection(f'INSERT INTO guild_roles VALUES'
                               f'({role.id}, \'{role.name}\', 2, {message.guild.id})')
        events.event_channels_buttons = \
            [Button(style=ButtonStyle.gray, label=channel) for channel in bot_install.guild_channels.keys()]
        print('Bot installed')

    if message.content == '!menu':
        if set([role.id for role in message.author.roles]) & \
                set(sql_connection('SELECT role_id FROM guild_roles WHERE admin=1')):
            print('i can admin')
            await message.delete()
            await admin_menu.open_menu(message, message.author.display_name)
        else:
            print('i cant admin')
            await message.delete()
            await menu.open_menu(message, message.author.display_name)

    if message.content == '!test':
        msg = await message.channel.send(content='test')
        msg_id = msg.id
        msgg = await bot.get_channel(message.channel.id).fetch_message(msg_id)
        await msgg.edit(content='edited')

    # reply - не то
    if message.content == '!test2':
        msg_id = message.id
        msg = await bot.get_channel(message.channel.id).fetch_message(msg_id)
        print(msg)
        await msg.reply(content='test2')

    if message.content == '!test3':
        mem = await bot.get_guild(message.guild.id).fetch_member(message.author.id)
        print(mem)
        print(message.author.display_name)


if __name__ == '__main__':
    bot_install = BotInstaller(None)
    menu = Menu()
    admin_menu = AdminMenu()
    events = Events()
    bot.run(configs.settings['token'])
