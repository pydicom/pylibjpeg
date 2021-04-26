
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

The pixel data decoding function will be passed two required parameters:

* *src*: a single encoded image frame as [bytes](https://docs.python.org/3/library/stdtypes.html#bytes)
* *ds*: a *pydicom* [Dataset](https://pydicom.github.io/pydicom/stable/reference/generated/pydicom.dataset.Dataset.html) object containing the (0028,eeee) elements corresponding to the pixel data

The function should return the decoded pixel data as a one-dimensional numpy [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html) of little-endian ordered `'uint8'`:

```python
def my_pixel_data_decoder(
    src: bytes, ds: pydicom.dataset.Dataset, **kwargs
) -> numpy.ndarray:
    """Return the encoded `src` as an unshaped numpy ndarray of uint8.

    .. versionchanged:: 1.3

        Added `kwargs`, added requirement to return little-endian ordered
        data by default.

    Parameters
    ----------
    src : bytes
        A single frame of the encoded *Pixel Data*.
    ds : pydicom.dataset.Dataset
        A dataset containing the group ``0x0028`` elements corresponding to
        the *Pixel Data*.
    kwargs
        Optional keyword parameters for the decoder.

    Returns
    -------
    numpy.ndarray
        A 1-dimensional ndarray of 'uint8' containing the little-endian ordered decoded pixel data.
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

* *src*: a single unencoded image frame as `bytes`
* *ds*: a *pydicom* `Dataset` object containing the (0028,eeee) elements corresponding to the image frame

And one optional parameter:

* *byteorder*: a `str` indicating the byte ordering used by the image frame, required when the number of bits per pixel is greater than 8.

The function should return the encoded pixel data as `bytes`.

```python
def my_pixel_data_encoder(
    src: bytes,
    ds: pydicom.dataset.Dataset,
    byteorder: Optional[str] = None,
    **kwargs
) -> bytes:
    """Return `src` as encoded bytes.

    Parameters
    ----------
    src : bytes
        A single frame of the encoded *Pixel Data*.
    ds : pydicom.dataset.Dataset
        A dataset containing the group ``0x0028`` elements corresponding to
        the *Pixel Data*.
    byteorder : str, optional
        Required when the number of bits per pixel is greater than 8, this
        should be ``'<'`` if `src` uses little-endian byte ordering, ``'>'``
        otherwise.
    **kwargs
        Optional keyword parameters for the encoder.

    Returns
    -------
    bytes
        The encoded image data.
    """
    # Encoding happens here
```
