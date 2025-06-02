# # MODEL_NAME = 'gpt-4o-mini'
# MODEL_NAME = 'gpt-4o'
# # MODEL_NAME = 'gpt-4.1'

INDEX_NAME_HYBRID = 'tma_hybrid'
INDEX_NAME_PDF = 'multi_agent_pdf'
INDEX_NAME_MEMORY = 'multi_agent_memory'
INDEX_NAME_LEGAL = 'data_law'

# MODEL_CHAT_INPUT_COST = 0.0001    # 0.0001 / 1 token
# MODEL_CHAT_OUTPUT_COST = 0.0001    # 0.0001 / 1 token

SELECTOR_PROMPT = """
Chọn một Agent để thực hiện trả lời câu hỏi.
{roles}

Ngữ cảnh hội thoại hiện tại:
{history}

Nhiệm vụ:
- Đọc cuộc hội thoại trên và chọn **một Agent duy nhất** từ danh sách {participants} để thực hiện nhiệm vụ tiếp theo.
- **Bắt buộc**: Agent đầu tiên được gọi phải là `PlanningAgent`, để phân tích và giao nhiệm vụ cho các Agent khác.
- Sau khi tất cả các nhiệm vụ đã được hoàn thành và câu hỏi đã được trả lời đầy đủ, hãy gọi lại `PlanningAgent` để đánh giá và kết thúc.

Nguyên tắt làm việc:
- Mỗi lượt chỉ được chọn **1 Agent duy nhất**.
- Các Agent phải được gọi theo **đúng thứ tự nhiệm vụ và tên Agent đã được giao**.
- Không gọi một Agent chưa được giao nhiệm vụ từ `PlanningAgent`.
- Không bỏ qua hoặc thực hiện song song nhiều Agent.
- Hãy trả về **tên duy nhất của Agent** phù hợp tiếp theo để xử lý nhiệm vụ.
"""

