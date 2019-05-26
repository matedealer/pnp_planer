import icalendar
from datetime import datetime, timedelta
import caldav
from caldav.elements import dav
from pnp_party import PnPParty




vcal = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp.//CalDAV Client//EN
BEGIN:VEVENT
UID:1234567890
DTSTAMP:20100510T182145Z
DTSTART:20100512T170000Z
DTEND:20100512T180000Z
SUMMARY:This is an event
END:VEVENT
END:VCALENDAR
"""





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

    def get_event(self, event_date: datetime,  slot:int):
        ical_list = self.calendar.date_search(event_date.date(),event_date.date()+timedelta(days=1))
        events = (PnPParty.generate_from_caldav(elem) for elem in ical_list)
        for event in events:
            if event.slot == slot and event.date.date() == event_date.date():
                return event


    def get_all_future_events(self):
        now = datetime.today()

        #bugworkaround
        endtime = now + timedelta(days=365)

        ical_list = self.calendar.date_search(now, endtime)

        events = [PnPParty.generate_from_caldav(elem) for elem in ical_list]

        return events



    def debug(self):

        print("Using calendar", self.calendar)

        #print("Renaming")
        #calendar.set_properties([dav.DisplayName("pnp_planer"),])
        print(self.calendar.get_properties([dav.DisplayName(),]))

        #event = calendar.add_event(vcal)
        #print("Event", event, "created")

        print("Looking for events in 2010-05")
        results = self.calendar.date_search(
            datetime(2010, 5, 1), datetime(2010, 6, 1))

        for event in results:
            print("Found", event)







