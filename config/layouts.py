from src.media_generation.layout.image_layout import ImageLayout
from src.media_generation.layout.pilot.pilot_box_layout import PilotBoxLayout
from src.media_generation.layout.pilot.pilot_face_layout import PilotFaceLayout
from src.media_generation.layout.pilot.pilot_lineup_layout import PilotLineupLayout
from src.media_generation.layout.polygons_layout import Polygon, PolygonsLayout
from src.media_generation.layout.race.round_layout import RoundLayout
from src.media_generation.layout.team.team_lineup_layout import TeamLineupLayout
from src.media_generation.layout.team.teams_layout import TeamsLayout
from src.media_generation.layout.text_layout import TextLayout

FBRT = {
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
            "fbrt": ImageLayout(
                "fbrt",
                path="assets/logos/FBRT/unbordered.png",
                width=175,
                left=1740,
                top=0,
            ),
            "fif": ImageLayout(
                "fif",
                path="assets/logos/fif/wide_black.png",
                width=175,
                left=0,
                top=1010,
            ),
            "date": TextLayout(
                name="date",
                content="{race.day} {month_fr}",
                width=1200,
                height=35,
                bottom=16,
                right=10,
                font_name='regular',
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
                font_name='regular',
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
                font_name='regular',
                bg=(10, 8, 32),
                fg=(255, 255, 255, 255)
            ),
            "circuit_flag": ImageLayout(
                name="flag_layout",
                path="assets/circuits/flags/{circuit.id}.png",
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
                children={
                    'team': TeamLineupLayout(
                        name="team",
                        width=680,
                        height=200,
                        children={
                            'logo': ImageLayout(
                                name="logo",
                                width=220,
                                height=90,
                                top=30
                            ),
                            'pilot_1': PilotLineupLayout(
                                name="pilot_1",
                                left=0,
                                top=0,
                                width=368,
                                height=200,
                                children={
                                    'face': PilotFaceLayout(
                                        name="face",
                                        width=368,
                                        height=143,
                                        top=5,
                                    ),
                                    'box': PilotBoxLayout(
                                        name="box",
                                        width=368,
                                        height=62,
                                        left=0,
                                        top=138,
                                        children={
                                            'name': TextLayout(
                                                content="{pilot_name}",
                                                name="name",
                                                height=28,
                                                width=250
                                            )
                                        }
                                    ),
                                }
                            ),
                            'pilot_2': PilotLineupLayout(
                                name="pilot_2",
                                left=312,
                                top=0,
                                width=368,
                                height=200,
                                children={
                                    'face': PilotFaceLayout(
                                        name="face",
                                        width=368,
                                        height=143,
                                        top=5,
                                    ),
                                    'box': PilotBoxLayout(
                                        name="box",
                                        width=368,
                                        height=62,
                                        left=0,
                                        top=138,
                                        children={
                                            'name': TextLayout(
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
                    )
                },
                positions=[
                    {'left': 295, 'top': 2},
                    {'left': 938, 'top': 2},
                    {'left': 150, 'top': 204},
                    {'left': 1095, 'top': 204},
                    {'left': 32, 'top': 406},
                    {'left': 1203, 'top': 406},
                    {'left': 150, 'top': 608},
                    {'left': 1098, 'top': 608},
                    {'left': 295, 'top': 810},
                    {'left': 938, 'top': 810},
                ]
            )
        },
        polygons=[
            Polygon(
                edges=(
                    (0, 263),
                    (0, 510),
                    (445, 64),
                    (200, 64),
                ),
                color=230
            ),
            Polygon(
                edges=(
                    (424, 523),
                    (1158, 523),
                    (605, 1080),
                    (0, 1080),
                    (0, 950),
                ),
                color=230
            ),
            Polygon(
                edges=(
                    (738, 523),
                    (1468, 523),
                    (1920, 74),
                    (1920, 0),
                    (1256, 0),
                ),
                color=230
            ),
            Polygon(
                edges=(
                    (1352, 1080),
                    (1920, 1080),
                    (1920, 523),
                    (1908, 523)
                ),
                color=230
            )
        ]
    ),
    "season_teams": PolygonsLayout(
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
            "fbrt": ImageLayout(
                "fbrt",
                path="assets/logos/FBRT/unbordered.png",
                width=175,
                left=1740,
                top=0,
            ),
            "fif": ImageLayout(
                "fif",
                path="assets/logos/fif/wide_black.png",
                width=175,
                left=0,
                top=1010,
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
            "saison_text": TextLayout(
                name="text",
                content="SAISON {season}",
                width=440,
                height=150,
                fg=(200, 0, 0),
                top=505
            ),
            "teams": TeamsLayout(
                name="teams",
                width=1920,
                height=1080,
                children={
                    'team': TeamLineupLayout(
                        name="team",
                        width=680,
                        height=200,
                        children={
                            'logo': ImageLayout(
                                name="logo",
                                width=220,
                                height=90,
                                top=30
                            ),
                            'pilot_1': PilotLineupLayout(
                                name="pilot_1",
                                left=0,
                                top=0,
                                width=368,
                                height=200,
                                children={
                                    'face': PilotFaceLayout(
                                        name="face",
                                        width=368,
                                        height=143,
                                        top=5,
                                    ),
                                    'box': PilotBoxLayout(
                                        name="box",
                                        width=368,
                                        height=62,
                                        left=0,
                                        top=138,
                                        children={
                                            'name': TextLayout(
                                                content="{pilot_name}",
                                                name="name",
                                                height=28,
                                                width=250
                                            )
                                        }
                                    ),
                                }
                            ),
                            'pilot_2': PilotLineupLayout(
                                name="pilot_2",
                                left=312,
                                top=0,
                                width=368,
                                height=200,
                                children={
                                    'face': PilotFaceLayout(
                                        name="face",
                                        width=368,
                                        height=143,
                                        top=5,
                                    ),
                                    'box': PilotBoxLayout(
                                        name="box",
                                        width=368,
                                        height=62,
                                        left=0,
                                        top=138,
                                        children={
                                            'name': TextLayout(
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
                    )
                },
                positions=[
                    {'left': 295, 'top': 2},
                    {'left': 938, 'top': 2},
                    {'left': 150, 'top': 204},
                    {'left': 1095, 'top': 204},
                    {'left': 32, 'top': 406},
                    {'left': 1203, 'top': 406},
                    {'left': 150, 'top': 608},
                    {'left': 1098, 'top': 608},
                    {'left': 295, 'top': 810},
                    {'left': 938, 'top': 810},
                ]
            )
        },
        polygons=[
            Polygon(
                edges=(
                    (0, 263),
                    (0, 510),
                    (445, 64),
                    (200, 64),
                ),
                color=230
            ),
            Polygon(
                edges=(
                    (424, 523),
                    (1158, 523),
                    (605, 1080),
                    (0, 1080),
                    (0, 950),
                ),
                color=230
            ),
            Polygon(
                edges=(
                    (738, 523),
                    (1468, 523),
                    (1920, 74),
                    (1920, 0),
                    (1256, 0),
                ),
                color=230
            ),
            Polygon(
                edges=(
                    (1352, 1080),
                    (1920, 1080),
                    (1920, 523),
                    (1908, 523)
                ),
                color=230
            )
        ]
    )
}
