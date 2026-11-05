# TechStore — Ứng dụng quản lý sản phẩm

*(Lưu ý: 
- Đối với tính năng nhận diện sản phẩm bằng camera điện thoại, cần cài đặt ứng dụng DroidCam trên máy tính và điện thoại.
- Đối với tính năng đăng nhập bằng khuôn mặt, cần phải lưu ảnh vào đường dẫn D:/Images/... và trên thiết bị phải có webcam
)*

---

## Mục lục
1. [Hướng dẫn cài đặt & Môi trường ảo (venv)](#1-hướng-dẫn-cài-đặt--môi-trường-ảo-venv)
2. [Giới thiệu các chức năng của ứng dụng](#2-giới-thệu-các-chức-năng-của-ứng-dụng)
3. [Xử lý tiếng Việt & Lưu ý kỹ thuật](#3-xử-lý-tiếng-việt--lưu-ý-kỹ-thuật)

---

## 1. Hướng dẫn cài đặt & Môi trường ảo (venv)

Dành cho người mới nhận mã nguồn. Quá trình cài đặt mất khoảng 10–15 phút (chủ yếu là thời gian tải và cấu hình MongoDB).

### Bước 0 — Giải nén
Giải nén mã nguồn ra một thư mục bất kỳ, ví dụ `D:\TechStore`.  
*(Tránh để thư mục nằm trong OneDrive hoặc Desktop đã đồng bộ để tránh lỗi khóa file khi ứng dụng ghi file PDF/Excel).*

### Bước 1 — Cài đặt Python
Cần cài sẵn **Python 3.10 trở lên**[cite: 8, 9]. Kiểm tra bằng lệnh:
```powershell
python --version

```

*Lưu ý quan trọng:* Khi cài đặt Python từ trang chủ, nhớ tích chọn ô **"Add python.exe to PATH"** ở màn hình đầu tiên.

### Bước 2 — Cài đặt MongoDB

1. Tải **MongoDB Community Server** bản dành cho Windows.


2. Trong quá trình cài đặt, ở màn hình *Service Configuration*, giữ nguyên tùy chọn mặc định **"Install MongoDB as a Service"** để MongoDB tự động chạy ngầm mỗi khi khởi động máy.


3. Kiểm tra MongoDB đã hoạt động hay chưa bằng lệnh:


```powershell
Get-Service MongoDB

```


(Cột `Status` phải là `Running`).



### Bước 3 — Tạo môi trường ảo (venv) và cài thư viện

Mở terminal (PowerShell/Git Bash) tại thư mục dự án và chạy các lệnh sau:

```powershell
cd D:/TechStore
python -m venv venv
venv/Scripts/activate
venv/Scripts/python -m pip install --upgrade 
venv/Scripts/pip install -r requirements.txt

```

Khi kích hoạt thành công, đầu dòng lệnh sẽ xuất hiện chữ `(venv)`. Thư mục `venv` này hoàn toàn có thể xóa đi trước khi bạn sao lưu hoặc nén dự án cá nhân.

### Bước 4 — Tạo file cấu hình

Sao chép file mẫu `.env.example` thành `.env`:

```powershell
copy .env.example .env

```

* Nếu dùng MongoDB chạy trên máy (local), bạn **giữ nguyên nội dung** file `.env`.


* Có thể bổ sung `API_KEY` trong `.env` nếu muốn Trợ lý AI trả lời trực tuyến bằng Gemini (nếu để trống, trợ lý tự động chuyển sang chế độ offline theo từ khóa).
Nhận diện sản phẩn bằng webcam


### Bước 5 — Tạo dữ liệu mẫu

Chạy lệnh sau để khởi tạo dữ liệu mẫu (chỉ cần chạy **một lần duy nhất** cho lần đầu tiên):

```powershell
python seed_data.py

```

### Bước 6 — Chạy ứng dụng

Cách nhanh nhất là **double-click vào file `run.bat**`, hoặc chạy qua terminal:

```powershell
python -m app.main

```

**Tài khoản đăng nhập mặc định:**

* Quản lý: `admin` / `admin123` (Thấy toàn bộ các tính năng)


* Nhân viên: `nhanvien` / `123456` (Chỉ thao tác Bán hàng, Hóa đơn, Khách hàng, Trợ lý AI)



---

## 2. Giới thiệu các chức năng của ứng dụng

Ứng dụng được thiết kế toàn diện dành cho cửa hàng bán lẻ đồ công nghệ với các phân hệ chính:

* **Đăng nhập & Phân quyền:** Quản lý và Nhân viên với mật khẩu được mã hóa an toàn (PBKDF2-SHA256). Giao diện hiển thị linh hoạt theo đúng quyền hạn tài khoản.


* **Bán hàng (POS):** Tìm kiếm sản phẩm thông minh (gõ-là-lọc), hỗ trợ quét mã vạch / SKU, quản lý giỏ hàng trực quan, tự động nhận diện khách quen qua số điện thoại, trừ kho nguyên tử chống xung đột và nhúng giá vốn tại thời điểm bán.


* **Quản lý sản phẩm & Danh mục:** Thêm, sửa, xóa (xóa mềm), chống trùng mã SKU, đánh dấu sản phẩm **yêu thích (★)** để hiển thị nổi bật, quản lý danh mục với tính năng tự động cập nhật tên cho các sản phẩm liên quan.


* **Tồn kho & Nhập hàng:** Theo dõi và cảnh báo sản phẩm dưới mức tồn kho tối thiểu, lập phiếu nhập hàng chi tiết theo nhà cung cấp, tự động tính giá vốn theo phương pháp bình quân gia quyền.


* **Tra cứu hóa đơn & Hoàn trả:** Bộ lọc hóa đơn linh hoạt theo ngày/tháng/năm, xem chi tiết hóa đơn, xuất file PDF hoặc Excel. Hỗ trợ **hoàn trả một phần sản phẩm** trong hóa đơn (tự động cộng trả tồn kho, điều chỉnh chi tiêu khách hàng và cập nhật lại số liệu thống kê).


* **Hủy hóa đơn:** Cho phép hủy đơn hàng, tự động hoàn lại tồn kho phần chưa hoàn trả và loại bỏ doanh thu đơn hủy khỏi các báo cáo.


* **Khách hàng:** Tự động ghi nhận thông tin từ giao dịch hoặc thêm mới thủ công, theo dõi lịch sử mua hàng chi tiết và đánh dấu khách hàng VIP.


* **Thống kê (Dành cho Quản lý):** Cung cấp các thẻ số liệu doanh thu, lợi nhuận thực tế (tính dựa trên giá vốn nhúng), số hóa đơn, cùng biểu đồ trực quan (matplotlib) theo thời gian, tỷ trọng danh mục và top bán chạy. Hỗ trợ xuất báo cáo Excel 4 sheet.


* **Trợ lý AI:** Tích hợp chatbot thông minh hỗ trợ giải đáp số liệu kinh doanh thực tế từ cơ sở dữ liệu hoặc tra cứu hướng dẫn sử dụng phần mềm.


* **Sao lưu & Khôi phục dữ liệu:** Cho phép sao lưu toàn bộ cơ sở dữ liệu ra file JSON và khôi phục an toàn (có cơ chế tự động backup dự phòng trước khi ghi đè).


* **Nhật ký hoạt động (Audit Logs):** Ghi nhận lịch sử thao tác của người dùng (đăng nhập, bán hàng, nhập kho, hủy đơn, sao lưu...) phục vụ công tác kiểm tra.



---

## 3. Xử lý tiếng Việt & Lưu ý kỹ thuật

* **Font chữ tiếng Việt:** Ứng dụng sử dụng font `DejaVuSans.ttf` đặt sẵn trong thư mục `assets/fonts/` để đảm bảo các file xuất PDF và biểu đồ matplotlib hiển thị chính xác tiếng Việt có dấu mà không phụ thuộc vào font chữ của hệ điều hành.


* **Kiến trúc phần mềm:** Tuân thủ mô hình phân lớp rõ ràng (View → Service → Model → MongoDB) giúp mã nguồn dễ bảo trì và mở rộng.



```

```
