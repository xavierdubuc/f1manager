from ..event import Event


class AbstractListener:
    SUBSCRIBED_EVENTS = []

    def on(self, event:Event, *args, **kwargs) -> str:
        unsp_name = event.name.lower()
        method = getattr(self, f'_on_{unsp_name}')
        if method:
            return method(*args, **kwargs)