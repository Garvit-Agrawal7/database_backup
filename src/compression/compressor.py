import gzip
import shutil
from pathlib import Path
import logging


class GzipCompressor:
    """Gzip Compressor for backup databases (Compression value can be changed; 9=best, 1=fastest (Default set to 6))"""

    def __init__(self, compression_level: int = 6):
        self.logger = logging.getLogger(__name__)
        self.compression_level = compression_level

    def compress(self, input_file: Path) -> Path:
        """
        Compresses files using Gzip compression algorithm
        :arg input_file: Takes the input file to compress
        """

        if input_file.is_dir():
            # MongoDB does the compression for the files (using mongodump --gzip)
            self.logger.info(f"MongoDB directory {input_file.name}")
            return input_file

        output_file = Path(str(input_file) + '.gz') # For everything other than MongoDB

        try:
            with open(input_file, 'rb') as f_in:
                with gzip.open(output_file, 'wb', 
                             compresslevel=self.compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)

            original_size = input_file.stat().st_size
            self.logging_compression(input_file, original_size, output_file)

            input_file.unlink()
            return output_file

        except Exception as e:
            self.logger.error(f"Compression failed: {e}")
            if output_file.exists():
                output_file.unlink()
            raise

    def decompress(self, input_file: Path) -> Path:
        """
        Decompress files previously compressed via Gzip algorithm
        :arg input_file: Takes the input file to compress
        """
        if not input_file.suffix == '.gz':
            raise ValueError("File must have .gz extension")

        output_file = Path(str(input_file)[:-3])

        try:
            with gzip.open(input_file, 'rb') as f_in:
                with open(output_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            self.logger.info(f"Decompressed {input_file.name}")
            return output_file

        except Exception as e:
            self.logger.error(f"Decompression failed: {e}")
            if output_file.exists():
                output_file.unlink()
            raise

    def logging_compression(self, input_file: Path, original_size: int, output_file: Path):
        """Logs Compression data (Size reduction, reduction ratio, etc.)"""
        compressed_size = output_file.stat().st_size
        ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0

        self.logger.info(
            f"Compressed {input_file.name}: "
            f"{original_size / (1024 ** 2):.2f}MB -> "
            f"{compressed_size / (1024 ** 2):.2f}MB "
            f"({ratio:.1f}% reduction)"
        )
