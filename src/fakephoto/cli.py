#!/usr/bin/env python3
"""
FakePhoto.ai CLI - Command line interface for AI detection
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_parser() -> argparse.ArgumentParser:
    """Set up argument parser"""
    parser = argparse.ArgumentParser(
        prog='fakephoto',
        description='FakePhoto.ai - Multi-Model AI Detection Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze image.jpg
  %(prog)s analyze video.mp4 --models openai,gemini
  %(prog)s batch ./images/ --output results.json
  %(prog)s config --show
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze a single image or video'
    )
    analyze_parser.add_argument(
        'file',
        type=str,
        help='Path to image or video file'
    )
    analyze_parser.add_argument(
        '--models',
        type=str,
        default='all',
        help='Comma-separated list of models to use (openai,gemini,anthropic,all)'
    )
    analyze_parser.add_argument(
        '--threshold',
        type=float,
        default=0.7,
        help='Confidence threshold for AI detection (0.0-1.0)'
    )
    analyze_parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='Output file for results (JSON)'
    )
    analyze_parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )
    
    # Batch command
    batch_parser = subparsers.add_parser(
        'batch',
        help='Batch process multiple files'
    )
    batch_parser.add_argument(
        'directory',
        type=str,
        help='Directory containing images/videos'
    )
    batch_parser.add_argument(
        '--models',
        type=str,
        default='all',
        help='Comma-separated list of models to use'
    )
    batch_parser.add_argument(
        '--threshold',
        type=float,
        default=0.7,
        help='Confidence threshold'
    )
    batch_parser.add_argument(
        '--output',
        '-o',
        type=str,
        default='results.json',
        help='Output JSON file'
    )
    batch_parser.add_argument(
        '--recursive',
        '-r',
        action='store_true',
        help='Process subdirectories recursively'
    )
    
    # Config command
    config_parser = subparsers.add_parser(
        'config',
        help='Manage configuration and API keys'
    )
    config_parser.add_argument(
        '--show',
        action='store_true',
        help='Show current configuration'
    )
    config_parser.add_argument(
        '--set-openai',
        type=str,
        metavar='KEY',
        help='Set OpenAI API key'
    )
    config_parser.add_argument(
        '--set-google',
        type=str,
        metavar='KEY',
        help='Set Google API key'
    )
    config_parser.add_argument(
        '--set-anthropic',
        type=str,
        metavar='KEY',
        help='Set Anthropic API key'
    )
    
    return parser


def load_env_file():
    """Load environment variables from .env file"""
    env_path = Path('.env')
    if env_path.exists():
        from dotenv import load_dotenv
        load_dotenv()


def get_api_keys(args) -> dict:
    """Get API keys from environment or config"""
    return {
        'openai': os.getenv('OPENAI_API_KEY'),
        'google': os.getenv('GOOGLE_API_KEY'),
        'anthropic': os.getenv('ANTHROPIC_API_KEY')
    }


def filter_models(keys: dict, model_arg: str) -> dict:
    """Filter API keys based on model selection"""
    if model_arg == 'all':
        return {k: v for k, v in keys.items() if v}
    
    selected = model_arg.lower().split(',')
    filtered = {}
    
    model_map = {
        'openai': 'openai',
        'gpt': 'openai',
        'gpt4': 'openai',
        'google': 'google',
        'gemini': 'google',
        'anthropic': 'anthropic',
        'claude': 'anthropic'
    }
    
    for sel in selected:
        sel = sel.strip()
        key_name = model_map.get(sel)
        if key_name and keys.get(key_name):
            filtered[key_name] = keys[key_name]
    
    return filtered


def analyze_file(file_path: Path, detector, args) -> dict:
    """Analyze a single file"""
    logger.info(f"Analyzing {file_path}...")
    
    result = detector.analyze(file_path)
    
    # Format result as dict
    output = {
        'filename': result.filename,
        'is_ai_generated': result.is_ai_generated,
        'confidence_score': round(result.confidence_score, 2),
        'consensus': result.consensus,
        'model_scores': result.model_scores,
        'indicators': result.indicators,
        'recommendations': result.recommendations
    }
    
    return output


def print_result(result: dict, verbose: bool = False):
    """Print analysis result"""
    print("\n" + "=" * 60)
    print(f"📄 File: {result['filename']}")
    print("=" * 60)
    
    # Verdict
    if result['is_ai_generated']:
        print(f"🤖 Verdict: LIKELY AI-GENERATED")
    else:
        print(f"✅ Verdict: LIKELY AUTHENTIC")
    
    print(f"📊 Confidence Score: {result['confidence_score']:.1f}%")
    print(f"🤝 Model Consensus: {result['consensus'].upper()}")
    
    # Model scores
    print("\n📈 Model Scores:")
    for model, scores in result['model_scores'].items():
        prob = scores['ai_probability'] * 100
        conf = scores['confidence'] * 100
        print(f"   • {model.capitalize():12} AI: {prob:5.1f}% | Confidence: {conf:5.1f}%")
    
    # Indicators
    if result['indicators']:
        print("\n⚠️  Indicators Found:")
        for indicator in result['indicators']:
            print(f"   • {indicator}")
    
    # Recommendations
    if result['recommendations']:
        print("\n💡 Recommendations:")
        for rec in result['recommendations']:
            print(f"   • {rec}")
    
    print("=" * 60 + "\n")


def cmd_analyze(args):
    """Handle analyze command"""
    from fakephoto import MultiModelDetector
    
    file_path = Path(args.file)
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return 1
    
    # Get and filter API keys
    keys = get_api_keys(args)
    filtered = filter_models(keys, args.models)
    
    if not filtered:
        logger.error("No valid API keys found for selected models")
        logger.error("Set API keys via environment variables:")
        logger.error("  OPENAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY")
        return 1
    
    # Initialize detector
    try:
        detector = MultiModelDetector(
            openai_api_key=filtered.get('openai'),
            google_api_key=filtered.get('google'),
            anthropic_api_key=filtered.get('anthropic'),
            confidence_threshold=args.threshold
        )
    except Exception as e:
        logger.error(f"Failed to initialize detector: {e}")
        return 1
    
    # Analyze
    try:
        result = analyze_file(file_path, detector, args)
        print_result(result, args.verbose)
        
        # Save to file if requested
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Results saved to {output_path}")
        
        return 0
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1


def cmd_batch(args):
    """Handle batch command"""
    from fakephoto import MultiModelDetector
    
    directory = Path(args.directory)
    if not directory.exists():
        logger.error(f"Directory not found: {directory}")
        return 1
    
    if not directory.is_dir():
        logger.error(f"Not a directory: {directory}")
        return 1
    
    # Get and filter API keys
    keys = get_api_keys(args)
    filtered = filter_models(keys, args.models)
    
    if not filtered:
        logger.error("No valid API keys found")
        return 1
    
    # Initialize detector
    try:
        detector = MultiModelDetector(
            openai_api_key=filtered.get('openai'),
            google_api_key=filtered.get('google'),
            anthropic_api_key=filtered.get('anthropic'),
            confidence_threshold=args.threshold
        )
    except Exception as e:
        logger.error(f"Failed to initialize detector: {e}")
        return 1
    
    # Collect files
    if args.recursive:
        files = list(directory.rglob('*'))
    else:
        files = list(directory.iterdir())
    
    # Filter supported files
    supported_exts = {
        '.jpg', '.jpeg', '.png', '.webp', '.heic',
        '.mp4', '.avi', '.mov', '.mkv', '.webm'
    }
    files = [f for f in files if f.suffix.lower() in supported_exts]
    
    if not files:
        logger.error(f"No supported files found in {directory}")
        return 1
    
    logger.info(f"Found {len(files)} files to analyze")
    
    # Process files
    results = []
    for i, file_path in enumerate(files, 1):
        logger.info(f"[{i}/{len(files)}] Processing {file_path.name}...")
        try:
            result = analyze_file(file_path, detector, args)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")
            results.append({
                'filename': file_path.name,
                'error': str(e)
            })
    
    # Save results
    output_path = Path(args.output)
    with open(output_path, 'w') as f:
        json.dump({
            'total_files': len(files),
            'successful': len([r for r in results if 'error' not in r]),
            'failed': len([r for r in results if 'error' in r]),
            'results': results
        }, f, indent=2)
    
    logger.info(f"Batch complete! Results saved to {output_path}")
    return 0


def cmd_config(args):
    """Handle config command"""
    env_path = Path('.env')
    
    if args.show:
        print("\nCurrent Configuration:\n")
        keys = get_api_keys(args)
        
        print("API Keys:")
        for name, value in keys.items():
            if value:
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"  {name.capitalize():12} {masked}")
            else:
                print(f"  {name.capitalize():12} Not set")
        print()
        return 0
    
    # Update keys
    env_vars = {}
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    env_vars[key] = val
    
    if args.set_openai:
        env_vars['OPENAI_API_KEY'] = args.set_openai
        print("✓ OpenAI API key updated")
    
    if args.set_google:
        env_vars['GOOGLE_API_KEY'] = args.set_google
        print("✓ Google API key updated")
    
    if args.set_anthropic:
        env_vars['ANTHROPIC_API_KEY'] = args.set_anthropic
        print("✓ Anthropic API key updated")
    
    # Save .env file
    with open(env_path, 'w') as f:
        for key, val in env_vars.items():
            f.write(f"{key}={val}\n")
    
    print(f"\nConfiguration saved to {env_path}")
    return 0


def main():
    """Main entry point"""
    # Load .env file
    load_env_file()
    
    # Parse arguments
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to command handler
    commands = {
        'analyze': cmd_analyze,
        'batch': cmd_batch,
        'config': cmd_config
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
