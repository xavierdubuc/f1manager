from src.media_generation.layout import *
from src.media_generation.layout.polygons_layout import DEFAULT_POLYGONS


FBRT = {
    # just _values
    "numbers": "data/layouts/numbers.xml",
    "season_pilots": "data/layouts/season_pilots.xml",
    "season_teams": "data/layouts/season_teams.xml",
    # RaceReader
    "lineup": "data/layouts/lineup.xml",
    "results": "data/layouts/results.xml",
    "time_trial": "data/layouts/time_trial.xml",
}

FBRT["time_trial"] = "data/layouts/time_trial.xml"


F140 = {
    "lineup": PolygonsLayout(
        name="lineup",
        width=1920,
        height=1080,
        bg=255,
        children={
            "black_rows": ImageLayout(
                "black_rows",
                path="assets/backgrounds/FBRT/lineup.png",
                width=1920,
                height=1080,
                top=0,
                left=0,
            ),
            "f140": ImageLayout(
                "f140",
                path="assets/logos/F140/black.png",
                width=175,
                left=1740,
                top=0,
            ),
            "date": TextLayout(
                name="date",
                content="{race.day} {month_fr}",
                width=1200,
                height=35,
                bottom=16,
                right=10,
                font_name="regular",
                bg=(10, 8, 32),
                fg=(255, 255, 255, 255)
            ),
            "hour": TextLayout(
                name="hour",
                content="{race.hour}",
                width=1200,
                height=35,
                bottom=60,
                right=10,
                font_name="regular",
                bg=(10, 8, 32),
                fg=(255, 255, 255, 255)
            ),
            "circuit_name": TextLayout(
                name="circuit_name",
                content="{circuit_city}",
                width=1200,
                height=35,
                left=300,
                bottom=16,
                font_name="regular",
                bg=(10, 8, 32),
                fg=(255, 255, 255, 255)
            ),
            "circuit_flag": ImageLayout(
                name="flag_layout",
                path="assets/circuits/flags/{race.circuit.id}.png",
                width=60,
                height=35,
                left=230,
                bottom=14
            ),
            "line_up_text": TextLayout(
                name="line_up_text",
                top=600,
                width=380,
                height=75,
                content="LINE-UP",
                font_name="black",
                fg=(0, 0, 0),
            ),
            "round": RoundLayout(
                name="round",
                width=125,
                height=125,
                top=425,
                fg=(255, 255, 255, 255),
                children={
                    "round_text": TextLayout(
                        name="round_text",
                        content="R{race.round}",
                        width=90,
                        height=45,
                    ),
                    "subtype_top": TextLayout(
                        name="subtype_top",
                        height=15,
                        top=10,
                        font_name="regular"
                    ),
                    "subtype_bottom": TextLayout(
                        name="subtype_bottom",
                        height=15,
                        bottom=10,
                        font_name="regular"
                    )
                }
            ),
            "teams": TeamsLayout(
                name="teams",
                width=1920,
                height=1080,
                templates={
                    "team": LayoutTemplate(
                        layout=TeamLineupLayout(
                            name="team",
                            width=680,
                            height=200,
                            children={
                                "logo": ImageLayout(
                                    name="logo",
                                    width=220,
                                    height=90,
                                    top=30
                                ),
                                "pilot_1": Layout(
                                    name="pilot_1",
                                    left=0,
                                    top=0,
                                    width=368,
                                    height=200,
                                    children={
                                        "face": PilotPhotoLayout(
                                            name="face",
                                            width=368,
                                            height=143,
                                            top=5,
                                        ),
                                        "box": PilotBoxLayout(
                                            name="box",
                                            width=368,
                                            height=62,
                                            left=0,
                                            top=138,
                                            children={
                                                "name": TextLayout(
                                                    content="{pilot_name}",
                                                    name="name",
                                                    height=28,
                                                    width=250
                                                )
                                            }
                                        ),
                                    }
                                ),
                                "pilot_2": Layout(
                                    name="pilot_2",
                                    left=312,
                                    top=0,
                                    width=368,
                                    height=200,
                                    children={
                                        "face": PilotPhotoLayout(
                                            name="face",
                                            width=368,
                                            height=143,
                                            top=5,
                                        ),
                                        "box": PilotBoxLayout(
                                            name="box",
                                            width=368,
                                            height=62,
                                            left=0,
                                            top=138,
                                            children={
                                                "name": TextLayout(
                                                    content="{pilot_name}",
                                                    name="name",
                                                    height=28,
                                                    width=250
                                                )
                                            }
                                        ),
                                    }
                                ),
                            }
                        ),
                        instances=[
                            {"left": 295, "top": 2},
                            {"left": 938, "top": 2},
                            {"left": 150, "top": 204},
                            {"left": 1095, "top": 204},
                            {"left": 32, "top": 406},
                            {"left": 1203, "top": 406},
                            {"left": 150, "top": 608},
                            {"left": 1098, "top": 608},
                            {"left": 295, "top": 810},
                            {"left": 938, "top": 810},
                        ]
                    )
                },
            )
        },
        polygons=DEFAULT_POLYGONS
    ),
}
