import sys
import os
import subprocess
import glob
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def find_ncmdump():
    """Find ncmdump.exe in common locations"""
    search_paths = [
        os.path.join(os.path.dirname(sys.argv[0]), 'ncmdump.exe'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ncmdump.exe'),
        r'H:\ncmdump.exe',
        r'H:\tools\ncmdump.exe',
        r'C:\tools\ncmdump.exe',
    ]
    for path in search_paths:
        if os.path.exists(path):
            return path
    # Check PATH
    for p in os.environ.get('PATH', '').split(os.pathsep):
        candidate = os.path.join(p, 'ncmdump.exe')
        if os.path.exists(candidate):
            return candidate
    return None

def convert_folder(folder_path, recursive=True, wait=False):
    """Convert all NCM files in a folder"""
    folder_path = os.path.abspath(folder_path)
    
    # Find ncmdump
    ncmdump = find_ncmdump()
    if not ncmdump:
        print("ERROR: ncmdump.exe not found!")
        print("Please put ncmdump.exe in the same folder as this program, or in H:\\")
        if wait:
            try: input("\nPress Enter to exit...")
            except: pass
        return
    
    print(f"Using ncmdump: {ncmdump}")
    print(f"Source folder: {folder_path}")
    print("-" * 50)
    
    # Find NCM files
    if recursive:
        pattern = os.path.join(folder_path, '**', '*.ncm')
        ncm_files = glob.glob(pattern, recursive=True)
    else:
        pattern = os.path.join(folder_path, '*.ncm')
        ncm_files = glob.glob(pattern)
    
    if not ncm_files:
        print("No .ncm files found!")
        if wait:
            try: input("\nPress Enter to exit...")
            except: pass
        return
    
    print(f"Found {len(ncm_files)} NCM file(s)\n")
    
    # Convert each file
    success = 0
    failed = 0
    
    for i, ncm_path in enumerate(ncm_files, 1):
        ncm_name = os.path.basename(ncm_path)
        print(f"[{i}/{len(ncm_files)}] Processing: {ncm_name}")
        
        try:
            result = subprocess.run(
                [ncmdump, '-d', os.path.dirname(ncm_path)],
                capture_output=True,
                timeout=120,
                encoding='utf-8',
                errors='replace'
            )
            if result.returncode == 0:
                print(f"  [OK] Converted")
                success += 1
            else:
                print(f"  [FAIL] Return code: {result.returncode}")
                failed += 1
        except subprocess.TimeoutExpired:
            print(f"  [FAIL] Timeout")
            failed += 1
        except Exception as e:
            print(f"  [FAIL] {e}")
            failed += 1
    
    print("-" * 50)
    print(f"Done! Success: {success}, Failed: {failed}")
    print(f"Converted files are saved in the same folder as the original NCM files.")
    
    if wait:
        try: input("\nPress Enter to exit...")
        except: pass

def main():
    has_args = len(sys.argv) >= 2
    
    if not has_args:
        print("NCM Batch Converter")
        print("=" * 50)
        print("Usage:")
        print("  Drag a folder onto this program to convert all NCM files")
        print("  Or run from command line: NCMConverter.exe <folder_path>")
        print("=" * 50)
        try:
            folder = input("\nPlease enter folder path: ").strip()
        except EOFError:
            folder = None
        if not folder:
            return
    else:
        folder = sys.argv[1]
    
    if not os.path.exists(folder):
        print(f"ERROR: Folder not found: {folder}")
        try: input("\nPress Enter to exit...")
        except: pass
        return
    
    if not os.path.isdir(folder):
        print(f"ERROR: Not a folder: {folder}")
        try: input("\nPress Enter to exit...")
        except: pass
        return
    
    convert_folder(folder, wait=True)

if __name__ == '__main__':
    main()
