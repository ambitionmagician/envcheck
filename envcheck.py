#!/usr/bin/env python3
"""
envcheck.py - Compare environment file templates with actual .env files.

Usage:
    envcheck.py .env.example .env
    envcheck.py --dir /path/to/project
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple


def parse_env_file(filepath: Path) -> Tuple[Dict[str, str], List[str]]:
    """
    Parse an environment file and return a dict of key-value pairs and a list of duplicate keys.
    
    Handles:
    - KEY=VALUE lines
    - Optional 'export' prefix
    - Quoted values (single and double quotes)
    - Comments (lines starting with #)
    - Blank lines
    """
    result: Dict[str, str] = {}
    duplicates: List[str] = []
    seen_keys: Set[str] = set()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip blank lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Handle export prefix
                if line.startswith('export '):
                    line = line[7:]
                
                # Parse KEY=VALUE
                if '=' not in line:
                    continue
                
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip()
                
                # Handle quoted values
                if value:
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]
                
                # Check for duplicates
                if key in seen_keys:
                    if key not in duplicates:
                        duplicates.append(key)
                else:
                    seen_keys.add(key)
                    result[key] = value
    
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied reading: {filepath}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        sys.exit(1)
    
    return result, duplicates


def compare_env_files(template_path: Path, actual_path: Path) -> Dict:
    """
    Compare two environment files and return a report.
    """
    template_data, template_dups = parse_env_file(template_path)
    actual_data, actual_dups = parse_env_file(actual_path)
    
    template_keys = set(template_data.keys())
    actual_keys = set(actual_data.keys())
    
    # Missing keys: in template but not in actual
    missing_keys = sorted(template_keys - actual_keys)
    
    # Extra keys: in actual but not in template
    extra_keys = sorted(actual_keys - template_keys)
    
    # Empty values: key present in actual but value is empty
    empty_keys = sorted([k for k in actual_keys if not actual_data[k]])
    
    # All duplicates
    all_duplicates = sorted(set(template_dups + actual_dups))
    
    return {
        'missing_keys': missing_keys,
        'extra_keys': extra_keys,
        'empty_keys': empty_keys,
        'duplicate_keys': all_duplicates
    }


def compare_dir(directory: Path) -> Dict:
    """
    Compare .env.example and .env in the specified directory.
    """
    template_path = directory / '.env.example'
    actual_path = directory / '.env'
    
    return compare_env_files(template_path, actual_path)


def main():
    parser = argparse.ArgumentParser(
        description='Compare environment file templates with actual .env files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  envcheck.py .env.example .env
  envcheck.py --dir /path/to/project
  envcheck.py --json .env.example .env
'''
    )
    
    parser.add_argument(
        'files',
        nargs='*',
        help='Two positional files: template first, actual second'
    )
    
    parser.add_argument(
        '--dir',
        dest='directory',
        type=Path,
        help='Compare .env.example and .env inside the specified directory'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.directory and args.files:
        print("Error: Cannot use both positional files and --dir", file=sys.stderr)
        sys.exit(1)
    
    if not args.directory and len(args.files) != 2:
        parser.error('Either provide exactly two positional files or use --dir')
    
    # Perform comparison
    try:
        if args.directory:
            if not args.directory.is_dir():
                print(f"Error: Not a directory: {args.directory}", file=sys.stderr)
                sys.exit(1)
            report = compare_dir(args.directory)
        else:
            template_path = Path(args.files[0])
            actual_path = Path(args.files[1])
            report = compare_env_files(template_path, actual_path)
    except Exception as e:
        print(f"Error during comparison: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Output results
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if not any(report.values()):
            print("OK: no missing, extra, empty, or duplicate keys.")
        if report['missing_keys']:
            print("Missing keys:")
            for key in report['missing_keys']:
                print(f"  {key}")

        if report['extra_keys']:
            print("Extra keys:")
            for key in report['extra_keys']:
                print(f"  {key}")

        if report['empty_keys']:
            print("Empty values:")
            for key in report['empty_keys']:
                print(f"  {key}")

        if report['duplicate_keys']:
            print("Duplicate keys:")
            for key in report['duplicate_keys']:
                print(f"  {key}")
    
    # Determine exit code
    if report['missing_keys'] or report['empty_keys']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
