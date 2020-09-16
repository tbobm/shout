"""
Command-line utility allowing interactions with ETNA's APIs.

Powered by etnawrapper: github.com/tbobm/etnawrapper
"""
import os
import datetime
from textwrap import dedent
import typing

import click
from etnawrapper import EtnaWrapper


__author__ = 'Theo "Bob" Massard <tbobm@pm.me>'


def get_wrapper():
    """Instantiate the APIWrapper."""
    # TODO: Config-based credential management ?
    login = os.environ.get("ETNA_USER")
    return EtnaWrapper(login=login, password=os.environ.get("ETNA_PASS"))


def find_targeted_activity_details(
    activities: dict, uv_name: str, project: str,
) -> typing.Tuple[int, int]:
    """Pretty print sub activities.

    Find the matching (module_id,activity_id)
    Raise ValueError in case None is found
    """
    # TODO: Avoid first found approach, prompt on conflict
    for name, value in activities.items():
        if name.lower() == uv_name.lower():
            if not value.get("project"):
                activity = value.get("quest")[0]
            else:
                activity = value["project"][0]
            if project.lower() in activity["name"].lower():
                return activity["module_id"], activity["activity_id"]
    raise ValueError("Could not find matching UV/project")


def set_date(yesterday: bool) -> datetime.datetime:
    date = datetime.datetime.today()
    if yesterday:
        date -= datetime.timedelta(days=1)
    return date.replace(second=0, microsecond=0)


def extract_time_limit(time_limit: str) -> typing.Tuple[int, int]:
    """Extract hour and minutes from string.

    >>> extract_time_limit("09:00")
    9, 0
    >>> extract_time_limit("14:30")
    14, 30
    """
    data = time_limit.split(":")
    parts_count = len(data)
    if parts_count == 1:
        print(f"Could not find minutes in {time_limit}, defaulting to 0")
        return int(data[0]), 0
    return int(data[0]), int(data[1])


def prepare_payload(data: dict, start, end, yesterday):
    """Format the payload in order to send the declaration."""
    # TODO: Create declaration structure
    day = set_date(yesterday)
    start_hour, start_minute = extract_time_limit(start)
    end_hour, end_minute = extract_time_limit(end)
    start_date = day.replace(hour=start_hour, minute=start_minute)
    end_date = day.replace(hour=end_hour, minute=end_minute)
    declaration = {
        "start": start_date.strftime('%Y-%m-%d %H:%M'),
        "end": end_date.strftime('%Y-%m-%d %H:%M'),
    }
    data["declaration"] = declaration
    return data


def display_payload(payload: dict):
    click.echo(f"{click.style('From:', bold=True)} {payload['declaration']['start']}")
    click.echo(f"{click.style('To:', bold=True)} {payload['declaration']['end']}")
    click.echo(f"{click.style('module_id:', bold=True)} {payload['module']}")
    click.echo(f"{click.style('activity_id:', bold=True)} {payload['activity']}")
    click.secho("Content:", bold=True)
    print(payload["declaration"]["content"])


@click.command()
@click.option(
    "-u",
    "--uv",
    required=True,
    help="The UV in which your project is (ex: TIC-SEC5, ...)",
)
@click.option(
    "-p",
    "--project",
    required=True,
    help="The project you spent time on (ex: FlySafe, Box, ...)",
)
@click.option(
    "-s", "--start", required=True, help="Starting hour of your session (ex: 9:00)",
)
@click.option(
    "-e", "--end", required=True, help="Closing hour of your session (ex: 12:00)",
)
@click.option(
    "-d",
    "--declaration",
    type=click.File("r"),
    help="Your pre-written declaration file",
)
@click.option(
    "-y",
    "--yesterday",
    type=bool,
    default=False,
    help="Did your work session happen yesterday",
)
@click.option(
    "-f",
    "--fast",
    type=bool,
    default=False,
    help="Did your work session happen yesterday",
)
def main(
    project: str,
    uv: str,
    start: str,
    end: str,
    declaration: typing.Optional[typing.IO],
    yesterday: bool,
    fast: bool,
):
    """Declare a working session at ETNA's."""
    wrapper = get_wrapper()
    activities = wrapper.get_current_activities()
    module_id, activity_id = find_targeted_activity_details(
        activities, uv, project,
    )
    if declaration is None:
        content = click.edit(
            dedent(
                """
                Objectifs:
                OBJECTIVES
                Actions:
                ACTIONS
                Résultats:
                RESULTS
                """
            )
        )
    else:
        content = declaration.read()
    if not content:
        click.secho("No declaration content found. Did you provide a file ?", fg="red")
        return 1
    data = {
        "module": module_id,
        "activity": activity_id,
    }
    payload = prepare_payload(data, start, end, yesterday)
    # TODO: Yuk, ugly, should not be there
    payload["declaration"]["content"] = content
    if not fast:
        display_payload(payload)
        try:
            input("If you wish to cancel, press ^C")
        except KeyboardInterrupt:
            click.secho('Cancelling.', fg='red')
            return

    click.secho('Firing declaration!', bold=True)
    wrapper.declare_log(module_id, payload)


if __name__ == "__main__":
    main()
