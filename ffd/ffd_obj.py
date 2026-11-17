from os import PathLike

from ncca.ngl import Obj, Vec3


class FFDObj(Obj):
    def __init__(self, file: str | PathLike[str]) -> None:
        super().__init__()
        self.load(file)
        self._bbox_min = Vec3(self.min_x, self.min_y, self.min_z)
        self._bbox_max = Vec3(self.max_x, self.max_y, self.max_z)
        # rest vertex used for calculating the deformations
        self._rest = [v.copy() for v in self.vertex]
        # local point cords
        self._stu: list[Vec3] = []

    @property
    def bbox_min(self) -> Vec3:
        return self._bbox_min

    @property
    def bbox_max(self) -> Vec3:
        return self._bbox_max
