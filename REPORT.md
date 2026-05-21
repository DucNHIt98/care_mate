# 🤝 Care Mate — Project Report

> **Mục đích:** File này tổng hợp toàn bộ thông tin repo, kiến trúc, các task đã làm, giải thích chi tiết từng phần để intern nắm được và report lên mentor.

---

## 1. TỔNG QUAN PROJECT

**Care Mate** là một Blog/Post Management API backend viết bằng Django REST Framework, kèm frontend HTML/CSS/JS cơ bản.

- **Mục tiêu:** Quản lý bài viết (CRUD) + Xác thực người dùng (JWT)
- **Đối tượng sử dụng:** Backend API cho mobile/web app, frontend demo để test
- **Database:** MySQL
- **Container:** Docker

---

## 2. TECH STACK

| Thành phần | Công nghệ | Version | Ghi chú |
|------------|-----------|---------|---------|
| Backend | Django | 4.2.30 | Web framework |
| REST API | djangorestframework | 3.15.2 | Xây dựng API endpoints |
| Auth | djangorestframework-simplejwt | 5.3.1 | JWT authentication |
| Database | MySQL | 8.x | Qua mysqlclient driver |
| Python | Python | 3.9 | (Docker image: python:3.9-slim) |
| Frontend | HTML/CSS/JS | — | Vanilla, không framework |
| Container | Docker | — | docker-compose single service |

---

## 3. CẤU TRÚC THƯ MỤC

```
care_mate/
├── care_mate/               # Django project config
│   ├── settings.py          # ⚙️ Cấu hình chính (DB, JWT, REST framework, templates)
│   ├── urls.py              # 🚪 Root URL: /admin/, /api/
│   ├── asgi.py / wsgi.py    # Entry points cho server
│
├── core/                    # 📦 Shared utilities (dùng chung cho cả project)
│   ├── response.py          # success_response() / error_response() — format JSON chuẩn
│   ├── panigation.py        # CustomPagination — phân trang custom
│   ├── permissions.py       # IsAuthor — check quyền author
│   ├── urls.py              # Router: ghép post/ + auth/ + web/ URLs
│
├── post/                    # 📝 Blog app (quản lý bài viết)
│   ├── models.py            # Post model (author, title, content, created_at)
│   ├── serializers.py       # PostSerializer (chuyển model ↔ JSON)
│   ├── services.py          # PostService — business logic (filter, CRUD)
│   ├── views.py             # 5 API views (thin controllers, gọi service)
│   ├── urls.py              # 5 endpoints /api/posts/...
│
├── user/                    # 👤 Auth app (xác thực người dùng)
│   ├── serializers.py       # RegisterSerializer (tạo user)
│   ├── services.py          # AuthService — business logic (register)
│   ├── views.py             # RegisterView + LoginView (thin controllers)
│   ├── urls.py              # 2 endpoints /api/auth/...
│
├── web/                     # 🌐 Frontend views (Django TemplateView)
│   ├── views.py             # 6 TemplateView trỏ tới từng file HTML
│   ├── __init__.py
│
├── templates/web/           # 📄 HTML frontend files
│   ├── login.html           # 🔑 Đăng nhập
│   ├── register.html        # 📝 Đăng ký
│   ├── posts.html           # 📋 Danh sách bài viết (filter + phân trang)
│   ├── post_create.html     # ✏️ Tạo bài viết
│   ├── post_detail.html     # 📖 Chi tiết bài viết (edit/delete nếu là author)
│   ├── post_edit.html       # ✏️ Chỉnh sửa bài viết
│
├── Dockerfile               # 🐳 Docker build
├── docker-compose.yml       # 🐳 Docker run (web service, port 8000)
├── manage.py                # 🔧 Django CLI
└── requirements.txt         # 📦 Python dependencies
```

---

## 4. KIẾN TRÚC API

### 4.1. URL Mapping

```
Host: http://localhost:8000

/api/............... core/urls.py (router gốc)
  ├── posts/........ post/urls.py
  │   ├── GET  posts/                → PostList      (public, có filter + paginate)
  │   ├── POST posts/create/         → PostCreate    (cần JWT)
  │   ├── GET  posts/<id>/           → PostDetail    (public)
  │   ├── PUT  posts/<id>/update/    → PostUpdate    (cần JWT + là author)
  │   └── DELETE posts/<id>/delete/  → PostDelete    (cần JWT + là author)
  │
  ├── auth/........ user/urls.py
  │   ├── POST auth/register/        → RegisterView  (public)
  │   └── POST auth/login/           → LoginView     (public, trả về JWT)
  │
  └── web/......... web URLs (frontend pages)
      ├── GET  web/                  → Login page
      ├── GET  web/register/         → Register page
      ├── GET  web/posts/            → Posts list page
      ├── GET  web/posts/create/     → Create post page
      ├── GET  web/posts/<id>/       → Post detail page
      └── GET  web/posts/<id>/edit/  → Edit post page

/admin/............ Django Admin
```

### 4.2. Response Format Chuẩn

Mọi API response đều theo format thống nhất qua `core/response.py`:

```json
{
  "is_success": true,
  "status": 200,
  "status_message": "Thành công!",
  "msg_code": "",
  "data": { ... }
}
```

**Giải thích:** `success_response()` và `error_response()` là 2 hàm wrapper, đảm bảo mọi endpoint đều trả về cùng cấu trúc JSON. Client chỉ cần check `is_success` thay vì parse HTTP status.

### 4.3. Pagination Response

Khi có phân trang, `data` chứa thêm metadata:

```json
{
  "is_success": true,
  "status": 200,
  "status_message": "Lấy danh sách bài viết!",
  "data": {
    "total_pages": 5,
    "total_records": 47,
    "current_page": 1,
    "page_size": 10,
    "total_all_records": 47,
    "sort_table_keys": {},
    "data": [ ... ]      // <-- danh sách bài viết thực tế
  }
}
```

Dùng `?limit=` để đổi số lượng item mỗi trang (mặc định 10).

---

## 5. CHI TIẾT CÁC TASK ĐÃ LÀM

### Task 1: Setup JWT Auth Config
**File:** `care_mate/settings.py:137-148`

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}
```

**Giải thích:**
- `JWTAuthentication` = mọi request đều được kiểm tra JWT token trong Header `Authorization: Bearer <token>`. Nếu không có token → request vẫn được xử lý với user là Anonymous (trừ khi view yêu cầu auth).
- Access token sống 1 ngày, Refresh token sống 7 ngày — đủ cho dev/demo.

---

### Task 2: Register API
**Endpoint:** `POST /api/auth/register/` (public)
**Views:** `user/views.py:RegisterView`
**Serializer:** `user/serializers.py:RegisterSerializer`

```python
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, message="Đăng ký thất bại!")
        user = serializer.save()
        return success_response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }, message="Đăng ký thành công!", status=201)
```

**Request body:**
```json
{ "username": "abc", "email": "abc@mail.com", "password": "123456" }
```

**Giải thích:** Dùng `RegisterSerializer` (extends ModelSerializer) tự động validate dữ liệu và gọi `create_user()` (hash password tự động). Password là `write_only` → không bao giờ trả về trong response.

---

### Task 3: Login API
**Endpoint:** `POST /api/auth/login/` (public)
**Views:** `user/views.py:LoginView`

```python
class LoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
```

**Response:**
```json
{ "access": "<jwt_token>", "refresh": "<refresh_token>" }
```

**Giải thích:** `TokenObtainPairView` là view có sẵn từ simplejwt. Nó nhận `username` + `password`, kiểm tra đúng → trả về cặp access/refresh token. Client lưu `access` token vào `localStorage` để gọi các API cần auth.

---

### Task 4: Protect API (Auth Required)
**File:** `care_mate/settings.py:141-143` + `post/views.py`

```python
# settings.py — global mặc định
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
```

| View | Permission class | Ý nghĩa |
|------|-----------------|---------|
| `PostList` | `[AllowAny]` | Public — ai cũng xem được danh sách |
| `PostDetail` | `[AllowAny]` | Public — ai cũng xem được chi tiết |
| `PostCreate` | *(global)* `IsAuthenticated` | Chỉ user có token mới tạo được |
| `PostUpdate` | `[IsAuthor]` | Chỉ tác giả mới sửa được |
| `PostDelete` | `[IsAuthor]` | Chỉ tác giả mới xóa được |

**Giải thích:**
- `DEFAULT_PERMISSION_CLASSES` là global — áp dụng cho mọi view không set `permission_classes` riêng.
- View nào public (List, Detail) phải set `AllowAny` để override global.
- Flow kiểm tra:
  1. Request đến → DRF check authentication (lấy user từ JWT)
  2. DRF check permission → nếu fail trả về 401/403 tự động
  3. View code chạy

---

### Task 5: Permission Owner Only
**File:** `core/permissions.py:IsAuthor`

```python
class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
```

Sử dụng trong `PostUpdate` & `PostDelete`:
```python
class PostUpdate(APIView):
    permission_classes = [IsAuthor]

    def put(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)  # <-- gọi IsAuthor check
        ...
```

**Giải thích:**
- `BasePermission` là class gốc của DRF, có 2 method: `has_permission()` (trước khi vào view) và `has_object_permission()` (kiểm tra trên object cụ thể).
- `self.check_object_permissions(request, post)` gọi `has_object_permission()` — nếu fail DRF tự động trả về 403.
- **Tại sao không dùng inline `if post.author != request.user` như cũ?** Vì dùng DRF permission class là chuẩn architecture, dễ test, dễ reuse (có thể dùng lại ở view khác).

---

### Task 6: Frontend HTML/CSS/JS
**Files:** `templates/web/*.html` (6 pages)

| Page | File | Tính năng |
|------|------|-----------|
| Login | `login.html` | Form username/password → gọi `/api/auth/login/` → lưu JWT → redirect |
| Register | `register.html` | Form + validate confirm password → gọi `/api/auth/register/` |
| Posts List | `posts.html` | Fetch + render danh sách, filter theo title/content, phân trang |
| Create Post | `post_create.html` | Form title/content → gọi `POST /api/posts/create/` (có JWT) |
| Post Detail | `post_detail.html` | View chi tiết + nút Edit/Delete nếu là author |
| Edit Post | `post_edit.html` | Form pre-filled → gọi `PUT /api/posts/<id>/update/` |

**Frontend architecture:**
- **No framework** — chỉ HTML thuần + CSS inline + JS vanilla
- **API calls** qua `fetch()` với `Authorization: Bearer <token>` header
- **JWT** lưu trong `localStorage`
- **Check auth** — nếu không có token → redirect về login
- **Author check** — decode JWT payload lấy `user_id`, so sánh với `post.author`

**Giải thích pattern:** Dùng Django `TemplateView` để serve file HTML → frontend và backend cùng domain/port → **không cần CORS**. File HTML là static, JS gọi API nội bộ.

---

### Task 7: Serializer bổ sung author_username
**File:** `post/serializers.py`

```python
class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()

    def get_author_username(self, obj):
        return obj.author.username if obj.author else None
```

**Giải thích:** `author` trong Post model là ForeignKey tới User → DRF mặc định chỉ serialize ra user ID. Thêm `author_username` để frontend có thể hiển thị tên tác giả mà không cần gọi thêm API.

---

### Task 8: Service Layer
**Files:** `post/services.py` + `user/services.py`

**Mục tiêu:** Tách business logic ra khỏi views. View chỉ lo HTTP, service lo xử lý dữ liệu.

```python
# post/services.py
class PostService:

    @staticmethod
    def get_queryset(filters=None):
        """Lấy danh sách posts, có filter theo content/title"""
        posts = Post.objects.all()
        if filters:
            content = filters.get("content")
            title = filters.get("title")
            if content:
                posts = posts.filter(content__icontains=content)
            if title:
                posts = posts.filter(title__icontains=title)
        return posts

    @staticmethod
    def get_by_id(pk):
        """Lấy 1 post hoặc 404"""
        return get_object_or_404(Post, pk=pk)

    @staticmethod
    def create(author, validated_data):
        """Tạo post mới"""
        return Post.objects.create(author=author, **validated_data)

    @staticmethod
    def update(post, validated_data):
        """Cập nhật post"""
        for attr, value in validated_data.items():
            setattr(post, attr, value)
        post.save()
        return post

    @staticmethod
    def delete(post):
        """Xóa post"""
        post.delete()
```

```python
# user/services.py
class AuthService:

    @staticmethod
    def register(validated_data):
        """Tạo user mới với password đã hash"""
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
```

**Giải thích:**
- Mỗi method là một `@staticmethod` — không cần instance, gọi thẳng `PostService.get_by_id(pk)`.
- Service **không biết gì về HTTP** — không import `request`, `Response`. Nó chỉ nhận data và trả về data.
- `get_queryset` nhận dict filters thay vì `request.query_params` → có thể gọi từ bất kỳ đâu (CLI, test, view khác).
- `create` nhận `author` + `validated_data` (đã validate từ serializer) → tránh duplicate validation.

---

### Task 9: Refactor Views → Thin Controllers
**Files:** `post/views.py` + `user/views.py`

Sau khi có service layer, views được rút gọn, mỗi view chỉ làm 3 việc:
1. **Parse input** (serializer + validate)
2. **Call service** (xử lý business)
3. **Trả response** (success_response / error_response)

```python
# post/views.py — sau refactor

class PostCreate(APIView):
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, message="Tạo bài viết thất bại!")
        post = PostService.create(request.user, serializer.validated_data)
        return success_response(PostSerializer(post).data, message="Tạo bài viết thành công!", status=201)

class PostDetail(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        post = PostService.get_by_id(pk)
        serializer = PostSerializer(post)
        return success_response(serializer.data, message="Lấy chi tiết bài viết!")

class PostUpdate(APIView):
    permission_classes = [IsAuthor]
    def put(self, request, pk):
        post = PostService.get_by_id(pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post, data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, message="Cập nhật bài viết thất bại!")
        post = PostService.update(post, serializer.validated_data)
        return success_response(PostSerializer(post).data, message="Cập nhật bài viết thành công!")

class PostDelete(APIView):
    permission_classes = [IsAuthor]
    def delete(self, request, pk):
        post = PostService.get_by_id(pk)
        self.check_object_permissions(request, post)
        PostService.delete(post)
        return success_response(None, message="Xóa bài viết thành công!")
```

**So sánh trước và sau:**

| View | Trước (lines) | Sau (lines) | Logic dư thừa được gỡ bỏ |
|------|---------------|-------------|--------------------------|
| PostCreate | 6 | 5 | `serializer.save(author=request.user)` → gọi `PostService.create()` |
| PostDetail | 4 | 4 | `get_object_or_404` → `PostService.get_by_id()` |
| PostUpdate | 9 | 8 | `get_object_or_404` + `serializer.save()` → `PostService.get_by_id()` + `PostService.update()` |
| PostDelete | 6 | 5 | `get_object_or_404` + `post.delete()` → `PostService.get_by_id()` + `PostService.delete()` |
| RegisterView | 7 | 7 | `serializer.save()` → `AuthService.register()` |

**Lợi ích:**
- View chỉ còn **orchestration** (điều phối), không còn **implementation** (cài đặt)
- Nếu đổi DB từ MySQL sang PostgreSQL, chỉ sửa service, không động vào view
- Có thể unit-test service riêng biệt không cần Django test client

---

## 6. DOCKER SETUP

### Dockerfile
- Base: `python:3.9-slim`
- Cài: `default-libmysqlclient-dev`, `build-essential`, `pkg-config`
- Copy requirements → `pip install`
- Expose port 8000

### docker-compose.yml
```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app          # bind mount → code change tự động reload
    environment:
      MYSQL_DATABASE: care_mate_db
      MYSQL_USER: root
      MYSQL_PASSWORD: 12345678
      MYSQL_HOST: host.docker.internal  # MySQL chạy ở host machine
      MYSQL_PORT: 3306
```

**Giải thích:** MySQL chạy trên host (không phải container riêng). Docker container dùng `host.docker.internal` để kết nối tới MySQL của máy host.

---

## 7. CÁCH CHẠY

### Option 1: Docker
```bash
# Yêu cầu: Docker Desktop đang chạy, MySQL đang chạy ở host (port 3306)
docker compose up --build
```
Truy cập: http://localhost:8000/api/web/

### Option 2: Local
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Sửa MYSQL_HOST trong settings.py hoặc set env
python manage.py migrate
python manage.py runserver
```

---

## 8. CÁC TASK TIẾP THEO (TODO)

### Task 10: DRY — Tái sử dụng code
Hiện tại vẫn còn pattern lặp:
- `serializer.is_valid() → error_response()` lặp ở PostCreate, PostUpdate, RegisterView
- Các view đều gọi `success_response(PostSerializer(post).data, ...)`

**Hướng giải quyết:** Tạo base class hoặc helper function để gom pattern validate → respond thành 1 dòng. Ví dụ:

```python
# core/response.py
def validate_or_error(serializer, error_msg):
    if not serializer.is_valid():
        return error_response(serializer.errors, message=error_msg)
    return None
```

**Khi nào nên làm:** Service layer đã ổn định, nếu thấy lặp nhiều thì extract sau.

---

## 9. MỘT SỐ LƯU Ý CHO INTERN

### Kiến trúc Django REST (sau refactor)
```
                     ┌─────────────────────────┐
                     │     URL (routing)        │
                     └──────────┬──────────────┘
                                │
                     ┌──────────▼──────────────┐
                     │   View (thin controller) │  ← chỉ: parse → call → respond
                     │   - validate serializer  │
                     │   - check permissions    │
                     │   - return Response      │
                     └──────────┬──────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                   │
     ┌────────▼────────┐ ┌─────▼──────┐  ┌─────────▼──────────┐
     │   Service Layer  │ │ Serializer │  │   Permission       │
     │   (business)     │ │ (transform) │  │   (auth/owner)     │
     │ - get_queryset   │ │ - validate  │  │ - IsAuthenticated  │
     │ - create/update  │ │ - to/from  │  │ - IsAuthor         │
     │ - delete         │ │   JSON     │  └────────────────────┘
     └────────┬────────┘ └─────┬──────┘
              │                 │
     ┌────────▼────────────────▼──┐
     │        Model (DB)          │
     └────────────────────────────┘
```

**Giải thích luồng request:**
1. `URL` → routing tới View đúng
2. `View` → check permission (nếu cần)
3. `View` → dùng Serializer validate input
4. `View` → gọi **Service** xử lý business logic
5. `View` → dùng Serializer chuyển data → JSON
6. `View` → return Response

Django REST framework làm theo pattern **CBV** (Class-Based Views). Project này dùng `APIView` làm base.

### JWT Flow
```
1. Client: POST /api/auth/login/ { username, password }
2. Server: verify → trả về { access_token, refresh_token }
3. Client: lưu access_token vào localStorage
4. Client: gọi API → Header { Authorization: Bearer <access_token> }
5. Server: verify token → lấy user → xử lý request
```

### Permission Flow (sau khi fix)
```
Request → JWTAuthentication (lấy user từ token)
       → DEFAULT_PERMISSION_CLASSES = [IsAuthenticated]
       → View specific (AllowAny / IsAuthor)
       → Nếu fail → 401 Unauthorized / 403 Forbidden
       → Nếu pass → vào view code
```

### Phân biệt Authentication vs Permission
- **Authentication:** Xác định **bạn là ai** (JWT token → User object)
- **Permission:** Xác định **bạn có được làm không** (IsAuthenticated, IsAdmin, IsAuthor...)

---

## 10. FILE SUMMARY

### Files Created (mới)

| File | Mục đích |
|------|----------|
| `web/views.py` | TemplateView cho 6 trang frontend |
| `web/__init__.py` | Python package |
| `templates/web/login.html` | Frontend: Đăng nhập |
| `templates/web/register.html` | Frontend: Đăng ký |
| `templates/web/posts.html` | Frontend: Danh sách bài viết |
| `templates/web/post_create.html` | Frontend: Tạo bài viết |
| `templates/web/post_detail.html` | Frontend: Chi tiết bài viết |
| `templates/web/post_edit.html` | Frontend: Chỉnh sửa bài viết |
| `core/permissions.py` | IsAuthor permission class |
| `post/services.py` | PostService — business logic (get_queryset, CRUD) |
| `user/services.py` | AuthService — business logic (register) |

### Files Modified (sửa)

| File | Thay đổi |
|------|----------|
| `care_mate/settings.py` | + TEMPLATES.DIRS (trỏ tới templates/) |
| | + DEFAULT_PERMISSION_CLASSES = [IsAuthenticated] |
| `core/urls.py` | + 6 routes web/* cho frontend pages |
| `post/views.py` | + permission_classes cho từng view |
| | + Dùng IsAuthor (core/permissions.py) |
| | + check_object_permissions thay cho inline if |
| | + Gọi PostService thay vì xử lý trực tiếp |
| `post/serializers.py` | + author_username field |
| `user/views.py` | + Gọi AuthService.register() thay vì serializer.save() |

---

> **Document này được tạo để hỗ trợ intern báo cáo mentor.**
> Mọi thắc mắc về kiến trúc hoặc task có thể trao đổi thêm.
