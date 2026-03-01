"""
Image Processor - Image normalization and preprocessing
"""

from PIL import Image, ImageOps, ImageEnhance
import numpy as np
from pathlib import Path
from typing import Tuple, Optional, Union, List
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Process and normalize images for AI detection analysis"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.heic', '.tiff', '.bmp'}
    
    def __init__(
        self,
        target_size: Tuple[int, int] = (1024, 1024),
        quality: int = 95,
        normalize_exif: bool = True
    ):
        """
        Initialize image processor
        
        Args:
            target_size: Target size for output images (width, height)
            quality: JPEG quality for saved images (1-100)
            normalize_exif: Whether to normalize EXIF orientation
        """
        self.target_size = target_size
        self.quality = quality
        self.normalize_exif = normalize_exif
    
    def is_supported(self, file_path: Path) -> bool:
        """Check if file format is supported"""
        return file_path.suffix.lower() in self.SUPPORTED_FORMATS
    
    def process(
        self,
        image_path: Path,
        output_path: Optional[Path] = None,
        **options
    ) -> Path:
        """
        Process an image file
        
        Args:
            image_path: Path to input image
            output_path: Path for output image (optional)
            **options: Additional processing options
            
        Returns:
            Path to processed image
        """
        if not self.is_supported(image_path):
            raise ValueError(f"Unsupported image format: {image_path.suffix}")
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Load image
        image = self.load_image(image_path)
        
        # Process
        image = self.normalize(image, **options)
        
        # Save
        if output_path is None:
            output_path = image_path.parent / f"{image_path.stem}_processed.jpg"
        
        self.save_image(image, output_path)
        logger.info(f"Processed image saved to {output_path}")
        
        return output_path
    
    def load_image(self, image_path: Path) -> Image.Image:
        """Load image from file"""
        try:
            image = Image.open(image_path)
            
            # Handle HEIC format
            if image_path.suffix.lower() == '.heic':
                try:
                    import pillow_heif
                    pillow_heif.register_heif_opener()
                    image = Image.open(image_path)
                except ImportError:
                    raise ImportError(
                        "HEIC support requires pillow-heif. "
                        "Install: pip install pillow-heif"
                    )
            
            return image
        except Exception as e:
            raise RuntimeError(f"Failed to load image: {e}")
    
    def normalize(
        self,
        image: Image.Image,
        auto_orient: bool = True,
        enhance_contrast: bool = False,
        normalize_colors: bool = True
    ) -> Image.Image:
        """
        Normalize image for analysis
        
        Args:
            image: PIL Image
            auto_orient: Correct orientation based on EXIF
            enhance_contrast: Apply contrast enhancement
            normalize_colors: Normalize color range
            
        Returns:
            Normalized PIL Image
        """
        # Convert to RGB if necessary
        if image.mode not in ('RGB', 'RGBA', 'L'):
            image = image.convert('RGB')
        elif image.mode == 'RGBA':
            # Convert RGBA to RGB with white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode == 'L':
            image = image.convert('RGB')
        
        # Auto-orient based on EXIF
        if auto_orient and self.normalize_exif:
            image = ImageOps.exif_transpose(image)
        
        # Resize maintaining aspect ratio
        image = self._resize_maintain_aspect(image, self.target_size)
        
        # Optional enhancements
        if enhance_contrast:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
        
        if normalize_colors:
            image = self._normalize_colors(image)
        
        return image
    
    def _resize_maintain_aspect(
        self,
        image: Image.Image,
        target_size: Tuple[int, int]
    ) -> Image.Image:
        """Resize image maintaining aspect ratio with padding"""
        target_w, target_h = target_size
        img_w, img_h = image.size
        
        # Calculate scaling factor
        scale = min(target_w / img_w, target_h / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        
        # Resize
        image = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Create new image with padding if needed
        if new_w != target_w or new_h != target_h:
            new_image = Image.new('RGB', target_size, (128, 128, 128))
            paste_x = (target_w - new_w) // 2
            paste_y = (target_h - new_h) // 2
            new_image.paste(image, (paste_x, paste_y))
            image = new_image
        
        return image
    
    def _normalize_colors(self, image: Image.Image) -> Image.Image:
        """Normalize color distribution"""
        # Convert to numpy for processing
        img_array = np.array(image).astype(np.float32)
        
        # Normalize to 0-255 range per channel
        for i in range(3):
            channel = img_array[:, :, i]
            min_val = channel.min()
            max_val = channel.max()
            if max_val > min_val:
                img_array[:, :, i] = 255 * (channel - min_val) / (max_val - min_val)
        
        # Clip and convert back
        img_array = np.clip(img_array, 0, 255).astype(np.uint8)
        return Image.fromarray(img_array)
    
    def save_image(self, image: Image.Image, output_path: Path):
        """Save image to file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.suffix.lower() in ('.jpg', '.jpeg'):
            image.save(
                output_path,
                'JPEG',
                quality=self.quality,
                optimize=True
            )
        else:
            image.save(output_path)
    
    def get_image_info(self, image_path: Path) -> dict:
        """Get image metadata"""
        image = self.load_image(image_path)
        
        info = {
            "width": image.width,
            "height": image.height,
            "mode": image.mode,
            "format": image.format,
        }
        
        # Extract EXIF if available
        if hasattr(image, '_getexif') and image._getexif():
            exif = image._getexif()
            exif_data = {}
            
            # Common EXIF tags
            tag_names = {
                271: 'make',
                272: 'model',
                306: 'datetime',
                33432: 'copyright',
                34853: 'gps_info',
                36867: 'datetime_original',
            }
            
            for tag_id, name in tag_names.items():
                if tag_id in exif:
                    exif_data[name] = str(exif[tag_id])
            
            info['exif'] = exif_data
        
        return info
    
    def create_thumbnail(
        self,
        image_path: Path,
        thumbnail_size: Tuple[int, int] = (256, 256),
        output_path: Optional[Path] = None
    ) -> Path:
        """Create a thumbnail"""
        image = self.load_image(image_path)
        image.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
        
        if output_path is None:
            output_path = image_path.parent / f"{image_path.stem}_thumb.jpg"
        
        self.save_image(image, output_path)
        return output_path
    
    def batch_process(
        self,
        input_dir: Path,
        output_dir: Path,
        **options
    ) -> List[Path]:
        """
        Process all images in a directory
        
        Args:
            input_dir: Directory containing images
            output_dir: Directory for processed images
            **options: Processing options
            
        Returns:
            List of output paths
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        output_paths = []
        
        for file_path in input_dir.iterdir():
            if self.is_supported(file_path):
                try:
                    output_path = output_dir / f"{file_path.stem}_processed.jpg"
                    result = self.process(file_path, output_path, **options)
                    output_paths.append(result)
                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")
        
        return output_paths


# Convenience function
def normalize_image(
    image_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    target_size: Tuple[int, int] = (1024, 1024)
) -> Path:
    """
    Quick image normalization function
    
    Args:
        image_path: Path to input image
        output_path: Path for output image
        target_size: Target size (width, height)
        
    Returns:
        Path to processed image
    """
    processor = ImageProcessor(target_size=target_size)
    return processor.process(
        Path(image_path),
        Path(output_path) if output_path else None
    )


# Add missing import
from typing import Union
