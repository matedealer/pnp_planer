import icalendar
from datetime import datetime, timedelta
import caldav
from caldav.elements import dav
from pnp_party import PnPParty
from config import SLOTS






class CalWrapper():
    def __init__(self, link):
        calendars = caldav.DAVClient(link).principal().calendars()
        if len(calendars) > 0:
            self.calendar = calendars[0]
        else:
            raise ValueError("No calender found!")

    def upload_event(self, pnp_party: PnPParty):
        ical = pnp_party.generate_ical()

        if pnp_party.event:
            pnp_party.event.data = ical
            pnp_party.event.save()
        else:
            self.calendar.add_event(ical)

    def delet_event(self, pnp_party):
        pnp_party.event.delete()
        del pnp_party

    def get_event(self, event_date: datetime,  slot:int):
        start = event_date
        end = event_date+timedelta(days=1)
        ical_list = self.calendar.date_search(start,end)
        events = (PnPParty.generate_from_caldav(elem) for elem in ical_list)
        for event in events:
            try:
                if event.slot == slot and event.date.date() == event_date.date():
                    return event
            except AttributeError as e:
                print(e)


    def get_all_future_events(self):
        now = datetime.today()

        #bugworkaround
        endtime = now + timedelta(days=365)

        ical_list = self.calendar.date_search(now, endtime)

        events = [PnPParty.generate_from_caldav(elem) for elem in ical_list]

        return events

    def get_events_on_date(self, event_date:datetime):
        start = event_date
        end = event_date + timedelta(days=1)
        ical_list = self.calendar.date_search(start, end)
        events = (PnPParty.generate_from_caldav(elem) for elem in ical_list)
        ret_list = []
        for event in events:
            try:
                if event.date.date() == event_date.date():
                    ret_list.append(event)
            except AttributeError as e:
                print(e)

        return ret_list

    def get_free_slot(self, event_date:datetime):
        events = self.get_events_on_date(event_date)
        return [slot for slot in SLOTS if not slot in [event.slot for event in events]]





