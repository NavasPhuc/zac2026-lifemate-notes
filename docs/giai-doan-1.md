# Giai đoạn 1: Làm quen dữ liệu

> Nhật ký học tập của mình trong cuộc thi Zalo AI Challenge 2026 (bài toán LifeMate: trợ lý giọng nói tiếng Việt gọi công cụ). Mình là sinh viên năm 2 ngành Robotics và AI, đây là lần đầu mình thi một cuộc thi AI kiểu này.
>
> **Lưu ý:** tài liệu này không chứa dữ liệu của cuộc thi. Các ví dụ bên dưới là ví dụ mình tự soạn, có cấu trúc tương tự dữ liệu thật. Các con số thống kê là kết quả mình tự đếm trên tập huấn luyện.

## 1. Bài toán trong một đoạn

Người dùng nói một yêu cầu bằng tiếng Việt, ví dụ *"Mai mưa thì dời lịch chạy bộ, nhắn giúp mình cho anh An"*. Hệ thống phải chọn đúng các "công cụ" (tool) của các ứng dụng giả lập (lịch, danh bạ, tin nhắn, thời tiết...) và điền đúng thông tin để việc đó được thực hiện. Kết quả được chấm dựa trên **trạng thái dữ liệu cuối cùng** và **mức độ khớp của danh sách lệnh gọi** so với đáp án chuẩn.

Mục tiêu của Giai đoạn 1: hiểu "đề" và "đáp án" trông như thế nào **trước khi** viết bất kỳ mô hình nào.

## 2. Thuật ngữ

| Từ | Nghĩa dễ hiểu |
|---|---|
| Agent | Chương trình tự quyết định bước tiếp theo (ở đây: chọn công cụ nào để gọi) |
| Tool / tool call | Một "nút bấm" trong một app / một lần bấm nút đó kèm thông tin điền vào |
| Tham số (argument) | Thông tin điền vào một tool, ví dụ ngày `2026-11-29` |
| ASR | Chuyển giọng nói thành chữ |
| LLM | Mô hình ngôn ngữ lớn, "bộ não" hiểu chữ và quyết định |
| JSONL | File mà mỗi dòng là một mẫu dữ liệu |
| Train / test | Train: có đáp án để học. Test: không có đáp án, để chấm |
| Tool `read` / `write` | Tool chỉ xem thông tin / tool làm thay đổi dữ liệu |

## 3. Cấu trúc một mẫu dữ liệu

Mỗi dòng trong file huấn luyện là một "hồ sơ" gồm nhiều phần có tên. Dưới đây là cấu trúc với ví dụ do mình tự soạn:

```
mẫu
├── id            "train_xxxx"                  mã mẫu
├── audio         đường dẫn file ghi âm
├── audio_text    "Mai mưa thì dời lịch ..."    câu người nói (chỉ tập train có)
├── context       bối cảnh lúc nói
│     ├── current_time    giờ hiện tại (dùng để hiểu "mai", "tối nay")
│     ├── user_profile    tên, địa chỉ nhà, thành phố
│     └── installed_apps  các app được phép dùng và tool của từng app
├── history       các lượt hội thoại trước đó (có thể rỗng)
└── label         ĐÁP ÁN (chỉ tập train có)
      ├── tool_calls      danh sách lệnh đúng cần gọi
      ├── tool_results    kết quả trả về của từng lệnh (cùng thứ tự)
      └── final_state     dữ liệu app sau khi làm xong
```

**Cách đọc:** muốn lấy thông tin gì, mở lần lượt từng "ngăn" theo tên. Ví dụ giờ hiện tại nằm ở `item["context"]["current_time"]`.

### Tính liên kết: "mã số dẫn đường"

Người nói chỉ nói tên ("anh An"), nhưng tool gửi tin nhắn cần **mã** của người đó. Mã này chỉ có sau khi tra danh bạ. Vì vậy đáp án luôn có dạng:

```
contacts.search {"query": "An"}          → trả về mã c_xx
sms.send {"contact_id": "c_xx", ...}     → dùng mã vừa lấy
```

Nguyên tắc: **đọc trước, ghi sau**. `tool_calls` và `tool_results` là hai danh sách cùng thứ tự: lệnh thứ n tương ứng kết quả thứ n. Tham số kiểu "chọn trong danh sách" (mã, số tiền, ngày) phải khớp chính xác, còn văn bản tự do (nội dung tin nhắn) được chấm gần đúng.

## 4. Các bước đã làm

### Bước 1: Xem vài mẫu đầu bằng `scripts/view.py`

**Mục đích:** file dữ liệu thô là một khối chữ rất dài. Mình viết một "kính lúp" nhỏ để in từng thông tin trên một dòng.

**Cách dùng:** `python3 view.py <vị trí bắt đầu> <số mẫu>`. Vị trí đếm từ 0.

**Các dòng chính:**

| Code | Việc nó làm |
|---|---|
| `json.loads(line)` | Đổi một dòng chữ thành dữ liệu Python để lấy từng ngăn |
| `item["context"]["current_time"]` | Mở ngăn `context`, rồi ngăn `current_time` |
| `item.get("audio_text")` | Giống `item["audio_text"]` nhưng không báo lỗi nếu ngăn không tồn tại (cần vì tập test không có `audio_text`) |
| `json.dumps(..., ensure_ascii=False)` | In tham số mà giữ nguyên dấu tiếng Việt |

**Hạn chế:** chỉ in câu nói và đáp án, chưa in `tool_results`; cắt phần history ở 300 ký tự.

### Bước phụ: Đọc "sách hướng dẫn" của một tool

Mỗi tool được mô tả bằng một khối gồm: `name`, `kind` (read/write/meta), `description`, `parameters` (các ô cần điền), `required` (ô bắt buộc). Một số tham số có dấu hiệu đặc biệt: `x-match: fuzzy` (chấm gần đúng), `x-ref` (phải là mã hợp lệ trong dữ liệu app), `x-one-of` (cần ít nhất một trong các nhóm).

**Bài học:** chỉ điền tham số khi người nói có nhắc; tham số không bắt buộc mà tự thêm có thể khiến lệnh không khớp đáp án.

### Bước 2: Đếm các loại mẫu đặc biệt

Mình duyệt toàn bộ mẫu và bỏ vị trí của từng loại vào các "giỏ":

| Loại | Dấu hiệu | Số mẫu | Tỷ lệ |
|---|---|---|---|
| Có `history` | Câu cuối nối tiếp câu trước | 1.018 | khoảng 66% |
| Hỏi lại | Đáp án có `sys.ask_missing_info` | 217 | khoảng 14% |
| Ngoài phạm vi | Đáp án rỗng `[]` | 111 | khoảng 7% |

Ba loại này cho thấy agent không chỉ "bấm nút theo yêu cầu", mà còn phải: đọc lịch sử để hiểu "cái đó", biết khi nào nên hỏi lại, và biết khi nào **không làm gì**.

**Ba tình huống minh họa (ví dụ tự soạn):**

- *Hỏi lại:* người nói "gọi cho bạn Minh" nhưng có nhiều người tên Minh → thay vì đoán, agent hỏi lại với đúng tên tool định gọi và tham số còn thiếu.
- *Ngoài phạm vi:* người nói nhờ đặt phòng khách sạn, nhưng các app được cài không có app nào làm việc đó → đáp án rỗng. Gọi bất kỳ lệnh nào, kể cả lệnh chỉ đọc, đều bị 0 điểm mẫu đó.
- *Có history:* trước đó người dùng xoá một báo thức, câu cuối là "dời cái còn lại" → phải đọc lịch sử mới biết "cái còn lại" là báo thức nào.

Các lệnh nằm trong history đã được thực hiện sẵn và không bị chấm điểm; chỉ phần xử lý câu cuối mới được chấm.

### Bước 3: Chọn tool theo app được cài

Quyết định "có làm được hay không" dựa vào hai thứ theo thứ tự:
1. App nào được cài (`installed_apps`).
2. Tool bên trong app đó có làm được việc không.

Mình từng suy luận sai khi chỉ nhìn tên app. Bài học: **đừng đoán app làm được gì từ tên app, hãy đọc danh sách tool bên trong**. Chọn tool theo động từ trong câu nói: "đặt/tạo" thường là `create`, "đổi/dời" là `update`, "xoá/hủy" là `delete`, "xem" là `list`. Đây chỉ là quy tắc thường gặp, không tuyệt đối.

### Bước 4: Thống kê bằng `scripts/stats.py`

Dùng `Counter` (một cuốn sổ ghi vạch) để đếm trên toàn bộ tập huấn luyện:

| Số lệnh trong đáp án | Số mẫu | Tỷ lệ |
|---|---|---|
| 0 | 111 | 7% |
| 1 | 369 | 24% |
| 2 | 428 | 28% |
| 3 | 359 | 23% |
| 4 | 161 | 10% |
| 5 | 107 | 7% |
| 6 | 10 | dưới 1% |

- Tổng số mẫu: **1.545**. Khoảng 75% mẫu có 1 đến 3 lệnh; dài nhất 6 lệnh.
- Loại lệnh: `read` 1.599 (45%), `write` 1.725 (49%), `meta` 217 (6%).
- Số app cài sẵn mỗi mẫu: từ 3 đến 18, trung bình 9,2.
- Tool hay gặp nhất: tìm người trong danh bạ (234 lần), hỏi lại (217), điều khiển đèn (126), tạo lời nhắc (115), liệt kê hóa đơn (112).

**Ý nghĩa cho các giai đoạn sau:**

- Đáp án ngắn → vòng lặp của agent chỉ cần giới hạn vài bước, giúp giữ giới hạn thời gian 30 giây mỗi mẫu.
- Lệnh đọc chiếm gần nửa → "đọc trước, ghi sau" là quy luật thật sự, không phải thói quen.
- Tra danh bạ đứng đầu → làm tốt riêng bước này đã ảnh hưởng đến rất nhiều mẫu.

## 5. Một giả thuyết đã bị dữ liệu bác bỏ

Mình từng đoán rằng khi tạo báo thức, đáp án thường gọi lệnh xem danh sách báo thức trước. Mình kiểm tra bằng dữ liệu: trong 77 mẫu có lệnh tạo báo thức, chỉ **1 mẫu** có lệnh xem danh sách đi kèm, còn 76 mẫu thì không.

**Bài học:** cảm giác "hợp lý" không thay thế được việc đếm. Gọi thừa một lệnh đọc cũng làm tụt điểm, nên thói quen nào của đáp án chuẩn cũng nên được kiểm chứng bằng thống kê trước khi đưa vào agent.

## 6. Những điều mình rút ra

1. Hơn nửa số mẫu có lịch sử hội thoại, nên đọc `history` là bắt buộc.
2. Cứ khoảng 7 mẫu có 1 mẫu cần hỏi lại, cứ 14 mẫu có 1 mẫu cần không làm gì. Hai loại này ít nhưng sai là mất trọn điểm mẫu đó.
3. Thông tin lệnh sau cần thường nằm trong kết quả của lệnh trước.
4. Luôn kiểm chứng suy đoán bằng dữ liệu.

## 7. Bước tiếp theo

Giai đoạn 2: tự tạo một môi trường chạy công cụ cho một mẫu, gọi vài lệnh bằng tay và quan sát kết quả trả về cũng như cách trạng thái dữ liệu thay đổi.
