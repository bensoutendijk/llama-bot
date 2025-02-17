#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from huggingface_hub import HfApi, hf_hub_download
from tqdm import tqdm


def human_readable_size(size_in_bytes: int) -> str:
    """Convert bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f} PB"

def get_model_files(repo_id: str) -> List[Tuple[str, int]]:
    """Get list of downloadable files and their sizes from a HuggingFace repository."""
    try:
        api = HfApi()
        files = api.list_repo_files(repo_id)
        
        # Get file info including sizes
        file_info = []
        for file in files:
            if not file.startswith('.'):
                try:
                    info = api.repo_info(
                        repo_id=repo_id,
                        revision=None,
                        files_metadata=True
                    )
                    # Find the file in the metadata
                    for file_meta in info.siblings:
                        if file_meta.rfilename == file:
                            file_info.append((file, file_meta.size))
                            break
                    else:
                        # If size not found, append with None
                        file_info.append((file, None))
                except:
                    file_info.append((file, None))
        
        return file_info
    except Exception as e:
        print(f"Error accessing repository {repo_id}: {str(e)}")
        sys.exit(1)

def prompt_file_selection(files: List[Tuple[str, int]]) -> str:
    """Prompt user to select which file to download."""
    print("\nAvailable files:")
    for i, (file, size) in enumerate(files, 1):
        size_str = human_readable_size(size) if size is not None else "Size unknown"
        print(f"{i}. {file} ({size_str})")
    
    while True:
        try:
            choice = int(input("\nEnter the number of the file you want to download: "))
            if 1 <= choice <= len(files):
                return files[choice - 1][0]
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def download_file(repo_id: str, filename: str, output_dir: str) -> None:
    """Download the selected file from HuggingFace."""
    try:
        output_path = Path(output_dir) / repo_id.split('/')[-1]
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\nDownloading {filename} to {output_path}")
        
        file_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=output_path,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        
        print(f"\nSuccessfully downloaded to: {file_path}")
        
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Download LLM files from HuggingFace")
    parser.add_argument("repo_id", help="HuggingFace repository ID (e.g., meta-llama/Llama-2-7b)")
    parser.add_argument("--output", "-o", default="./llm-models",
                      help="Output directory (default: ./llm-models)")
    
    args = parser.parse_args()
    
    # Get list of files
    print(f"Fetching file list from {args.repo_id}...")
    files = get_model_files(args.repo_id)
    
    if not files:
        print("No files found in repository.")
        sys.exit(1)
    
    # Let user select file
    selected_file = prompt_file_selection(files)
    
    # Download the file
    download_file(args.repo_id, selected_file, args.output)

if __name__ == "__main__":
    main()