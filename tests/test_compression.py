import pytest

from src.compression.compressor import GzipCompressor


class TestGzipCompressor:

    def test_compress(self, temp_backup_dir):
        # Create a test file
        test_file = temp_backup_dir / 'test.txt'
        test_file.write_text('This is test data ' * 1000)

        compressor = GzipCompressor()
        compressed_file = compressor.compress(test_file)

        assert compressed_file.exists()
        assert compressed_file.suffix == '.gz'
        assert not test_file.exists()
        assert compressed_file.stat().st_size < 5000

    def test_decompress(self, temp_backup_dir):

        # Create a compressed file
        test_file = temp_backup_dir / 'test.txt'
        test_data = b'This is test data ' * 1000
        test_file.write_bytes(test_data)

        compressor = GzipCompressor()
        compressed_file = compressor.compress(test_file)

        decompressed_file = compressor.decompress(compressed_file)

        assert decompressed_file.exists()
        assert decompressed_file.read_bytes() == test_data

    def test_compress_invalid_file(self, temp_backup_dir):
        compressor = GzipCompressor()
        invalid_file = temp_backup_dir / 'nonexistent.txt'

        with pytest.raises(Exception):
            compressor.compress(invalid_file)

    def test_decompress_non_gz_file(self, temp_backup_dir):
        test_file = temp_backup_dir / 'test.txt'
        test_file.write_text('test data')

        compressor = GzipCompressor()
        with pytest.raises(ValueError):
            compressor.decompress(test_file)

    def test_compression_levels(self, temp_backup_dir):
        """Test different compression levels"""
        test_file = temp_backup_dir / 'test.txt'
        test_file.write_text('This is test data ' * 1000)

        # Test different compression levels
        for level in [1, 6, 9]:
            test_copy = temp_backup_dir / f'test_level_{level}.txt'
            test_copy.write_text('This is test data ' * 1000)

            compressor = GzipCompressor(compression_level=level)
            compressed = compressor.compress(test_copy)

            assert compressed.exists()
            assert compressed.suffix == '.gz'
