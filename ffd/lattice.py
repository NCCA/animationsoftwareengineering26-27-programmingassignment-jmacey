"""The main lattice and control point module for the FFD algorithm

This module contains the `ControlPoint` and `Lattice` classes

Typical usage will be that Lattice is constructed and uses the Control points. 

Notes : 
    Does CP need to be public? Lattice will create so perhaps could be private
    

"""

from ncca.ngl import Vec3

class ControlPoint: 
    """Single Control Point for the Lattice. 
        Args :
            pos : initial position of the CP : Vec3 

        Attributes :
            pos : Vec3 the current cp position
            selected : bool if the cp is active
    """
    def __init__(self, pos : Vec3) :
        self._pos = pos
        self._selected = False

    @property
    def pos(self) -> Vec3 :
        return self._pos 

    @property
    def selected(self) -> bool :
        return self._selected