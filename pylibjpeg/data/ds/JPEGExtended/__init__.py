"""1.2.840.10008.1.2.4.51 - JPEG Extended (Process 2 and 4)"""

INDEX = {
    'JPGExtended_1s_1f_16_12.dcm' : {
        'TransferSyntaxUID' : ('UI', '1.2.840.10008.1.2.4.51'),
        'SamplesPerPixel' : ('US', 1),
        'PhotometricInterpretation' : ('CS', 'MONOCHROME2'),
        'PlanarConfiguration' : ('US', 0),
        'NumberOfFrames' : ('IS', '1'),
        'Rows' : ('US', 1024),
        'Columns' : ('US', 256),
        'BitsAllocated' : ('US', 16),
        'BitsStored' : ('US', 12),
        'HighBit' : ('US', 11),
        'PixelRepresentation' : ('US', 0),
        # Optional DICOM keys
        'ImageComments' : ('LT', 'Fixed version of JPEG-lossy.dcm'),
    },
    'JPEG-lossy.dcm' : {
        'TransferSyntaxUID' : ('UI', '1.2.840.10008.1.2.4.51'),
        'SamplesPerPixel' : ('US', 1),
        'PhotometricInterpretation' : ('CS', 'MONOCHROME2'),
        'PlanarConfiguration' : ('US', 0),
        'NumberOfFrames' : ('IS', '1'),
        'Rows' : ('US', 1024),
        'Columns' : ('US', 256),
        'BitsAllocated' : ('US', 16),
        'BitsStored' : ('US', 12),
        'HighBit' : ('US', 11),
        'PixelRepresentation' : ('US', 0),
        # Optional DICOM keys
        'Status' : ('US', 0xC000),
        'ImageComments' : ('LT', 'SOS::Se invalid value 0 (should be 63)'),
    }
}
