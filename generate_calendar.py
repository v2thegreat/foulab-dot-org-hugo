#!/usr/bin/env python3
"""
Usage:
    python generate_calendar.py <PATH_TO_NEWS_ARTICLE>

Given a text file of lines that start with "###" containing a date/time in the format:
    ### Some event title - Monday January 23rd @ 18:00 - 20:00
this script outputs ICS (iCalendar) events for each matching line in that file.
"""

import sys
import uuid
from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo


def header_into_event(header: str) -> str:
    """
    Convert a line from the news article (which starts with "###")
    into an iCalendar event (VEVENT) string.

    Expected line format example:
        ### Some event - Monday January 23rd @ 18:00 - 20:00
    """
    # Split out time (right of '@') and date (right of the last '-')
    header, evtime = header.rsplit("@", 1)
    header, evdate = header.rsplit("-", 1)

    # Clean up the header text
    header = header.removeprefix("###").strip()

    now = datetime.now()
    # Remove possible suffixes on the day (st, nd, rd, th) and assume current year
    evdate = (
        evdate.strip()
        .removesuffix("st")
        .removesuffix("nd")
        .removesuffix("rd")
        .removesuffix("th")
    )
    evdate += f" {now.year}" if now.month != 12 else f" {now.year + 1}"

    # Convert date string to a datetime object
    evdate = datetime.strptime(evdate, "%A %B %d %Y")

    # Parse start/end times from the remaining string
    start_time_str, end_time_str = (t.strip() for t in evtime.split("-"))
    start_time = time.fromisoformat(start_time_str)
    end_time = time.fromisoformat(end_time_str)

    # Combine date + time, with a fixed timezone
    start_dt = datetime.combine(
        evdate.date(), start_time, tzinfo=ZoneInfo("America/New_York")
    )
    end_dt = datetime.combine(
        evdate.date(), end_time, tzinfo=ZoneInfo("America/New_York")
    )

    # Build ICS-format timestamps
    dtstamp = (
        now.astimezone(timezone.utc)
        .replace(tzinfo=None)
        .isoformat()
        .replace("-", "")
        .replace(":", "")
        .split(".")[0]
    )

    # Return a multi-line string for the event
    return (
        "BEGIN:VEVENT\n"
        f"DTSTAMP:{dtstamp}Z\n"
        f"UID:{uuid.uuid4()}\n"
        f'DTSTART;TZID="America/New_York":'
        f"{start_dt.replace(tzinfo=None).isoformat().replace('-', '').replace(':', '')}\n"
        f'DTEND;TZID="America/New_York":'
        f"{end_dt.replace(tzinfo=None).isoformat().replace('-', '').replace(':', '')}\n"
        f"SUMMARY:{header}\n"
        "URL:https://foulab.org\n"
        f"DESCRIPTION:{header}\n"
        "LOCATION:Foulab\\, 999 Rue du Collège\\, Montréal\\, QC H4C 2S2\\, Canada\n"
        "END:VEVENT"
    )


def main() -> None:
    """
    Main entry point: read the specified file, process each line starting with '###',
    and print an ICS event.
    """
    if len(sys.argv) != 2:
        print("Usage: python generate_calendar.py <PATH_TO_NEWS_ARTICLE>")
        sys.exit(1)

    filename = sys.argv[1]

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            # Strip whitespace before checking/processing
            line = line.strip()
            if line.startswith("###"):
                try:
                    print(header_into_event(line))
                except Exception as e:
                    print(f"Error processing line '{line}': {e}")


if __name__ == "__main__":
    main()
