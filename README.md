# napari-video
Napari plugin for working with videos.

Relies on [pyvideoreader](https://pypi.org/project/pyvideoreader/) as a backend which itself uses [opencv](https://opencv.org) for reading videos.

## Installation
```shell
pip install napari[all] napari_video
```

## Usage
From a terminal:
```shell
napari video.avi
```

Or from within python:
```shell
import napari
from napari_video.napari_video import VideoReaderNP

path='video.mp4'
vr = VideoReaderNP(path)
with napari.gui_qt():
    viewer = napari.view_image(vr, name=path)
```

## Internals
`napari_video.napari_video.VideoReaderNP` exposes a video with a numpy-like interface, using opencv as a backend.

For instance, open a video:
```python
vr = VideoReaderNP('video.avi')
print(vr)
```
```
video.avi with 60932 frames of size (920, 912, 3) at 100.00 fps
```
Then

- `vr[100]` will return the 100th frame as a numpy array with shape `(902, 912, 3)`.
- `vr[100:200:10]` will return 10 frames evenly spaced between frame number 100 and 200 (shape `(10, 902, 912, 3)`).
- Note that by default, single-frame and slice indexing return 3D and 4D arrays, respectively. To consistently return 4D arrays, open the video with `remove_leading_singleton=False`. `vr[100]` will then return a `(1, 902, 912, 3)` array.
- We can also request specific ROIs and channels. For instance, `vr[100:200:10,100:400,800:850,1]` will return an array with shape `(10, 300, 50, 1)`.

