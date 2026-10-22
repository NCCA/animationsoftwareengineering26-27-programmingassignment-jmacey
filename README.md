# Jon Macey ASE Assignment

## Introduction

For this project I am going to develop a simple Free Form Deformation demo using PySide6, Numpy and PyNGL. It will start by implementing the original Sederberg and Parry FFD paper. https://people.eecs.berkeley.edu/~sequin/CS285/PAPERS/Sederberg_Parry.pdf the I may look at some of the later improvements.

## Inital Design

For the basic setup I will use some of the existing PyNGL demos to get started. Initially I will need to load a mesh (I will use Obj to get started) and then develop a simple grid overlay to allow the user to select control points.

After that I will need to implement the FFD algorithm itself using the Bernstein polynomial basis functions (using numpy for speed).
