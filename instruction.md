# Assignment 2: Isosurfaces and Color Mapping

## Objectives

The topic of this assignment is the visualization of three-dimensional scalar
fields (3D fields of numbers) using isosurfaces. Specifically, we will consider
a medical imaging dataset corresponding to CT scans of a female subject. Your
objective will be to combine isosurfaces, transparency, clipping planes, and
color mapping to show the anatomical structures present in the data.

## Background

The data corresponds to [CT scans](https://en.wikipedia.org/wiki/CT_scan) of a
human female head and feet, courtesy of the Visible Human Project. For each
dataset, both high and low-resolution versions are available. The small
resolution was created by halving the size of the original data along each
direction (it is, therefore, eight times smaller). For each resolution, you will
find a CT volume along with a dataset corresponding to the magnitude of the
gradient of the CT image. As a reminder, the gradient of a scalar field is the
vector-valued derivative of the scalar field. Here, however, we are only
interested in the magnitude of the derivative. In each case, the CT data is of
type `unsigned short` (16 bits), yielding values between 0 and 65535, while the
gradient magnitude data is of type `float`. Note that the small resolution is
mainly provided as a convenience for the testing phase of your implementation. I
expect to see high-quality results at full resolution in your reports. The
interesting features in this dataset correspond to skin, bones, and muscles.
Note that other soft tissues (e.g., fat or brain) are too difficult to extract.

## Overview

Your experimentation with the head dataset should allow you to identify values
that correspond to the skin, skull, and muscles. In the foot dataset, you will
use isosurfaces to reveal the bone structure and the skin and surrounding
muscles. Note that for each dataset, the CT and gradient magnitude volumes will
offer you complementary means to identify interesting features. To permit the
selection of good isovalues, you will create a GUI to select individual values
associated with the various structures you are looking for. A slider bar will
allow you to interactively browse the value range in search of the proper
isovalue, while two additional slider bars will allow you to select a range of
gradient magnitudes to act as a filter on the constructed isosurface. You will
use transparency and clipping planes to mitigate the occlusion caused by the
surfaces' nested arrangement. Clipping planes will allow you to remove the
occluding parts of the surfaces to reveal internal structures. Finally, you will
use color mapping to convey the quantitative properties of the selected
isosurfaces.

## Task 1 - Interactive Isosurfacing

The first task consists in visualizing a 3D scalar dataset using isosurfacing
while supporting the interactive modification of the corresponding isovalue.
This initial step will yield a set of isovalues that correspond to the major
anatomical structures present in each dataset. Specifically, skin, bones, and
muscles.

### Implementation

Write a program that uses
[`vtkContourFilter`](https://vtk.org/doc/nightly/html/classvtkContourFilter.html)
to extract isosurfaces and ties it to a slider bar GUI to manipulate the
isovalue interactively. To address occlusion issues, your program will offer
interactive control over three clipping planes implemented as a
[`vtkClipPolyData`](https://vtk.org/doc/nightly/html/classvtkClipPolyData.html)
filter with an implicit function called
[`vtkPlanes`](https://vtk.org/doc/nightly/html/classvtkPlanes.html), which
allows you to clip away portions of the volume to reveal internal structures.
You will also add a color bar to your render window to show the meaning of the
colors used in your visualization. This is done with the help of
[`vtkScalarBarActor`](https://vtk.org/doc/nightly/html/classvtkScalarBarActor.html).
Note the helper VTK software that I shared (`vtk_colorbar.py`) contains the code
necessary to create a color bar. Specifically, your program must satisfy the
following requirements.

- Implement the API described below.
- Perform an isosurface visualization of the dataset.
- Provide a slider bar to control the isovalue to be used within a range of
  interesting values.
- Display next to the slider bar the value currently selected.
- Ensure consistency between slider bar selection and isosurface.
- Provide three additional slider bars GUI to control the position of three
  clipping planes moving along the X, Y, and Z coordinate axes, respectively.
  Each plane defines two half spaces, one of which will not be shown. Note: the
  clipping planes should be applied sequentially: only the half-space selected
  by the X clipping plane will be available to the Y clipping plane, etc...
- Show the color scale through a color bar.
- Optionally import the initial isovalue and initial X, Y, and Z clipping plane
  positions from the command line and initialize the corresponding sliders
  accordingly.

### API

Your program will have the following API:

```sh
python isosurface.py -i [--input] <data> [--value <value>] [--clip <X> <Y> <Z>]
```

where `<data>` is the 3D scalar dataset to visualize, `<value>` is the optional
initial isovalue to be used by the program, and `<X>` `<Y>` `<Z>` are the
optional initial positions of the three clipping planes.

### Report

Include in your report high-quality images showing the anatomical structures
that you were able to extract with isosurfaces. Each image should include a
color bar. Indicate which isovalues you identified for each structure and the
visual settings associated with each visualization. Use clipping planes at your
discretion to facilitate the visual inspection of your results. In addition,
include answers to the following questions in your report.

1. Which isosurfaces look the most interesting and why?
1. How did you select the position of clipping planes?

## Task 2 - Value vs. Gradient Magnitude

Now that you have identified interesting isosurfaces corresponding to major
anatomical structures in each dataset, your second task is to color map the
value of the gradient magnitude on those isosurfaces. In other words, you will
visualize the values that the gradient magnitude takes on each isosurface. This
visualization will give you additional insight into the properties of each
isosurface.

### Implementation

Write a program that takes both scalar volume and gradient magnitude in input as
well as a set of pre-selected isovalues in Task 1 and perform the color coding
of the gradient magnitude on the isosurfaces. More precisely, you will use
[`vtkProbeFilter`](https://vtk.org/doc/nightly/html/classvtkProbeFilter.html)
jointly on the geometry of the isosurfaces and the gradient magnitude volume to
associate each vertex of the isosurfaces with the corresponding gradient
magnitude value. The color mapping will be controlled by a color map supplied by
the user. Specifically, your program must meet the following requirements:

- Take in input the name of the scalar volume and the corresponding gradient
  magnitude volume from the command line
- Take in input the name of a file containing a set of isovalues (1) to be used
  for isosurface extraction
- Perform the resampling of the gradient magnitude on these isosurfaces and
  apply color mapping to visualize the resulting values
- Optionally take in input a color map to be used for the color mapping of
  gradient magnitude on the isosurfaces. Otherwise, resort to a default color
  map
- Provide the same three sliders GUI (2) used in Task 1 to control the position
  of 3 clipping planes to be used in the visualization
- Include a color bar to document the selected color map

### Notes

1. The isovalues used by the program must be included in a file (see API below).
1. The GUI only controls the clipping planes. There is no isovalue slider for
   this task.

### API

Your program will have the following API:

```sh
python isogm.py -i [--input] <data> -g [--grad] <gradmag> -v [--value] <isoval> [--cmap <colors>] [--clip <X> <Y> <Z>]
```

where `<data>` is the 3D scalar dataset, `<gradmag>` is the corresponding
gradient magnitude, `<isoval>` is the name of a file containing the isovalues to
be used, `<colors>` is the optional name of a file containing a color map
definition with the following syntax:

- Lines preceded by the character '#' contain comments and should be ignored
- Each non-comment line must contain a scalar value followed by the R, G, and B
  values of the associated color.

Finally, `<X>` `<Y>` `<Z>` are the optional initial positions of the three
clipping planes.

### Report

Include in your report images of the color-mapped isosurfaces computed by your
program. Indicate clearly for each surface the corresponding isovalue. Each
image should include a color bar. In addition, answer the following questions:

1. What relationship can you identify between the gradient magnitude
   distribution of the various isosurfaces?
1. How do you interpret these results? Explain.
1. What does that tell you about the value of the resulting visualization?
   Explain.

## Task 3 - Two-dimensional Transfer Function

Combining the insight you gained from Task 1 and Task 2, you will now use the
gradient magnitude data to filter out unwanted portions of your isosurfaces.
Specifically, Task 2 has shown you what values of the gradient magnitude
coincide with certain portions of your isosurface. You can therefore use this
information to discard from an isosurface uninteresting portions by specifying a
gradient magnitude interval outside which isosurface points should be removed.
This kind of downstream filtering can be achieved by using
[`vtkClipPolyData`](https://vtk.org/doc/nightly/html/classvtkClipPolyData.html)
again. However, this time you will be applying it directly to the gradient
magnitude values attached to the vertices of the isosurface. In fact, you will
need to use two such filters in a row for a given [_grad-min_, _grad-max_]
gradient magnitude interval, one to discard all the values below grad-min and
one to discard all the values above grad-max among the values that passed the
first filtering stage.

### Implementation

Write a program similar to the one you wrote for Task 2, except that this time,
the gradient magnitude information will not be directly displayed on the
isosurface after resampling but instead used to determine which points should be
removed from the isosurface in the visualization pipeline. Your program should
allow the user to interactively modify the [gradmin,gradmax] selection interval
to facilitate the identification of an optimal range. Specifically, your program
should meet the following requirements:

- Take in input the name of both scalar volume and gradient magnitude datasets
  to be processed from the command line.
- Take in input the isovalue to consider
- Provide a GUI with two slider bars to allow the user to control the range (min
  et max) of gradient magnitude values to select
- Provide the same GUI as in Task 1 to control the position of 3 clipping planes
  to be used in the visualization
- Perform a resampling of the gradient magnitude on the isosurface
- Filter the isosurface using two consecutive
  [`vtkClipPolyData`](https://vtk.org/doc/nightly/html/classvtkClipPolyData.html)
  consistent with the gradient magnitude range currently selected
- Visualize the resulting filtered isosurface

Note that in contrast to Task 2, you will only be considering one isosurface at
a time here. This is meant to facilitate the adjustment of the gradient
magnitude range independently for each surface.

### API

Your program will have the following API:

```sh
python iso2dtf.py -i [--input] <data> -g [--grad] <gradientmag> -v [--value] <value> [--clip <X> <Y> <Z>]
```

where `<data>` is the 3D scalar dataset and `<gradientmag>` is the corresponding
gradient magnitude to visualize, `<value>` is the initial isovalue, and `<X>`
`<Y>` `<Z>` are the optional initial positions of the three clipping planes
(optional as well).

### Report

Include high-quality images for each dataset corresponding to each filtered
isosurface in your report while precisely indicating the matching isovalue.
Indicate for each visualization which parameters / visual settings were used to
create the image. In addition, provide an answer to the following questions,
with images to support your answers as necessary.

1. Did the gradient magnitude filtering help in refining the isosurface
   selection? If so, how? Be specific.
1. Which isosurfaces benefited the most from this filtering? Why?

## Task 4 - Complete visualization

Using the isovalues that you identified in Task 1 and the gradient magnitude
ranges that you discovered in Task 3, you will now create a visualization where
all the filtered isosurfaces are shown simultaneously using color and
transparency.

### Implementation

For this final implementation task, you will write a program that incorporates
the various features of the programs written so far and uses transparency in
addition to clipping planes to allow for all relevant isosurfaces to be shown
simultaneously without excessive occlusion. Remember to use Depth Peeling to
achieve correct transparency results! Specifically, your program must satisfy
the following requirements.

- Take in input from the command line the name of both scalar volume and
  gradient magnitude datasets to be processed.
- Take in input the name of a file that specifies, for each isosurface, the
  corresponding isovalue, the associated gradient magnitude range, and the
  associated color and transparency.
- Perform a resampling of the gradient magnitude on each isosurface
- Filter each isosurface using two consecutive vtkClipPolyData consistent with
  the gradient magnitude range specified for that isosurface
- Visualize the resulting filtered isosurfaces with the correct colors and
  transparency
- Provide the same GUI as in Task 1 to control the position of 3 clipping planes
  to be used in the visualization

### API

Your program will have the following API:

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
  "`<isovalue> <grad_min> <grad_max> <R> <G> <B> <alpha>`" where
  "`<grad_min> <grad_max>`" indicates the gradient magnitude filtering range for
  that particular isosurface, "`<R> <G> <B>`" specify the color associated with
  `<isovalue>`, and `<alpha>` is the associated opacity.

### Report

Include in your report high-quality images showing the results produced by your
method for your particular selection of parameters for each dataset.

- Comment on your selection of the transparency for each isosurface.
- Does transparency benefit your visualization, and if so, how? Explain.

## Summary Analysis

Comment on the effectiveness of isosurfaces for these medical imaging datasets
in your report. Isosurfaces, in general, are widely used in medical
applications.

1. What explanation can you offer for this success?
1. Comment on the quality of the images you obtained in each case.
1. Discuss any shortcomings of the isosurfacing technique you may have
   encountered in this project.
1. Comment on the role and meaning of gradient magnitude to filter isosurfaces.
1. Comment on the benefits and limitations of transparency and clipping planes
   to enhance the visualization.

## Datasets

The datasets are available online. All datasets are of type vtkStructuredPoints,
which is itself a specialized type of vtkImageData.

!! TODO !!
