import discord
from config import CALDAV_LINK, SLOTS, TOKEN, TIME_FORMATER, ERROR_MSG
from datetime import datetime, timedelta
from discord.ext import commands
from pnp_party import PnPParty
from caldav_wrapper import CalWrapper
from utils import string_to_date
from tabulate import tabulate


description = '''A bot to have a nice tool for planing pnp parties in discord.
                The source code is public available on https://github.com/matedealer/pnp_planer \n
                Date formats: 
                * today, heute, now 
                * tomorrow, morgen  
                * Weekdays (Full or Abbr.) in English or German. 
                * 13.04.2019-14:56 
                * 13.04.2019 
                * 13.04
                
                
'''



bot = commands.Bot(command_prefix='\\', description=description)
cal = CalWrapper(CALDAV_LINK)

def validate_room(room):
    try:
        room = int(room)
    except ValueError:
        return ( False, ERROR_MSG['invalid_slot'].format(room))

    if not room in SLOTS:
        return (False, ERROR_MSG['invalid_slot'].format(room))

    return True, room

async def print_date_pretty(ctx, msg, events):
    if isinstance(events, PnPParty):
        resp = tabulate([events.display()],
                        headers=["Date", "Room", "Title", "Game Master", "Players"],
                        tablefmt="pipe"
                        )
    else:
        resp = tabulate([event.display() for event in sorted(events, key=lambda x: x.date)],
                    headers=["Date","Room", "Title", "Game Master", "Players"],
                    tablefmt="pipe"
                    )
    await ctx.send("{}: ```{}```".format(msg, resp))


@bot.event
async def on_ready():
    print('Logged in as {} with ID {}'.format(bot.user.name, bot.user.id))
    print('------')



@bot.command()
async def new(ctx, date:str="today", room:str=None, as_gm:str=False):
    '''Set up new event'''
    if room:
        room, err_msg = validate_room(room)
        if not room:
            await ctx.send(err_msg)
            return

    event_date = string_to_date(date)
    if not event_date:
        await ctx.send(ERROR_MSG['invalid_date'].format(date))
        return

    free_slots = cal.get_free_slot(event_date)

    if not free_slots:
        await ctx.send("Sorry, on {} we don't have any room available :frowning2:".format(event_date.strftime(TIME_FORMATER)))
        return

    if room in free_slots:
        old_slot = room
        room = free_slots[0]

        await ctx.send("Sorry, on {} room {} is already book, but we reserved you room {}".format(
            event_date.strftime(TIME_FORMATER), old_slot, room))

    if not room:
        room = free_slots[0]

    event = PnPParty(event_date, ctx.author.name if as_gm else None, [], room)
    cal.upload_event(event)
    await print_date_pretty(ctx, "We create a new event", event)



@bot.command()
async def delete(ctx, date:str="no date given", room:str= "no room given"):
    '''Delete an event on given date and room.'''
    room, err_msg = validate_room(room)
    if not room:
        await ctx.send(err_msg)
        return

    event_date = string_to_date(date)
    if not event_date:
        await ctx.send(ERROR_MSG['invalid_date'].format(date))
        return

    event = cal.get_event(event_date, room)

    if not event:
        await ctx.send("No event found to delete :frowning2:")
        return

    if not event.gm or event.gm == ctx.author.name:
        cal.delet_event(event)
        await ctx.send("Deleted event on {} in room {}!".format(event_date.strftime(TIME_FORMATER), room))
        return

    await ctx.send(ERROR_MSG['insufficient_rights'])


@bot.command()
async def attend(ctx, date:str ="today", room:str=1):
    '''Attend at a event'''
    room, err_msg = validate_room(room)
    if not room:
        await ctx.send(err_msg)
        return

    event_date = string_to_date(date)
    if not event_date:
        await ctx.send(ERROR_MSG['invalid_date'].format(date))
        return
    event = cal.get_event(event_date, room)

    if event:
        event.add_player(ctx.author.name)
    else:
        event = PnPParty(event_date,player_list=[ctx.author.name])
        await ctx.send("We create a new event on {} at room {}".format(event_date.strftime(TIME_FORMATER), room))

    cal.upload_event(event)
    await ctx.send("You're registered as player for {} in room {}".format(event_date.strftime(TIME_FORMATER), room))


@bot.command()
async def add_player(ctx, date:str ="no value given", room:str = "no value given", player_name:str=None):
    '''As gm add players to your event'''
    room, err_msg = validate_room(room)
    if not room:
        await ctx.send(err_msg)
        return

    event_date = string_to_date(date)
    if not event_date:
        await ctx.send(ERROR_MSG['invalid_date'].format(date))
        return

    event = cal.get_event(event_date, room)

    if event and ctx.author.name == event.gm:
        event.add_player(player_name)
    else:
        await  ctx.send("Couldn't find any event at {} on room {} with you as GM. Please create an event first.".format(
            event_date.strftime(TIME_FORMATER), room))
        return

    cal.upload_event(event)
    await ctx.send("You're registered {} as player for {} in room {}".format(player_name, event_date.strftime(TIME_FORMATER), room))


@bot.command()
async def del_player(ctx, date:str ="today", room:str = 1, player_name:str=None):
    '''Remove yourself from a event.'''
    room, err_msg = validate_room(room)
    if not room:
        await ctx.send(err_msg)
        return

    event_date = string_to_date(date)
    if not event_date:
        await ctx.send(ERROR_MSG['invalid_date'].format(date))
        return

    event = cal.get_event(event_date, room)

    if not player_name:
        success = event.remove_player(ctx.author.name)
        if success:
            await ctx.send("Successful removed you from player list on {} at room {}".format(
                event_date.strftime(TIME_FORMATER), room
            ))
            cal.upload_event(event)
            return

        await ctx.send("Couldn't find you on {} room {} as player. We searched with your name {}".format(
            event_date.strftime(TIME_FORMATER), room, ctx.author.name
        ))
        return


    if player_name and event.gm == ctx.author.name:
        success = event.remove_player(player_name)
        if success:
            await ctx.send("Successful removed {} from player list on {} at room {}".format(
                player_name, event_date.strftime(TIME_FORMATER), room
            ))
            cal.upload_event(event)
            return

        await ctx.send("Couldn't find {} on {} room {} as player.".format(
            player_name, event_date.strftime(TIME_FORMATER), room
        ))
        return

    await ctx.send(ERROR_MSG['insufficient_rights'])



@bot.command()
async def gm(ctx, date:str ="today", room:str = 1):
    '''Register yourself as a game master'''
    room, err_msg = validate_room(room)
    if not room:
        await ctx.send(err_msg)
        return

    event_date = string_to_date(date)
    if not event_date:
        await ctx.send(ERROR_MSG['invalid_date'].format(date))
        return


    event = cal.get_event(event_date, room)

    if event:
        if event.gm == "":
            event.gm = ctx.author.name
        else:
            await ctx.send("There can be only one GM: {}".format(event.gm))
            return
    else:
        event = PnPParty(event_date, ctx.author.name, [], room)


    cal.upload_event(event)
    await print_date_pretty(ctx, "Add you as new GM for", event)



@bot.command()
async def del_gm(ctx, date:str ="today", room:str = 1):
    '''Remove yourself as a game master'''
    room, err_msg = validate_room(room)
    if not room:
        await ctx.send(err_msg)
        return

    event_date = string_to_date(date)
    if not event_date:
        await ctx.send(ERROR_MSG['invalid_date'].format(date))
        return


    event = cal.get_event(event_date, room)

    if event and event.gm == ctx.author.name:
        del event.gm
        cal.upload_event(event)
        await ctx.send("Remove you successful from event: {} - room {}".format(
            event_date.strftime(TIME_FORMATER), room
        ))
        return
    else:
       await ctx.send("There is no event to remove you as gm from to given date {} on room {}".format(
            event_date.strftime(TIME_FORMATER), room
        ))

@bot.command()
async  def add_title(ctx, title:str, date:str ="today", room:str ="1"):
    '''Add title to event'''
    room, err_msg = validate_room(room)
    if not room:
        await ctx.send(err_msg)
        return

    event_date = string_to_date(date)
    if not event_date:
        await ctx.send(ERROR_MSG['invalid_date'].format(date))
        return

    event = cal.get_event(event_date, room)

    if event:
        event.title = title
        cal.upload_event(event)
        await print_date_pretty(ctx, "We changed title of event", event)




@bot.command()
async def change_date(ctx, old_date:str = "-", new_date:str = "-", room:str = 1):
    '''Change date of event'''
    room, err_msg = validate_room(room)
    if not room:
        await ctx.send(err_msg)
        return

    old_event_date = string_to_date(old_date)
    new_event_date = string_to_date(new_date)
    if not old_event_date:
        await ctx.send(ERROR_MSG['invalid_date'].format(old_date))
        return

    if not new_event_date:
        await ctx.send(ERROR_MSG['invalid_date'].format(new_date))
        return

    event = cal.get_event(old_event_date, room)

    if not event:
        await  ctx.send("Couldn't find any event at {} on room {}.".format(
            old_event_date.strftime(TIME_FORMATER), room))
        return

    event.date = new_event_date
    cal.upload_event(event)
    await print_date_pretty(ctx, "We changed the date of event", event)




@bot.command()
async def overview(ctx, date:str = None):
    '''Show an overview over future pnp parties'''
    if date:
        event_date = string_to_date(date)
        if not event_date:
            await ctx.send(ERROR_MSG['invalid_date'].format(date))
            return

        events = cal.get_events_on_date(event_date)
    else:
        events = cal.get_all_future_events()

    if not events:
        await ctx.send("Couldn't find any date!")
        return

    await print_date_pretty(ctx, "You ask for an overview", events)




bot.run(TOKEN)
