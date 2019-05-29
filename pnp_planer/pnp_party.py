from datetime import datetime, timedelta, timezone
from config import SLOTS, TIME_FORMATER
from json import loads, dumps
from icalendar import Calendar, Event
from uuid import uuid4
import caldav
import logging

class PnPParty():
    def __init__(self, date: datetime, gamemaster: str = None, player_list: list = None,
                 slot: int = 1, max_player: int = 4, title: str ="", duration:int = 4):

        self._date=date
        self._gm =gamemaster
        self._players = player_list
        self._slot = slot
        self._max_player = max_player
        self._event = None
        self._title = title
        self._duration = duration


    @staticmethod
    def generate_from_caldav(event: caldav.Event):
        def gt(dt_str):
            dt, _, us= dt_str.partition(".")
            dt= datetime.strptime("{} +0000".format(dt), "%Y-%m-%dT%H:%M:%S %z")
            return dt

        def obj_hook(obj):
            if '__type__' in obj and obj['__type__']=='PnPParty':
                return PnPParty(gt(obj['date']),
                                obj['gm'],
                                obj['players'],
                                obj['slot'],
                                obj['max_players']
                                )

        subcomponents = Calendar.from_ical(event.data).subcomponents
        if len(subcomponents) == 1:
            tmp_event = subcomponents[0]
            json_string = tmp_event.get('DESCRIPTION')
            try:
                obj = loads(json_string, object_hook=obj_hook)
            except TypeError as e:
                print('The JSON was malformed: {}'.format(e))
                return None
        else:
            print('There are {} submodules, we need exactly 1'.format(len(subcomponents)))
            return None

        obj.event = event
        obj.title = tmp_event.get('SUMMARY')

        if not tmp_event.get("dtstart").dt == obj.date :
            print(obj.date, tmp_event.get("dtstart").dt)
            logging.warning("json date and dtstart are not equal.")
            obj.date = tmp_event.get("dtstart").dt

        return obj



    def _build_json(self):
        j_dict = {
            '__type__':'PnPParty',
            'gm':self.gm,
            'players':self.players,
            'date':self.date.strftime("%Y-%m-%dT%H:%M:%S"),
            'slot':self.slot,
            'max_players':self.max_players
        }

        return dumps(j_dict)

    def generate_ical(self):
        cal = Calendar()
        cal.add('proid', '-//The PnP Planer//')
        cal.add('version', '2.0')

        event = Event()
        if self.title:
            event.add('summary', self.title)
        elif self.gm:
            event.add('summary','Room {} - GM {}'.format(self.slot, self.gm))
        else:
            event.add('summary', 'Room {} - We want you for GM'.format(self.slot))

        event.add('dtstart', self.date)
        event.add('dtend', self.date + timedelta(hours=self.duration))
        event.add('description', self._build_json())
        event.add('uid', uuid4())

        cal.add_component(event)

        return cal.to_ical()

    def display(self):
        return [self.date.strftime(TIME_FORMATER), "Room {}".format(self.slot), self.title, self.gm, ", ".join(self.players)]

    @property
    def event(self):
        return self._event

    @event.setter
    def event(self, event:caldav.Event):
        self._event = event

    @property
    def gm(self):
        if self._gm:
            return self._gm
        else:
            return ""

    @gm.setter
    def gm(self, gamemaster):
        self._gm = gamemaster

    @gm.deleter
    def gm(self):
        self._gm = ""

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

    @date.setter
    def date(self, date):
        self._date = date

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, duration):
        self._duration = duration

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
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @title.deleter
    def title(self):
        self._title=""

    @property
    def players(self):
        if self._players:
            return self._players
        return []

    def add_player(self, player):
        if not self._players:
            self._players = [player]
            return
        if len(self._players) == self._max_player:
            raise ValueError("Max Player Count Reached!")

        self._players.append(player)

    def remove_player(self, player):

        before = len(self.players)
        self._players = [p for p in self._players if p != player]
        after = len(self.players)

        if not before == after:
            return True



