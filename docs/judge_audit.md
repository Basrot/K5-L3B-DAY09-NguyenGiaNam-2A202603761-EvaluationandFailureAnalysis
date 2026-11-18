# Judge audit — replay công khai

Nhãn `FAIL` là lớp dương. Lệnh kiểm tra: `python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5` và tương tự cho `judge_helpful_public.csv`.

| Tiêu chí | n | TP/FP/FN/TN | κ | Precision | Recall | Quyết định |
|---|---:|---|---:|---:|---:|---|
| tone_ok | 100 | 24/4/6/66 | 0.757 | 0.857 | 0.800 | Dùng có giám sát: qua cả 3 sàn |
| helpful | 100 | 9/0/21/70 | 0.375 | 1.000 | 0.300 | Loại khỏi gate: bỏ sót 21/30 lỗi |

Với `tone_ok`, tỉ lệ lỗi judge quan sát là 0.28; Rogan–Gladen hiệu chỉnh thành 0.30. Với `helpful`, 0.09 thành 0.30; chỉ nhìn tỉ lệ lỗi do judge trả về sẽ đánh giá quá lạc quan.

## Audit bất đồng `tone_ok`

| Case | Judge | Người | Ai đúng, hành động sửa rubric |
|---|---|---|---|
| H-008 | PASS | FAIL | Người: “nha, anh check giúp em” quá suồng sã trong thông báo hoàn tiền; thêm ví dụ này vào rubric giọng điệu. |
| H-017 | PASS | FAIL | Người: lời thân mật “bạn ơi ... nha” không phù hợp; quy định rõ cách xưng hô. |
| H-029 | PASS | FAIL | Người: “không cần nhắn thêm” mang tính gạt bỏ; thêm quy tắc về câu chỉ dẫn thiếu lịch sự. |
| H-042 | FAIL | PASS | Người: thông báo hoàn tiền và thời gian nhận tiền lịch sự, rõ ràng; bổ sung ví dụ đạt. |
| H-051 | FAIL | PASS | Người: từ “refund” xen tiếng Anh không tự nó làm giọng điệu kém; tách tiêu chí ngôn ngữ khỏi tone. |

Đây là nhãn người trong bộ replay, chưa phải xác minh độc lập về kết quả nghiệp vụ. Judge `tone_ok` chỉ dùng cho tiêu chí ngôn ngữ; số tiền và phê duyệt luôn dùng grader code. Replay đã công khai nên cần tập nhãn người mới để kiểm tra held-out trước triển khai thật.
