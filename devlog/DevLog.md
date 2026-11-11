# Week 1

Decided on the initial idea of doing an FFD project using the original FFD paper to start with (the one with the incorred maths! which I will explain later).

Have made the initial design in the README.md and am going to start setting up the project for using the tools I need.

To do this we just run the following

```bash
uv init
git add .
git commit -am "updated to add uv project at root"
```

At present this has setup things as a src project and I need to decide how to structure it properly later. For now I will just keep it as a flat structure. I will also add the pyngl library as I am going to use it for the maths and 3D stuff.

```bash
uv add ncca-ngl
```

Finally get ready for testing with pytest I will add pytest and other things I need such as coverage and pytest-qt.

```
uv add --dev pytest
uv add --dev pytest-qt
uv add --dev pytest-coverage
```

## Basic Testing plan

Write Lattice, and ControlPoint classes first
Mesh will use Obj from PyNGL but access the verts directly for FFD
Draw lattice and control points and allow for selection of control points.
Add manipulators and allow for selections of control points.
Update all selected control points when the lattice is moved.
