"""1.2.840.10008.1.2.4.70 - JPEG Lossless, Non-Hierarchical, First-Order
Prediction (Process 14 [Selection Value 1])
"""

INDEX = {
    'JPEG-LL.dcm' : {
        'TransferSyntaxUID' : ('UI', '1.2.840.10008.1.2.4.70'),
        'SamplesPerPixel' : ('US', 1),
        'PhotometricInterpretation' : ('CS', 'MONOCHROME2'),
        'PlanarConfiguration' : ('US', 0),
        'NumberOfFrames' : ('IS', '1'),
        'Rows' : ('US', 1024),
        'Columns' : ('US', 256),
        'BitsAllocated' : ('US', 16),
        'BitsStored' : ('US', 16),
        'HighBit' : ('US', 15),
        'PixelRepresentation' : ('US', 1),
    },
    'JPGLosslessP14SV1_1s_1f_8b.dcm' : {
        'TransferSyntaxUID' : ('UI', '1.2.840.10008.1.2.4.70'),
        'SamplesPerPixel' : ('US', 1),
        'PhotometricInterpretation' : ('CS', 'MONOCHROME2'),
        'PlanarConfiguration' : ('US', 0),
        'NumberOfFrames' : ('IS', '1'),
        'Rows' : ('US', 768),
        'Columns' : ('US', 1024),
        'BitsAllocated' : ('US', 8),
        'BitsStored' : ('US', 8),
        'HighBit' : ('US', 7),
        'PixelRepresentation' : ('US', 1),
        'WindowCenter' : ('DS', '127'),
        'WindowWidth' : ('DS', '254'),
    },
    'SC_rgb_jpeg_gdcm.dcm' : {
        'TransferSyntaxUID' : ('UI', '1.2.840.10008.1.2.4.70'),
        'SamplesPerPixel' : ('US', 3),
        'PhotometricInterpretation' : ('CS', 'RGB'),
        'PlanarConfiguration' : ('US', 0),
        'NumberOfFrames' : ('IS', '1'),
        'Rows' : ('US', 100),
        'Columns' : ('US', 100),
        'BitsAllocated' : ('US', 8),
        'BitsStored' : ('US', 8),
        'HighBit' : ('US', 7),
        'PixelRepresentation' : ('US', 0),
    },
}
