"""1.2.840.10008.1.2.1 - Little Endian Explicit VR"""

INDEX = {
    'CT_small.dcm' : {
        'TransferSyntaxUID' : ('UI', '1.2.840.10008.1.2.1'),
        'SamplesPerPixel' : ('US', 1),
        'PhotometricInterpretation' : ('CS', 'MONOCHROME2'),
        'PlanarConfiguration' : ('US', 0),
        'NumberOfFrames' : ('IS', '1'),
        'Rows' : ('US', 128),
        'Columns' : ('US', 128),
        'BitsAllocated' : ('US', 16),
        'BitsStored' : ('US', 16),
        'HighBit' : ('US', 15),
        'PixelRepresentation' : ('US', 1),
        'RescaleIntercept' : ('DS', '-1024'),
        'RescaleSlope' : ('DS', '1'),
    },
}
