# angel-data

Public data files for the Angel app, fetched by the app to stay current between releases.

## calendar/iran.json

First days of Hijri months in the official calendar of Iran, as published on
[time.ir](https://www.time.ir) (Calendar Center, Institute of Geophysics, University of Tehran).
A lunar month starts on the sighting of the new crescent, so its first day is known only when it is
announced; the app uses these starts and estimates the months after the last one.

- `starts[].first`: the month's first day (Gregorian, ISO 8601).
- `starts[].seen`: when that start was first recorded.
- `checked`: the last day the file was compared with time.ir.

`scripts/update_iran_calendar.py` updates the file; the GitHub Action runs it every six hours and
commits only when something changed. prayer.aviny.com is read as a second opinion and any
disagreement shows as a warning in the run.
