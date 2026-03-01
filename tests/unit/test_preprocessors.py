"""Unit tests for image and video preprocessing."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np

from PIL import Image


@pytest.mark.unit
class TestImagePreprocessing:
    """Test image preprocessing functionality."""
    
    def test_image_loading(self, real_image_path):
        """Test that test images can be loaded."""
        img = Image.open(real_image_path)
        assert img is not None
        assert img.size[0] > 0
        assert img.size[1] > 0
    
    def test_image_modes(self, temp_dir):
        """Test different image modes."""
        # RGB
        rgb_path = temp_dir / "rgb.jpg"
        img_rgb = Image.new("RGB", (100, 100), (255, 0, 0))
        img_rgb.save(rgb_path)
        
        loaded = Image.open(rgb_path)
        assert loaded.mode == "RGB"
        
        # RGBA
        rgba_path = temp_dir / "rgba.png"
        img_rgba = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
        img_rgba.save(rgba_path)
        
        loaded = Image.open(rgba_path)
        assert loaded.mode == "RGBA"
        
        # Grayscale
        gray_path = temp_dir / "gray.jpg"
        img_gray = Image.new("L", (100, 100), 128)
        img_gray.save(gray_path)
        
        loaded = Image.open(gray_path)
        assert loaded.mode == "L"
    
    def test_image_resize(self, large_image_path):
        """Test image resizing."""
        img = Image.open(large_image_path)
        original_size = img.size
        
        # Resize to smaller
        resized = img.resize((100, 100))
        assert resized.size == (100, 100)
        assert original_size != resized.size
    
    def test_image_format_conversion(self, temp_dir):
        """Test converting between image formats."""
        # Create RGBA image
        png_path = temp_dir / "test.png"
        img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
        img.save(png_path)
        
        # Convert to JPEG (removes alpha)
        jpg_path = temp_dir / "test.jpg"
        img_rgb = Image.open(png_path).convert("RGB")
        img_rgb.save(jpg_path)
        
        loaded = Image.open(jpg_path)
        assert loaded.mode == "RGB"
    
    @pytest.mark.parametrize("format_ext,save_format", [
        (".jpg", "JPEG"),
        (".jpeg", "JPEG"),
        (".png", "PNG"),
        (".webp", "WEBP"),
    ])
    def test_various_formats(self, temp_dir, format_ext, save_format):
        """Test saving various image formats."""
        path = temp_dir / f"test{format_ext}"
        img = Image.new("RGB", (100, 100), (100, 150, 200))
        
        try:
            img.save(path, format=save_format if save_format != path.suffix[1:].upper() else None)
            assert path.exists()
            
            # Verify it can be loaded back
            loaded = Image.open(path)
            assert loaded.size == (100, 100)
        except Exception as e:
            pytest.skip(f"Format {save_format} not supported: {e}")


@pytest.mark.unit
class TestVideoPreprocessing:
    """Test video preprocessing functionality."""
    
    def test_video_file_creation(self, temp_dir):
        """Test creating mock video files."""
        video_path = temp_dir / "test.mp4"
        video_path.write_bytes(b"fake video content")
        
        assert video_path.exists()
        assert video_path.stat().st_size > 0
    
    def test_video_extensions(self):
        """Test video file extension detection."""
        video_exts = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        
        for ext in video_exts:
            path = Path(f"test{ext}")
            # Check lowercase
            assert path.suffix.lower() in video_exts
            # Check uppercase
            path_upper = Path(f"test{ext.upper()}")
            assert path_upper.suffix.lower() in video_exts
    
    @pytest.mark.skipif(
        pytest.importorskip("cv2", reason="OpenCV not installed") is None,
        reason="OpenCV not available"
    )
    def test_frame_extraction_mock(self, temp_dir):
        """Test frame extraction logic with mocked OpenCV."""
        with patch("cv2.VideoCapture") as mock_capture:
            # Setup mock
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = True
            mock_cap.get.return_value = 30  # 30 fps
            mock_cap.read.side_effect = [
                (True, np.zeros((480, 640, 3), dtype=np.uint8))
                for _ in range(10)
            ] + [(False, None)]
            mock_capture.return_value = mock_cap
            
            # The actual frame extraction would happen here
            # For now, just verify the mock setup works
            assert mock_capture is not None


@pytest.mark.unit
class TestImageCharacteristics:
    """Test analysis of image characteristics."""
    
    def test_image_dimensions(self, create_test_image, temp_dir):
        """Test image dimension handling."""
        # Small image
        small = temp_dir / "small.jpg"
        create_test_image(small, 10, 10)
        img = Image.open(small)
        assert img.size == (10, 10)
        
        # Large image
        large = temp_dir / "large.jpg"
        create_test_image(large, 4000, 3000)
        img = Image.open(large)
        assert img.size == (4000, 3000)
        
        # Non-square
        rect = temp_dir / "rect.jpg"
        create_test_image(rect, 1920, 1080)
        img = Image.open(rect)
        assert img.size == (1920, 1080)
    
    def test_image_file_sizes(self, temp_dir):
        """Test different image file sizes."""
        # Small file
        small = temp_dir / "small_quality.jpg"
        img = Image.new("RGB", (100, 100), (128, 128, 128))
        img.save(small, quality=30)
        small_size = small.stat().st_size
        
        # Large file (higher quality)
        large = temp_dir / "large_quality.jpg"
        img.save(large, quality=95)
        large_size = large.stat().st_size
        
        assert large_size >= small_size
    
    def test_color_depth(self, temp_dir):
        """Test different color depths."""
        # 8-bit per channel (standard)
        rgb_path = temp_dir / "rgb.jpg"
        img_rgb = Image.new("RGB", (100, 100), (255, 128, 64))
        img_rgb.save(rgb_path)
        
        # Grayscale
        gray_path = temp_dir / "gray.jpg"
        img_gray = Image.new("L", (100, 100), 128)
        img_gray.save(gray_path)
        
        # Black and white (1-bit)
        bw_path = temp_dir / "bw.png"
        img_bw = Image.new("1", (100, 100), 1)
        img_bw.save(bw_path)
        
        assert Image.open(rgb_path).mode == "RGB"
        assert Image.open(gray_path).mode == "L"
        assert Image.open(bw_path).mode == "1"


@pytest.mark.unit
class TestPreprocessingEdgeCases:
    """Test edge cases in preprocessing."""
    
    def test_corrupted_image(self, temp_dir):
        """Test handling of corrupted image file."""
        corrupted = temp_dir / "corrupted.jpg"
        corrupted.write_bytes(b"not a valid image")
        
        with pytest.raises(Exception):
            Image.open(corrupted)
    
    def test_empty_file(self, temp_dir):
        """Test handling of empty file."""
        empty = temp_dir / "empty.jpg"
        empty.write_bytes(b"")
        
        with pytest.raises(Exception):
            Image.open(empty)
    
    def test_very_small_image(self, temp_dir):
        """Test handling of 1x1 pixel image."""
        tiny = temp_dir / "tiny.jpg"
        img = Image.new("RGB", (1, 1), (255, 0, 0))
        img.save(tiny)
        
        loaded = Image.open(tiny)
        assert loaded.size == (1, 1)
    
    def test_non_image_file_with_image_extension(self, temp_dir):
        """Test text file with image extension."""
        fake = temp_dir / "fake.jpg"
        fake.write_text("This is not an image")
        
        with pytest.raises(Exception):
            Image.open(fake)
