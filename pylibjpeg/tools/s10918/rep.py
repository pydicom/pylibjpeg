from typing import Any, cast, Dict, Tuple, List

from ._printers import PRINTERS


class JPEG:
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

    def __init__(self, meta: Dict[Tuple[str, int], Any]) -> None:
        """Initialise a new JPEG.

        Parameters
        ----------
        meta : dict
            The parsed JPEG image.
        """
        self.info = meta

    @property
    def columns(self) -> int:
        """Return the number of columns in the image as an int."""
        keys = self.get_keys("SOF")
        if keys:
            return cast(int, self.info[keys[0]][2]["X"])

        raise ValueError(
            "Unable to get the number of columns in the image as no SOFn "
            "marker was found"
        )

    def get_keys(self, name: str) -> List[Any]:
        """Return a list of keys with marker containing `name`."""
        return [mm for mm in self._keys if name in mm[0]]

    @property
    def is_baseline(self) -> bool:
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
        return "SOF0" in self.markers

    @property
    def is_extended(self) -> bool:
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
        extended_markers = ("SOF1", "SOF9", "SOF5", "SOF13")
        if [mm for mm in extended_markers if mm in self.markers]:
            return True

        return False

    @property
    def is_hierarchical(self) -> bool:
        """Return True if the JPEG is hierarchical, False otherwise.

        Hierarchical processess
        * Multiple frames (non-differential and differential)
        * Uses extended DCT-based or lossless processes
        * Decoders shall process scans with 1, 2, 3 and 4 components
        * Interleaved and non-interleaved scans
        """
        return "DHP" in self.markers

    @property
    def is_lossless(self) -> bool:
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
        lossless_markers = ("SOF3", "SOF11")  # , 'SOF7', 'SOF15')
        if [mm for mm in lossless_markers if mm in self.markers]:
            return True

        return False

    @property
    def is_sequential(self) -> bool:
        return not self.is_hierarchical

    @property
    def _keys(self) -> List[Tuple[str, int]]:
        """Return a list of the info keys, ordered by offset."""
        return sorted(self.info.keys(), key=lambda x: x[1])

    @property
    def markers(self) -> List[str]:
        """Return a list of the found JPEG markers, ordered by offset."""
        return [mm[0] for mm in self._keys]

    @property
    def precision(self) -> int:
        """Return the precision of the sample as an int."""
        keys = self.get_keys("SOF")
        if keys:
            return cast(int, self.info[keys[0]][2]["P"])

        raise ValueError(
            "Unable to get the sample precision of the image as no SOFn "
            "marker was found"
        )

    @property
    def rows(self) -> int:
        """Return the number of rows in the image as an int."""
        keys = self.get_keys("SOF")
        if keys:
            return cast(int, self.info[keys[0]][2]["Y"])

        raise ValueError(
            "Unable to get the number of rows in the image as no SOFn "
            "marker was found"
        )

    @property
    def samples(self) -> int:
        """Return the number of components in the JPEG as an int."""
        keys = self.get_keys("SOF")
        if keys:
            return cast(int, self.info[keys[0]][2]["Nf"])

        raise ValueError(
            "Unable to get the number of components in the image as no SOFn "
            "marker was found"
        )

    @property
    def selection_value(self) -> int:
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
            raise ValueError("Selection value is only available for lossless JPEG")

        sos_markers = [mm for mm in self._keys if "SOS" in mm]
        return cast(int, self.info[sos_markers[0]][2]["Ss"])

    def __str__(self) -> str:
        """"""
        ss = []
        for marker, offset in self.info:
            info = self.info[(marker, offset)]
            printer = PRINTERS[marker[:3]]
            ss.append(printer(marker, offset, info))

        return "\n".join(ss)
