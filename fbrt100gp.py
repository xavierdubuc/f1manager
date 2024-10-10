from config.layouts import DEFAULT_POLYGONS
from src.media_generation.layout.image_layout import ImageLayout
from src.media_generation.layout.layout import Layout
from src.media_generation.layout.polygons_layout import PolygonsLayout
from src.media_generation.layout.rounded_layout import RoundedLayout
from src.media_generation.layout.text_layout import TextLayout
from src.logging import setup as setup_logging

setup_logging("debug")


GP_ewocflo_parts = {
    "illu": ImageLayout(
        name="illu",
        path="assets/100gp/GP ewocflo.png",
        bottom=0
    ),
    "date": TextLayout(
        name="date",
        height=15,
        right=10,
        top=70,
        fg=(255, 255, 255),
        content="13 Février 2023",
        font_name="regular",
    ),
    "f1_logo": ImageLayout(
        name="f1_logo",
        path="assets/logos/f1/22_white.png",
        height=30,
        width=200,
        right=10,
        bottom=10,
    ),
    "gp_round": Layout(
        name="gp_round",
        top=2,
        width=135,
        height=50,
        children={
            "gp": TextLayout(
                name="round",
                height=50,
                width=50,
                left=0,
                content="GP",
                font_name="BebasNeue",
            ),
            "round": TextLayout(
                name="round",
                left=60,
                height=50,
                width=75,
                content="#42",
                fg=(200, 0, 0),
                font_name="BebasNeue",
            ),
        }
    ),
    "season_round": TextLayout(
        name="season_round",
        top=52,
        height=28,
        content="Saison 4 - Course 8",
        font_name="BebasNeue",
    ),
    "track_container": Layout(
        name="track_container",
        bg=(0, 0, 0),
        width=610,
        height=50,
        top=90,
        children={
            "track": TextLayout(
                name="track",
                height=35,
                fg=(255, 255, 255),
                content="GRAND PRIX DU MEXIQUE",
                font_name="BebasNeue",
            ),
        }
    ),
    'description_container': Layout(
        name="description_container",
        bg=(255, 255, 255, 100),
        width=610,
        height=50,
        top=140,
        children={
            "description": TextLayout(
                height=40,
                name="description",
                # bg=(255,255,255,100),
                top=2,
                content="Le départ légendaire d'ewocflo ",
                font_name="BebasNeue",
            ),
        }
    ),
}

GP_majforti_parts = {
    "illu": ImageLayout(
        name="illu",
        path="assets/100gp/GP majforti.png",
        bottom=0
    ),
    "date": TextLayout(
        name="date",
        height=14,
        right=10,
        top=70,
        fg=(255, 255, 255),
        bg=0,
        content="20 Novembre 2023",
        font_name="regular",
    ),
    "f1_logo": ImageLayout(
        name="f1_logo",
        path="assets/logos/f1/23_white.png",
        height=30,
        width=200,
        right=10,
        bottom=10,
    ),
    "gp_round": Layout(
        name="gp_round",
        top=2,
        width=135,
        height=50,
        children={
            "gp": TextLayout(
                name="round",
                height=50,
                width=50,
                left=0,
                content="GP",
                font_name="BebasNeue",
            ),
            "round": TextLayout(
                name="round",
                left=60,
                height=50,
                width=75,
                content="#69",
                fg=(0, 0, 255),
                font_name="BebasNeue",
            ),
        }
    ),
    "season_round": TextLayout(
        name="season_round",
        top=52,
        height=28,
        content="Saison 6 - Course 12",
        font_name="BebasNeue",
    ),
    "track_container": Layout(
        name="track_container",
        bg=(0, 0, 0),
        width=610,
        height=50,
        top=90,
        children={
            "track": TextLayout(
                name="track",
                height=35,
                fg=(255, 255, 255),
                content="GRAND PRIX DU CANADA",
                font_name="BebasNeue",
            ),
        }
    ),
    'description_container': Layout(
        name="description_container",
        bg=(255, 255, 255, 100),
        width=610,
        height=50,
        top=140,
        children={
            "description": TextLayout(
                height=40,
                name="description",
                # bg=(255,255,255,100),
                top=2,
                content="Majforti DNF et offre le titre à Kayzor",
                font_name="BebasNeue",
            ),
        }
    ),
}

GP_remontada_parts = {
    "illu": ImageLayout(
        name="illu",
        path="assets/100gp/GP remontada.png",
        bottom=0
    ),
    "date": TextLayout(
        name="date",
        height=15,
        right=10,
        top=70,
        fg=(255, 255, 255),
        content="16 Février 2024",
        font_name="regular",
    ),
    "f1_logo": ImageLayout(
        name="f1_logo",
        path="assets/logos/f1/24_white.png",
        height=30,
        width=200,
        right=10,
        bottom=10,
    ),
    "gp_round": Layout(
        name="gp_round",
        top=2,
        width=135,
        height=50,
        children={
            "gp": TextLayout(
                name="round",
                height=50,
                width=50,
                left=0,
                content="GP",
                font_name="BebasNeue",
            ),
            "round": TextLayout(
                name="round",
                left=60,
                height=50,
                width=75,
                content="#97",
                fg=(0, 0, 200),
                font_name="BebasNeue",
            ),
        }
    ),
    "season_round": TextLayout(
        name="season_round",
        top=52,
        height=28,
        content="Saison 9 - Course 3",
        font_name="BebasNeue",
    ),
    "track_container": Layout(
        name="track_container",
        bg=(0, 0, 0),
        width=610,
        height=50,
        top=90,
        children={
            "track": TextLayout(
                name="track",
                height=35,
                fg=(255, 255, 255),
                content="GRAND PRIX DES PAYS-BAS",
                font_name="BebasNeue",
            ),
        }
    ),
    'description_container': Layout(
        name="description_container",
        bg=(255, 255, 255, 100),
        width=610,
        height=50,
        top=140,
        children={
            "description": TextLayout(
                height=40,
                name="description",
                # bg=(255,255,255,100),
                top=2,
                content="Cid: + 1 tour à vainqueur",
                font_name="BebasNeue",
            ),
        }
    ),
}

GP_season1_parts = {
    "illu": ImageLayout(
        name="illu",
        path="assets/100gp/GP last season 1.png",
        bottom=0
    ),
    "date": TextLayout(
        name="date",
        height=15,
        right=10,
        top=70,
        fg=255,
        bg=0,
        content="21 Mars 2022",
        font_name="regular",
    ),
    "f1_logo": ImageLayout(
        name="f1_logo",
        path="assets/logos/f1/21_white.png",
        height=30,
        width=200,
        right=10,
        bottom=10,
    ),
    "gp_round": Layout(
        name="gp_round",
        top=2,
        width=135,
        height=50,
        children={
            "gp": TextLayout(
                name="round",
                height=50,
                width=50,
                left=0,
                content="GP",
                font_name="BebasNeue",
            ),
            "round": TextLayout(
                name="round",
                left=60,
                height=50,
                width=75,
                content="#10",
                fg=255,
                font_name="BebasNeue",
            ),
        }
    ),
    "season_round": TextLayout(
        name="season_round",
        top=52,
        height=28,
        content="Saison 1 - Course 10",
        font_name="BebasNeue",
    ),
    "track_container": Layout(
        name="track_container",
        bg=(0, 0, 0),
        width=610,
        height=50,
        top=90,
        children={
            "track": TextLayout(
                name="track",
                height=35,
                fg=(255, 255, 255),
                content="GRAND PRIX D'ABU DHABI'",
                font_name="BebasNeue",
            ),
        }
    ),
    'description_container': Layout(
        name="description_container",
        bg=(255, 255, 255, 100),
        width=610,
        height=50,
        top=140,
        children={
            "description": TextLayout(
                height=40,
                name="description",
                # bg=(255,255,255,100),
                top=2,
                content="MCLAREN PERD LE TITRE PAR DNF",
                font_name="BebasNeue",
            ),
        }
    ),
}

texts = [
    "La FBRT a RDV à ABU DHABI ce soir avec",
    "un format inédit puisque c'est le format",
    "sprint nouvelle edition qui se présente à eux !",
    "",
    "2 sessions de qualifs , 2 courses !",
    "De quoi passer une très bonne soirée et peut-être",
    "mettre un peu de pression aux favoris qui",
    "ne devront pas se louper !",
]

layout = Layout(
    name="FBRT 100 GP",
    width=1920,
    height=1080,
    bg=(25, 34, 47),
    children={
        "container": PolygonsLayout(
            name="container",
            polygons=DEFAULT_POLYGONS,
            width=1860,
            height=1020,
            left=30,
            top=30,
            bg=255,
            children={
                'GP 1': Layout(
                    name="GP 1",
                    width=590,
                    height=490,
                    top=5,
                    left=10,
                    children=GP_season1_parts,
                ),
                'GP 2': Layout(
                    name="GP 2",
                    width=590,
                    height=490,
                    top=5,
                    left=1240,
                    children=GP_ewocflo_parts,
                ),
                'GP 3': Layout(
                    name="GP 3",
                    width=590,
                    height=490,
                    top=520,
                    left=10,
                    children=GP_majforti_parts,
                ),
                'GP 4': Layout(
                    name="GP 4",
                    width=590,
                    height=490,
                    top=520,
                    left=1240,
                    children=GP_remontada_parts,
                ),
                'GP 100': Layout(
                    name="GP 100",
                    width=590,
                    height=1000,
                    top=10,
                    left=625,
                    children={
                        "gp_img": ImageLayout(
                            name="gp_img",
                            path="assets/circuits/photos/abudhabi.png",
                            width=3000,
                            top=0,
                        ),
                        'blur': Layout(
                            name="blur",
                            width=590,
                            height=1000,
                            bg=(255,255,255,100),
                        ),
                        "logo100": ImageLayout(
                            name="logo100",
                            width=500,
                            path="assets/logos/FBRT/100.png"
                        ),
                        "text_lines": RoundedLayout(
                            name="text_lines",
                            width=590,
                            height=250,
                            top=640,
                            bg=0,
                            radius=0,
                            children={
                                f"text_line_{i}" : TextLayout(
                                    name=f"text_line_{i}",
                                    top=25+i*25,
                                    height=20,
                                    width=580,
                                    fg=255,
                                    font_name="regular",
                                    content=line_content,
                                ) for i, line_content in enumerate(texts)
                            }
                        ),
                        "text_box_twitch": RoundedLayout(
                            name="text_box_twitch",
                            width=590,
                            height=50,
                            top=920,
                            bg=(146, 70, 255),
                            radius=0,
                            children={
                                "twitch_text_line": TextLayout(
                                    name="twitch_text_line",
                                    width=570,
                                    height=25,
                                    fg=255,
                                    content="RDV 20h45 sur notre chaine Twitch !",
                                )
                            },
                        ),
                        "f124_logo": ImageLayout(
                            name="f124_logo",
                            path="assets/logos/f1/24_black.png",
                            height=50,
                            width=300,
                            top=300,
                        ),
                        "date_container": RoundedLayout(
                            name="date_container",
                            width=450,
                            height=50,
                            right=0,
                            top=200,
                            bg=0,
                            radius=0,
                            children={
                                "date": TextLayout(
                                    name="date",
                                    width=300,
                                    fg=(255, 255, 255),
                                    bg=0,
                                    content="7 Octobre, 20h45",
                                    font_name="regular",
                                ),
                            }
                        ),
                        "flag": ImageLayout(
                            name="flag",
                            path="assets/circuits/flags/abudhabi.png",
                            height=75,
                            top=40,
                        ),
                        "country_container": RoundedLayout(
                            name="country_container",
                            width=450,
                            left=0,
                            height=50,
                            top=150,
                            bg=(200,0,0),
                            radius=0,
                            children={
                                "country_name": TextLayout(
                                    name="country_name",
                                    height=30,
                                    content="YAS MARINA, ABU DHABI",
                                    bg=(200,0,0),
                                    fg=(255,255,255),
                                ),
                            }
                        ),
                    }
                ),
                "fr_separator": Layout(
                    name="fr_separator",
                    width=590,
                    height=10,
                    top=505,
                    left=1240,
                    bg=0,
                    children={
                        'fr_blue': Layout(
                            name='fr_blue',
                            bg=(0, 38, 84),
                            width=200,
                            left=0
                        ),
                        'fr_white': Layout(
                            name='fr_white',
                            bg=255,
                            width=210,
                            left=200,
                        ),
                        'fr_red': Layout(
                            name='fr_red',
                            bg=(206, 17, 38),
                            width=200,
                            left=410,
                        ),
                    }
                ),
                "be_separator": Layout(
                    name="be_separator",
                    width=590,
                    height=10,
                    top=505,
                    left=10,
                    bg=0,
                    children={
                        'be_black': Layout(
                            name='be_black',
                            bg=(0, 0, 0),
                            width=200,
                            left=0
                        ),
                        'be_yellow': Layout(
                            name='be_yellow',
                            bg=(253, 218, 37),
                            width=210,
                            left=200,
                        ),
                        'be_red': Layout(
                            name='be_red',
                            bg=(239, 51, 64),
                            width=200,
                            left=410,
                        ),
                    }
                ),
            }
        )
    }
)
ctx = {

}
img = layout.render(ctx)
img.save('f11000gp.png', quality=100)
