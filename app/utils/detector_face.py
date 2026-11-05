import cv2
import os
import time
import numpy as np
from pathlib import Path
from deepface import DeepFace
from app.database.connection import get_db
from tkinter import messagebox

def draw_hud_face_box(img, x, y, w, h, label_text="", color=(0, 140, 255), thickness=3, line_length=40, progress=1.0, elapsed_time=0.0, state_manager=None):
    padding_x = int(w * 0.3)
    padding_top = int(h * 0.2)
    padding_bottom = int(h * 0.1) - 5
    
    x_new = max(0, x - padding_x)
    y_new = max(0, y - padding_top - 20)
    w_new = w + (padding_x * 2)
    h_new = (y + h + padding_bottom) - y_new

    # Top-left
    cv2.line(img, (x_new, y_new), (x_new + line_length, y_new), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x_new, y_new), (x_new, y_new + line_length), color, thickness, cv2.LINE_AA)
    # Top-right
    cv2.line(img, (x_new + w_new, y_new), (x_new + w_new - line_length, y_new), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x_new + w_new, y_new), (x_new + w_new, y_new + line_length), color, thickness, cv2.LINE_AA)
    # Bottom-left
    cv2.line(img, (x_new, y_new + h_new), (x_new + line_length, y_new + h_new), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x_new, y_new + h_new), (x_new, y_new + h_new - line_length), color, thickness, cv2.LINE_AA)
    # Bottom-right
    cv2.line(img, (x_new + w_new, y_new + h_new), (x_new + w_new - line_length, y_new + h_new), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x_new + w_new, y_new + h_new), (x_new + w_new, y_new + h_new - line_length), color, thickness, cv2.LINE_AA)
    # Rectangle
    margin = 10
    cv2.rectangle(img, (x_new - margin, y_new - margin), (x_new + w_new + margin, y_new + h_new + margin), (0, 255, 0), 1, cv2.LINE_AA)
    # Line 1
    m1 = 3
    cv2.line(img, (x_new + line_length*2, y_new - m1), (x_new + w_new - line_length*2, y_new - m1), (150, 255, 150), 1, cv2.LINE_AA)
    cv2.line(img, (x_new + line_length*2, y_new + h_new + m1), (x_new + w_new - line_length*2, y_new + h_new + m1), (150, 255, 150), 1, cv2.LINE_AA)
    cv2.line(img, (x_new - m1, y_new + line_length*2), (x_new - m1, y_new + int(h_new * 0.5) - 10), (150, 255, 150), 1, cv2.LINE_AA)
    cv2.line(img, (x_new - m1, y_new + int(h_new * 0.5) + 10), (x_new - m1, y_new + h_new - line_length*2), (150, 255, 150), 1, cv2.LINE_AA)
    cv2.line(img, (x_new + w_new + m1, y_new + line_length*2), (x_new + w_new + m1, y_new + int(h_new * 0.5) - 10), (150, 255, 150), 1, cv2.LINE_AA)
    cv2.line(img, (x_new + w_new + m1, y_new + int(h_new * 0.5) + 10), (x_new + w_new + m1, y_new + h_new - line_length*2), (150, 255, 150), 1, cv2.LINE_AA)
    # Line 2
    m2 = int(margin * 0.5)
    cv2.line(img, (x_new - m2, y_new + int(h_new * 0.5)), (x_new + line_length + m2, y_new + int(h_new * 0.5)), color, thickness, cv2.LINE_AA)
    cv2.line(img, (x_new + w_new + m2, y_new + int(h_new * 0.5)), (x_new + w_new - line_length - m2, y_new + int(h_new * 0.5)), color, thickness, cv2.LINE_AA)

    # Label
    if label_text:
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.65
        thickness_text = 2
        (text_w, text_h), baseline = cv2.getTextSize(label_text, font, font_scale, thickness_text)
        
        # Tọa độ nền chứa text bên dưới khung
        box_x1 = x_new + int(line_length * 0.5)
        box_y1 = y_new + h_new + 10

        # Định nghĩa độ rộng tối thiểu cho thanh ngang để chứa chữ + khoảng đệm padding
        padding_text = 20
        min_bar_width = text_w + (padding_text * 2)
        
        # Điểm bắt đầu và kết thúc của thanh ngang (đảm bảo luôn đủ chỗ cho tên dài)
        hx_start = box_x1 + 25
        hx_end = max(x_new + w_new + 5, hx_start + min_bar_width)
        
        # 2. Tính toán tọa độ X để chữ nằm CHÍNH GIỮA khoảng không gian của thanh ngang
        bar_width = hx_end - hx_start
        text_x = hx_start + (bar_width - text_w) // 2
        text_y = box_y1 + 40 - margin

        # Tọa độ đích của toàn bộ đường line
        target_x2 = box_x1 + 25
        target_y2 = box_y1 + 40
        target_x3 = hx_end

        # Nội suy độ dài nét vẽ dựa trên progress (từ 0.0 đến 1.0)
        current_len_progress = progress * (target_x3 - box_x1)

        if current_len_progress > 0:
            p1_x = int(box_x1 + min(25, current_len_progress))
            p1_y = int(box_y1 + min(40, (current_len_progress / 25) * 40))
            cv2.line(img, (box_x1, box_y1), (p1_x, p1_y), (255, 255, 255), thickness_text, cv2.LINE_AA)

        if current_len_progress > 25:
            horiz_len = current_len_progress - 25
            max_horiz_len = target_x3 - target_x2
            p2_x = int(target_x2 + min(max_horiz_len, horiz_len))
            cv2.line(img, (target_x2, target_y2), (p2_x, target_y2), (255, 255, 255), thickness_text, cv2.LINE_AA)

        # Chữ hiện lên khi đường line đã chạy được > 80% tiến trình
        if progress >= 0.8:
            cv2.putText(img, label_text, (text_x, text_y), font, font_scale, (0, 0, 255), thickness_text + 1, cv2.LINE_AA)
            cv2.putText(img, label_text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness_text, cv2.LINE_AA)

        anim_duration = 0.7
        delay_time = 1

        if elapsed_time >= anim_duration + delay_time:
            clear_text = "SUCCESS"
            font_clear = cv2.FONT_HERSHEY_SIMPLEX
            scale_clear = 3
            thick_clear = 10
            img_h, img_w, _ = img.shape
            
            # Tính kích thước chữ CLEAR
            (cw, ch), c_base = cv2.getTextSize(clear_text, font_clear, scale_clear, thick_clear)

            # Cấu hình kích thước Banner
            banner_w = cw + 140
            banner_h = ch + 80
            
            # Tính tọa độ để đặt Banner vào CHÍNH GIỮA MÀN HÌNH
            bx1 = (img_w - banner_w) // 2
            by1 = (img_h - banner_h) // 2
            bx2 = bx1 + banner_w
            by2 = by1 + banner_h

            # --- 1. TẠO PHẦN NỀN TRONG SUỐT (SEMI-TRANSPARENT GREEN) ---
            overlay = img.copy()
            
            # Đỉnh đa giác vắt góc top-left (Chamfer corner)
            cut_size = 25
            pts = np.array([
                [bx1 + cut_size, by1],       # Top-left (vắt chéo)
                [bx2, by1],                  # Top-right
                [bx2, by2],                  # Bottom-right
                [bx1, by2],                  # Bottom-left
                [bx1, by1 + cut_size]        # Điểm nối vắt chéo
            ], np.int32)
            pts = pts.reshape((-1, 1, 2))

            # Tô màu nền xanh lục Sci-Fi (BGR: Green-Yellowish)
            cv2.fillPoly(overlay, [pts], (40, 220, 80))

            # Trộn overlay để tạo độ trong suốt (alpha = 0.7)
            alpha = 0.7
            cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

            # --- 2. VẼ VIỀN BẢNG HUD (BORDER & ACCENT CORNER) ---
            cv2.polylines(img, [pts], isClosed=True, color=(100, 255, 150), thickness=2, lineType=cv2.LINE_AA)
            cv2.line(img, (bx1, by1 + cut_size), (bx1 + cut_size, by1), (0, 255, 255), 2, cv2.LINE_AA)

            # --- 3. VẼ CHỮ "SUCCESS" CÓ VIỀN TẠO HIỆU ỨNG NỔI (STROKE TEXT) ---
            tx = bx1 + (banner_w - cw) // 2
            ty = by1 + (banner_h + ch) // 2 - 4

            # --- 4. VẼ THÊM HÌNH TAM GIÁC VUÔNG
            offset_x = 24   # Khoảng cách lùi sang trái/phải
            offset_y = -1  # Khoảng cách dịch dọc (giảm xuống để kéo tam giác thấp xuống sát góc khuyết)
            tri_size = 15  # Kích thước cạnh tam giác
            
            base_x = (bx1 + cut_size) - offset_x
            base_y = by1 - offset_y

            tri_pts = np.array([
                [base_x, base_y],                               # Đỉnh góc vuông
                [base_x + tri_size, base_y],                    # Cạnh kéo dài sang phải
                [base_x, base_y + tri_size]                     # Cạnh kéo dài xuống dưới
            ], np.int32)
            tri_pts = tri_pts.reshape((-1, 1, 2))
            tri_overlay = img.copy()
            # Tô màu nền và vẽ viền sắc nét cho tam giác
            cv2.fillPoly(overlay, [tri_pts], (40, 200, 80))
            cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
            cv2.polylines(img, [tri_pts], isClosed=True, color=(40, 255, 80), thickness=2, lineType=cv2.LINE_AA)

            # Viền ngoài chữ
            cv2.putText(img, clear_text, (tx, ty), font_clear, scale_clear, (10, 60, 20), thick_clear + 3, cv2.LINE_AA)
            # Lớp chữ chính màu trắng sáng ở giữa
            cv2.putText(img, clear_text, (tx, ty), font_clear, scale_clear, (255, 255, 255), thick_clear, cv2.LINE_AA)
            if state_manager is not None and not state_manager.get("audio_played", False):
                state_manager["audio_played"] = True
                try:
                    import threading
                    import winsound
                    def play_rapid_beeps():
                        try:
                            winsound.Beep(2500, 300)
                        except Exception:
                            print("\a\a")
                    threading.Thread(target=play_rapid_beeps, daemon=True).start()
                except Exception:
                    print("\a\a")
        
def verify_face_from_camera(username_input):
    if not username_input:
        return False, "Vui lòng nhập tên đăng nhập trước khi xác thực khuôn mặt!", None

    db = get_db()
    user = db.users.find_one({"username": username_input})
    
    if not user:
        return False, f"Không tìm thấy tài khoản '{username_input}' trong hệ thống!", None

    # Hỗ trợ đa ảnh mẫu (Multi-sample)
    stored_paths = user.get("image_paths", [])
    if not stored_paths and user.get("image_path"):
        stored_paths = [user.get("image_path")]

    # Lọc lại các đường dẫn file ảnh mẫu thực sự tồn tại trên ổ cứng
    valid_stored_paths = [p for p in stored_paths if os.path.exists(p)]
    
    if not valid_stored_paths:
        return False, f"Tài khoản '{username_input}' chưa đăng ký ảnh khuôn mặt mẫu nào trong hệ thống!", None

    # 1. Mở Webcam quét liên tục
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return False, "Không thể kết nối với Webcam!", None
    
    messagebox.showinfo("Thông báo", f"Hệ thống nhận diện khuôn mặt. Hãy nhìn thẳng, xoay nhẹ trái/phải, tìm được khung hình khớp sẽ tự động đăng nhập!")

    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    cascade_path = str(BASE_DIR / "haarcascade_frontalface_default.xml")
    face_cascade = cv2.CascadeClassifier(cascade_path) if os.path.exists(cascade_path) else None

    if not face_cascade:
        cap.release()
        return False, "Không tìm thấy file Haar Cascade để nhận diện mặt!", None

    start_time = time.time()
    TIMEOUT = 15.0           # Quét tối đa 10 giây
    CHECK_INTERVAL = 0.7     # Kiểm tra AI mỗi 0.7 giây
    last_check_time = time.time()

    success_start_time = None
    success_result = None
    hud_state = {"audio_played": False}

    temp_dir = Path("D:/Image")
    temp_dir.mkdir(parents=True, exist_ok=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        display_frame = frame.copy()
        
        current_time = time.time()
        elapsed = current_time - start_time
        remaining_time = max(0, int(TIMEOUT - elapsed))

        # Phát hiện mặt để vẽ khung xanh hướng dẫn
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))

        if success_start_time is not None:
            elapsed_success = current_time - success_start_time
            if current_time - success_start_time >= 5.0:
                break
            if 'anim_start_time' not in locals() or anim_start_time is None:
                anim_start_time = current_time
            anim_duration = 0.7
            progress = min(1.0, (current_time - anim_start_time) / anim_duration)
            for (x, y, w, h) in faces:
                draw_hud_face_box(display_frame, x, y, w, h, label_text=username_input.upper(), color=(0, 200, 0), thickness=3, progress=progress, elapsed_time=elapsed_success, state_manager=hud_state)

        else:
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    draw_hud_face_box(display_frame, x, y, w, h, label_text="", color=(0, 140, 255), thickness=3)

        window_name="Face Login"
        cv2.imshow(window_name, display_frame)

        if cv2.waitKey(1) & 0xFF == 27 or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:  # Hủy đăng nhập
            break

        if elapsed >= TIMEOUT:
            break

        # Cứ mỗi khoảng thời gian và thấy mặt -> Thực hiện đối chiếu
        if success_start_time is None and current_time - last_check_time >= CHECK_INTERVAL and len(faces) > 0:
            last_check_time = current_time
            
            try:
                ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
                channels = list(cv2.split(ycrcb))
                channels[0] = cv2.equalizeHist(channels[0])
                balanced_frame = cv2.merge(channels)
                balanced_frame = cv2.cvtColor(balanced_frame, cv2.COLOR_YCrCb2BGR)

                temp_captured_path = str(temp_dir / f"temp_multi_{username_input}.jpg")
                
                # Cắt mặt
                (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
                padding = int(w * 0.1)
                img_h, img_w, _ = balanced_frame.shape
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(img_w, x + w + padding)
                y2 = min(img_h, y + h + padding)
                cropped = balanced_frame[y1:y2, x1:x2]

                if cropped.shape[0] > 50 and cropped.shape[1] > 50:
                    cv2.imwrite(temp_captured_path, cropped)
                else:
                    cv2.imwrite(temp_captured_path, balanced_frame)

                # ĐỐI CHIẾU LẦN LƯỢT VỚI TẤT CẢ CÁC ẢNH MẪU TRONG DANH SÁCH
                best_distance_for_frame = float('inf')
                for sample_path in valid_stored_paths:
                    try:
                        result = DeepFace.verify(
                            img1_path=sample_path,
                            img2_path=temp_captured_path,
                            model_name="ArcFace",
                            detector_backend="opencv"
                        )
                        dist = result["distance"]
                        if dist < best_distance_for_frame:
                            best_distance_for_frame = dist
                    except:
                        continue

                if os.path.exists(temp_captured_path):
                    os.remove(temp_captured_path)

                CUSTOM_THRESHOLD = 0.25  # Ngưỡng của mô hình ArcFace

                # ĐẠT NGƯỠNG -> ĐĂNG NHẬP 
                if best_distance_for_frame <= CUSTOM_THRESHOLD:
                    similarity_score = max(0, (1 - (best_distance_for_frame / 1.0))) * 100
                    success_result = (True, f"Xác thực thành công!", user)
                    success_start_time = time.time()

            except Exception:
                pass

    cap.release()
    cv2.destroyAllWindows()

    if success_result:
        return success_result
    else:
        return False, "Hết thời gian quét hoặc không tìm thấy góc khuôn mặt nào khớp!", None