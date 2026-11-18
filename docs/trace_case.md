# Trace case — C-002@11

Chạy từ `src/`: `python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11` và đối chứng bằng `--shape fixed`.

| Trường | Kết quả |
|---|---|
| Trial | `seeded_regression C-002@11`, run ID `E-seeded_regression-20261118-df17`; xem `reports/eval_seeded_regression.json` |
| Triệu chứng | Lab 8 grader FAIL: `status resolved != denied`; ledger hoàn 20.000đ, nhãn yêu cầu 0đ. |
| Bước sai đầu tiên | Event **3 `model_override`** ghi `delay_days: 5`. |
| Vì sao đầu tiên | Event 1 handoff và event 2 investigator chỉ chuyển việc/đọc đơn; event 3 thay dữ kiện DB bằng số ngày ticket trước khi event 4 quote 20.000đ. |
| Failure mode | FM-03 `ticket_trust` |
| Đối chứng | `fixed C-002@11` không có `model_override`, ledger 0đ và Lab 8 grader PASS. |
| Regression test | `tests/test_lab9_trace_regression.py::test_c002_ticket_override_changes_refund` kiểm tra event đầu sai, số tiền và kết quả đối chứng. |
| Chưa chắc chắn | Trace MockLLM này không chứng minh tần suất trên model thật hoặc với ticket ngoài tập công khai. |
