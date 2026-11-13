# ZAC 2026 LifeMate: nhật ký học tập

Ghi chép quá trình mình học và làm bài toán **LifeMate** trong cuộc thi **Zalo AI Challenge 2026**: xây dựng trợ lý giọng nói tiếng Việt biết chọn và gọi đúng công cụ (tool) của các ứng dụng giả lập (lịch, danh bạ, tin nhắn, ngân hàng, nhà thông minh...).

Mình là sinh viên năm 2 ngành Robotics và AI, đây là lần đầu mình thi một cuộc thi AI kiểu này. Repo này ghi lại **cách mình học**: mỗi giai đoạn gồm mục tiêu, các bước làm, đoạn code, kết quả và bài học, kể cả những suy đoán đã bị dữ liệu bác bỏ.

> **Lưu ý:** repo không chứa dữ liệu, âm thanh, file nhãn, schema công cụ hay thư viện của ban tổ chức. Ví dụ trong tài liệu là ví dụ tự soạn. Repo này là ghi chép cá nhân, không phải tài liệu chính thức của cuộc thi.

## Bài toán trong một đoạn

Người dùng nói một yêu cầu, ví dụ *"Mai mưa thì dời lịch chạy bộ, nhắn giúp mình cho anh An"*. Hệ thống nghe, hiểu, rồi gọi đúng chuỗi công cụ: xem thời tiết, tìm lịch, sửa lịch, tra danh bạ, gửi tin nhắn. Kết quả được chấm theo trạng thái dữ liệu cuối cùng và mức độ khớp của các lệnh gọi so với đáp án chuẩn.

## Tiến độ

| Giai đoạn | Nội dung | Trạng thái |
|---|---|---|
| 0 | Đọc luật, dựng môi trường (Python, môi trường ảo, thư viện chạy công cụ) | Xong |
| 1 | Làm quen dữ liệu: cấu trúc một mẫu, các loại tình huống đặc biệt, thống kê | Xong |
| 2 | Tự chạy môi trường công cụ bằng tay, quan sát kết quả trả về | Sắp làm |
| 3 | Bản agent đầu tiên (chữ vào, lệnh gọi ra) | Dự kiến |
| 4 | Tự chấm điểm trên tập huấn luyện và phân tích lỗi | Dự kiến |
| 5 | Thêm nhận dạng giọng nói | Dự kiến |
| 6 | Cải tiến | Dự kiến |
| 7 | Đóng gói và nộp bài | Dự kiến |

## Nội dung repo

```
docs/
  giai-doan-1.md    Nhật ký Giai đoạn 1: làm quen dữ liệu
scripts/
  view.py           In các mẫu huấn luyện dưới dạng dễ đọc
  stats.py          Thống kê toàn bộ tập huấn luyện
```

Hai script chỉ **đọc** dữ liệu huấn luyện và cần chạy từ thư mục chứa dữ liệu của cuộc thi (không có trong repo này).

## Một vài điều mình đã học được

- Hơn một nửa số mẫu có lịch sử hội thoại, nên hiểu ngữ cảnh là bắt buộc.
- Đáp án chuẩn thường ngắn (khoảng 75% mẫu có 1 đến 3 lệnh), và gần một nửa số lệnh là lệnh **đọc** để lấy mã định danh trước khi **ghi**.
- Một giả thuyết hợp lý về thói quen của đáp án chuẩn đã bị thống kê bác bỏ. Chi tiết trong [`docs/giai-doan-1.md`](docs/giai-doan-1.md).

## Công nghệ

Python 3, chạy trên Ubuntu. Các giai đoạn sau dự kiến dùng mô hình nhận dạng giọng nói và mô hình ngôn ngữ nhỏ chạy offline, theo đúng giới hạn của cuộc thi.
