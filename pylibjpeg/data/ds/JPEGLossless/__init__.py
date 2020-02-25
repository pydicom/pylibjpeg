"""1.2.840.10008.1.2.4.57 - JPEG Lossless, Non-Hierarchical (Process 14)"""

INDEX = {
    'JPEGLossless_1s_1f_u_16_12.dcm' : {
        'TransferSyntaxUID' : ('UI', '1.2.840.10008.1.2.4.57'),
        'SamplesPerPixel' : ('US', 1),
        'PhotometricInterpretation' : ('CS', 'MONOCHROME2'),
        'PlanarConfiguration' : ('US', 0),  # Use 0 if not present
        'NumberOfFrames' : ('IS', '1'),  # Use '1' if not present
        'Rows' : ('US', 1024),
        'Columns' : ('US', 1024),
        'BitsAllocated' : ('US', 16),
        'BitsStored' : ('US', 12),
        'HighBit' : ('US', 11),
        'PixelRepresentation' : ('US', 0),
        'WindowCenter' : ('DS', '1000'),
        'WindowWidth' : ('DS', '2000'),
        'RescaleIntercept' : ('DS', '0.000061'),
        'RescaleSlope' : ('DS', '3.774114'),
    },
}
