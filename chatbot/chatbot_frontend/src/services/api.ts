import axios from "axios";

// const API_BASE_URL = "http://localhost:9999"; // Port của backend nếu dùng docker-compose thì dùng network /chatbot_backend
const API_BASE_URL = import.meta.env.VITE_API_URL;

export interface ChatRequest {
  prompt: string;
  session_id_choiced?: string;
  tmp_file_path?: string;
}

export interface pdfFile {
  file: File;
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 500000,
});

export const chatService = {
  // sendMessage là api call nhỏ bên trong chatService
  sendMessage: async (request: ChatRequest) => {
    try {
      console.log("--API_BASE_URL: ", API_BASE_URL);
      const response = await api.post("/chat", request);
      console.log("api.ts: ", response);
      return response.data.trim();
    } catch (error) {
      console.error("Error sending message:", error);
      throw error;
    }
  },
  // làm tương tự cho pdfSendMessage là api call nhỏ bên trong chatService
  sendPdf: async (request: pdfFile) => {
    try {
      const formData = new FormData();
      formData.append("file", request.file);
      const response = await axios.post(
        `${API_BASE_URL}/parser_index`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      return response.data;
    } catch (error) {
      console.error("Error sending message:", error);
      throw error;
    }
  },
};

export default api;
