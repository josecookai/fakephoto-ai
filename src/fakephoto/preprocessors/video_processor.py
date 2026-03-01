"""
Video Processor - Frame extraction and video handling
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
import logging
import tempfile

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Process video files for AI detection analysis"""
    
    SUPPORTED_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}
    
    def __init__(
        self,
        target_size: Tuple[int, int] = (1024, 1024),
        num_frames: int = 5,
        temp_dir: Optional[Path] = None
    ):
        """
        Initialize video processor
        
        Args:
            target_size: Target size for extracted frames (width, height)
            num_frames: Number of frames to extract from video
            temp_dir: Directory for temporary frame storage
        """
        self.target_size = target_size
        self.num_frames = num_frames
        self.temp_dir = temp_dir or Path(tempfile.gettempdir()) / "fakephoto_frames"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def is_supported(self, file_path: Path) -> bool:
        """Check if file format is supported"""
        return file_path.suffix.lower() in self.SUPPORTED_FORMATS
    
    def extract_frames(
        self,
        video_path: Path,
        num_frames: Optional[int] = None,
        method: str = "uniform"
    ) -> List[Path]:
        """
        Extract frames from video file
        
        Args:
            video_path: Path to video file
            num_frames: Number of frames to extract (defaults to self.num_frames)
            method: Frame selection method - "uniform" or "keyframe"
            
        Returns:
            List of paths to extracted frame images
        """
        if not self.is_supported(video_path):
            raise ValueError(f"Unsupported video format: {video_path.suffix}")
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        num_frames = num_frames or self.num_frames
        
        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video: {video_path}")
        
        try:
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            logger.info(
                f"Processing video: {total_frames} frames, "
                f"{fps:.2f} fps, {duration:.2f}s duration"
            )
            
            if method == "uniform":
                frame_indices = self._uniform_sampling(total_frames, num_frames)
            elif method == "keyframe":
                frame_indices = self._keyframe_sampling(cap, num_frames)
            else:
                raise ValueError(f"Unknown sampling method: {method}")
            
            extracted_frames = []
            for idx, frame_num in enumerate(frame_indices):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                
                if not ret or frame is None:
                    logger.warning(f"Failed to extract frame {frame_num}")
                    continue
                
                # Process frame
                processed_frame = self._process_frame(frame)
                
                # Save frame
                frame_path = self._save_frame(
                    processed_frame,
                    video_path.stem,
                    idx
                )
                extracted_frames.append(frame_path)
                
                logger.debug(f"Extracted frame {idx + 1}/{len(frame_indices)}")
            
            if not extracted_frames:
                raise RuntimeError("No frames could be extracted from video")
            
            logger.info(f"Successfully extracted {len(extracted_frames)} frames")
            return extracted_frames
            
        finally:
            cap.release()
    
    def _uniform_sampling(self, total_frames: int, num_frames: int) -> List[int]:
        """Uniformly sample frame indices"""
        if total_frames <= num_frames:
            return list(range(total_frames))
        
        # Exclude first and last 5% to avoid intro/outro
        start_offset = int(total_frames * 0.05)
        end_offset = int(total_frames * 0.95)
        usable_frames = end_offset - start_offset
        
        if usable_frames < num_frames:
            start_offset = 0
            end_offset = total_frames
            usable_frames = total_frames
        
        step = usable_frames / num_frames
        indices = [
            int(start_offset + step * i + step / 2)
            for i in range(num_frames)
        ]
        
        return indices
    
    def _keyframe_sampling(
        self,
        cap: cv2.VideoCapture,
        num_frames: int
    ) -> List[int]:
        """Sample frames based on scene changes"""
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames <= num_frames:
            return list(range(total_frames))
        
        # Calculate frame differences to find scene changes
        prev_frame = None
        frame_scores = []
        
        sample_interval = max(1, total_frames // (num_frames * 10))
        
        for frame_num in range(0, total_frames, sample_interval):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            
            if not ret:
                continue
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (320, 240))  # Resize for faster processing
            
            if prev_frame is not None:
                diff = cv2.absdiff(prev_frame, gray)
                score = np.mean(diff)
                frame_scores.append((frame_num, score))
            
            prev_frame = gray
        
        # Sort by score and select top frames
        frame_scores.sort(key=lambda x: x[1], reverse=True)
        top_frames = sorted([x[0] for x in frame_scores[:num_frames]])
        
        # If not enough keyframes, fill with uniform sampling
        if len(top_frames) < num_frames:
            remaining = num_frames - len(top_frames)
            existing_set = set(top_frames)
            uniform = self._uniform_sampling(total_frames, num_frames * 2)
            for idx in uniform:
                if idx not in existing_set:
                    top_frames.append(idx)
                    if len(top_frames) >= num_frames:
                        break
            top_frames.sort()
        
        return top_frames[:num_frames]
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process frame for analysis"""
        # Convert BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Resize while maintaining aspect ratio
        h, w = frame.shape[:2]
        target_w, target_h = self.target_size
        
        # Calculate scaling factor
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize
        frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
        
        # Pad to target size if needed
        if new_w < target_w or new_h < target_h:
            pad_top = (target_h - new_h) // 2
            pad_bottom = target_h - new_h - pad_top
            pad_left = (target_w - new_w) // 2
            pad_right = target_w - new_w - pad_left
            
            frame = cv2.copyMakeBorder(
                frame,
                pad_top, pad_bottom, pad_left, pad_right,
                cv2.BORDER_CONSTANT,
                value=[0, 0, 0]
            )
        
        return frame
    
    def _save_frame(
        self,
        frame: np.ndarray,
        video_name: str,
        index: int
    ) -> Path:
        """Save processed frame to disk"""
        frame_path = self.temp_dir / f"{video_name}_frame_{index:04d}.jpg"
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imwrite(str(frame_path), frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
        return frame_path
    
    def get_video_info(self, video_path: Path) -> dict:
        """Get video metadata"""
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video: {video_path}")
        
        try:
            info = {
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "fps": cap.get(cv2.CAP_PROP_FPS),
                "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                "duration_seconds": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / 
                                   cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0,
                "codec": self._get_codec_name(cap)
            }
            return info
        finally:
            cap.release()
    
    def _get_codec_name(self, cap: cv2.VideoCapture) -> str:
        """Get video codec name"""
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
        return codec.strip()
    
    def cleanup(self):
        """Clean up temporary frame files"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            logger.info(f"Cleaned up temporary frames in {self.temp_dir}")


def extract_frames(
    video_path: Union[str, Path],
    num_frames: int = 5,
    **kwargs
) -> List[Path]:
    """
    Convenience function to extract frames from video
    
    Args:
        video_path: Path to video file
        num_frames: Number of frames to extract
        **kwargs: Additional arguments for VideoProcessor
        
    Returns:
        List of frame paths
    """
    processor = VideoProcessor(num_frames=num_frames, **kwargs)
    return processor.extract_frames(Path(video_path), num_frames=num_frames)
