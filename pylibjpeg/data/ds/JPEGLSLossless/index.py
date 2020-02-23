"""1.2.840.10008.1.2.4.80 - JPEG-LS Lossless"""

INDEX = {
    'emri_small_jpeg_ls_lossless.dcm' : {
        'TransferSyntaxUID' : ('UI', '1.2.840.10008.1.2.4.80'),
        'SamplesPerPixel' : ('US', 1),
        'PhotometricInterpretation' : ('CS', 'MONOCHROME2'),
        'PlanarConfiguration' : ('US', 0),
        'NumberOfFrames' : ('IS', '10'),
        'Rows' : ('US', 64),
        'Columns' : ('US', 64),
        'BitsAllocated' : ('US', 16),
        'BitsStored' : ('US', 12),
        'HighBit' : ('US', 11),
        'PixelRepresentation' : ('US', 0),
    },
    'MR_small_jpeg_ls_lossless.dcm' : {
        'TransferSyntaxUID' : ('UI', '1.2.840.10008.1.2.4.80'),
        'SamplesPerPixel' : ('US', 1),
        'PhotometricInterpretation' : ('CS', 'MONOCHROME2'),
        'PlanarConfiguration' : ('US', 0),
        'NumberOfFrames' : ('IS', '1'),
        'Rows' : ('US', 64),
        'Columns' : ('US', 64),
        'BitsAllocated' : ('US', 16),
        'BitsStored' : ('US', 16),
        'HighBit' : ('US', 15),
        'PixelRepresentation' : ('US', 0),
        'WindowCenter' : ('DS', '600'),
        'WindowWidth' : ('DS', '1600'),
    },
}
