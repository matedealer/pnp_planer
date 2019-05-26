from datetime import datetime, timedelta, time, date
from config import SLOTS
from json import loads, dumps
from icalendar import Calendar, Event
from uuid import uuid4
import caldav

class PnPParty():
    def __init__(self, date: datetime, gamemaster:str = None, player_list: list = None, slot = 1, max_player: int = 4):
        self._date=date
        self._gm =gamemaster
        self._players = player_list
        self._slot = slot
        self._max_player = max_player


    @staticmethod
    def generate_from_caldav(event: caldav.Event):
        def gt(dt_str):
            dt, _, us= dt_str.partition(".")
            dt= datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
            us= int(us.rstrip("Z"), 10)
            return dt + timedelta(microseconds=us)

        def obj_hook(obj):
            if '__type__' in obj and obj['__type__']=='PnPParty':
                return PnPParty(gt(obj['date']),
                                obj['gm'],
                                obj['players'],
                                obj['slot'],
                                obj['max_players'],
                                )

        subcomponents = Calendar.from_ical(event.data).subcomponents
        if len(subcomponents) == 1:
            json_string = subcomponents[0].get('DESCRIPTION')
            try:
                obj = loads(json_string, object_hook=obj_hook)
            except TypeError as e:
                print('The JSON was malformed: {}'.format(e))
                return None
        else:
            print('There are {} submodules, we need exactly 1'.format(len(subcomponents)))
            return None

        obj.event = event
        return obj



    def _build_json(self):
        j_dict = {
            '__type__':'PnPParty',
            'gm':self.gm,
            'players':self.players,
            'date':self.date.isoformat(),
            'slot':self.slot,
            'max_players':self.max_players
        }

        return dumps(j_dict)

    def generate_ical(self):
        cal = Calendar()
        cal.add('proid', '-//The PnP Planer//')
        cal.add('version', '2.0')

        event = Event()
        event.add('summary','Slot {} - SL {}'.format(self.slot, self.gm))
        event.add('dtstart', self.date)
        event.add('dtend', self.date + timedelta(hours=4))
        event.add('description', self._build_json())
        event.add('uid', uuid4())

        cal.add_component(event)

        return cal.to_ical()

    @property
    def event(self):
        return self._event

    @event.setter
    def event(self, event:caldav.Event):
        self._event = event

    @property
    def gm(self):
        return self._gm

    @gm.setter
    def gm(self, gamemaster):
        self._gm = gamemaster

    @gm.deleter
    def gm(self):
        del self._gm

    @property
    def slot(self):
        return self._slot

    @slot.setter
    def slot(self, slot):
        if slot in SLOTS:
            self._slot = slot
        else:
            raise ValueError("No Slot {} avaible!".format(slot))

    @property
    def date(self):
        return self._date

    def set_time(self, time):
        self._date = datetime.combine(self.date.date(), time)


    @property
    def max_players(self):
        return self._max_player

    @max_players.setter
    def max_players(self, max):
        self._max_player = max

    @max_players.deleter
    def max_players(self):
        del self._max_player

    @property
    def players(self):
        return self._players

    @players.deleter
    def players(self):
        del self._players

    def add_player(self, player):
        if not list:
            self._players = []
        if len(self._players) == self._max_player:
            raise ValueError("Max Player Count Reached!")

        self.players.append(player)

    def remove_player(self, player):
        self._players = [p for p in self._players if p != player]


