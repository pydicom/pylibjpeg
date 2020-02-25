Description
-----------

DICOM datasets used to test the *pydicom* pixel data handler. New datasets must
have a ``.dcm`` extension and should be placed in the subfolder corresponding
to the value of the (0002,0010) *Transfer Syntax UID* and a new ``key:value``
pair added to the ``__init__.py`` file using the following format:

.. code-block:: python

    INDEX = {
        'filename' : {
            # 'Keyword' : ('VR', value),
            'TransferSyntaxUID' : ('UI', ),
            'SamplesPerPixel' : ('US', ),
            'PhotometricInterpretation' : ('CS', ),
            'PlanarConfiguration' : ('US', ),  # Use 0 if not present
            'NumberOfFrames' : ('IS', ),  # Use '1' if not present
            'Rows' : ('US', ),
            'Columns' : ('US', ),
            'BitsAllocated' : ('US', ),
            'BitsStored' : ('US', ),
            'HighBit' : ('US', ),
            'PixelRepresentation' : ('US', ),
            # Conditional items - should be included if present
            'WindowCenter' : ('DS', ),
            'WindowWidth' : ('DS', ),
            'RescaleIntercept' : ('DS', ),
            'RescaleSlope' : ('DS', ),
            # Optional items
            'Status' : ('US', 0xC000),  # If the image data is bad
            'ImageComments' : ('LT', ),  # Details of the image
            'RetrieveURI' : ('UR', ),  # URL of source (if applicable)
        },
    }


+--------------------------------------------------------------------------+----------------------+
| Transfer Syntax                                                          | Subfolder            |
+------------------------+-------------------------------------------------+----------------------+
| UID                    | Name                                            |                      |
+========================+=================================================+======================+
| 1.2.840.10008.1.2.1    | Explicit VR Little Endian                       | LittleEndianExplicit |
+------------------------+-------------------------------------------------+----------------------+
| 1.2.840.10008.1.2.4.50 | JPEG Baseline (Process 1)                       | JPEGBaseline         |
+------------------------+-------------------------------------------------+----------------------+
| 1.2.840.10008.1.2.4.51 | JPEG Extended (Process 2 and 4)                 | JPEGExtended         |
+------------------------+-------------------------------------------------+----------------------+
| 1.2.840.10008.1.2.4.57 | JPEG Lossless, Non-Hierarchical (Process 14)    | JPEGLossless         |
+------------------------+-------------------------------------------------+----------------------+
| 1.2.840.10008.1.2.4.70 | JPEG Lossless, Non-Hierarchical, First-Order    | JPEGLosslessSV1      |
|                        | Prediction (Process 14 [Selection Value 1])     |                      |
+------------------------+-------------------------------------------------+----------------------+
| 1.2.840.10008.1.2.4.80 | JPEG-LS Lossless Image Compression              | JPEGLSLossless       |
+------------------------+-------------------------------------------------+----------------------+
| 1.2.840.10008.1.2.4.81 | JPEG-LS Lossy (Near-Lossless) Image Compression | JPEGLS               |
+------------------------+-------------------------------------------------+----------------------+
| 1.2.840.10008.1.2.4.90 | JPEG 2000 Image Compression (Lossless Only)     | JPEG2000Lossless     |
+------------------------+-------------------------------------------------+----------------------+
| 1.2.840.10008.1.2.4.91 | JPEG 2000 Image Compression                     | JPEG2000             |
+------------------------+-------------------------------------------------+----------------------+
