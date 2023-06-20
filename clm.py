import tabulate


def print_clm(l: list):
    ranking = [
        (i+1, l[i][0], l[i][1])
        for i in range(len(l))
    ]
    print(tabulate.tabulate(ranking, tablefmt='simple_grid'))


CANADA = [
    ('xKayysor',        '1:09.424'),
    ('majforti-07',     '1:09.884'),
    ('GT10_LeMac',      '1:09.968'),
    ('FBRT_CiD16',      '1:09.984'),
    ('FBRT_Nico',       '1:10.229'),
    ('Gros-Nain-Vert',  '1.10:435'),
    ('Iceman7301',      '1.10.608'),
    ('Xionhearts',      '1:10.639'),
    ('ewocflo',         '1:10.725'),
    ('FBRT_Seb07',      '1:10.747'),
    ('DimDim91270',     '1:10.863'),
    ('Juraptors',       '1:10.904'),
    ('djeck',           '1:11.043'),
    ('APX_Maxeagle',    '1:11.058'),
    ('Prolactron',      '1:11.170'),
    ('x0-STEWEN_26-0x', '1:11.184'),
    ('Enakozi',         '1:11.197'),
    ('FBRT_REMBRO',     '1:11.301'),
    ('Alpha_Darrk',     '1:11.330'),
    ('VRA-RedAym62',    '1:12.633'),
    ('CedricB-TOH1',    '1:13.333'),
]

BAHREIN = [
    ('majforti-07',     '1:27.928'),
    ('GT10_LeMac',      '1:28.269'),
    ('Gros-Nain-Vert',  '1.28.325'),
    ('WSC_Gregy21',     '1:28.327'),
    ('FBRT_CiD16',      '1:28.346'),
    ('xKayysor',        '1:28.459'),
    ('x0-STEWEN_26-0x', '1:28.461'),
    ('FBRT_Seb07',      '1:28.532'),
    ('Iceman7301',      '1.28.558'),
    ('FBRT_Naax',       '1.28.651'),
    ('Alpha_Darrk',     '1:28.677'),
    ('Juraptors',       '1:28.778'),
    ('APX_Maxeagle',    '1:28.839'),
    ('ewocflo',         '1:28.974'),
    ('DimDim91270',     '1:29.002'),
    ('FBRT_Nico',       '1:29.005'),
    ('Prolactron',      '1:29.063'),
    ('djeck',           '1:29.212'),
    ('Enakozi',         '1:29.298'),
    ('Xionhearts',      '1:29.362'),
    ('VRA-RedAym62',    '1:30.001'),
    ('FBRT_REMBRO',     '1:30.288'),
    ('CedricB-TOH1',    '1:30.469'),
]
