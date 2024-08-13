from ..generators.abstract_race_generator import AbstractRaceGenerator


class LineupGenerator(AbstractRaceGenerator):
    def _get_visual_type(self) -> str:
        return 'lineup'
