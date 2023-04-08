from psd_tools import PSDImage
psd = PSDImage.open('test.psd')
visages = psd[1]
tenues = psd[2]
total_visages = len(visages)
total_tenues = len(tenues)
for i, v in enumerate(visages):
    print(f'Visage {v.name} ({i}/{total_visages})')
    for v2 in visages:
        v2.visible = False
    v.visible = True
    for j, t in enumerate(tenues):
        print(f'\tTenue {t.name} ({j}/{total_tenues})')
        for t2 in tenues:
            t2.visible = False
        t.visible = True
        file_name = f'output/pilots/{t.name}_{v.name}.png'
        psd.composite(layer_filter=lambda x:x.is_visible()).save(file_name)
        t.visible = False
    v.visible = False