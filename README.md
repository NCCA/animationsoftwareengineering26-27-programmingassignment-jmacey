# Jon Macey ASE Assignment

## Introduction

For this project I am going to develop a simple Free Form Deformation demo using PySide6, Numpy and PyNGL. It will start by implementing the original Sederberg and Parry FFD paper. https://people.eecs.berkeley.edu/~sequin/CS285/PAPERS/Sederberg_Parry.pdf the I may look at some of the later improvements.

Most of the work will be documented in the [DevLog](devlog/DevLog.md) for ease and this will get updated as the project progresses.

## Inital Design

For the basic setup I will use some of the existing PyNGL demos to get started. Initially I will need to load a mesh (I will use Obj to get started) and then develop a simple grid overlay to allow the user to select control points.

After that I will need to implement the FFD algorithm itself using the Bernstein polynomial basis functions (using numpy for speed).

![](images/InitialClassDiagram.png)

## A better class diagram.

It is possible to use [mermaid](https://mermaid.js.org/) to create better class diagrams and render them in GitHub Markdown. The following mermaid code can be used to render the class diagram (we use the triple quotes ````mermaid` to denote the start and end of the code block and github will render to a diagram). If you open this file in the editor you can see the raw mermaid code.

```mermaid
classDiagram
    class Mesh {
        +list~Vec3~ verts
        +list~Vec2~ uv
        +list~Vec3~ normals
        +deform(lattice: Lattice)
        +load(path: str)
        +save(path: str)
    }

    class Lattice {
        +int width
        +int depth
        +int height
        +list~ControlPoint~ cvs
    }

    class ControlPoint {
        +Vec3 pos
        +bool selected
    }

    class Manip {
        +translate(delta: Vec3)
    }

    Lattice "1" --> "1" Mesh : deforms
    Lattice "1" *-- "many" ControlPoint : contains
    Manip "1" --> "many" ControlPoint : moves
```

This is still the initial design and will change as I progress, but this is the first thing you should do when starting the project.

## New Lattice Design

The next stage is to design the lattice class here is a new basic class diagram.

```mermaid
classDiagram
class ControlPoint {
        +Vec3 pos
        +bool selected
    }

class Lattice {
        +tuple~int~ shape
        +Vec3 origin
        +Vec3 s
        +Vec3 t
        +Vec3 u
        +int version
        +list~ControlPoint~ cvs
        +from_extents(shape, bbox_min, bbox_max, padding)$ Lattice
        +select_all()
        +deselect_all()
        +selection_centre() Vec3
        +move_selected(delta: Vec3)
        +rotate_selected(angle, axis, pivot)
        +scale_selected(factor: Vec3, pivot)
        +reset()
        +edges() list
        +embed(point: Vec3) Vec3
        +evaluate(stu: Vec3) Vec3
    }

    Lattice "1" *-- "many" ControlPoint : contains

```

```mermaid
classDiagram
  direction LR

  class Lattice {
      -tuple _shape
      -Vec3 _origin
      -Vec3 _s
      -Vec3 _t
      -Vec3 _u
      -float _volume
      -list~Vec3~ _rest
      -list~ControlPoint~ _cvs
      -int _version
      +shape tuple «property»
      +origin Vec3 «property»
      +s Vec3 «property»
      +t Vec3 «property»
      +u Vec3 «property»
      +cvs tuple~ControlPoint~ «property»
      +version int «property»
      +selected list~ControlPoint~ «property»
      +__init__(shape, bbox_min Vec3, bbox_max Vec3)
      +from_extents(shape, bbox_min Vec3, bbox_max Vec3, padding float)$ Lattice
      -_build_grid() list~Vec3~
      +index(i int, j int, k int) int
      +__getitem__(ijk) ControlPoint
      +__len__() int
      +__iter__() Iterator
      +select_all() None
      +deselect_all() None
      +selection_centre() Optional~Vec3~
      +move_selected(delta Vec3) None
      +rotate_selected(angle float, axis str, pivot Vec3) None
      +scale_selected(factor Vec3, pivot Vec3) None
      +reset() None
      +edges() list~tuple~
      +positions() list~Vec3~
      +embed(point Vec3) Vec3
      +inside(stu Vec3)$ bool
      +evaluate(stu Vec3) Vec3
  }

  class ControlPoint {
      +pos Vec3
      +selected bool
      +move(delta Vec3) None
      +toggle_selected() None
  }

  class bernstein {
      <<function>>
      +bernstein(degree int, t float) list~float~
  }

  class Vec3 {
      <<ngl>>
  }

  class Mat3 {
      <<ngl>>
      +rotate_x(angle)$ Mat3
      +rotate_y(angle)$ Mat3
      +rotate_z(angle)$ Mat3
  }

  Lattice "1" *-- "l·m·n" ControlPoint : _cvs (flat, k fastest)
  Lattice --> Vec3 : origin, s, t, u, _rest
  Lattice ..> Mat3 : rotate_selected
  Lattice ..> bernstein : evaluate
  ControlPoint --> Vec3 : pos


```
