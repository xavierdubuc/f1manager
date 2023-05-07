class LapRecord:
    best_lap_time_lap_num: int = None
    best_sector1_lap_num: int = None
    best_sector2_lap_num: int = None
    best_sector3_lap_num: int = None
    best_lap_time: int = None
    best_sector1_time: int = None
    best_sector2_time: int = None
    best_sector3_time: int = None

    def __str__(self):
        return (
            f"{self.best_lap_time} (Lap {self.best_lap_time_lap_num})\n"
            f"Sector 1: {self.best_sector1_time} (Lap {self.best_sector1_lap_num})\n"
            f"Sector 2: {self.best_sector2_time} (Lap {self.best_sector2_lap_num})\n"
            f"Sector 3: {self.best_sector3_time} (Lap {self.best_sector2_lap_num})"
        )