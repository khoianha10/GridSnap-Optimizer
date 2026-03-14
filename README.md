# 📸 GridSnap-Optimizer (v2.7)
**Smart batch image resizer & optimizer that preserves pixel density and sharpness across mixed orientations.**
*Công cụ tối ưu ảnh hàng loạt, bảo toàn mật độ điểm ảnh và độ nét cho cả ảnh ngang và dọc.*

---

### 😫 The Pain Points (Nỗi đau người dùng)
*   **Mixed Orientation Chaos:** Generic resizers often fail when handling a mix of landscape and portrait images, resulting in inconsistent scaling (some too small, some too large).
    *(Resize hỗn hợp ảnh ngang & dọc lộn xộn khiến ảnh dọc bị quá bé hoặc ảnh ngang bị quá to, không đồng nhất.)*
*   **Retina Blurriness:** Compressing images to "round numbers" (like 1000px or 2000px) forces High-DPI displays (MacBook, iPhone) to resample, causing **softness** or **aliasing**.
    *(Nén ảnh về các mốc lẻ làm hỏng lưới pixel, gây hiện tượng mờ hoặc răng cưa trên màn hình Retina.)*
*   **Loss of Detail:** Traditional tools often sacrifice fine details (text, icons, hair) to save space.
    *(Các công cụ truyền thống thường làm mất chi tiết mảnh để đổi lấy dung lượng.)*

---

### 💡 The GridSnap Solution (Giải pháp)
**GridSnap** automatically snaps the longest side of your images to **Optimal Grid Steps** (Multiples of 8 & Apple-standard resolutions).
*GridSnap tự động đưa cạnh dài nhất của ảnh về các **mốc lưới tối ưu** (bội số của 8 và chuẩn Retina).*

*   **Density-Aware Scaling:** Ensures consistent pixel density across your entire batch (960px to 3200px steps).
    *(Đảm bảo mật độ điểm ảnh đồng nhất cho toàn bộ batch theo dải mốc từ 960px đến 3200px.)*
*   **LANCZOS + Unsharp Mask:** Downscales with the highest quality filter and applies a light sharpening pass to keep images crisp.
    *(Hạ size với bộ lọc LANCZOS kết hợp Unsharp Mask nhẹ để giữ chi tiết.)*
*   **Anti-Collision & Anti-Bloat:** Prevents file overwriting and automatically skips files if compression results in a larger size than the original.
    *(Chống ghi đè file và tự động giữ nguyên bản gốc nếu nén xong file lại nặng hơn.)*
*   **Color Integrity:** Preserves ICC Profiles (Display P3, sRGB) for professional color accuracy.
    *(Bảo toàn Profile màu gốc, cực kỳ quan trọng cho người dùng Apple.)*

---

### 🚀 How to use (Hướng dẫn sử dụng)
1.  **Install dependencies:** `pip install pillow pillow-heif pillow-avif-plugin`
2.  **Add images:** Put your photos (JPG, PNG, HEIC, AVIF...) into the `Anh_Goc` folder.
3.  **Run:** Execute `GridSnap_v2.7.py` and check the `Anh_Da_Nen` folder for results.

---

### 📜 License
This project is licensed under the **MIT License**. Feel free to use, study, and improve!
