# 🧠 BẢN ĐỒ TƯ DUY — Python Training qua repo Care Mate

> **Mục tiêu:** Hình dung tổng quan + mối quan hệ kiến thức Python (và Django/DRF dựng trên Python) bằng chính code thật trong repo này.
> **Cách đọc:** Đi từ tầng **🟢 Cơ bản → 🟡 Trung cấp → 🔴 Nâng cao**. Mỗi khái niệm có ví dụ lấy từ file trong repo.
> **Ký hiệu:** ⭐ = khái niệm trọng tâm BẮT BUỘC nhớ · 📁 = nơi xem code thật.

---

## 0. SƠ ĐỒ TỔNG QUAN (Big Picture)

```
                          PYTHON (ngôn ngữ nền)
                                  │
        ┌──────────────┬──────────┴───────────┬────────────────┐
        │              │                       │                │
   🟢 CƠ BẢN       🟡 TRUNG CẤP           🔴 NÂNG CAO      🧩 ECOSYSTEM
   (cú pháp)      (OOP + tổ chức)       (design pattern)   (framework)
        │              │                       │                │
   ┌────┴───┐     ┌────┴────┐           ┌──────┴─────┐    ┌──────┴──────┐
   biến/kiểu  class/method  decorator/staticmethod   Django/DRF        │
   hàm/import  kế thừa       service layer pattern    JWT auth          │
   dict/list   **kwargs      permission pattern       ORM/migration     │
   string      validate      response wrapper         pagination        │
        │              │                       │                │
        └──────────────┴───────────┬───────────┴────────────────┘
                                    ▼
                  ┌─────────────────────────────────────┐
                  │   LUỒNG 1 REQUEST (kết nối tất cả)   │
                  │ URL → View → Serializer → Service →  │
                  │       Model → DB → Response          │
                  └─────────────────────────────────────┘
```

**Mối quan hệ cốt lõi cần thấy ngay:**
Python (cú pháp) → cho phép viết **class/hàm** → DRF dùng class để dựng **View/Serializer/Permission** → tổ chức lại thành **Service Layer** → tất cả ghép thành **1 luồng xử lý request**.

---

## 🟢 TẦNG 1 — CƠ BẢN (nền tảng Python, phải vững trước)

### 1.1 ⭐ Biến, kiểu dữ liệu & cấu trúc dữ liệu
- **Khái niệm:** Python là dynamic typing — biến không cần khai báo kiểu. Cấu trúc hay dùng: `dict`, `list`, `str`, `int`, `bool`.
- **Ví dụ (📁 `core/response.py`):** một `dict` chính là payload JSON trả về:
```python
result = {
    "is_success": True,      # bool
    "status": status,        # int
    "status_message": message,  # str
    "data": data,            # có thể là dict / list / None
}
```
- **Liên kết →:** `dict` là nền cho **JSON response** và **request.data** ở tầng trên.

### 1.2 ⭐ Hàm (function) & tham số mặc định
- **Khái niệm:** `def`, tham số mặc định `param=value`, trả về `return`.
- **Ví dụ (📁 `core/response.py`):**
```python
def success_response(data=None, message="Thành công!", status=200):
    ...
```
  → Gọi `success_response()` không truyền gì vẫn chạy nhờ giá trị mặc định.
- **Liên kết →:** tham số mặc định là tiền đề hiểu `filters=None` trong service (1.6).

### 1.3 Import & module/package
- **Khái niệm:** chia code thành file (`module`) và thư mục có `__init__.py` (`package`). `import` để dùng lại.
- **Ví dụ (📁 `post/views.py`):**
```python
from core.response import success_response, error_response
from .models import Post          # '.' = cùng package
from .services import PostService
```
- **Liên kết →:** import đúng = nền cho việc **tách lớp** (mỗi lớp 1 file) ở tầng trung cấp.

### 1.4 ⭐ `dict.get()` vs truy cập trực tiếp (an toàn null)
- **Khái niệm:** `d["key"]` lỗi `KeyError` nếu thiếu key; `d.get("key")` trả `None`; `d.get("key", default)` trả mặc định.
- **Ví dụ (📁 `user/services.py`):**
```python
email=validated_data.get("email", ""),   # an toàn: thiếu email → ""
password=validated_data["password"],     # bắt buộc phải có
```
- **Liên kết →:** đây chính là tư duy **null-safety** — rất quan trọng khi trả data cho client.

### 1.5 Chuỗi & f-string / format
- **Khái niệm:** thao tác chuỗi, nối, biểu diễn object qua `__str__`.
- **Ví dụ (📁 `post/models.py`):**
```python
def __str__(self):
    return self.title   # cách object hiển thị dưới dạng chuỗi
```

### 1.6 Điều kiện & vòng lặp
- **Khái niệm:** `if/else`, `for ... in`.
- **Ví dụ (📁 `post/services.py`):**
```python
for attr, value in validated_data.items():   # lặp qua dict
    setattr(post, attr, value)
```

---

## 🟡 TẦNG 2 — TRUNG CẤP (OOP & tổ chức code)

### 2.1 ⭐ Class & Object (OOP)
- **Khái niệm:** `class` đóng gói dữ liệu + hành vi. `self` = instance hiện tại.
- **Ví dụ (📁 `post/models.py`):**
```python
class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
```
- **Liên kết →:** mọi thứ trong Django/DRF (View, Serializer, Permission) đều là **class**. Vững OOP = học framework dễ.

### 2.2 ⭐ Kế thừa (Inheritance)
- **Khái niệm:** class con kế thừa class cha → tái sử dụng + override method.
- **Ví dụ (📁 nhiều file):**
```python
class Post(models.Model): ...              # kế thừa Model
class PostList(APIView): ...               # kế thừa APIView
class PostSerializer(serializers.ModelSerializer): ...
class IsAuthor(BasePermission): ...
class LoginView(TokenObtainPairView): ...  # kế thừa NGUYÊN view có sẵn
```
- **Liên kết →:** `LoginView` là ví dụ đẹp — kế thừa class có sẵn, gần như không viết gì thêm. Hiểu kế thừa = hiểu vì sao "code ít mà chạy nhiều".

### 2.3 ⭐ `@staticmethod` & method thường
- **Khái niệm:** `@staticmethod` = hàm gắn trong class nhưng KHÔNG cần `self` (không cần tạo instance). Gọi thẳng `Class.method()`.
- **Ví dụ (📁 `post/services.py`):**
```python
class PostService:
    @staticmethod
    def get_by_id(pk):
        return get_object_or_404(Post, pk=pk)
# gọi: PostService.get_by_id(5)  ← không cần PostService()
```
- **So sánh:** method có `self` (như `def post(self, request)` trong View) cần instance; `@staticmethod` thì không.
- **Liên kết →:** đây là kỹ thuật làm nên **Service Layer Pattern** (3.2).

### 2.4 ⭐ Decorator
- **Khái niệm:** hàm/cú pháp `@xxx` bọc lên function/class để thêm hành vi mà không sửa ruột.
- **Ví dụ:** `@staticmethod` (post/services.py), `@property`-style trong DRF. Decorator phổ biến nhất bạn gặp ở đây là `@staticmethod`.
- **Liên kết →:** decorator là nền tảng để hiểu cách DRF "tự động" làm việc (authentication, permission chạy ngầm).

### 2.5 ⭐ `*args` / `**kwargs` (unpacking)
- **Khái niệm:** `**dict` "bung" dict thành các keyword argument.
- **Ví dụ (📁 `post/services.py`):**
```python
return Post.objects.create(author=author, **validated_data)
# **validated_data tương đương: title=..., content=...
```
- **Liên kết →:** giúp viết hàm linh hoạt, không cần liệt kê từng field.

### 2.6 `setattr` / introspection cơ bản
- **Khái niệm:** gán thuộc tính động bằng tên (string).
- **Ví dụ (📁 `post/services.py`):**
```python
for attr, value in validated_data.items():
    setattr(post, attr, value)   # post.title = ..., post.content = ...
```

### 2.7 Validate dữ liệu qua Serializer
- **Khái niệm:** kiểm tra & chuẩn hóa input trước khi xử lý (DRF Serializer).
- **Ví dụ (📁 `user/serializers.py`):**
```python
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
```
  `write_only=True` → password không bao giờ lộ ra response (bảo mật). `min_length=6` → tự validate.
- **Liên kết →:** kết nối tầng cơ bản (dict input) với tầng nâng cao (business logic an toàn).
- **Nhớ kỹ DRF:** `serializer.is_valid()` chỉ validate và tạo `validated_data`; `serializer.save()` mới gọi `create()` hoặc `update()` trong serializer. Repo này không dùng `serializer.save()` khi register, mà gọi `AuthService.register(serializer.validated_data)`, nên `RegisterSerializer.create()` hiện không phải flow chính.

---

## 🔴 TẦNG 3 — NÂNG CAO (Design Pattern & Kiến trúc)

### 3.1 ⭐⭐ Thin Controller (View chỉ điều phối)
- **Khái niệm:** View chỉ làm 3 việc: **parse input → gọi service → trả response**. Không chứa business logic.
- **Ví dụ (📁 `post/views.py`):**
```python
class PostCreate(APIView):
    def post(self, request):
        serializer = PostSerializer(data=request.data)      # 1. parse
        if not serializer.is_valid():
            return error_response(serializer.errors, message="Tạo bài viết thất bại!")
        post = PostService.create(request.user, serializer.validated_data)  # 2. gọi service
        return success_response(PostSerializer(post).data, status=201)      # 3. respond
```
- **Liên kết →:** dựa trên 2.1 (class), 2.3 (staticmethod service), 2.7 (serializer).

### 3.2 ⭐⭐ Service Layer Pattern (tách business logic)
- **Khái niệm:** gom logic nghiệp vụ vào class riêng (`PostService`, `AuthService`), KHÔNG biết gì về HTTP. → dễ test, dễ tái dùng, View ít bị ảnh hưởng khi logic lưu/xử lý thay đổi.
- **Ví dụ (📁 `post/services.py`):** `get_queryset`, `create`, `update`, `delete` đều là `@staticmethod`, nhận **data nghiệp vụ** trả **object/data nghiệp vụ** (không nhận `request`, không trả `Response`).
- **Liên kết →:** chính là lý do tồn tại của 2.3 (`@staticmethod`). Đây là pattern QUAN TRỌNG NHẤT của repo.
- **Ranh giới phải thuộc:** View nhận `request` và trả `Response`; Serializer validate/serialize; Service xử lý nghiệp vụ và ORM; Permission quyết định quyền. Service không nên import `request`, không trả `Response`, không set HTTP status.

**Flow chuẩn trong repo:**
```
request.data → serializer.is_valid() → serializer.validated_data
→ PostService/AuthService → Model/ORM → Serializer(instance).data
→ success_response/error_response
```

### 3.3 ⭐ Permission Pattern (phân quyền theo object)
- **Khái niệm:** tách logic "ai được làm gì" thành class permission tái dùng được.
- **Ví dụ (📁 `core/permissions.py`):**
```python
class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
```
  Dùng ở View: `permission_classes = [IsAuthor]` + `self.check_object_permissions(request, post)`.
- **Liên kết →:** kế thừa (2.2) + class (2.1). Thay cho `if post.author != request.user` rải rác.
- **Phân biệt nhớ kỹ:** **Authentication** = "bạn là AI" (JWT → user) · **Permission** = "bạn được LÀM không".
- **Secure by default trong repo:** `settings.py` đặt global `IsAuthenticated`, nên endpoint public phải set `permission_classes = [AllowAny]`. `PostList`/`PostDetail` đã set. `RegisterView` hiện chưa set `AllowAny`, đây là điểm cần chú ý/sửa khi học auth flow.

### 3.4 ⭐ Response Wrapper Pattern (chuẩn hóa output)
- **Khái niệm:** mọi endpoint trả CÙNG 1 cấu trúc JSON → client chỉ cần check `is_success`.
- **Ví dụ (📁 `core/response.py`):** `success_response()` / `error_response()` bọc data vào shape thống nhất.
- **Liên kết →:** dùng 1.1 (dict) + 1.2 (default param). Giúp client (Flutter/web) parse ổn định, **nullability rõ ràng**.

### 3.5 ⭐ Pagination tùy biến
- **Khái niệm:** kế thừa `PageNumberPagination`, override `get_paginated_response` để trả metadata (total_pages, current_page...).
- **Ví dụ (📁 `core/panigation.py`):** `page_size = 10`, `page_size_query_param = "limit"` → client gọi `?limit=20`.
- **Liên kết →:** kế thừa (2.2) + override method. Quan trọng cho mọi **list endpoint** (tránh trả 10.000 record 1 lần).
- **Note naming:** file hiện là `panigation.py` theo repo thật, nhưng tên chuẩn nên là `pagination.py`. Khi đọc code nhớ đây là typo tên file, không phải thuật ngữ mới.
- **Hiểu đúng performance:** pagination không load toàn bộ record vào RAM; với page-number pagination thường có `COUNT(*)` để tính tổng và query `LIMIT/OFFSET` để lấy page hiện tại.

### 3.6 ⭐ ORM & Migration (Django)
- **Khái niệm:** thao tác DB bằng Python object thay vì SQL. Migration = phiên bản hóa schema.
- **Ví dụ (📁 `post/services.py`):**
```python
Post.objects.all()
Post.objects.filter(title__icontains=title)   # WHERE title LIKE %...%
Post.objects.create(author=author, **data)
```
- **⚠️ Lưu ý lineage (thực tế trong repo này):** `Post` model nằm ở app `post` nhưng `db_table = 'core_post'`, và có migration `core/0003_move_post_to_post_app.py`. → Khi deploy phải cẩn thận thứ tự migration để tránh schema divergence.
- **Chi tiết quan trọng:** `core/0003` xóa model khỏi state app `core` bằng `SeparateDatabaseAndState` nhưng không drop bảng thật; `post/0001_initial.py` tạo state model mới ở app `post`, vẫn map vào bảng cũ `core_post`, và update `ContentType` từ `core.post` sang `post.post`.

---

## 🧩 TẦNG 4 — ECOSYSTEM (ghép tất cả lại)

### 4.1 ⭐⭐ JWT Authentication Flow
```
1. POST /api/auth/login/ {username, password}
2. Server verify → trả {access, refresh}        (📁 user/views.py: LoginView)
3. Client lưu access token (localStorage)
4. Mỗi request: Header Authorization: Bearer <token>
5. JWTAuthentication giải mã → gắn request.user   (📁 settings.py: REST_FRAMEWORK)
```
- **Cấu hình (📁 `settings.py`):** `ACCESS_TOKEN_LIFETIME = 1 ngày`, `REFRESH = 7 ngày`.

### 4.2 ⭐⭐ Luồng 1 Request hoàn chỉnh (xương sống nối mọi khái niệm)
```
HTTP Request
   │
   ▼
[URL routing]  📁 root urls → core/urls → post/urls
   │
   ▼
[Authentication]  JWTAuthentication → request.user   (tầng 4.1)
   │
   ▼
[Permission]  IsAuthenticated / AllowAny / IsAuthor   (3.3)
   │
   ▼
[View - thin controller]  parse → call → respond      (3.1)
   │           │
   │           ├──► [Serializer] validate + to/from JSON   (2.7)
   │           │
   │           └──► [Service Layer] business logic          (3.2)
   │                      │
   │                      ▼
   │                  [Model / ORM] ↔ Database              (3.6)
   ▼
[Response Wrapper]  success/error_response → JSON chuẩn     (3.4)
```

---

## 🎯 DANH SÁCH KHÁI NIỆM TRỌNG TÂM (ôn nhanh trước khi quên)

| # | Khái niệm | Tầng | Vì sao trọng tâm | File |
|---|-----------|------|------------------|------|
| ⭐1 | `dict` & null-safe `.get()` | 🟢 | Nền của JSON & tránh crash null | `core/response.py`, `user/services.py` |
| ⭐2 | Hàm + tham số mặc định | 🟢 | Viết API linh hoạt | `core/response.py` |
| ⭐3 | Class & `self` (OOP) | 🟡 | Mọi thứ DRF đều là class | `post/models.py` |
| ⭐4 | Kế thừa | 🟡 | "Code ít, chạy nhiều" | `user/views.py` (LoginView) |
| ⭐5 | `@staticmethod` | 🟡 | Làm nên Service Layer | `post/services.py` |
| ⭐6 | `**kwargs` unpacking | 🟡 | `create(**validated_data)` | `post/services.py` |
| ⭐⭐7 | Service Layer Pattern | 🔴 | Pattern quan trọng nhất repo | `post/services.py` |
| ⭐⭐8 | Thin Controller | 🔴 | Tách HTTP khỏi logic | `post/views.py` |
| ⭐9 | Permission Pattern | 🔴 | Auth vs Permission | `core/permissions.py` |
| ⭐10 | Response Wrapper | 🔴 | Output ổn định cho client | `core/response.py` |
| ⭐⭐11 | JWT Flow | 🧩 | Bảo mật toàn hệ thống | `settings.py`, `user/views.py` |
| ⭐⭐12 | Luồng 1 Request | 🧩 | Sợi chỉ nối TẤT CẢ | (toàn repo) |

---

## 🪜 LỘ TRÌNH HỌC ĐỀ XUẤT (đường đi trong bản đồ)

```
🟢 dict/hàm/import  →  🟡 class/kế thừa/staticmethod  →  🔴 service+view+permission  →  🧩 JWT + luồng request
   (1-2 ngày)              (2-3 ngày)                       (3-4 ngày)                     (kết nối, thực hành)
```

**Bài tập tự kiểm tra (dùng repo này):**
1. 🟢 Mở `core/response.py`, giải thích vì sao gọi `success_response()` không tham số vẫn chạy.
2. 🟡 Vì sao `PostService.get_by_id(5)` gọi được mà không cần `PostService()`?
3. 🔴 Thêm 1 permission `IsAuthorOrReadOnly` mới — kế thừa từ đâu, override method nào?
4. 🧩 Vẽ lại luồng 1 request `PUT /api/posts/5/update/` đi qua những lớp nào.
