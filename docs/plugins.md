
## Plugins

Plugins should register their entry points via the *entry_points* kwarg for [setuptools.setup()](https://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins) in their `setup.py` file.

### DICOM Pixel Data decoders
#### Decoder plugin registration

Plugins that decode DICOM *Pixel Data* should register their decoding functions using the corresponding *Transfer Syntax UID* as the entry point name. For example, if the `my_plugin` plugin supported *JPEG Baseline* (1.2.840.10008.1.2.4.50) with the decoding function `decode_jpeg_baseline()` and *JPEG-LS Lossless* (1.2.840.10008.1.2.4.80) with the decoding function `decode_jls_lossless()` then it should include the following in its `setup.py`:

```python
from setuptools import setup

setup(
    ...,
    entry_points={
        "pylibjpeg.pixel_data_decoders": [
            "1.2.840.10008.1.2.4.50 = my_plugin:decode_jpeg_baseline",
            "1.2.840.10008.1.2.4.80 = my_plugin:decode_jls_lossless",
        ],
    }
)
```

#### Decoder function signature

The pixel data decoding function will be passed one required parameter:

* *src*: a single encoded image frame as [bytes](https://docs.python.org/3/library/stdtypes.html#bytes)

And at least one of:
* *ds*: a *pydicom* [Dataset](https://pydicom.github.io/pydicom/stable/reference/generated/pydicom.dataset.Dataset.html) object containing the (0028,eeee) elements corresponding to the pixel data
* *kwargs*: a dict with at least the following keys:
    * `"transfer_syntax_uid": pydicom.uid.UID` - the *Transfer Syntax UID* of
      the encoded data.
    * `'rows': int` - the number of rows of pixels in the *src*.
    * `'columns': int` -  the number of columns of pixels in the
      *src*.
    * `'samples_per_pixel': int` - the number of samples used per
      pixel, e.g. `1` for grayscale images or `3` for RGB.
    * `'bits_allocated': int` - the number of bits used to contain
      each pixel in *src*, should be 8, 16, 32 or 64.
    * `'bits_stored': int` - the number of bits actually used by
      each pixel in *src*.
    * `'bits_stored': int` - the number of bits actually used by
      each pixel in *src*, e.g. 12-bit pixel data (range 0 to 4095) will be
      contained by 16-bits (range 0 to 65535).
    * `'pixel_representation': int` - the type of data in *src*,
      `0` for unsigned integers, `1` for 2's complement (signed)
      integers.
    * `'photometric_interpretation': str` - the color space
      of the encoded data, such as `'YBR_FULL'`.

Other decoder-specific optional keyword parameters may also be present.

The function should return the decoded pixel data as a one-dimensional numpy [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html) of little-endian ordered `'uint8'`, with the data ordered from left-to-right, top-to-bottom (i.e. the first byte corresponds to the upper left pixel and the last byte corresponds to the lower-right pixel) and a planar configuration that matches
the requirements of the transfer syntax:

```python
def my_pixel_data_decoder(
    src: bytes,
    ds: pydicom.dataset.Dataset | None = None,
    version: int = 1,
    **kwargs: Any,
) -> numpy.ndarray | bytearray:
    """Return the encoded *src* as an unshaped numpy ndarray of uint8.

    .. versionchanged: 1.3

        Added requirement to return little-endian ordered data by default.

    .. versionchanged: 2.0

        Added `version` keyword argument and support for returning :class:`bytearray`

    Parameters
    ----------
    src : bytes
        A single frame of the encoded *Pixel Data*.
    ds : pydicom.dataset.Dataset, optional
        A dataset containing the group ``0x0028`` elements corresponding to
        the *Pixel Data*. If not used then *kwargs* must be supplied.
    version : int, optional

      * If ``1`` (default) then either supplying either `ds` or `kwargs` is
        required and the return type is a :class:`~numpy.ndarray`
      * If ``2`` then `ds` will be ignored, `kwargs` is required and the return
        type is :class:`bytearray`
    kwargs : Dict[str, Any]
        A dict containing relevant image pixel module elements:

        * "rows": int - the number of rows of pixels in *src*, maximum 65535.
        * "columns": int - the number of columns of pixels in *src*, maximum
          65535.
        * "number_of_frames": int - the number of frames in *src*.
        * "samples_per_pixel": int - the number of samples per pixel in *src*,
          should be 1 or 3.
        * "bits_allocated": int - the number of bits used to contain each
          pixel, should be a multiple of 8.
        * "bits_stored": int - the number of bits actually used per pixel.
        * "pixel_representation": int - the type of data being decoded, 0 for
          unsigned, 1 for 2's complement (signed)
        * "photometric_interpretation": the color space of the *encoded* pixel
          data, such as "YBR_FULL".

        And optional keyword parameters for the decoder.

    Returns
    -------
    numpy.ndarray | bytearray
        Either a 1-dimensional ndarray of 'uint8' or a bytearray containing the
        little-endian ordered decoded pixel data, depending on the value of
        `version`.
    """
    # Decoding happens here
```

### JPEG decoders
#### Decoder plugin registration

Plugins that decoder JPEG data should register their decoding functions uding
the name of the plugin as the entry point name. For example, if the `my_plugin`
plugin supports decoding JPEG images via the `decode_jpeg()` function then
it should include the following in its `setup.py`:

```python
from setuptools import setup

setup(
    ...,
    entry_points={
        "pylibjpeg.jpeg_decoders": "my_plugin = my_plugin:decode_jpeg",
    }
)
```

Possible entry points for JPEG decoding are:

| JPEG Format | ISO/IEC Standard | Entry Point |
| --- | --- | --- |
| JPEG |  [10918](https://www.iso.org/standard/18902.html) | `"pylibjpeg.jpeg_decoders"` |
| JPEG XT | [18477](https://www.iso.org/standard/62552.html) | `"pylibjpeg.jpeg_xt_decoders"` |
| JPEG-LS | [14495](https://www.iso.org/standard/22397.html) | `"pylibjpeg.jpeg_ls_decoders"` |
| JPEG 2000 | [15444](https://www.iso.org/standard/78321.html) | `"pylibjpeg.jpeg_2000_decoders"` |


#### Decoder function signature

The JPEG decoding function will be passed the encoded JPEG *data* as [bytes](https://docs.python.org/3/library/stdtypes.html#bytes) and a
[dict](https://docs.python.org/3/library/stdtypes.html#dict) containing keyword arguments passed to the function. The function should return the decoded image data as a numpy [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html) with a dtype and shape matching the image format and dimensions:

```python
def my_jpeg_decoder(src, **kwargs):
    """Return the encoded JPEG `src` as an numpy ndarray.

    Parameters
    ----------
    src : bytes
        The encoded JPEG data.
    kwargs
        Keyword arguments passed to the decoder.

    Returns
    -------
    numpy.ndarray
        An ndarray containing the decoded pixel data.
    """
    # Decoding happens here
```

### DICOM Pixel Data encoders
#### Encoder plugin registration

Plugins that encode DICOM *Pixel Data* should register their encoding functions using the corresponding *Transfer Syntax UID* as the entry point name. For example, if the `my_plugin` plugin supported encoding *RLE Lossless* (1.2.840.10008.1.2.5) with the encoding function `encode_rle_lossless()` then it should include the following in its `setup.py`:

```python
from setuptools import setup

setup(
    ...,
    entry_points={
        "pylibjpeg.pixel_data_encoders": [
            "1.2.840.10008.1.2.5 = my_plugin:encode_rle_lossless",
        ],
    }
)
```

#### Encoder function signature

The pixel data encoding function will be passed two required parameters:

* *src*: a single unencoded image frame as `bytes`, with the data ordered from
  left-to-right, top-to-bottom (i.e. the first byte corresponds to the upper
  left pixel and the last byte corresponds to the lower-right pixel) and a
  planar configuration of 0 if more than 1 sample per pixel is used
* *kwargs*: a dict with at least the following keys

    * `'transfer_syntax_uid': pydicom.uid.UID` - the intended
      *Transfer Syntax UID* of the encoded data.
    * `'byteorder': str` - the byte ordering used by *src*, `'<'`
      for little-endian (the default), `'>'` for big-endian.
    * `'rows': int` - the number of rows of pixels in the *src*.
    * `'columns': int` -  the number of columns of pixels in the
      *src*.
    * `'samples_per_pixel': int` - the number of samples used per
      pixel, e.g. `1` for grayscale images or `3` for RGB.
    * `'number_of_frames': int` - the number of image frames
      contained in *src*.
    * `'bits_allocated': int` - the number of bits used to contain
      each pixel in *src*, should be 8, 16, 32 or 64.
    * `'bits_stored': int` - the number of bits actually used by
      each pixel in *src*, e.g. 12-bit pixel data (range 0 to 4095) will be
      contained by 16-bits (range 0 to 65535).
    * `'pixel_representation': int` - the type of data in *src*,
      `0` for unsigned integers, `1` for 2's complement (signed)
      integers.
    * `'photometric_interpretation: str` - the intended colorspace
      of the encoded data, such as `'YBR'`.

The function should return the encoded pixel data as `bytes`.

```python
def my_pixel_data_encoder(src: bytes, **kwargs: Any) -> bytes:
    """Return `src` as encoded bytes.

    Parameters
    ----------
    src : bytes
        A single frame of the encoded *Pixel Data*.
    **kwargs
        Required and optional parameters for the encoder.

    Returns
    -------
    bytes
        The encoded image data.
    """
    # Encoding happens here
```
