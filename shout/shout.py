"""
Command-line utility allowing interactions with ETNA's APIs.

Powered by etnawrapper: github.com/tbobm/etnawrapper
"""
import os
import argparse
import typing

from etnawrapper import EtnaWrapper


__author__ = 'Theo "Bob" Massard <massar_t@etna-alternance.net>'


def parse_args() -> argparse.ArgumentParser:
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
        required=True,
        help="File containing the declaration",
    )
    parser.add_argument(
        "-s", "--start-date", type=str, required=True, help="Lower bound working limit"
    )
    parser.add_argument(
        "-e", "--end-date", type=str, required=True, help="Upper bound working limit"
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


def prepare_payload(module_id: int, activity_id: int, parsed):
    """Format the payload in order to send the declaration."""
    # TODO: Create declaration structure
    data = {"module": module_id, "activity": activity_id}
    start_date = parsed.start_date
    end_date = parsed.end_date
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
