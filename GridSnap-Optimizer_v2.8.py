#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GridSnap-Optimizer v2.8 - Batch image resizer & optimizer
https://github.com/khoianha10/GridSnap-Optimizer

Purpose: Standardize image sizes to Retina steps, optimize storage,
preserve quality for both landscape and portrait images.

Requirements:
- Python 3.6+
- Install: pip install pillow pillow-heif pillow-avif-plugin

If HEIC/AVIF libraries are missing, program still works with JPG/PNG/WEBP.
"""

import os
import sys
import traceback
import shutil
from PIL import Image, ImageFilter, ImageOps
import warnings

# Optional HEIC/AVIF support
try:
    import pillow_heif
    import pillow_avif
    pillow_heif.register_heif_opener()
    HEIC_AVIF_SUPPORT = True
except ImportError:
    HEIC_AVIF_SUPPORT = False
    warnings.warn("HEIC/AVIF support not installed. Install: pip install pillow-heif pillow-avif-plugin")

# ================= CONFIGURATION =================
CHAT_LUONG = 85
THU_MUC_ANH = "Anh_Goc"
THU_MUC_XUAT = "Anh_Da_Nen"
# Optimal Grid-Snap Steps (Longest Side) - Apple Retina standards
MOC_CHuan = [1170, 1284, 1536, 1728, 1920, 2048, 2304, 2560, 2732, 3024, 3200]
# =================================================

def format_size(size_bytes):
    """Accurate file size formatting up to TB"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def ten_file_an_toan(path_output, base_name, ext=".jpg"):
    """
    Ensures no overwriting by adding suffixes _1, _2...
    Args:
        path_output: output directory
        base_name: filename without extension
        ext: extension (including dot, default .jpg)
    """
    target_path = os.path.join(path_output, base_name + ext)
    if not os.path.exists(target_path):
        return target_path
    
    counter = 1
    while True:
        new_path = os.path.join(path_output, f"{base_name}_{counter}{ext}")
        if not os.path.exists(new_path):
            return new_path
        counter += 1

def tim_moc_phu_hop(w, h):
    """Find optimal grid step - only downscale, never upscale"""
    max_dim = max(w, h)
    if max_dim <= 960: 
        return w, h, "Original (Small)"
    
    # Find nearest smaller step
    target_size = None
    for moc in sorted(MOC_CHuan, reverse=True):
        if max_dim > moc:
            # If close to step (<5% difference), keep original
            if (max_dim - moc) / moc < 0.05:
                return w, h, f"Original (Near {moc}px)"
            target_size = moc
            break
    
    if not target_size:
        return w, h, "Original (Below smallest step)"
    
    # Calculate new dimensions preserving aspect ratio
    ratio = target_size / float(max_dim)
    new_w = int(w * ratio)
    new_h = int(h * ratio)
    return new_w, new_h, f"Grid-Snap {target_size}px"

def xu_ly_anh():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path_input = os.path.join(base_dir, THU_MUC_ANH)
    path_output = os.path.join(base_dir, THU_MUC_XUAT)

    # Check write permissions
    try:
        os.makedirs(path_output, exist_ok=True)
        test_file = os.path.join(path_output, '.write_test')
        with open(test_file, 'w') as f: 
            f.write('test')
        os.remove(test_file)
    except (PermissionError, OSError) as e:
        print(f"\n[!] ERROR: Cannot write to directory {path_output}")
        print(f"    {e}")
        return

    if not os.path.exists(path_input):
        os.makedirs(path_input)
        print(f"\n[+] Created folder: {THU_MUC_ANH}")
        print("    Please add images and run again!")
        return

    # Supported formats
    exts = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff')
    if HEIC_AVIF_SUPPORT:
        exts = exts + ('.heic', '.heif', '.avif')
    
    files = [f for f in os.listdir(path_input) if f.lower().endswith(exts)]
    
    if not files:
        print("\n>>> No valid images found!")
        print(f"    Supported formats: {', '.join(exts)}")
        return

    total_old, total_new = 0, 0
    print(f"\n>>> GridSnap v2.8 | Processing {len(files)} files...")
    print("-" * 65)

    for file_name in files:
        p_goc = os.path.join(path_input, file_name)
        base_name_only = os.path.splitext(file_name)[0]
        p_moi = ten_file_an_toan(path_output, base_name_only)  # Default .jpg
        final_file_name = os.path.basename(p_moi)
        
        size_goc = os.path.getsize(p_goc)
        total_old += size_goc
        
        try:
            with Image.open(p_goc) as img:
                # Capture ICC profile BEFORE any processing
                icc = img.info.get("icc_profile")
                
                # Handle EXIF orientation
                img = ImageOps.exif_transpose(img)
                
                # Handle transparent images (PNG, WEBP with alpha)
                if img.mode == 'RGBA':
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                elif img.mode not in ('RGB', 'L'):
                    # Convert other modes
                    img = img.convert('RGB')
                
                w, h = img.size
                
                # Calculate new dimensions
                moi_w, moi_h, note = tim_moc_phu_hop(w, h)
                
                # Resize if needed
                if (moi_w, moi_h) != (w, h):
                    img = img.resize((moi_w, moi_h), Image.Resampling.LANCZOS)
                    img = img.filter(ImageFilter.UnsharpMask(radius=0.8, percent=40, threshold=3))
                
                # Save with quality 85%, subsampling=0 (4:4:4 chroma)
                img.save(p_moi, "JPEG", optimize=True, quality=CHAT_LUONG, 
                        subsampling=0, icc_profile=icc)
                
                # Check result
                size_moi = os.path.getsize(p_moi)
                if size_moi > size_goc:
                    os.remove(p_moi)  # Delete the larger JPG
                    
                    ext_goc = os.path.splitext(p_goc)[1].lower()
                    
                    # Handle based on original format
                    if ext_goc in ['.jpg', '.jpeg']:
                        # Case 1: Original JPG is smaller -> copy it
                        shutil.copy2(p_goc, p_moi)
                        total_new += size_goc
                        print(f" [Keep Orig] {final_file_name} (Original JPG smaller)")
                    
                    elif ext_goc == '.png':
                        # Case 2: Original PNG is smaller (graphics/limited colors)
                        p_moi_png = ten_file_an_toan(path_output, base_name_only, '.png')
                        shutil.copy2(p_goc, p_moi_png)
                        total_new += size_goc
                        print(f" [Keep PNG]  {os.path.basename(p_moi_png)} (PNG smaller than JPG)")
                    
                    else:
                        # Case 3: Other formats (very rare)
                        p_moi_orig = ten_file_an_toan(path_output, base_name_only, ext_goc)
                        shutil.copy2(p_goc, p_moi_orig)
                        total_new += size_goc
                        print(f" [Keep Orig] {os.path.basename(p_moi_orig)} (Kept as {ext_goc})")
                else:
                    total_new += size_moi
                    if (moi_w, moi_h) != (w, h):
                        action = "Resize"
                    else:
                        action = "Compress"
                    per = (1 - size_moi/size_goc) * 100
                    print(f" [{action:10s}] {final_file_name} -> {note} (Saved {per:.1f}%)")
                        
        except Exception as e:
            print(f" [Error]     {file_name}: {str(e)[:50]}")
            # If error, copy original file to ensure no data loss
            try:
                ext_goc = os.path.splitext(p_goc)[1].lower()
                p_moi_error = ten_file_an_toan(path_output, base_name_only, ext_goc)
                shutil.copy2(p_goc, p_moi_error)
                total_new += size_goc
            except:
                pass

    # Final report
    saved = total_old - total_new
    per_total = (saved/total_old*100) if total_old > 0 else 0
    print("\n" + "="*60)
    print("GRIDSNAP OPTIMIZATION REPORT:")
    print(f"- Total original size:   {format_size(total_old)}")
    print(f"- Total optimized size:  {format_size(total_new)}")
    print(f"- SPACE SAVED:           {format_size(saved)} ({per_total:.1f}%)")
    print("="*60)

if __name__ == "__main__":
    try:
        xu_ly_anh()
    except KeyboardInterrupt:
        print("\n\n[!] User cancelled operation.")
    except Exception:
        print("\n[!] SYSTEM ERROR:")
        traceback.print_exc()
    finally:
        input("\nPress Enter to exit...")
