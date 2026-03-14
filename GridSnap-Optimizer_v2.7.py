import os, sys, traceback, shutil
from PIL import Image, ImageFilter
import pillow_heif
import pillow_avif

# Register decoders for modern formats
pillow_heif.register_heif_opener()

# ================= CONFIGURATION =================
CHAT_LUONG = 85
THU_MUC_ANH = "Anh_Goc"
THU_MUC_XUAT = "Anh_Da_Nen"
# Optimal Grid-Snap Steps (Longest Side)
MOC_CHuan = [1170, 1284, 1536, 1728, 1920, 2048, 2304, 2560, 2732, 3024, 3200]
# =================================================

def format_size(size_bytes):
    """Accurate file size formatting up to TB"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def ten_file_an_toan(path_output, base_name):
    """Ensures no overwriting by adding suffixes _1, _2..."""
    target_path = os.path.join(path_output, base_name + ".jpg")
    if not os.path.exists(target_path):
        return target_path
    
    counter = 1
    while True:
        new_path = os.path.join(path_output, f"{base_name}_{counter}.jpg")
        if not os.path.exists(new_path):
            return new_path
        counter += 1

def tim_moc_phu_hop(w, h):
    max_dim = max(w, h)
    if max_dim <= 960: return w, h, "Original (Small)"
    
    target_size = None
    for moc in reversed(MOC_CHuan):
        if max_dim > moc:
            if (max_dim - moc) / moc < 0.05:
                return w, h, f"Original (Near {moc}px)"
            target_size = moc
            break
    
    if not target_size: return w, h, "Original"
    ratio = target_size / float(max_dim)
    return int(w * ratio), int(h * ratio), f"Grid-Snap {target_size}px"

def xu_ly_anh():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path_input = os.path.join(base_dir, THU_MUC_ANH)
    path_output = os.path.join(base_dir, THU_MUC_XUAT)

    if not os.path.exists(path_output): os.makedirs(path_output)
    if not os.path.exists(path_input): 
        os.makedirs(path_input)
        print(f"[-] Created folder: {THU_MUC_ANH}. Please add images and restart!")
        return

    exts = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.heic', '.heif', '.avif', '.tiff')
    files = [f for f in os.listdir(path_input) if f.lower().endswith(exts)]
    
    if not files:
        print(">>> No compatible images found!")
        return

    total_old, total_new = 0, 0
    print(f">>> GridSnap v2.7 | Smart Orientation | Processing {len(files)} files...")
    print("-" * 65)

    for file_name in files:
        p_goc = os.path.join(path_input, file_name)
        # Use ten_file_an_toan to prevent overwriting
        base_name_only = os.path.splitext(file_name)[0]
        p_moi = ten_file_an_toan(path_output, base_name_only)
        final_file_name = os.path.basename(p_moi)
        
        size_goc = os.path.getsize(p_goc)
        total_old += size_goc
        
        try:
            with Image.open(p_goc) as img:
                icc = img.info.get("icc_profile")
                w, h = img.size
                moi_w, moi_h, note = tim_moc_phu_hop(w, h)
                
                if (moi_w, moi_h) != (w, h):
                    img = img.resize((moi_w, moi_h), Image.Resampling.LANCZOS)
                    img = img.filter(ImageFilter.UnsharpMask(radius=0.8, percent=40, threshold=3))
                
                if img.mode != "RGB": img = img.convert("RGB")
                img.save(p_moi, "JPEG", optimize=True, quality=CHAT_LUONG, icc_profile=icc)
                
                size_moi = os.path.getsize(p_moi)
                if size_moi > size_goc:
                    os.remove(p_moi)
                    shutil.copy2(p_goc, p_moi)
                    total_new += size_goc
                    print(f" [Copy Orig] {final_file_name} (Optimized > Original)")
                else:
                    total_new += size_moi
                    per = (1 - size_moi/size_goc) * 100
                    print(f" [OK]        {final_file_name} -> {note} (Saved {per:.1f}%)")
                        
        except Exception as e:
            print(f" [Error]     {file_name}: {e}")
            total_new += size_goc

    saved = total_old - total_new
    per_total = (saved/total_old*100) if total_old > 0 else 0
    print("\n" + "="*60)
    print(f"GRIDSNAP OPTIMIZATION REPORT:")
    print(f"- Total Original Size:  {format_size(total_old)}")
    print(f"- Total Optimized Size: {format_size(total_new)}")
    print(f"- TOTAL SAVED:         {format_size(saved)} ({per_total:.1f}%)")
    print("="*60)

if __name__ == "__main__":
    try:
        xu_ly_anh()
    except Exception:
        print("\n[!] SYSTEM ERROR DETECTED:")
        traceback.print_exc()
    finally:
        input("\nPress Enter to exit...")
