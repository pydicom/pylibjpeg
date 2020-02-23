"""
DATA = {
    'filename' : {
        'TransferSyntaxUID' : ('UI', ),
        'SamplesPerPixel' : ('US', ),
        'PhotometricInterpretation' : ('CS', ),
        'PlanarConfiguration' : ('US', ),
        'NumberOfFrames' : ('IS', ),
        'Rows' : ('US', ),
        'Columns' : ('US', ),
        'BitsAllocated' : ('US', ),
        'BitsStored' : ('US', ),
        'HighBit' : ('US', ),
        'PixelRepresentation' : ('US', ),
        ...
        # Optional DICOM keys
        'WindowCenter' : ('DS', ),
        'WindowWidth' : ('DS', ),
        'RescaleIntercept' : ('DS', ),
        'RescaleSlope' : ('DS', ),
        'Status' : ('US', 0xC000),  # 0xC000 if bad, 0x0000 if good
        'ImageComments' : ('LT', ),  
    },
}
"""
