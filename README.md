# Isosurfaces and Color Mapping

CS530 Introduction to Scientific Visualization assignment 2 @Purdue.

## Dataset

Get the dataset
[here](https://www.cs.purdue.edu/homes/cs530/projects/project2.html).

## Getting Started

Install Python 3.11.1 or later.

Install Poetry **1.3.2 or later**. See
[Poetry's documentation](https://python-poetry.org/docs/) for details.

> Poetry earlier than 1.3 will not work.

Install the project's dependencies:

```sh
poetry install --no-root
```

Activate the virtual environment:

```sh
poetry shell
```

Execute the application:

```sh
python isosurface.py -i [--input] <data> [--value <value>] [--clip <X> <Y> <Z>]
```

where `<data>` is the 3D scalar dataset to visualize, `<value>` is the optional
initial isovalue to be used by the program, and `<X>` `<Y>` `<Z>` are the
optional initial positions of the three clipping planes.

```sh
python isogm.py -i [--input] <data> -g [--grad] <gradmag> -v [--value] <isoval> [--cmap <colors>] [--clip <X> <Y> <Z>]
```

where `<data>` is the 3D scalar dataset, `<gradmag>` is the corresponding
gradient magnitude, `<isoval>` is the name of a file containing the isovalues
(line-separated) to be used, `<colors>` is the optional name of a file
containing a color map definition with the following syntax:

- Lines preceded by the character `#` contain comments and should be ignored
- Each non-comment line must contain a scalar value (of the gradient magnitude)
  followed by the R, G, and B values of the associated color. Finally, `<X>`
  `<Y>` `<Z>` are the optional initial positions of the three clipping planes.

See `assets/isovalues.txt` and `assets/colormap.txt` for examples.

```sh
python iso2dtf.py -i [--input] <data> -g [--grad] <gradientmag> [-v [—value] <value>] [--clip <X> <Y> <Z>]
```

where `<data>` is the 3D scalar dataset and `<gradientmag>` is the corresponding
gradient magnitude to visualize, `<value>` is the initial isovalue (optional) ,
and `<X>` `<Y>` `<Z>` are the optional initial positions of the three clipping
planes (optional as well).

```sh
python isocomplete.py -i [--input] <data> -g [--grad] <gradientmag> -p [--param] <params> [--clip <X> <Y> <Z>]
```

where `<data>` is the 3D scalar dataset, `<gradientmag>` is the corresponding
gradient magnitude to use for filtering, `<params>` is the name of a file
containing all the information necessary to select, filter, and visualize the
isosurfaces. The format of this file will be as follows.

- Lines starting with '#' will be considered comments and ignored.
- Each following line that is not a comment will indicate an isovalue, a
  gradient magnitude range (min then max value), an RGB color, and an opacity
  value. It will have the form
  `<isovalue> <grad_min> <grad_max> <R> <G> <B> <alpha>` where
  `<grad_min> <grad_max>` indicates the gradient magnitude filtering range for
  that particular isosurface, `<R> <G> <B>` specify the color associated with
  `<isovalue>`, and `<alpha>` is the associated opacity.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).
