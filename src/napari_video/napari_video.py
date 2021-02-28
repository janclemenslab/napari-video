import numpy as np
from videoreader import VideoReader
from napari_plugin_engine import napari_hook_implementation
from dask import delayed


class VideoReaderNP(VideoReader):
    """VideoReader posing as numpy array."""

    def __init__(self, filename: str, remove_leading_singleton: bool = True):
        super().__init__(filename)
        self.remove_leading_singleton = remove_leading_singleton

    def __getitem__(self, index):
        # numpy-like slice imaging into arbitrary dims of the video
        # ugly.hacky but works
        frames = None
        if isinstance(index, int):  # single frame
            ret, frames = self.read(index)
        elif isinstance(index, slice):  # slice of frames
            frames = np.stack([self[ii] for ii in range(*index.indices(len(self)))])
        elif isinstance(index, range):  # range of frames
            frames = np.stack([self[ii] for ii in index])
        elif isinstance(index, tuple):  # unpack tuple of indices
            if isinstance(index[0], slice):
                indices = range(*index[0].indices(len(self)))
            elif isinstance(index[0], (np.integer, int)):
                indices = int(index[0])
            else:
                indices = None

            if indices is not None:
                frames = self[indices]

                # index into pixels and channels
                for cnt, idx in enumerate(index[1:]):
                    if isinstance(idx, slice):
                        ix = range(*idx.indices(self.shape[cnt+1]))
                    elif isinstance(idx, int):
                        ix = range(idx-1, idx)
                    else:
                        continue

                    if frames.ndim==4: # ugly indexing from the back (-1,-2 etc)
                        cnt = cnt+1
                    frames = np.take(frames, ix, axis=cnt)

        if self.remove_leading_singleton and frames is not None:
            if frames.shape[0] == 1:
                frames = frames[0]
        return frames

    @property
    def dtype(self):
        return np.uint8

    @property
    def shape(self):
        return (self.number_of_frames, *self.frame_shape)

    @property
    def ndim(self):
        return len(self.shape)+1

    @property
    def size(self):
        return np.product(self.shape)

    def min(self):
        return 0

    def max(self):
        return 255


def video_file_reader(path):
    array = VideoReaderNP(path, remove_leading_singleton=True)
    return [(array, {'name': path}, 'image')]


@napari_hook_implementation
def napari_get_reader(path):
    # remember, path can be a list, so we check it's type first...
    if isinstance(path, str) and any([path.endswith(ext) for ext in [".mp4", ".mov", ".avi"]]):
        # If we recognize the format, we return the actual reader function
        return video_file_reader
    # otherwise we return None.
    return None
