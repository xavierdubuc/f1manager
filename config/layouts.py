from src.media_generation.layout import *
from src.media_generation.layout.pilot.pilot_photo_layout import WHOLE

FBRT = {
    # just _values
    "numbers": ImageLayout(
        name="bg",
        path="assets/backgrounds/FBRT/numbers.png",
        width=1920,
        height=1080,
        bg=255,
        children={
            "numbers": PilotNumbersLayout(
                name="numbers",
                width=1880,  # 1920 - 2 * 20
                height=1052,  # 1080 - 2 * 14
                locked_numbers={
                    1: "-",
                    2: "Sargeant",
                    3: "Ricciardo",
                    4: "Norris",
                    10: "Gasly",
                    11: "Perez",
                    14: "Alonso",
                    16: "Leclerc",
                    17: "/",
                    18: "Stroll",
                    20: "Magnussen",
                    22: "Tsunoda",
                    23: "Albon",
                    24: "Zhou",
                    27: "Hulkenberg",
                    31: "Ocon",
                    33: "Verstappen",
                    44: "Hamilton",
                    55: "Sainz",
                    63: "Russell",
                    77: "Bottas",
                    81: "Piastri"
                },
                templates={
                    "pilot_number": LayoutTemplate(
                        layout=PilotNumberLayout(
                            name="pilot_number",
                            width=360,  # 360 * 5 + (4*20) = 1880
                            height=45,  # 45 * 20 = 900 -> + (19 * 8) = 1052
                            children={
                                "number": TextLayout(
                                    name="number",
                                    content="{number}",
                                    width=45,
                                    height=35,
                                    left=0,
                                    stroke_width=18,
                                    text_top=-10,
                                    text_left=15,
                                ),
                                "card": PilotCardLayout(
                                    name="card",
                                    width=300,
                                    height=45,
                                    left=60,
                                    children={
                                        "logo_container": Layout(
                                            name="logo_container",
                                            left=0,
                                            width=65,
                                            height=45,
                                            children={
                                                "logo": ImageLayout(
                                                    name="logo",
                                                    path="{team_logo_path}",
                                                    width=65,
                                                    height=45
                                                ),
                                            }
                                        ),
                                        "pilot_name": TextLayout(
                                            name="pilot_name",
                                            content="{pilot_name}",
                                            width=205,
                                            height=22,
                                            left=80,
                                            top=10,
                                            underscore_top=12,
                                            long_top=15,
                                        ),
                                    }
                                )
                            }
                        ),
                        instances=[
                            {"left": 0, "top": 0},  # 1
                            {"left": 0, "top": 53},  # 2
                            {"left": 0, "top": 106},  # 3
                            {"left": 0, "top": 159},  # 4
                            {"left": 0, "top": 212},  # 5
                            {"left": 0, "top": 265},  # 6
                            {"left": 0, "top": 318},  # 7
                            {"left": 0, "top": 371},  # 8
                            {"left": 0, "top": 424},  # 9
                            {"left": 0, "top": 477},  # 10
                            {"left": 0, "top": 530},  # 11
                            {"left": 0, "top": 583},  # 12
                            {"left": 0, "top": 636},  # 13
                            {"left": 0, "top": 689},  # 14
                            {"left": 0, "top": 742},  # 15
                            {"left": 0, "top": 795},  # 16
                            {"left": 0, "top": 848},  # 17
                            {"left": 0, "top": 901},  # 18
                            {"left": 0, "top": 954},  # 19
                            {"left": 0, "top": 1007},  # 20
                            {"left": 380, "top": 0},  # 21
                            {"left": 380, "top": 53},  # 22
                            {"left": 380, "top": 106},  # 23
                            {"left": 380, "top": 159},  # 24
                            {"left": 380, "top": 212},  # 25
                            {"left": 380, "top": 265},  # 26
                            {"left": 380, "top": 318},  # 27
                            {"left": 380, "top": 371},  # 28
                            {"left": 380, "top": 424},  # 29
                            {"left": 380, "top": 477},  # 30
                            {"left": 380, "top": 530},  # 31
                            {"left": 380, "top": 583},  # 32
                            {"left": 380, "top": 636},  # 33
                            {"left": 380, "top": 689},  # 34
                            {"left": 380, "top": 742},  # 35
                            {"left": 380, "top": 795},  # 36
                            {"left": 380, "top": 848},  # 37
                            {"left": 380, "top": 901},  # 38
                            {"left": 380, "top": 954},  # 39
                            {"left": 380, "top": 1007},  # 40
                            {"left": 760, "top": 0},  # 41
                            {"left": 760, "top": 53},  # 42
                            {"left": 760, "top": 106},  # 43
                            {"left": 760, "top": 159},  # 44
                            {"left": 760, "top": 212},  # 45
                            {"left": 760, "top": 265},  # 46
                            {"left": 760, "top": 318},  # 47
                            {"left": 760, "top": 371},  # 48
                            {"left": 760, "top": 424},  # 49
                            {"left": 760, "top": 477},  # 50
                            {"left": 760, "top": 530},  # 51
                            {"left": 760, "top": 583},  # 52
                            {"left": 760, "top": 636},  # 53
                            {"left": 760, "top": 689},  # 54
                            {"left": 760, "top": 742},  # 55
                            {"left": 760, "top": 795},  # 56
                            {"left": 760, "top": 848},  # 57
                            {"left": 760, "top": 901},  # 58
                            {"left": 760, "top": 954},  # 59
                            {"left": 760, "top": 1007},  # 60
                            {"left": 1140, "top": 0},  # 61
                            {"left": 1140, "top": 53},  # 62
                            {"left": 1140, "top": 106},  # 63
                            {"left": 1140, "top": 159},  # 64
                            {"left": 1140, "top": 212},  # 65
                            {"left": 1140, "top": 265},  # 66
                            {"left": 1140, "top": 318},  # 67
                            {"left": 1140, "top": 371},  # 68
                            {"left": 1140, "top": 424},  # 69
                            {"left": 1140, "top": 477},  # 70
                            {"left": 1140, "top": 530},  # 71
                            {"left": 1140, "top": 583},  # 72
                            {"left": 1140, "top": 636},  # 73
                            {"left": 1140, "top": 689},  # 74
                            {"left": 1140, "top": 742},  # 75
                            {"left": 1140, "top": 795},  # 76
                            {"left": 1140, "top": 848},  # 77
                            {"left": 1140, "top": 901},  # 78
                            {"left": 1140, "top": 954},  # 79
                            {"left": 1140, "top": 1007},  # 80
                            {"left": 1520, "top": 0},  # 81
                            {"left": 1520, "top": 53},  # 82
                            {"left": 1520, "top": 106},  # 83
                            {"left": 1520, "top": 159},  # 84
                            {"left": 1520, "top": 212},  # 85
                            {"left": 1520, "top": 265},  # 86
                            {"left": 1520, "top": 318},  # 87
                            {"left": 1520, "top": 371},  # 88
                            {"left": 1520, "top": 424},  # 89
                            {"left": 1520, "top": 477},  # 90
                            {"left": 1520, "top": 530},  # 91
                            {"left": 1520, "top": 583},  # 92
                            {"left": 1520, "top": 636},  # 93
                            {"left": 1520, "top": 689},  # 94
                            {"left": 1520, "top": 742},  # 95
                            {"left": 1520, "top": 795},  # 96
                            {"left": 1520, "top": 848},  # 97
                            {"left": 1520, "top": 901},  # 98
                            {"left": 1520, "top": 954},  # 99
                        ]
                    )
                }
            )
        }
    ),
    "season_pilots": PolygonsLayout(
        name="season_pilots",
        width=1080,
        height=1080,
        bg=255,
        polygons=[
            Polygon(
                edges=(
                    (0, 263),
                    (0, 510),
                    (505, 0),
                    (260, 0),
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
        ],
        children={
            "fbrt": ImageLayout(
                "fbrt",
                path="assets/logos/FBRT/unbordered.png",
                width=175,
                top=20,
                left=40,
            ),
            "saison_text": TextLayout(
                name="text",
                content="SAISON {season}",
                width=440,
                height=60,
                fg=(0, 0, 0),
                top=40
            ),
            "line_up_text": IdentifierDependantTextLayout(
                name="pilots_text",
                top=110,
                width=380,
                height=60,
                content={
                    "default": "PILOTES",
                    "reservists": "RÉSERVISTES",
                    "reservist": "RÉSERVISTES"
                },
                font_name="black",
                fg=(0, 0, 0),
            ),
            "fif": ImageLayout(
                "fif",
                path="assets/logos/fif/wide_black.png",
                width=175,
                right=40,
                top=120,
            ),
            "pilots": SeasonPilotsLayout(
                name="pilots",
                width=1000,
                height=860,
                top=200,
                templates={
                    "pilot_number": LayoutTemplate(
                        layout=PilotNumberLayout(
                            name="pilot_number",
                            width=480,
                            height=75,
                            children={
                                "number": TextLayout(
                                    name="number",
                                    content="{number}",
                                    width=90,
                                    height=60,
                                    left=0,
                                    stroke_width=18,
                                    text_top=-10,
                                    text_left=15,
                                    center=True
                                ),
                                "card": PilotCardLayout(
                                    name="card",
                                    width=380,
                                    height=75,
                                    left=100,
                                    children={
                                        "logo_container": Layout(
                                            name="logo_container",
                                            left=0,
                                            width=120,
                                            height=75,
                                            children={
                                                "logo": ImageLayout(
                                                    name="logo",
                                                    path="{team_logo_path}",
                                                    height=80
                                                ),
                                            }
                                        ),
                                        "pilot_row": ImageLayout(
                                            name="pilot_row",
                                            path="assets/backgrounds/FBRT/ranking_row_bg.png",
                                            width=280,
                                            height=75,
                                            left=100,
                                            top=0,
                                            keep_ratio=False,
                                            children={
                                                "pilot_name": TextLayout(
                                                    name="pilot_name",
                                                    content="{pilot_name}",
                                                    width=215,
                                                    height=30,
                                                    left=60,
                                                ),
                                            }
                                        ),
                                        "face": PilotPhotoLayout(
                                            name="face",
                                            width=820,
                                            height=115,
                                            left=45,
                                            top=-15
                                        ),
                                    }
                                )
                            }
                        ),
                        instances=[
                            {"left": 0, "top": 0},
                            {"left": 520, "top": 20},
                            {"left": 0, "top": 85},
                            {"left": 520, "top": 105},
                            {"left": 0, "top": 170},
                            {"left": 520, "top": 190},
                            {"left": 0, "top": 255},
                            {"left": 520, "top": 275},
                            {"left": 0, "top": 340},
                            {"left": 520, "top": 360},
                            {"left": 0, "top": 425},
                            {"left": 520, "top": 445},
                            {"left": 0, "top": 510},
                            {"left": 520, "top": 530},
                            {"left": 0, "top": 595},
                            {"left": 520, "top": 615},
                            {"left": 0, "top": 680},
                            {"left": 520, "top": 700},
                            {"left": 0, "top": 765},
                            {"left": 520, "top": 785},
                        ]
                    )
                },
            )
        },
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
                }
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
    # RaceReader
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
    "results": ImageLayout(
        name="results",
        width=1920,
        height=1200,
        path="assets/backgrounds/FBRT/results.png",
        gaussian_blur=5,
        children={
            "bg_overlay": Layout(
                name="bg_overlay",
                width=1920,
                height=1200,
                bg=(0, 0, 0, 100)
            ),
            "top3": RaceRankingLayout(
                name="top3",
                width=900,
                height=615,
                left=30,
                top=30,
                templates={
                    "full_size_pilots": LayoutTemplate(
                        FullSizeRankingRowLayout(
                            name="full_size_pilots",
                            width=280,
                            bottom=0,
                            default_bg=(241, 241, 241, 255),
                            driver_of_the_day_bg=(246, 212, 136, 255),
                            fastest_lap_bg=(191, 140, 210, 255),
                            children={
                                "bg": RoundedLayout(
                                    name="bg",
                                    width=280,
                                    children={
                                        "position": TextLayout(
                                            name="position",
                                            width=122,
                                            height=142,
                                            fg=255,
                                            left=20,
                                            top=10,
                                            content="{race_ranking_row.position}"
                                        ),
                                        "face": PilotPhotoLayout(
                                            photo_type=WHOLE,
                                            name="face",
                                            width=500,
                                            height=730,
                                            left=45,
                                            top=-15
                                        ),
                                        "pilot_name": TextLayout(
                                            name="pilot_name",
                                            fg="{race_ranking_row.pilot.team.standing_fg}",
                                            bg="{race_ranking_row.pilot.team.standing_bg}",
                                            content="{pilot_name}",
                                            font_name="bold",
                                            height=55,
                                            text_width=200,
                                            text_height=35,
                                            width=280,
                                            left=0,
                                            bottom=55,
                                            center=True,
                                        ),
                                        "result_row_bg": DottedImageLayout(
                                            name="result_row_bg",
                                            height=55,
                                            width=225,
                                            left=0,
                                            bottom=0,
                                            bg="{bg_color}",
                                            round_bottom_left=True,
                                            left_part_width=0,
                                            children={
                                                'delta': TextLayout(
                                                    name="delta",
                                                    font_name="regular",
                                                    content="{race_ranking_row.delta}",
                                                    top=5,
                                                    fg=(0, 0, 0, 255),
                                                    bg="{bg_color}",
                                                    height=18,
                                                    width=225,
                                                ),
                                                'tyres': TyresLayout(
                                                    name="tyres",
                                                    height=20,
                                                    tyre_spacing=1,
                                                    width=225,
                                                    bottom=5
                                                )
                                            },
                                        ),
                                    },
                                ),
                                'points': RoundedLayout(
                                    name="points",
                                    height=55,
                                    width=55,
                                    bg=0,
                                    radius=20,
                                    right=0,
                                    bottom=0,
                                    round_bottom_left=False,
                                    round_top_left=False,
                                    round_top_right=False,
                                    round_bottom_right=True,
                                    children={
                                        "points_txt": TextLayout(
                                            content="+{race_ranking_row.points}",
                                            name="points_txt",
                                            height=40,
                                            width=40,
                                            fg=255,
                                            bg=0,
                                        ),
                                    }
                                ),
                            }
                        ),
                        instances=[
                            {"left": 310, "height": 575},  # 1
                            {"left": 0, "height": 495},  # 2
                            {"left": 620, "height": 495},  # 3
                        ]
                    )
                }
            ),
            "top20": RaceRankingLayout(
                name="top20",
                width=1920,
                height=1200,
                initial_position=4,
                children={
                    # FIXME put here 4th, 10th, 11th & 20th to handle differencies
                },
                templates={
                    "ranking_result_row": LayoutTemplate(
                        SimpleRankingRowLayout(
                            name="ranking_result_row",
                            width=900,
                            height=72,
                            even_bg=(241, 241, 241, 255),
                            odd_bg=(227, 227, 227, 255),
                            driver_of_the_day_bg=(246, 212, 136, 255),
                            fastest_lap_bg=(191, 140, 210, 255),
                            children={
                                # TODO Handle NT color (text + bg)
                                "result_row_bg": DottedImageLayout(
                                    name="result_row_bg",
                                    height=72,
                                    width=900,
                                    left=0,
                                    bottom=0,
                                    bg="{bg_color}",
                                    round_top_left="race_ranking_row.position in (4,11)",
                                    round_top_right="race_ranking_row.position in (4,11)",
                                    round_bottom_left="race_ranking_row.position in (10, 20)",
                                    round_bottom_right="race_ranking_row.position in (10, 20)",
                                    crosses_positions="[(74, 71), (430, 71)] if race_ranking_row.position in (4, 11) else ([(74, -1), (430, -1)] if race_ranking_row.position in (10, 20) else [(74, -1), (74, 71), (430, -1), (430, 71)])",
                                    crosses_color=(80, 80, 80),
                                    crosses_thickness=2,
                                    crosses_size=5,
                                    dots_color=(200, 200, 200, 255),
                                    dots_size=2,
                                    left_part_width=75,
                                    children={
                                        "position": TextLayout(
                                            name="position",
                                            font_name="bold",
                                            width=75,
                                            height=26,
                                            fg=0,
                                            left=0,
                                            center=True,
                                            content="{race_ranking_row.position}"
                                        ),
                                        "pilot_name": TextLayout(
                                            font_name="bold",
                                            name="pilot_name",
                                            width=290,
                                            height=20,
                                            content="{pilot_name}",
                                            left=100
                                        ),
                                        'delta': TextLayout(
                                            name="delta",
                                            font_name="regular",
                                            content="{race_ranking_row.delta}",
                                            top=10,
                                            fg=(0, 0, 0, 255),
                                            bg="{bg_color}",
                                            height=18,
                                            width=225,
                                            right=85,
                                        ),
                                        'tyres': TyresLayout(
                                            name="tyres",
                                            height=20,
                                            tyre_spacing=-3,
                                            tyre_size=18,
                                            width=225,
                                            bottom=8,
                                            right=85
                                        ),
                                        'points': RoundedLayout(
                                            name="points",
                                            height=72,
                                            width=72,
                                            bg=0,
                                            radius=20,
                                            right=0,
                                            bottom=0,
                                            round_top_left=False,
                                            round_top_right="race_ranking_row.position in (4,11)",
                                            round_bottom_left=False,
                                            round_bottom_right="race_ranking_row.position in (10, 20)",
                                            children={
                                                "points_txt": TextLayout(
                                                    content="+{race_ranking_row.points}",
                                                    name="points_txt",
                                                    height=30,
                                                    width=38,
                                                    fg=255,
                                                    bg=0,
                                                ),
                                            }
                                        ),
                                    },
                                ),
                            }
                        ),
                        instances=[
                            {"left": 30, "top": 660},  # 4
                            {"left": 30, "top": 732},  # 5
                            {"left": 30, "top": 804},  # 6
                            {"left": 30, "top": 876},  # 7
                            {"left": 30, "top": 948},  # 8
                            {"left": 30, "top": 1020},  # 9
                            {"left": 30, "top": 1092},  # 10
                            {"left": 990, "top": 124, 'height': 72},  # 11
                            {"left": 990, "top": 196, 'height': 72},  # 12
                            {"left": 990, "top": 268, 'height': 72},  # 13
                            {"left": 990, "top": 340, 'height': 72},  # 14
                            {"left": 990, "top": 412, 'height': 72},  # 14
                            {"left": 990, "top": 484, 'height': 72},  # 14
                            {"left": 990, "top": 556, 'height': 72},  # 14
                            {"left": 990, "top": 628, 'height': 72},  # 14
                            {"left": 990, "top": 700, 'height': 72},  # 14
                            {"left": 990, "top": 772, 'height': 72},  # 14
                        ]
                    )
                }
            ),
            "logos": Layout(
                name="logos",
                width=905,
                height=280,
                right=20,
                bottom=20,
                bg=(25, 25, 25, 150),
                children={
                    "fbrt": ImageLayout(
                        name="fbrt",
                        path="assets/logos/FBRT/unbordered.png",
                        height=260,
                        left=40,
                        top=15,
                    ),
                    "fif": ImageLayout(
                        name="fif",
                        path="assets/logos/fif/wide_white.png",
                        height=140,
                        right=40,
                        top=20,
                    ),
                    "f1": ImageLayout(
                        name="f1",
                        path="assets/logos/f1/24_white.png",
                        height=140,
                        width=450,
                        right=40,
                        bottom=30,
                    ),
                }
            )
        }
    ),
    "time_trial": PolygonsLayout(
        name="time_trial",
        width=1200,
        height=1080,
        bg=20,
        children={
            "fbrt": ImageLayout(
                name="fbrt",
                path="assets/logos/FBRT/unbordered.png",
                width=1200,
                height=1080,
            ),
            "bg": Layout(
                name="bg",
                width=1140,
                height=1040,
                left=30,
                top=20,
                bg=(20, 20, 20, 80),
                children={
                    "headers": Layout(
                        name="headers",
                        width=1200,
                        height=80,
                        left=0,
                        top=0,
                        children={
                            "circuit_flag": ImageLayout(
                                name="flag_layout",
                                path="assets/circuits/flags/{circuit.id}.png",
                                width=60,
                                height=80,
                                left=25,
                                top=25
                            ),
                            "pilot_header": TextLayout(
                                name="pilot_header",
                                content="PILOTE",
                                font_name="bold",
                                fg=255,
                                width=200,
                                left=120,
                                height=40
                            ),
                            "s1_header": TextLayout(
                                name="s1_header",
                                content="S1",
                                font_name="bold",
                                fg=255,
                                width=200,
                                left=500,
                                height=40
                            ),
                            "s2_header": TextLayout(
                                name="s2_header",
                                content="S2",
                                font_name="bold",
                                fg=255,
                                width=200,
                                left=650,
                                height=40
                            ),
                            "s3_header": TextLayout(
                                name="s3_header",
                                content="S3",
                                font_name="bold",
                                fg=255,
                                width=200,
                                left=800,
                                height=40
                            ),
                        }
                    ),
                    "body": TimingRowsLayout(
                        name="body",
                        width=1140,
                        height=900,
                        top=100,
                        left=0,
                        fastest_fg=(142, 135, 188, 255),
                        templates={
                            'row': LayoutTemplate(
                                layout=Layout(
                                    name="time_trial_row",
                                    width=1220,
                                    height=45,
                                    left=0,
                                    bg="{bg_color}",
                                    children={
                                        "position_wrapper": Layout(
                                            name="position_wrapper",
                                            width=50,
                                            left=20,
                                            children={
                                                "position": TextLayout(
                                                    name="position",
                                                    width=38,
                                                    font_name="regular",
                                                    fg=255,
                                                    height=24,
                                                    right=0,
                                                    content="{row[0]}"
                                                ),
                                            }
                                        ),
                                        "pilot": TextLayout(
                                            name="pilot",
                                            content="{row[1]}",
                                            height=24,
                                            width=250,
                                            fg=255,
                                            left=120,
                                            font_name="regular",
                                        ),
                                        "s1": TextLayout(
                                            name="s1",
                                            content="{row[2]}",
                                            height=24,
                                            width=90,
                                            fg="{s1_fg}",
                                            left=500,
                                            font_name="regular",
                                        ),
                                        "s2": TextLayout(
                                            name="s2",
                                            content="{row[3]}",
                                            height=24,
                                            width=90,
                                            fg="{s2_fg}",
                                            left=650,
                                            font_name="regular",
                                        ),
                                        "s3": TextLayout(
                                            name="s3",
                                            content="{row[4]}",
                                            height=24,
                                            width=90,
                                            fg="{s3_fg}",
                                            left=800,
                                            font_name="regular",
                                        ),
                                        "lap": TextLayout(
                                            name="lap",
                                            content="{row[5]}",
                                            height=24,
                                            width=250,
                                            fg="{lap_fg}",
                                            left=975,
                                            font_name="regular",
                                        ),
                                    }
                                ),
                                instances=[
                                    {"top": 0},
                                    {"top": 45},
                                    {"top": 90},
                                    {"top": 135},
                                    {"top": 180},
                                    {"top": 225},
                                    {"top": 270},
                                    {"top": 315},
                                    {"top": 360},
                                    {"top": 405},
                                    {"top": 450},
                                    {"top": 495},
                                    {"top": 540},
                                    {"top": 585},
                                    {"top": 630},
                                    {"top": 675},
                                    {"top": 720},
                                    {"top": 765},
                                    {"top": 810},
                                    {"top": 855},
                                ])
                        }
                    )
                }
            ),
        },
        polygons=[
            Polygon(
                edges=(
                    (0, 263),
                    (0, 510),
                    (505, 0),
                    (260, 0),
                ),
                color=60
            ),
            Polygon(
                edges=(
                    (424, 523),
                    (1158, 523),
                    (605, 1080),
                    (0, 1080),
                    (0, 950),
                ),
                color=60
            ),
            Polygon(
                edges=(
                    (738, 523),
                    (1468, 523),
                    (1920, 74),
                    (1920, 0),
                    (1256, 0),
                ),
                color=60
            ),
            Polygon(
                edges=(
                    (1352, 1080),
                    (1920, 1080),
                    (1920, 523),
                    (1908, 523)
                ),
                color=60
            )
        ],
    )
}

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
}

del FBRT['results']  # FIXME quand le result est réglé
