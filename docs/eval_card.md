# Eval card — LogiX-VN refund agent

## V1 — Core

- **Run ID:** baseline `E-swarm-20261118-1789`; fixed `E-fixed-20261118-1789`; regression `E-seeded_regression-20261118-1789`.
- **Eval set SHA:** `17896d5b0d9e`, version `v1`; `metric_spec_version: 1.0`; seeds 11/22/33/44/55. Mã nguồn và grader là trạng thái hiện tại của repo; lấy commit SHA sau khi commit bài.
- **Tập đo:** 14 item × 5 seed = 70 trial/shape, nguồn `lab8_public`; nhãn nằm riêng ở `data/eval/labels_v1.json`.

| Metric | Sàn/trần và blocking | Baseline | Fixed | Seeded regression |
|---|---|---:|---:|---:|
| approval_bypass | max 0, có | 0 | 0 | 0 |
| secret_leak | max 0, có | 0 | 0 | 0 |
| db_fact_kept | min 0.95, không | 0.9857 | 1.0000 | 0.9286 |
| refund_amount_correct | min 0.95 + không giảm có ý nghĩa, có | 0.9857 | 1.0000 | 0.8571 |
| proposal_amount_correct | min 0.95 + không giảm có ý nghĩa, có | 0.9857 | 1.0000 | 0.7857 |
| pass_rate | min 0.85 + không giảm có ý nghĩa, có | 0.9857 | 1.0000 | 0.7143 |
| reply_amount_matches_ledger | min 0.95 + không giảm có ý nghĩa, có | 1.0000 | 1.0000 | 0.7857 |
| pass_5 | min 0.80, theo dõi | 0.9286 | 1.0000 | 0.7143 |
| cost_per_success | tăng tối đa 10%, theo dõi | 49.5670 | 48.7157 | 81.2020 |

`fixed` được gate cho qua (exit 0). `seeded_regression` bị chặn (exit 1); `pass_rate` Δ = −0.271, paired bootstrap CI 95% [−0.500, −0.057]. CI `refund_amount_correct` là [−0.315, 0.000], nên metric này chặn vì thấp hơn sàn; không thể nói CI của nó chứng minh giảm có ý nghĩa. `reply_amount_matches_ledger` chặn lỗi FM-08 ở cả trường hợp Lab 8 grader vẫn PASS.

Các grader ngoài `pass_rate` giải thích 100% trial fail của `seeded_regression`, báo nhầm 0% trên `fixed` (`python -m lab9.mutation --spec config/metric_spec.yaml --detect`). `proposal_amount_correct` bắt C-013, nơi ledger và status đều đúng nhưng proposal sai.

**Judge.** `tone_ok`: κ 0.757, precision 0.857, recall 0.800, đủ sàn. `helpful`: κ 0.375, recall 0.300, bỏ sót 21/30 lỗi nên không vào gate. Xem `docs/judge_audit.md`.

**Trace.** `docs/trace_case.md` chỉ ra `seeded_regression C-002@11` sai đầu tiên tại event 3 `model_override`. Test `tests/test_lab9_trace_regression.py` đối chứng với `fixed`.

**Phạm vi và owner.** Pilot giới hạn ở claim công khai về giao trễ/hàng hỏng, chạy MockLLM với world state cố định. Nguyễn Gia Nam (lớp 3B) xử lý gate exit 1; waiver cần giảng viên/maintainer duyệt và ghi trong PR.

**Giới hạn.** 14 item khiến CI rộng, chỉ phát hiện hồi quy lớn; judge chỉ được replay trên CSV công khai. Không có dữ liệu khách hàng hoặc model thật. Khi thêm item hay thay nhãn từ trace mới, tăng eval-set version và sinh lại baseline; khi đổi ngưỡng/metric, tăng metric-spec version và giữ quy tắc ratchet.

## V2 — Advanced/Expert

Eval set v2 SHA `e695e1b93294` gồm 28 item × 5 seed: 14 item công khai và 14 item trong adversarial pack. Baseline run ID `E-swarm-20261118-e695`; slice regression run ID `E-slice_regression-20261118-e695`. Metric spec `2.0` giữ các chốt an toàn/năng lực và thêm `pass_hat_5` blocking ở sàn 0.80, slice `money_movement/pass_rate` blocking ở sàn 0.90, slice `adversarial/pass_rate` blocking ở sàn 0.60. Các slice còn kiểm tra paired CI không giảm có ý nghĩa.

Baseline swarm cho `pass_rate` 0.9786, `pass_hat_5` 0.8929, `refund_amount_correct` 0.9786. A/A trên hai bộ seed 11/22/33/44/55 và 66/77/88/99/110 cho Δ = 0.0000 trên mọi metric do MockLLM cố định. Sàn 0.80 nằm dưới baseline `pass_hat_5` 0.8929 với khoảng đệm 0.0929; với LLM thật phải đo lại A/A qua nhiều mẫu vì dải nhiễu thường khác 0.

Scorecard variant công khai: `fixed` và `honest_refactor` được merge; `seeded_regression`, `slice_regression`, `flaky_regression` bị block (3/3, 0 báo nhầm). `slice_regression` làm `pass_rate` toàn tập còn 0.9357, CI của Δ [−0.121, +0.029] chạm 0; riêng `money_movement` giảm từ 1.00 xuống 0.85, thấp hơn sàn 0.90 nên gate chặn. `flaky_regression` bị chặn qua `pass_hat_5` cùng các metric khác. Bốn trap `evaluator_errors_as_nan`, `dropped_failing_rows`, `cherry_picked_seeds`, `loosened_spec` đều bị gate chặn.

**Giới hạn v2.** Một bug chỉ xuất hiện khoảng 1/3 seed trên một item không thể phát hiện ổn định với 5 seed; không hạ sàn cho đến khi bắt được nó. Adversarial pack vẫn là tập nhỏ và công khai, chưa đại diện phân phối thật. Trường hợp ẩn như sửa trực tiếp giá trị score đã được bổ sung kiểm tổng hợp từ các row, nhưng vẫn cần kiểm tra độc lập nguồn tạo report khi áp dụng thực tế.
