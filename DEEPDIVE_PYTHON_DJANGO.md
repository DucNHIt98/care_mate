# 📚 ĐÀO SÂU — Python & Django/DRF (companion của MINDMAP)

> **Đọc cùng:** `MINDMAP_PYTHON_TRAINING.md` (bản đồ tổng quan). File này **mổ xẻ từng khái niệm** ở mức chi tiết nhất: *bản chất → cơ chế bên trong → trong repo này → bảo mật & cạm bẫy*.
> Mỗi mục trả lời: **Nó là gì? Nó lưu/giữ gì? Nó xử lý gì? An toàn ra sao? Sai ở đâu hay gặp?**

**Mục lục**
- [PHẦN A — PYTHON CỐT LÕI](#phần-a--python-cốt-lõi)
  - A1 dict & null-safety · A2 Hàm & default args · A3 Import system · A4 Class/self/`__init__` · A5 Kế thừa & MRO/super · A6 staticmethod/classmethod/instance · A7 Decorator · A8 `*args`/`**kwargs` · A9 setattr/getattr
- [PHẦN B — DJANGO & DRF](#phần-b--django--drf)
  - B1 Vòng đời request/WSGI · B2 ORM & QuerySet lazy · B3 Migration & lineage · B4 Serializer · B5 APIView & dispatch · B6 Authentication vs Permission · B7 **JWT (đào sâu nhất)** · B8 Pagination · B9 Response rendering · B10 Settings & Middleware · B11 Service Layer (lý do tồn tại)

---

# PHẦN A — PYTHON CỐT LÕI

## A1. `dict` & null-safety (`[]` vs `.get()`)

**Bản chất:** `dict` là **hash map** — lưu cặp `key → value`, tra cứu O(1) trung bình. Key phải *hashable* (immutable: str, int, tuple). Bên dưới Python dùng bảng băm mở (open addressing) và từ 3.7 **giữ thứ tự chèn**.

**Nó xử lý gì khi tra key:**
```python
d["email"]        # tính hash("email") → tìm slot → KHÔNG có → raise KeyError (CRASH)
d.get("email")    # như trên nhưng KHÔNG có → trả None (an toàn)
d.get("email","") # KHÔNG có → trả "" (mặc định bạn chọn)
```

**Trong repo (`user/services.py`):**
```python
email=validated_data.get("email", ""),   # email optional → fallback ""
password=validated_data["password"],     # CHỦ Ý để [] : thiếu password là lỗi nghiêm trọng, nên cho nó nổ
```
→ Lựa chọn `[]` vs `.get()` là **chủ ý thiết kế**: field bắt buộc dùng `[]` (fail fast), field optional dùng `.get(key, default)`.

**An toàn / cạm bẫy:**
- Với client (Flutter/web) — trả `None` bất ngờ trong JSON có thể làm app crash do null-safety. Vì vậy `core/response.py` luôn bọc `data` trong cùng 1 shape: client biết trước cấu trúc.
- Đừng dùng `list`/`dict` làm key (unhashable → `TypeError`).

---

## A2. Hàm & tham số mặc định — kèm **cạm bẫy mutable default argument**

**Bản chất:** `def` tạo một **object hàm** (first-class — gán biến, truyền đi được). Tham số mặc định được **đánh giá MỘT LẦN lúc định nghĩa hàm**, không phải mỗi lần gọi.

**Trong repo (`core/response.py`):**
```python
def success_response(data=None, message="Thành công!", status=200): ...
```
Gọi `success_response()` → dùng `None/"Thành công!"/200`. Đây là **immutable defaults** → an toàn.

**⚠️ CẠM BẪY KINH ĐIỂN — mutable default:**
```python
def add(item, bucket=[]):     # SAI: list được tạo 1 lần, dùng chung mọi lần gọi
    bucket.append(item); return bucket
add(1)  # [1]
add(2)  # [1, 2]  ← KHÔNG phải [2]! Vì cùng 1 list

def add(item, bucket=None):   # ĐÚNG
    if bucket is None: bucket = []
    bucket.append(item); return bucket
```
→ Quy tắc vàng: **không bao giờ để default là `[]`, `{}`, hay object mutable.** Dùng `None` rồi khởi tạo bên trong — y như `get_queryset(filters=None)` trong `post/services.py`.

**Kiểu tham số:** positional, keyword, `*args`, `**kwargs`, keyword-only (sau `*`). Thứ tự bắt buộc: `def f(pos, *args, kw_only, **kwargs)`.

---

## A3. Import system / module / package

**Bản chất:**
- **Module** = 1 file `.py`. **Package** = thư mục có `__init__.py`.
- Khi `import X`, Python: (1) tìm trong `sys.modules` (cache) → (2) tìm theo `sys.path` → (3) thực thi file MỘT LẦN → (4) lưu vào `sys.modules`. Lần import sau lấy từ cache (vì vậy code top-level của module chỉ chạy 1 lần).

**Absolute vs relative (trong repo):**
```python
from core.response import success_response   # absolute: từ gốc project
from .models import Post                      # relative: '.' = package hiện tại (post/)
from .services import PostService             # '.' tránh phải gõ 'post.services'
```

**Cạm bẫy:**
- **Circular import:** A import B, B import A → lỗi. Service layer giúp giảm: View→Service→Model là một chiều, không vòng.
- Code đặt ở **top-level module** chạy ngay khi import → đừng đặt việc nặng/side-effect ở đó.
- `INSTALLED_APPS` trong `settings.py` quyết định Django “thấy” app nào (ở đây: `core`, `post`, `user`).

---

## A4. Class, `self`, `__init__`, `__str__`

**Bản chất:** `class` là **factory tạo object**. Mỗi object có namespace riêng (`__dict__`). `self` = tham chiếu tới instance đang gọi method (Python truyền instance làm tham số đầu **ngầm định**).

```python
class Post(models.Model):
    title = models.CharField(max_length=255)   # ← class attribute (Django field descriptor)
    def __str__(self):                          # dunder method
        return self.title
```

**Dunder (double-underscore) methods — “giao thức” của Python:**
| Method | Khi nào chạy | Ví dụ |
|--------|--------------|-------|
| `__init__` | lúc tạo object `Post()` | gán giá trị ban đầu |
| `__str__` | `str(obj)`, `print(obj)`, admin Django | `return self.title` |
| `__eq__` | `a == b` | so sánh — DRF/Django dùng nhiều |
| `__repr__` | debug/REPL | biểu diễn chính xác |

**Class attribute vs instance attribute (rất hay nhầm):**
```python
class A:
    items = []        # CHIA SẺ giữa mọi instance (giống mutable default!)
    def __init__(self):
        self.name = ""# RIÊNG mỗi instance
```
→ Trong Django, `title = models.CharField(...)` là class attribute đặc biệt (descriptor) — Django metaclass biến nó thành cột DB. Đây là magic bạn sẽ hiểu sâu hơn ở B2.

---

## A5. Kế thừa, `super()`, MRO

**Bản chất:** class con thừa hưởng attribute/method của cha; có thể **override** (ghi đè) hoặc **mở rộng** (gọi `super()` rồi thêm).

**Trong repo — 3 mức độ kế thừa:**
```python
class LoginView(TokenObtainPairView):        # (1) gần như không sửa gì → tái dùng 100%
    serializer_class = TokenObtainPairSerializer
class IsAuthor(BasePermission):              # (2) override has_object_permission
    def has_object_permission(...): ...
class CustomPagination(PageNumberPagination):# (3) override get_paginated_response + đổi config
    page_size = 10
```

**`super()` — gọi lên cha:**
```python
class Child(Parent):
    def method(self):
        super().method()   # chạy logic cha trước
        # rồi thêm logic con
```

**MRO (Method Resolution Order) — quan trọng khi đa kế thừa:** Python dùng thuật toán **C3 linearization** để quyết định gọi method nào trước khi 1 class kế thừa nhiều cha. Xem bằng `ClassName.__mro__`. DRF dùng nhiều mixin (đa kế thừa) nên hiểu MRO giúp debug “sao method này lại chạy”.

**Cạm bẫy:** quên gọi `super().__init__()` khi override `__init__` → object khởi tạo thiếu → lỗi khó hiểu.

---

## A6. `@staticmethod` vs `@classmethod` vs method thường

| Loại | Tham số đầu | Truy cập được gì | Gọi thế nào | Dùng khi |
|------|-------------|------------------|-------------|----------|
| Instance method | `self` | instance + class | cần `obj.method()` | cần dữ liệu của object |
| `@classmethod` | `cls` | class (không instance) | `Class.method()` | factory, thao tác cấp class |
| `@staticmethod` | *(không)* | không tự động gì | `Class.method()` | hàm tiện ích gom theo nhóm logic |

**Trong repo (`post/services.py`):** tất cả method service là `@staticmethod`:
```python
class PostService:
    @staticmethod
    def get_by_id(pk):
        return get_object_or_404(Post, pk=pk)
# Gọi: PostService.get_by_id(5)   ← KHÔNG cần PostService() vì không có state
```
**Vì sao chọn staticmethod ở đây?** Service không giữ trạng thái (stateless), chỉ là nhóm hàm thuần nhận-data-trả-data. Không cần `self` → static là đúng nhất, gọi gọn, dễ test (`PostService.create(...)` không cần dựng object).

**Khi nào dùng classmethod thay thế?** Nếu sau này muốn có nhiều “loại” service kế thừa và override → `cls` cho phép gọi đúng class con. Hiện tại chưa cần.

---

## A7. Decorator — “hàm bọc hàm”

**Bản chất:** decorator là **hàm nhận 1 hàm, trả về 1 hàm mới** (thường bọc thêm hành vi). Cú pháp `@deco` chỉ là đường tắt:
```python
@deco
def f(): ...
# TƯƠNG ĐƯƠNG:
def f(): ...
f = deco(f)
```

**Tự viết để hiểu cơ chế:**
```python
import functools
def log_calls(func):
    @functools.wraps(func)          # giữ tên/docstring gốc của func
    def wrapper(*args, **kwargs):   # *args/**kwargs để bọc MỌI hàm
        print(f"Gọi {func.__name__}")
        result = func(*args, **kwargs)
        print("Xong")
        return result
    return wrapper

@log_calls
def create_post(title): ...
```

**Trong repo:** `@staticmethod` chính là một decorator (do Python cấp sẵn) — nó biến method thành hàm không nhận `self`. DRF còn dùng decorator như `@api_view`, `@action` ở các project lớn hơn.

**Vì sao quan trọng cho Django/DRF:** rất nhiều “magic chạy ngầm” (authentication, permission check, transaction `@transaction.atomic`, cache `@cache_page`) đều là decorator/cơ chế tương tự. Hiểu decorator = hết thấy framework “ảo diệu”.

**Cạm bẫy:** quên `@functools.wraps` → mất `__name__`, `__doc__`, gây khó debug và một số introspection của framework sai.

---

## A8. `*args` / `**kwargs` & unpacking

**Bản chất:** `*` và `**` có 2 vai trò đối xứng:

| Ngữ cảnh | `*` | `**` |
|----------|-----|------|
| **Định nghĩa hàm** (gom lại) | `*args` → tuple các positional | `**kwargs` → dict các keyword |
| **Gọi hàm** (bung ra) | `f(*mylist)` bung list thành positional | `f(**mydict)` bung dict thành keyword |

**Trong repo (`post/services.py`):**
```python
@staticmethod
def create(author, validated_data):
    return Post.objects.create(author=author, **validated_data)
    #                                          ^^^^^^^^^^^^^^^^
    # nếu validated_data = {"title": "x", "content": "y"}
    # thì tương đương: Post.objects.create(author=author, title="x", content="y")
```
→ Nhờ vậy `create` **không cần biết trước** Post có những field nào — thêm field mới vào model, code service không phải sửa.

**Cạm bẫy:** `**` yêu cầu key là **string hợp lệ làm tên biến** và **không trùng** tham số đã truyền (`f(author=1, **{"author":2})` → `TypeError: multiple values`).

---

## A9. `setattr` / `getattr` / introspection

**Bản chất:** Python cho phép thao tác attribute **bằng tên dạng string** lúc runtime — vì mọi object lưu attribute trong `__dict__`.

```python
getattr(obj, "title")          # = obj.title
getattr(obj, "title", default) # an toàn nếu không có attr
setattr(obj, "title", "x")     # = obj.title = "x"
hasattr(obj, "title")          # True/False
```

**Trong repo (`post/services.py`):**
```python
@staticmethod
def update(post, validated_data):
    for attr, value in validated_data.items():
        setattr(post, attr, value)   # gán động: post.title=..., post.content=...
    post.save()
    return post
```
→ Đây là **partial update tổng quát**: chỉ field nào có trong `validated_data` mới bị set. Không cần `post.title = data["title"]; post.content = data["content"]; ...` thủ công.

**An toàn / cạm bẫy:** `setattr` không validate — nó tin `validated_data` đã được **Serializer làm sạch** (xem B4). Nếu bỏ qua serializer mà `setattr` thẳng từ `request.data` → có thể bị **mass assignment** (gán field nhạy cảm như `is_admin`). Bài học: luôn `setattr` từ `validated_data`, không từ input thô.

---

# PHẦN B — DJANGO & DRF

## B1. Vòng đời 1 request (WSGI → Middleware → View → Response)

**Nó xử lý gì, theo thứ tự:**
```
1. Web server (gunicorn/runserver) nhận HTTP, dựng đối tượng theo chuẩn WSGI
2. Django tạo HttpRequest
3. MIDDLEWARE chạy lần lượt (settings.py):
   SecurityMiddleware → SessionMiddleware → CommonMiddleware
   → CsrfViewMiddleware → AuthenticationMiddleware → ...
4. URL resolver: care_mate/urls.py → api/ → core/urls.py → post/urls.py
5. View được gọi (APIView.dispatch — xem B5)
6. Response đi NGƯỢC qua middleware → trả client
```
**Middleware là gì:** lớp bọc xử lý *trước* và *sau* mọi request (bảo mật, session, CSRF...). Thứ tự trong list = thứ tự áp dụng. Đây là một dạng **pattern decorator ở tầng kiến trúc** (liên hệ A7).

---

## B2. ORM & QuerySet — **tính LAZY là chìa khóa**

**Bản chất:** ORM ánh xạ class Python ↔ bảng DB. `Post.objects` là một **Manager**; `.all()/.filter()` trả về **QuerySet**.

**⭐ QuerySet LAZY — không chạy SQL ngay:**
```python
posts = Post.objects.all()                       # CHƯA query DB
posts = posts.filter(title__icontains="abc")     # vẫn CHƯA query, chỉ build câu SQL
# SQL chỉ chạy khi BẮT BUỘC có dữ liệu:
list(posts)        # ← lúc này mới SELECT
for p in posts: ...# ← hoặc lúc này
posts[0]           # ← hoặc indexing
len(posts)         # ← hoặc đếm
```
→ Trong repo (`post/services.py`), `get_queryset` build filter chồng nhau rồi mới được pagination cắt trang → **không load hết DB vào RAM**. Với DRF page-number pagination, DB thường chạy 2 việc: một query `COUNT(*)` để tính tổng record/trang, và một query lấy page hiện tại bằng `LIMIT/OFFSET`. Đây vẫn tốt hơn rất nhiều so với `list(Post.objects.all())` rồi tự cắt bằng Python.

**Vì sao trả về QuerySet thay vì list:**
```python
posts = PostService.get_queryset(request.query_params)  # QuerySet lazy
page = paginator.paginate_queryset(posts, request)      # lúc này mới cắt page
```
Nếu `get_queryset()` trả `list`, toàn bộ record đã bị load trước pagination → tốn RAM, chậm, và pagination không còn đẩy việc cắt trang xuống DB.

**Field lookup (cú pháp `__`):**
```python
title__icontains="x"  # WHERE title LIKE '%x%' (i = case-insensitive)
created_at__gte=date  # >=
author__username="a"  # join sang bảng user, lọc theo username
```

**⚠️ Cạm bẫy N+1 query (quan trọng cho list endpoint):**
```python
for post in Post.objects.all():
    print(post.author.username)   # mỗi vòng lặp = 1 query phụ tới bảng user!
# 100 post → 1 + 100 = 101 query
```
**Khắc phục:**
- `select_related("author")` → JOIN sẵn (cho ForeignKey/OneToOne) → 1 query.
- `prefetch_related(...)` → cho ManyToMany/reverse FK.
→ Trong repo, `PostSerializer.get_author_username` đọc `obj.author.username`. Khi list nhiều post **nên** đổi `get_queryset` thành `Post.objects.select_related("author").all()` để tránh N+1. (Hiện chưa có — đây là điểm tối ưu thực tế.)

**Migration liên quan:** `Post.objects.create(...)` ghi vào bảng `core_post` (do `db_table='core_post'` trong model) — xem B3.

---

## B3. Migration & **lineage** (điểm rủi ro thật của repo)

**Bản chất:** migration là **lịch sử thay đổi schema** dưới dạng file Python có thứ tự (`0001`, `0002`...), mỗi file `depends_on` file trước → tạo thành **chuỗi (lineage)**. Django lưu migration nào đã chạy trong bảng `django_migrations`.

**Nó xử lý gì:** `makemigrations` (so model với state hiện tại → sinh file diff) và `migrate` (áp file lên DB theo đúng thứ tự dependency).

**⚠️ Trong repo này — case học rất hay:**
```
core/migrations/0001_initial.py
core/migrations/0002_post_author.py
core/migrations/0003_move_post_to_post_app.py   ← Post được "chuyển" từ app core sang app post
post/migrations/0001_initial.py
post/models.py → class Post(...): db_table = 'core_post'   ← vẫn TRỎ bảng cũ 'core_post'
```
**Diễn giải chính xác theo migration thật:** Post ban đầu nằm trong app `core`, sau được tách sang app `post` nhưng **giữ nguyên tên bảng vật lý** `core_post` để không phải migrate dữ liệu.

Luồng migration đang là:
```python
# core/migrations/0003_move_post_to_post_app.py
migrations.SeparateDatabaseAndState(
    state_operations=[migrations.DeleteModel(name='Post')],
)
```
File này nói với Django: “trong state của app `core`, model `Post` không còn nữa”, nhưng **không drop bảng DB thật**.

Sau đó:
```python
# post/migrations/0001_initial.py
dependencies = [('core', '0003_move_post_to_post_app'), ...]
migrations.SeparateDatabaseAndState(
    state_operations=[migrations.CreateModel(..., options={'db_table': 'core_post'})]
)
migrations.RunPython(update_content_type, migrations.RunPython.noop)
```
File này nói với Django: “trong state của app `post`, có model `Post`, nhưng nó map vào bảng cũ `core_post`”. `RunPython(update_content_type)` cập nhật `django_content_type` từ `core.post` sang `post.post` để permission/admin/content type không bị lệch.

→ Đây là kỹ thuật **đổi ownership model ở state của Django** mà không đổi bảng vật lý. Cần cực kỳ cẩn thận vì nếu dependency sai, Django có thể tưởng cần tạo/drop bảng.

**Bài học bảo mật/release:**
- Khi deploy lên môi trường đã có DB cũ, **thứ tự & dependency migration phải khớp** — nếu chạy lệch, Django tưởng phải tạo lại bảng → có thể mất dữ liệu hoặc lỗi “table already exists”.
- Đổi `db_table` mà không cẩn thận = **schema divergence** giữa dev và prod.
- Quy tắc: trước khi tạo migration mới luôn chạy `python manage.py makemigrations --check` và review file sinh ra; không sửa tay migration đã apply ở prod.

---

## B4. Serializer — validate + chuyển đổi 2 chiều

**Bản chất:** Serializer của DRF làm 2 việc:
- **Deserialize (vào):** `request.data` (dict thô) → validate → `validated_data` (dict sạch, đúng kiểu).
- **Serialize (ra):** model/queryset → dict/JSON.

**Luồng validate (`is_valid()`) xử lý gì, theo thứ tự:**
```
1. Field-level: kiểu, required, max_length, min_length...   (vd password min_length=6)
2. validate_<field>(self, value): custom 1 field
3. validate(self, attrs): custom nhiều field (vd password == confirm)
→ Pass: dồn vào serializer.validated_data
→ Fail: dồn vào serializer.errors (dict {field: [lỗi]})
```

**Trong repo (`user/serializers.py`):**
```python
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
    def create(self, validated_data):
        return User.objects.create_user(...)   # hash password TỰ ĐỘNG
```
- `write_only=True` → password **nhận vào được, nhưng KHÔNG bao giờ xuất ra** response. ⭐ Đây là điểm bảo mật cốt lõi: tránh lộ mật khẩu.
- `ModelSerializer` tự suy field từ model → đỡ khai báo tay.

**Quan trọng: `serializer.create()` chỉ chạy khi nào?**
Trong DRF, method `create()` của serializer **không tự chạy khi gọi `is_valid()`**. Nó chỉ chạy khi gọi `serializer.save()`:
```python
serializer = RegisterSerializer(data=request.data)
serializer.is_valid(raise_exception=True)
user = serializer.save()   # DRF gọi RegisterSerializer.create(validated_data)
```

Nhưng repo này đang dùng flow khác trong `user/views.py`:
```python
serializer = RegisterSerializer(data=request.data)
if not serializer.is_valid(): ...
user = AuthService.register(serializer.validated_data)
```
→ Nghĩa là `RegisterSerializer.create()` hiện **không được gọi** trong register API. Password vẫn được hash an toàn vì `AuthService.register()` gọi `User.objects.create_user(...)`, nhưng khi học phải nhớ rõ ranh giới:
- `is_valid()` chỉ validate và tạo `validated_data`.
- `serializer.save()` mới gọi `create()` hoặc `update()` của serializer.
- Repo này cố ý đưa bước tạo user sang **service layer**, nên view gọi `AuthService.register(...)` thay vì `serializer.save()`.

**Bài học DRF:** có 2 style hợp lệ:
```python
# Style 1: serializer validate và tự tạo object
serializer.is_valid(raise_exception=True)
user = serializer.save()

# Style 2: serializer chỉ validate, service chịu trách nhiệm business logic
serializer.is_valid(raise_exception=True)
user = AuthService.register(serializer.validated_data)
```
Repo này theo style 2. Đừng nhầm `create()` trong serializer là lúc nào cũng chạy.

**`PostSerializer` (`post/serializers.py`):**
```python
class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()   # field "ảo", tính toán
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['author']        # client KHÔNG được tự set author
    def get_author_username(self, obj):       # quy ước: get_<tên field>
        return obj.author.username if obj.author else None
```
- `SerializerMethodField` = field read-only, giá trị do hàm `get_<field>` trả → dùng để “nhồi” dữ liệu cho client mà không cần gọi thêm API.
- `read_only_fields=['author']` ⭐ **chống mass assignment**: dù client gửi `author=999`, serializer bỏ qua; author được gán ở service từ `request.user`.
- `if obj.author else None` → **null-safety cho client** (Dart/Flutter): field luôn có, hoặc string hoặc null, không bao giờ ném lỗi attribute.

**Cạm bẫy:** `fields='__all__'` tiện nhưng nguy hiểm khi model có field nhạy cảm — nó sẽ phơi hết. Ở repo này Post không có field nhạy cảm nên ổn, nhưng với User thì phải liệt kê tay (đúng như `RegisterSerializer` đang làm).

---

## B5. APIView & `dispatch()` — vì sao `def get/post` lại tự chạy

**Bản chất:** `APIView` kế thừa Django `View`. Khi URL trỏ tới `View.as_view()`, request đi vào method `dispatch()`:
```
dispatch(request):
  1. initialize_request()  → bọc thành DRF Request (có .data, .query_params)
  2. perform_authentication() → chạy DEFAULT_AUTHENTICATION_CLASSES → gắn request.user
  3. check_permissions()      → chạy permission_classes (has_permission)
  4. Chọn handler theo HTTP method: GET→self.get, POST→self.post, PUT→self.put...
  5. Gọi handler, nhận Response
  6. finalize_response() → render ra JSON
```
→ Đây là lý do bạn chỉ cần viết `def post(self, request)` mà không gọi tay: `dispatch` route giúp.

**Trong repo:** `check_object_permissions` được gọi **thủ công** trong `PostUpdate/PostDelete`:
```python
def put(self, request, pk):
    post = PostService.get_by_id(pk)
    self.check_object_permissions(request, post)   # ← bước 3 ở cấp OBJECT
```
Vì `dispatch` chỉ tự chạy `check_permissions` (cấp view, `has_permission`), còn **object-level** (`has_object_permission`) phải tự gọi sau khi đã lấy được object. Quên dòng này = lỗ hổng phân quyền (ai cũng sửa được post người khác).

---

## B6. Authentication vs Permission — phân biệt tận gốc

| | **Authentication** | **Permission** |
|--|--------------------|----------------|
| Câu hỏi | “Bạn LÀ AI?” | “Bạn ĐƯỢC LÀM không?” |
| Output | `request.user` (User hoặc AnonymousUser) | cho qua / chặn (403/401) |
| Repo | `JWTAuthentication` (settings) | `IsAuthenticated` (default), `AllowAny`, `IsAuthor` |
| Khi nào fail | token sai/hết hạn → 401 | đúng người nhưng không đủ quyền → 403 |

**Cấu hình global (`settings.py`):**
```python
REST_FRAMEWORK = {
  'DEFAULT_AUTHENTICATION_CLASSES': ('...JWTAuthentication',),  # ai cũng bị soi token
  'DEFAULT_PERMISSION_CLASSES': ('...IsAuthenticated',),        # MẶC ĐỊNH: phải đăng nhập
}
```
→ Vì default là `IsAuthenticated`, nên view public **phải override** `permission_classes=[AllowAny]` (như `PostList`, `PostDetail`). Đây là tư duy **secure by default**: quên set thì mặc định là *khóa*, an toàn hơn mặc định *mở*.

**⚠️ Điểm cần nhìn thật kỹ trong repo:**
```python
class RegisterView(APIView):
    def post(self, request): ...
```
`RegisterView` hiện **chưa khai báo** `permission_classes = [AllowAny]`, trong khi global default là `IsAuthenticated`. Về nguyên tắc DRF, endpoint register có thể bị chặn vì user chưa đăng nhập. Cách sửa đúng thường là:
```python
from rest_framework.permissions import AllowAny

class RegisterView(APIView):
    permission_classes = [AllowAny]
```
`LoginView` kế thừa SimpleJWT `TokenObtainPairView`, class gốc thường public để user chưa đăng nhập vẫn lấy token được. Nhưng với `RegisterView` tự viết bằng `APIView`, muốn public thì phải set rõ.

**Bài học:** secure by default tốt, nhưng endpoint như `login`, `register`, `forgot-password`, public list/detail phải được review explicit permission. Đừng assume “đăng ký thì chắc public” nếu code không ghi.

**`IsAuthor` (`core/permissions.py`):**
```python
class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
```
- `has_permission` (cấp view) vs `has_object_permission` (cấp object) — xem B5.
- So sánh `obj.author == request.user` → chỉ tác giả mới qua.

---

## B7. ⭐⭐ JWT — đào sâu nhất (theo đúng câu hỏi của bạn)

### B7.1 JWT là gì?
**JSON Web Token** = một chuỗi text dùng để **chứng minh danh tính** giữa client và server mà **server không cần lưu session**. Đây là cơ chế **stateless authentication**: thông tin user nằm ngay trong token, server chỉ cần *xác minh chữ ký*.

### B7.2 Cấu trúc — JWT lưu những gì?
JWT gồm **3 phần nối bằng dấu chấm**: `HEADER.PAYLOAD.SIGNATURE`
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 . eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjox... . SflKxwRJSMeKKF2QT4f...
└──────── HEADER ────────┘   └──────────── PAYLOAD ────────────┘   └──── SIGNATURE ────┘
```

**1) HEADER** (base64url của JSON) — metadata thuật toán:
```json
{ "alg": "HS256", "typ": "JWT" }
```

**2) PAYLOAD** (base64url) — các **claim** (thông tin). Với simplejwt (repo này), access token mặc định chứa:
```json
{
  "token_type": "access",
  "exp": 1716800000,    // expiry (Unix timestamp) — TÍNH từ ACCESS_TOKEN_LIFETIME=1 ngày
  "iat": 1716713600,    // issued at — lúc cấp
  "jti": "a1b2c3...",   // JWT ID — mã định danh duy nhất của token
  "user_id": 42         // ⭐ thứ server dùng để biết "bạn là ai" → load User
}
```
→ **JWT KHÔNG lưu password.** Nó lưu `user_id` + thời hạn + loại token. Khi request đến, simplejwt đọc `user_id` → `User.objects.get(id=user_id)` → gắn `request.user`.

**3) SIGNATURE** — chữ ký chống giả mạo:
```
HMAC-SHA256( base64url(header) + "." + base64url(payload), SECRET_KEY )
```

### B7.3 JWT xử lý gì (luồng đầy đủ trong repo)
```
ĐĂNG NHẬP (user/views.py: LoginView → TokenObtainPairView):
1. POST /api/auth/login/ {username, password}
2. simplejwt verify username/password với DB (so hash)
3. Đúng → tạo access (1 ngày) + refresh (7 ngày), ký bằng SECRET_KEY
4. Trả {access, refresh}

GỌI API CẦN AUTH (vd POST /api/posts/create/):
5. Client gửi Header: Authorization: Bearer <access_token>
6. JWTAuthentication (settings): tách token → verify chữ ký → check exp
7. Hợp lệ → đọc user_id → load User → request.user = user đó
8. Permission check (IsAuthenticated) → vào view
```

### B7.4 Bảo mật — JWT an toàn ra sao? (phần quan trọng nhất)

**✅ Cái JWT BẢO VỆ được:**
- **Chống sửa nội dung (tampering):** đổi 1 ký tự trong payload (vd `user_id: 42 → 1`) → signature không khớp → server từ chối. Vì attacker không có `SECRET_KEY` nên **không ký lại được**.

**❌ Cái JWT KHÔNG bảo vệ — phải nhớ:**
1. **JWT KHÔNG mã hóa, chỉ KÝ.** Payload là base64 — *ai cũng decode đọc được* (vào jwt.io dán vào là thấy `user_id`). → **TUYỆT ĐỐI không nhét dữ liệu nhạy cảm** (password, số thẻ) vào payload.
2. **Stateless = khó thu hồi.** Token đã cấp thì **valid tới khi hết hạn** (`exp`), kể cả khi user đổi mật khẩu hay logout. Repo này **chưa cài blacklist app** của simplejwt → không revoke được token sớm. Đây là rủi ro nếu token bị lộ.
3. **SECRET_KEY lộ = thảm họa.** Ai có key → tự ký token với `user_id` bất kỳ → giả mạo mọi user.
   ⚠️ **Trong repo:** `settings.py` đang dùng `SECRET_KEY = 'django-insecure-...'` (key mặc định Django sinh) **hardcode trong code + DEBUG=True**. simplejwt mặc định ký bằng chính `SECRET_KEY` này (HS256). → **Trước khi lên production BẮT BUỘC** đổi `SECRET_KEY` thành biến môi trường ngẫu nhiên đủ dài, `DEBUG=False`.

**🛡️ Phòng thủ chuẩn (nên áp dụng):**
- Truyền token chỉ qua **HTTPS** (tránh nghe lén trên đường truyền).
- Access token **sống ngắn** (repo: 1 ngày — với app thật nên ngắn hơn, vài phút–vài giờ), refresh token dài hơn và xoay vòng (`ROTATE_REFRESH_TOKENS`).
- Bật **token blacklist** để logout/đổi mật khẩu thu hồi được token.
- Lưu token client: web nên cân nhắc **HttpOnly cookie** thay vì `localStorage` (chống XSS đọc trộm). Repo demo dùng `localStorage` cho đơn giản.

### B7.5 Access vs Refresh token
| | Access | Refresh |
|--|--------|---------|
| Dùng để | gọi API | xin access token mới khi access hết hạn |
| Tuổi thọ (repo) | 1 ngày | 7 ngày |
| Gửi kèm mỗi request? | Có (Bearer) | Không — chỉ gửi khi refresh |
→ Mục đích tách: access ngắn để giảm thiệt hại nếu lộ; refresh dài để user không phải đăng nhập lại liên tục.

---

## B8. Pagination — vì sao cần & nó xử lý gì

**Bản chất:** chia danh sách lớn thành **trang** → chỉ query + trả về 1 phần → tránh load 10.000 record vào RAM & qua mạng.

**Trong repo (`core/panigation.py`):**
```python
class CustomPagination(PageNumberPagination):
    page_size = 10                       # mặc định 10/trang
    page_size_query_param = "limit"      # client gọi ?limit=20 để đổi
```
Tên file hiện là `panigation.py` — gần như chắc là typo của `pagination.py`. Tài liệu dùng đúng tên file hiện tại để bạn mở code không bị lạc, nhưng trong project thật nên đặt lại thành `pagination.py` để code dễ đọc hơn.
- `paginate_queryset(qs, request)` → cắt QuerySet bằng SQL `LIMIT/OFFSET` (nhờ QuerySet lazy ở B2, **không load toàn bộ record vào RAM**; thường có thêm query `COUNT(*)` để tính tổng trang).
- `get_paginated_response(data)` được override để trả metadata: `total_pages`, `current_page`, `total_records`...
- `format_non_paginated` → khi không phân trang vẫn giữ **cùng shape** → client (Flutter) parse 1 kiểu duy nhất (nhất quán = ít bug null).

**Cạm bẫy thực tế:** OFFSET lớn (trang 9999) chậm dần trên DB lớn → app thật cân nhắc *cursor pagination*. Với demo thì PageNumber ổn.

---

## B9. DRF `Response` & rendering

**Bản chất:** `Response(data, status=...)` của DRF khác `HttpResponse` thường: nó nhận **Python data thô** (dict/list) và **hoãn render** đến cuối `dispatch` — lúc đó *renderer* (mặc định JSONRenderer) biến nó thành JSON + set `Content-Type: application/json`.

**Trong repo (`core/response.py`):** `success_response`/`error_response` chỉ là **wrapper** đảm bảo mọi response có cùng khung:
```python
{ "is_success": bool, "status": int, "status_message": str, "msg_code": str, "data": ... }
```
→ Lợi ích: client check **1 field `is_success`** thay vì phải hiểu mọi HTTP status. `status=` vẫn set đúng HTTP code (200/201/400/403) cho đúng chuẩn REST, nhưng thân JSON thì thống nhất.

---

## B10. Settings & Middleware (cấu hình toàn cục)

**`settings.py` xử lý gì:** điểm cấu hình trung tâm — DB, app, middleware, REST framework, JWT, templates.
```python
INSTALLED_APPS = [..., 'rest_framework', 'core', 'post', 'user']  # Django thấy app nào
DATABASES = { 'default': { 'ENGINE': 'django.db.backends.mysql', ... os.getenv ... } }
```
- ⭐ Dùng `os.getenv('MYSQL_PASSWORD', 'default')` → **đọc từ biến môi trường** (12-factor), tách config khỏi code. (Nhưng password mặc định `'12345678'` đang để trong code/compose — chỉ chấp nhận cho demo.)
- `REST_FRAMEWORK`, `SIMPLE_JWT` → cấu hình DRF & JWT (B6, B7).

**Cạm bẫy production:** `DEBUG=True` + `SECRET_KEY` hardcode + `ALLOWED_HOSTS` lỏng = không được lên prod. Checklist: `python manage.py check --deploy`.

---

## B11. Service Layer — tổng kết “vì sao tách”

**Vấn đề nếu KHÔNG có service:** logic nghiệp vụ nằm lẫn trong View → View vừa lo HTTP vừa lo DB → khó test (phải dựng request giả), khó tái dùng, đổi DB phải sửa View.

**Service giải quyết (repo):** `PostService`/`AuthService` là class chứa `@staticmethod`, **nhận data nghiệp vụ trả object/data nghiệp vụ**, không import `request`/`Response`:
```python
PostService.create(request.user, serializer.validated_data)   # View đưa data sạch vào
```
**3 lợi ích cụ thể:**
1. **Test dễ:** `PostService.create(user, {...})` gọi thẳng, không cần Django test client.
2. **Tái dùng:** gọi được từ View khác, management command, Celery task, CLI.
3. **Cô lập thay đổi:** đổi cách tạo/cập nhật/xóa object → thường sửa service, View ít bị ảnh hưởng. Riêng đổi MySQL→Postgres vẫn cần sửa settings, migration/index/query behavior; service layer không “miễn nhiễm” hoàn toàn, nhưng giúp business logic tập trung hơn.

**Quy tắc ranh giới (nhớ):** Service **không được** biết HTTP (`request`, `Response`, status code). Việc đó là của View. Đây là biểu hiện của nguyên lý **Separation of Concerns**.

**Ranh giới chuẩn trong repo:**
| Thành phần | Nên làm | Không nên làm |
|------------|---------|---------------|
| Serializer | validate input, convert model ↔ dict, khai báo field public/read-only | chứa business flow phức tạp, gọi API ngoài, tự quyết permission |
| View/APIView | nhận request, chọn serializer, gọi service, trả response | nhét query/update phức tạp trực tiếp vào view |
| Service | nghiệp vụ, ORM operation, transaction nếu có nhiều bước DB | import `request`, trả `Response`, phụ thuộc HTTP status |
| Permission | quyết định user có quyền hay không | query/update dữ liệu nghiệp vụ |

**Flow cần thuộc lòng:**
```python
request.data                # dữ liệu thô từ client, chưa tin được
serializer.is_valid()       # validate
serializer.validated_data   # dữ liệu sạch, đã đúng kiểu/field
Service.do_something(...)   # xử lý nghiệp vụ / ORM
Serializer(instance).data    # biến object thành dict trả client
success_response(...)       # bọc response shape thống nhất
```
Sai lầm hay gặp là dùng thẳng `request.data` trong service hoặc `setattr()` trực tiếp từ input thô. Repo làm đúng ở `PostService.update()` vì nó nhận `serializer.validated_data`, không nhận `request.data`.

---

## 🧪 BÀI TẬP ĐÀO SÂU (tự kiểm chứng hiểu)

1. **A2:** Viết lại `get_queryset(filters=[])` rồi giải thích vì sao nó nguy hiểm, sửa thành đúng.
2. **B2:** Thêm `select_related("author")` vào `PostService.get_queryset` — đo số query trước/sau với `django-debug-toolbar` hoặc `connection.queries`.
3. **B5:** Xóa dòng `self.check_object_permissions(...)` trong `PostUpdate` → thử cho user A sửa post của user B → quan sát lỗ hổng. Rồi khôi phục.
4. **B7:** Lấy 1 access token, dán vào jwt.io, đọc payload → xác nhận thấy `user_id` nhưng KHÔNG thấy password. Thử sửa 1 ký tự payload → gọi API → quan sát bị 401.
5. **B7:** Giải thích điều gì xảy ra với token đang hợp lệ nếu user đổi mật khẩu — vì sao (gợi ý: stateless + chưa có blacklist).
6. **B3:** Mở `core/migrations/0003_move_post_to_post_app.py`, xác định nó dùng operation gì để đổi app mà không mất dữ liệu.
7. **B4:** Thử thêm `print("serializer create called")` trong `RegisterSerializer.create()`, gọi API register và quan sát nó không chạy. Sau đó đổi view sang `serializer.save()` để hiểu DRF gọi `create()` khi nào.
8. **B6:** Thêm `permission_classes = [AllowAny]` vào `RegisterView`, rồi so sánh behavior trước/sau khi global default permission là `IsAuthenticated`.
