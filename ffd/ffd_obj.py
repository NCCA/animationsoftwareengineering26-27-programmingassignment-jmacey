from ncca.ngl import Obj, Vec3

from lattice import Lattice


class FFDObj(Obj):
    def __init__(self, file_name):
        super().__init__()
        self.load(file_name)
        self._bbox_min = Vec3(self.min_x, self.min_y, self.min_z)
        self._bbox_max = Vec3(self.max_x, self.max_y, self.max_z)
        self._rest = [v.copy() for v in self.vertex]
        self._stu: list[Vec3] = []

        # extent = self._bbox_max - self._bbox_min
        # # axis aligned edges for now, the stu maths below works for any edges
        # self._s = Vec3(extent.x, 0.0, 0.0)
        # self._t = Vec3(0.0, extent.y, 0.0)
        # self._u = Vec3(0.0, 0.0, extent.z)

    @property
    def bbox_min(self) -> Vec3:
        return self._bbox_min

    @property
    def bbox_max(self) -> Vec3:
        return self._bbox_max

    def bind(self, lattice: Lattice) -> None:
        """
        Embed every rest vertex in the lattice, this needs to run every time the lattice changes.
        This will generate the _stu verts for each point from the rest mesh.
        """
        self._stu = []
        for vertex in self._rest:
            stu = lattice.embed(vertex)
            stu = Vec3(*(min(max(float(v), 0.0), 1.0) for v in (stu.x, stu.y, stu.z)))
            self._stu.append(stu)

    def deform(self, lattice: Lattice) -> None:
        """
        Set the mesh vertices from the current lattice cps
        """
        if not self._stu:
            raise RuntimeError("bind must be called before deform")
        self.vertex = [lattice.evaluate(stu) for stu in self._stu]
