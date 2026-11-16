from ncca.ngl import Obj, Vec3


class FFDObj(Obj):
    def __init__(self, file_name):
        super().__init__()
        self.load(file_name)
        self._bbox_min = Vec3(self.min_x, self.min_y, self.min_z)
        self._bbox_max = Vec3(self.max_x, self.max_y, self.max_z)
        self._transformed_vertices = self.vertex.copy()
        extent = self._bbox_max - self._bbox_min
        # axis aligned edges for now, the stu maths below works for any edges
        self._s = Vec3(extent.x, 0.0, 0.0)
        self._t = Vec3(0.0, extent.y, 0.0)
        self._u = Vec3(0.0, 0.0, extent.z)

    @property
    def bbox_min(self) -> Vec3:
        return self._bbox_min

    @property
    def bbox_max(self) -> Vec3:
        return self._bbox_max
