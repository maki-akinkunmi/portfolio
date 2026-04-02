# Backwards Ray Tracer

A backward ray tracer implemented in Python. This project demonstrates foundational computer graphics concepts, including ray-object intersections, transformation matrices, local illumination, and recursive reflections. 

## Features

* **Scene Parsing** - Reads custom `.txt` configuration files to dynamically load camera settings, resolution, lights, and objects.
* **Geometry** - Accurately renders spheres and ellipsoids (non-uniformly scaled spheres) by transforming rays into local object space using inverse transformation matrices.
* **Local Illumination** - Implements the Ambient, Diffuse, and Specular (ADS) lighting model to calculate realistic surface shading.
* **Shadows** - Casts shadow rays toward point light sources, accurately calculating occlusions and preventing self-shadowing (shadow acne) using surface normal offsets.
* **Recursive Reflections** - Simulates mirrored surfaces by bouncing rays off objects, with a configurable maximum recursion depth (default of 3 bounces).
* **Image Output** - Generates standard text-based ASCII PPM (P3) image files that can be opened in viewers like GIMP or IrfanView.

## Input File Format

The ray tracer parses space-delimited text files. The syntax requires the following commands, with vectors and colors represented by floats and resolution by integers:

* `NEAR <n>`: The near clipping plane distance.
* `LEFT <l>`, `RIGHT <r>`, `BOTTOM <b>`, `TOP <t>`: The image plane boundaries.
* `RES <x> <y>`: The resolution of the output image in pixels.
* `SPHERE <name> <pos x> <pos y> <pos z> <scl x> <scl y> <scl z> <r> <g> <b> <ka> <kd> <ks> <kr> <n>`: Defines a sphere/ellipsoid with position, non-uniform scaling, RGB color, ambient (ka), diffuse (kd), specular (ks), and reflection (kr) coefficients, and specular exponent (n).
* `LIGHT <name> <pos x> <pos y> <pos z> <ir> <ig> <ib>`: Defines a point light source with position and RGB intensity.
* `BACK <r> <g> <b>`: The background color.
* `AMBIENT <ir> <ig> <ib>`: The global ambient light intensity.
* `OUTPUT <name>`: The name of the output PPM file.4

---

## Prerequisites

To run this project, you will need **Python 3.x** and the **NumPy** library installed on your system for vector and matrix mathematics.

You can install the required library using `pip`:

```bash
pip install numpy
```

---

## Running the Ray Tracer

Because this is an interpreted Python script, no compilation via `make` is required. 

1. Clone the repository and navigate to the project directory.
2. Run the ray tracer on a single scene file by passing the text file as an argument:
```bash
python RayTracer2.py testIllum.txt
```
3. To batch render all test cases in the directory and its subfolders automatically, a helper script is included:
```bash
python run_all.py
```
4. The output `.ppm` image files will be generated and saved in the same directory as their respective input `.txt` files.

---

## Technical Details

* **Language** - Python 3
* **Core Libraries** - `numpy` (for high-performance linear algebra), standard Python libraries (`sys`, `os`, `glob`).
* **Architecture** - The engine operates on a classic backward ray-tracing algorithm. It parses scene data into `Scene`, `Sphere`, and `Light` objects. For every pixel on the image plane, it generates a primary viewing ray. Intersections are calculated by solving the quadratic equation for a canonical unit sphere, utilizing 4x4 homogeneous coordinate matrices to handle non-uniform scaling (ellipsoids). Lighting and shadows are calculated at the intersection point, and reflection rays are recursively traced up to the maximum depth limit. The final RGB values are clamped and written out to a 2D image array.
