from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import Diary
import calendar

class Calendar(HTMLCalendar):
    calendar.setfirstweekday(calendar.SUNDAY)
    def __init__(self, year=None, month=None, user=None):
        self.year=year
        self.month=month
        super(Calendar, self).__init__()
        self.user = user

    def formatday(self, day, events):
            events_per_day = events.filter(write_date__day=day)
            d = ''
            for event in events_per_day:
                d += f'<a><br> {event.get_html_url} </a>'
                # print(d)
            if self.month == datetime.today().month and day == datetime.today().day:
                return f"<td style = 'border:3px solid black; height:100px'><span class='date'>{day}</span><url>{d}</url></td>"
            elif day != 0:
                return f"<td style = 'height:100px; border-top:1px solid gray'><span class='date'>{day}</span><url>{d}</url></td>"
            # print(d)
            return '<td></td>'

    def formatweek(self, theweek, events):
            week = ''
            for d, weekday in theweek:
                week += self.formatday(d, events)
                
            return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
            events = Diary.objects.filter(author = self.user).filter(write_date__year=self.year, write_date__month=self.month)

            cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
            cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
            cal += f'{self.formatweekheader()}\n'
            for week in self.monthdays2calendar(self.year, self.month):
                cal += f'{self.formatweek(week, events)}\n'

            cal += f'</table>\n'
            return cal