import os
import chromadb
from chromadb.utils import embedding_functions

# Khởi tạo client lưu trữ cục bộ tại thư mục chroma_db của dự án
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "../../chroma_db")
client = chromadb.PersistentClient(path=CHROMA_PATH)

# Sử dụng mô hình embedding chuẩn hoặc embedding mặc định của Chroma
# Ở đây ta dùng hàm embedding mặc định (all-MiniLM-L6-v2 hoặc tương đương)
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="techstore_knowledge",
    embedding_function=embedding_fn
)

def init_vector_db():
    """Nạp dữ liệu cẩm nang / tài liệu hướng dẫn vào Vector DB (chỉ cần chạy khi khởi động hoặc đồng bộ)."""
    if collection.count() > 0:
        return  # Đã có dữ liệu thì bỏ qua

    documents = [
        "Màn hình Bán hàng: tìm sản phẩm bằng cách gõ tên vào ô tìm kiếm (lọc ngay lập tức), double-click hoặc bấm 'Thêm vào giỏ'. Gõ đúng mã SKU rồi nhấn Enter là thêm thẳng vào giỏ, hỗ trợ quét mã vạch. Sau đó nhập giảm giá, tên và số điện thoại khách rồi bấm THANH TOÁN.",
        "Màn hình Sản phẩm (chỉ Quản lý): dùng để thêm, sửa, xóa sản phẩm, chọn ảnh đại diện và đặt mức tồn kho tối thiểu.",
        "Màn hình Danh mục (chỉ Quản lý): thêm, sửa, xóa danh mục sản phẩm; khi đổi tên danh mục, hệ thống sẽ tự động cập nhật cho mọi sản phẩm liên quan.",
        "Màn hình Tồn kho (chỉ Quản lý): xem danh sách sản phẩm sắp hết hàng và thực hiện nhập thêm hàng. Sản phẩm dưới mức tối thiểu được cảnh báo màu nổi bật.",
        "Màn hình Hóa đơn: cho phép lọc theo mã hóa đơn, tên khách hàng hoặc khoảng thời gian. Có thể xem chi tiết, xuất file PDF, xuất file Excel, hoặc thực hiện HỦY ĐƠN (tồn kho sẽ được cộng trả lại và thống kê tự động bỏ qua các đơn đã hủy).",
        "Màn hình Khách hàng: hệ thống tự động ghi nhận thông tin khách hàng từ các đơn có số điện thoại. Double-click vào một khách hàng để xem toàn bộ lịch sử mua sắm.",
        "Màn hình Thống kê (chỉ Quản lý): cung cấp 4 thẻ số liệu tổng quan cùng 3 biểu đồ trực quan, hỗ trợ xuất báo cáo ra file Excel.",
        "Thông tin tài khoản đăng nhập mặc định: admin/admin123 dành cho Quản lý (thấy toàn bộ menu), và nhanvien/123456 dành cho Nhân viên (chỉ thao tác bán hàng, hóa đơn, khách hàng).",
        "Đổi giao diện sáng/tối: bấm vào biểu tượng mặt trăng (🌙) ở góc dưới thanh bên trái giao diện chính. Lựa chọn này được lưu tự động cho lần đăng nhập sau."
    ]
    
    ids = [f"doc_{i}" for i in range(len(documents))]
    collection.add(
        documents=documents,
        ids=ids
    )

def query_rag_context(question: str, n_results: int = 2) -> str:
    """Tìm kiếm các đoạn văn bản có ý nghĩa tương đồng nhất với câu hỏi của người dùng."""
    try:
        init_vector_db()
        results = collection.query(
            query_texts=[question],
            n_results=n_results
        )
        matches = results.get("documents", [[]])[0]
        return "\n".join(matches) if matches else ""
    except Exception as e:
        print(f"Lỗi truy vấn Vector DB: {e}")
        return ""