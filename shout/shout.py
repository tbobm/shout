"""
Command-line utility allowing interactions with ETNA's APIs.

Powered by etnawrapper: github.com/tbobm/etnawrapper
"""
import os
import argparse
import datetime
import typing

from etnawrapper import EtnaWrapper


__author__ = 'Theo "Bob" Massard <massar_t@etna-alternance.net>'


def parse_args() -> argparse.Namespace:
    """Prepare parser for command-line interaction."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", action="store_true", help="display the current version"
    )
    parser.add_argument("-v", action="store_true", help="increase verbosity")
    parser.add_argument("-u", "--uv", required=True, help="Targeted module")
    parser.add_argument(
        "-p", "--project", required=True, help="Name of the project or quest step"
    )
    parser.add_argument(
        "-d",
        "--declaration",
        type=argparse.FileType("r"),
        help="File containing the declaration",
    )
    parser.add_argument(
        "-s", "--start-time",
        type=str, required=True,
        help="Start hour of working session",
    )
    parser.add_argument(
        "-e", "--end-time",
        type=str, required=True,
        help="End hour of the working session",
    )
    parser.add_argument(
        "-y",
        "--yesterday",
        action="store_true",
        help="Declare for the previous day",
    )
    parser.add_argument(
        "-f",
        "--fast",
        action="store_true",
        help="Do not prompt for anything, fire the declaration right away",
    )
    parsed = parser.parse_args()
    return parsed


def get_wrapper():
    """Instantiate the APIWrapper."""
    # TODO: Config-based credential management ?
    login = os.environ.get("ETNA_USER")
    return EtnaWrapper(login=login, password=os.environ.get("ETNA_PASS"))


def find_targeted_activity_details(
    activities: dict, uv_name: str, project: str, verbose=False
) -> typing.Tuple[int, int]:
    """Pretty print sub activities.

    Find the matching (module_id,activity_id)
    Raise ValueError in case None is found
    """
    # TODO: Avoid first found approach, prompt on conflict
    project_type = ''
    for name, value in activities.items():
        if name.lower() == uv_name.lower():
            if not value.get("project"):
                activity = value.get('quest')[0]
                project_type == 'quest'
            else:
                activity = value["project"][0]
                project_type == 'project'
            if project.lower() in activity["name"].lower():
                return activity["module_id"], activity["activity_id"]
    raise ValueError("Could not find matching UV/project")


def set_date(arguments: argparse.Namespace) -> datetime.datetime:
    date = datetime.datetime.today()
    if arguments.yesterday:
        date -= datetime.timedelta(days=1)
    return date.replace(second=0, microsecond=0)


def extract_time_limit(time_limit: str) -> typing.Tuple[int, int]:
    """Extract hour and minutes from string.

    >>> extract_time_limit("09:00")
    9, 0
    >>> extract_time_limit("14:30")
    14, 30
    """
    data = time_limit.split(':')
    parts_count = len(data)
    if parts_count == 1:
        print(f'Could not find minutes in {time_limit}, defaulting to 0')
        return int(data[0]), 0
    return int(data[0]), int(data[1])


def prepare_payload(module_id: int, activity_id: int, parsed: argparse.Namespace):
    """Format the payload in order to send the declaration."""
    # TODO: Create declaration structure
    data = {"module": module_id, "activity": activity_id}
    day = set_date(parsed)
    start_hour, start_minute = extract_time_limit(parsed.start_time)
    end_hour, end_minute = extract_time_limit(parsed.end_time)
    start_date = day.replace(hour=start_hour, minute=start_minute)
    end_date = day.replace(hour=end_hour, minute=end_minute)
    declaration = {
        "start": start_date,
        "end": end_date,
        "content": parsed.declaration.read(),
    }
    data["declaration"] = declaration
    print(data)
    return data


def display_payload(payload: dict):
    print("From: {}".format(payload["declaration"]["start"]))
    print("To: {}".format(payload["declaration"]["end"]))
    print("module_id: {}".format(payload["module"]))
    print("activity_id: {}".format(payload["activity"]))
    print("Content:")
    print(payload["declaration"]["content"])


def main():
    """Run the shouter."""
    parsed = parse_args()
    wrapper = get_wrapper()
    activities = wrapper.get_current_activities()
    module_id, activity_id = find_targeted_activity_details(
        activities, parsed.uv, parsed.project, parsed.v
    )
    print(module_id, activity_id)
    payload = prepare_payload(module_id, activity_id, parsed)
    if not parsed.fast:
        display_payload(payload)
        input("If you wish to cancel, press ^C")

    response = wrapper.declare_log(module_id, payload)


if __name__ == "__main__":
    main()
