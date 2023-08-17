from ..event import Event


class AbstractListener:
    SUBSCRIBED_EVENTS = []

    # TODO idée de retourner une liste de "DiscordMessage" permettant de spécifier
    # quel type/urgence du message pour pouvoir envoyer dans différents channels si on le souhaite
    # ce mapping pourrait même être une config du championnat
    def on(self, event:Event, *args, **kwargs) -> str:
        unsp_name = event.name.lower()
        method = getattr(self, f'_on_{unsp_name}')
        if method:
            return method(*args, **kwargs)