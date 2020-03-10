

from ._printers import PRINTERS


class JPEG(object):
    """A representation of an ISO/IEC 10918-1 JPEG file.

    **Non-hierarchical**

    **DCT-based sequential**
    1: Baseline DCT
    2: Extended sequential DCT, Huffman, 8-bit
    3: Extended sequential DCT, arithmetic, 8-bit
    4: Extended sequential DCT, Huffman, 12-bit
    5: Extended sequential DCT, arithmetic, 12-bit

    **DCT-based progressive**
    6: Spectral selection, Huffman, 8-bit
    7: Spectral selection, arithmetic, 8-bit
    8: Spectral selection, Huffman, 12-bit
    9: Spectral seletion, arithmetic, 12-bit
    10: Full progression, Huffman, 8-bit
    11: Full progression, arithmetic, 8-bit
    12: Full progression, Huffman, 12-bit
    13: Full progression, arithmetic, 12-bit

    **Lossless**
    14: Lossless, Huffman, 2 to 16-bit
    15: Lossless, arithmetic, 2 to 16-bit

    **Hierarchical**

    **DCT-based sequential**
    16: Extended sequential DCT, Huffman, 8-bit
    17: Extended sequential DCT, arithmetic, 8-bit
    18: Extended sequential DCT, Huffman, 12-bit
    19: Extended sequential DCT, arithmetic, 12-bit

    **DCT-based progressive**
    20: Spectral selection, Huffman, 8-bit
    21: Spectral selection, arithmetic, 8-bit
    22: Spectral selection, Huffman, 12-bit
    23: Spectral selection, arithmetic, 12-bit
    24: Full progression, Huffman, 8-bit
    25: Full progression, arithmetic, 8-bit
    26: Full progression, Huffman, 12-bit
    27: Full progression, arithmetic, 12-bit

    **Lossless**
    28: Lossless, Huffman, 2 to 16-bit
    29: Lossless, arithmetic, 2 to 16-bit

    """
    def __init__(self, meta):
        """Initialise a new JPEG.

        Parameters
        ----------
        meta : dict
            The parsed JPEG image.
        """
        self.info = meta

    @property
    def columns(self):
        """Return the number of columns in the image as an int."""
        keys = self.get_keys('SOF')
        if keys:
            return self.info[keys[0]][2]['X']

        raise ValueError(
            "Unable to get the number of columns in the image as no SOFn "
            "marker was found"
        )

    def _decode(self):
        """Decode the JPEG image data in place.

        Raises
        ------
        NotImplementedError
            If the JPEG image data is of a type for which decoding is not
            supported.
        """
        if not self.is_decodable:
            raise NotImplementedError(
                "Unable to decode the JPEG image data as it's of a type "
                "for which decoding is not supported"
            )

        if self.is_process1:
            decoder = decode_baseline
        #elif self.is_process2:
        #    decoder = decode_extended_8
        #elif self.is_process4:
        #    decoder = decode_extended_12
        #elif self.is_process14:
        #    decoder = decode_lossless
        #elif self.is_process14_sv1:
        #    decoder = decode_lossless

        try:
            self._array = decoder(self)
            self._array_id = id(self._array)
        except Exception as exc:
            self._array = None
            self._array_id = None
            raise exc

    def get_keys(self, name):
        """Return a list of keys with marker containing `name`."""
        return [mm for mm in self._keys if name in mm[0]]

    @property
    def is_baseline(self):
        """Return True if the JPEG is baseline, False otherwise.

        Baseline process
        * DCT-based process
        * Each component of the source image has 8-bit samples
        * Sequential
        * Huffman coding has up to 2 AC and 2 DC tables
        * Decoders shall process scans with 1, 2, 3 and 4 components
        * Interleaved and non-interleaved scans

        Non-hierarchical baseline processes are:
            1
        Hierarchical baseline processes are:
            16, 17, 20, 21, 24, 25.
        """
        return 'SOF0' in self.markers

    @property
    def is_extended(self):
        """Return True if the JPEG is extended, False otherwise.

        Extended DCT-based processess
        * DCT-based process
        * Each component of the source image has 8- or 12-bit samples
        * Sequential or progressive
        * Huffman or arithmetic coding with up to 4 AC and 4 DC tables
        * Decoders shall process scans with 1, 2, 3 and 4 components
        * Interleaved and non-interleaved scans

        Non-hierarchical extended processes are:
            2, 4
        Hierarchical extended processes are:
            16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27
        """
        extended_markers = ('SOF1', 'SOF9', 'SOF5', 'SOF13')
        if [mm for mm in extended_markers if mm in self.markers]:
            return True

        return False

    @property
    def is_hierarchical(self):
        """Return True if the JPEG is hierarchical, False otherwise.

        Hierarchical processess
        * Multiple frames (non-differential and differential)
        * Uses extended DCT-based or lossless processes
        * Decoders shall process scans with 1, 2, 3 and 4 components
        * Interleaved and non-interleaved scans
        """
        return 'DHP' in self.markers

    @property
    def is_lossless(self):
        """Return True if the JPEG is lossless, False otherwise.

        Lossless processess
        * Predictive process (not DCT-based)
        * Each component of the source image P-bit samples (2 <= P <= 16)
        * Sequential
        * Huffman or arithmetic coding with up to 4 DC tables
        * Decoders shall process scans with 1, 2, 3 and 4 components
        * Interleaved and non-interleaved scans

        Non-hierarchical lossless processes are:
            14, 15
        Hierarchical lossless processes are:
            28, 29
        """
        lossless_markers = ('SOF3', 'SOF11') #, 'SOF7', 'SOF15')
        if [mm for mm in lossless_markers if mm in self.markers]:
            return True

        return False

    # TODO: Remove
    @property
    def is_process1(self):
        """Return True if the JPEG is Process 1, False otherwise."""
        if not self.is_hierarchical and self.is_baseline:
            return True

        return False

    # TODO: Remove
    @property
    def is_process2(self):
        """Return True if the JPEG is Process 2, False otherwise."""
        try:
            precision = self.precision
        except ValueError:
            return False

        if not self.is_hierarchical and self.is_extended and precision == 8:
            return True

        return False

    # TODO: Remove
    @property
    def is_process4(self):
        """Return True if the JPEG is Process 4, False otherwise."""
        try:
            precision = self.precision
        except ValueError:
            return False

        if not self.is_hierarchical and self.is_extended and precision == 12:
            return True

        return False

    # TODO: Remove
    @property
    def is_process14(self):
        """Return True if the JPEG is Process 14, False otherwise."""
        if 'SOF3' not in self.markers:
            return False

        if not self.is_hierarchical and self.is_lossless:
            return True

        raise False

    # TODO: Remove
    @property
    def is_process14_sv1(self):
        """Return True if the JPEG is Process 14 SV1, False otherwise.

        Returns
        -------
        bool
            True if JPEG is process 14, first-order prediction, selection
            value 1, False otherwise.
        """
        if 'SOF3' not in self.markers:
            return False

        if self.is_hierarchical or not self.is_lossless:
            return False

        if self.selection_value == 1:
            return True

        return False

    @property
    def is_sequential(self):
        return not self.is_hierarchical

    @property
    def is_spectral(self):
        pass

    @property
    def _keys(self):
        """Return a list of the info keys, ordered by offset."""
        return sorted(self.info.keys(), key=lambda x: x[1])

    @property
    def markers(self):
        """Return a list of the found JPEG markers, ordered by offset."""
        return [mm[0] for mm in self._keys]

    @property
    def precision(self):
        """Return the precision of the sample as an int."""
        keys = self.get_keys('SOF')
        if keys:
            return self.info[keys[0]][2]['P']

        raise ValueError(
            "Unable to get the sample precision of the image as no SOFn "
            "marker was found"
        )

    @property
    def process(self):
        """Return the process number as :class:`int`."""
        prec = self.precision
        process = None

        if self.is_baseline:
            # Baseline sequential DCT, 8-bit
            return 1

        if self.is_extended:
            # Extended sequential DCT
            if self.is_huffman and prec == 8:
                process = 2
            elif self.is_arithmetic and prec == 8:
                process = 3
            elif self.is_huffman and prec == 12:
                process = 4
            elif self.is_arithmetic and prec == 12:
                process = 5
        elif self.is_spectral:
            # Spectral selection only
            if self.is_huffman and prec == 8:
                process = 6
            elif self.is_arithmetic and prec == 8:
                process = 7
            elif self.is_huffman and prec == 12:
                process = 8
            elif self.is_arithmetic and prec == 12:
                process = 9
        elif self.full_progression:
            # Full progression
            if self.is_huffman and prec == 8:
                process = 10
            elif self.is_arithmetic and prec == 8:
                process = 11
            elif self.is_huffman and prec == 12:
                process = 12
            elif self.is_arithmetic and prec == 12:
                process = 13
        elif self.is_lossless:
            # Lossless
            if self.is_huffman and 2 <= prec <= 16:
                process = 14
            elif self.is_arithmetic and 2 <= prec <= 16:
                process = 15

        if process is None:
            raise ValueError("Unable to determine the JPEG process")

        if self.is_sequential:
            return process
        elif self.is_hierarchical:
            return process + 14

    @property
    def rows(self):
        """Return the number of rows in the image as an int."""
        keys = self.get_keys('SOF')
        if keys:
            return self.info[keys[0]][2]['Y']

        raise ValueError(
            "Unable to get the number of rows in the image as no SOFn "
            "marker was found"
        )

    @property
    def samples(self):
        """Return the number of components in the JPEG as an int."""
        keys = self.get_keys('SOF')
        if keys:
            return self.info[keys[0]][2]['Nf']

        raise ValueError(
            "Unable to get the number of components in the image as no SOFn "
            "marker was found"
        )

    @property
    def selection_value(self):
        """Return the JPEG lossless selection value.

        Returns
        -------
        int
            The selection value for the lossless prediction (0-7). 0 shall
            only be used for differential coding in the hierarchical mode of
            operation. 1-3 are one-dimensional predictors and 4-7 are two-
            dimensional predictors.

        Raises
        ------
        ValueError
            If the JPEG is not lossless.
        """
        if not self.is_lossless:
            raise ValueError(
                "Selection value is only available for lossless JPEG"
            )

        sos_markers = [mm for mm in self._keys if 'SOS' in mm]
        return self.info[sos_markers[0]][2]['Ss']

    def __str__(self):
        """"""
        ss = []
        for marker, offset in self.info:
            info = self.info[(marker, offset)]
            printer = PRINTERS[marker[:3]]
            ss.append(printer(marker, offset, info))

        return '\n'.join(ss)

    @property
    def uid(self):
        """Return the DICOM UID corresponding to the JPEG.

        Returns
        -------
        uid.UID
            The DICOM transfer syntax UID corresponding to the JPEG.

        Raises
        ------
        ValueError
            If the JPEG doesn't correspond to a DICOM transfer syntax.
        """
        if self.is_process1:
            return JPEGBaseline
        elif self.is_process2 or self.is_process4:
            return JPEGExtended
        elif self.is_process14_sv1:
            return JPEGLossless
        elif self.is_process14:
            return JPEGLosslessP14

        raise ValueError("JPEG doesn't correspond to a DICOM UID")
