Description
-----------

DICOM datasets used to test the *pydicom* pixel data handler. New datasets
should be placed in the subfolder corresponding to the value of the
(0002,0010) *Transfer Syntax UID* and a new `key:value` pair added to the
`index.py` file using the following format:


```python
INDEX = {
    'filename' : {
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
```
