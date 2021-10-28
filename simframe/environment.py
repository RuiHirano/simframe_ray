from .area import IArea, Area

class Environment:
    def __init__(self):
        self.area = Area(
            id="environment",
            start_x=0,
            end_x=100,
            start_y=0,
            end_y=100
        )

    def set_area(self, area: IArea):
        self.area = area
    
