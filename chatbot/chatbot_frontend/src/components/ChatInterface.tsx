import { Send, Bot, FileUp, User } from "lucide-react";
import { useState, KeyboardEvent, useRef, useEffect } from "react";
import Spinner from "./Spinner";
import { chatService } from "../services/api";
import SelectBoxHistory from "./SelectBoxHistory";
import { langfuse } from "../services/langfuse";
import { v4 as uuidv4 } from "uuid";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Trace {
  id: string;
  sender: "user" | "system";
  text: string;
  sectionId: string;
}

const ChatInterface = () => {
  const [isLoading, setIsLoading] = useState(false); // Giúp đánh dấu trạng thái khi chatbot trả lời
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [message, setMessage] = useState(""); // Giúp lưu trữ message của user

  const [isLoadingPDF, setIsLoadingPDF] = useState(false); // Giúp đánh dấu trạng thái khi chatbot trả lời
  const [pdfPath, setPdfPath] = useState(""); // Giúp lưu trữ pdf của user có thể có
  const [sessionIdNow, setSessionIdNow] = useState("1703");

  const [allMessages, setAllMessages] = useState<Trace[]>([]); // Tất cả message được lấy từ Langfuse được lưu ở đây
  const [allMessagesTerm, setAllMessagesTerm] = useState<Trace[]>([]); // Chỉ có message của sesstion chat được lưu ở đây
  const [isNewChat, setIsNewChat] = useState(true);

  const [selectedBox, setSelectedBox] = useState<Trace[]>([
    {
      id: "1703",
      sender: "user",
      text: "New Chat",
      sectionId: "1703",
    },
  ]);

  const fetchTraces = async (sessionId: string): Promise<Trace | null> => {
    try {
      const traces = await langfuse.fetchTraces({
        sessionId: sessionId,
      });

      if (traces.data.length > 0) {
        const sortedTraces = traces.data.sort(
          (a, b) =>
            new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        );

        const allTraceItems: Trace[] = [];
        sortedTraces.forEach((trace) => {
          const itemUser: Trace = {
            id: trace.id + "_user",
            text:
              typeof trace.input === "string"
                ? trace.input.trim()
                : JSON.stringify(trace.input),
            sender: "user",
            sectionId: sessionId,
          };

          const itemSystem: Trace = {
            id: trace.id + "_system",
            text:
              typeof trace.output === "string"
                ? trace.output
                : JSON.stringify(trace.output),
            sender: "system",
            sectionId: sessionId,
          };

          allTraceItems.push(itemUser, itemSystem);
        });
        setAllMessages((prev) => [...prev, ...allTraceItems]);
        // Trả về trace đầu tiên để tạo selectedBox
        const first = sortedTraces[0];
        return {
          id: first.id + "_user",
          sender: "user",
          text:
            typeof first.input === "string"
              ? first.input.trim()
              : JSON.stringify(first.input),
          sectionId: sessionId,
        };
      }
      return null;
    } catch (error) {
      console.error(`Error fetching traces for session ${sessionId}:`, error);
      return null;
    }
  };

  const fetchData = async () => {
    try {
      const fetchSessionsAndTraces = async () => {
        const now = new Date();
        const startOfDay = new Date(
          now.getFullYear(),
          now.getMonth(),
          now.getDate()
        );

        try {
          const sessions = await langfuse.fetchSessions({
            fromTimestamp: startOfDay,
            toTimestamp: now,
          });

          const sortedSessions = sessions.data.sort(
            (a, b) =>
              new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
          );

          const selectedItems: Trace[] = [
            {
              id: "1703",
              sender: "user",
              text: "New Chat",
              sectionId: "1703",
            },
          ];
          for (const session of sortedSessions) {
            const selectedTrace = await fetchTraces(session.id);
            if (selectedTrace) {
              selectedItems.push(selectedTrace);
            }
          }

          setSelectedBox(selectedItems);
        } catch (error) {
          console.error("❌ Error fetching sessions:", error);
        }
      };
      await fetchSessionsAndTraces();
    } catch (error) {
      console.error("Error fetching chat history:", error);
    }
  };
  useEffect(() => {
    fetchData();
    console.log("CALL FETCH DATA FIRST LOAD");
  }, []);

  const handleSendMessage = async () => {
    if (!message.trim()) return;
    setIsLoading(true);

    try {
      console.log("----selectedBox: ", selectedBox);
      // let sessionIdNow = sessionIdNow;
      console.log("isNewChat: ", isNewChat);
      console.log("sessionIdNow: ", sessionIdNow);
      let sessionIdSent = sessionIdNow;
      if (isNewChat) {
        // Mới chat trong session mới
        if (sessionIdNow === "1703") {
          // setAllMessages([]);
          setAllMessagesTerm([]);
          setIsNewChat(false);
          const newID = uuidv4();
          setSessionIdNow(newID);
          sessionIdSent = newID;
        } else {
          // Mơi chat trong session cũ
          setIsNewChat(false);
        }
      } else {
        if (sessionIdNow === "1703") {
          const newID = uuidv4();
          setSessionIdNow(newID); // Tạo session mới
          sessionIdSent = newID;
          // setAllMessages([]);
          setAllMessagesTerm([]);
          setIsNewChat(true);
        } else {
          // Vẫn đang trong session cũ hợp lệ → giữ nguyên
          setIsNewChat(false);
        }
      }
      // Add user message
      const userMessage: Trace = {
        id: Date.now().toString() + "_user",
        text: message.trim(),
        sender: "user",
        sectionId: sessionIdSent,
      };

      if (sessionIdNow === "1703" && isNewChat) {
        console.log("userMessage 1: ", userMessage);
        setSelectedBox((prev) => [...prev, userMessage]);
      } else if (sessionIdNow === "1703" && sessionIdSent !== sessionIdNow) {
        console.log("userMessage 2: ", userMessage);
        setSelectedBox((prev) => [...prev, userMessage]);
      }

      setAllMessages((prev) => [...prev, userMessage]);
      setAllMessagesTerm((prev) => [...prev, userMessage]);

      // Clear input
      setMessage("");

      console.log("sessionIdNow send: ", sessionIdSent);
      const results = await chatService.sendMessage({
        prompt: message.trim(),
        tmp_file_path: pdfPath,
        session_id_choiced: sessionIdSent,
      });
      const systemMessage: Trace = {
        id: (Date.now() + 1).toString() + "_system",
        sender: "system",
        text: results,
        sectionId: sessionIdSent,
      };
      setAllMessages((prev) => [...prev, systemMessage]);
      setAllMessagesTerm((prev) => [...prev, systemMessage]);
    } catch (error) {
      // Handle any errors
      console.log("\n\n---CC: ", allMessagesTerm);
      console.error("Lỗi:", error);
    } finally {
      setIsLoading(false);
      if (pdfPath) {
        setPdfPath("");
      }
    }
  };

  const handleSelectChat = (sectionId: string) => {
    console.log("Session cũ là: ", sessionIdNow);
    console.log("Session đang chọn bây giờ là: ", sectionId);
    console.log("allMessages: ", allMessages);
    const sectionChat = allMessages.filter(
      (msg) => msg.sectionId === sectionId
    );
    setSessionIdNow(sectionId);
    setAllMessagesTerm(sectionChat);
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileUpload = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (file && file.type === "application/pdf") {
      // Handle PDF file upload
      setIsLoadingPDF(true);

      try {
        const result = await chatService.sendPdf({ file });
        console.log("result: ", result);
        setPdfPath(result);
      } catch (error) {
        console.error("⚠️ Error while uploading file:", error);
      } finally {
        setIsLoadingPDF(false);
      }
    }
  };

  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      const { scrollHeight, clientHeight } = messagesContainerRef.current;
      // console.log(scrollHeight, '-', clientHeight)
      messagesContainerRef.current.scrollTo({
        top: scrollHeight - clientHeight,
        behavior: "smooth",
      });
    }
  };
  // Scroll when messages change
  useEffect(() => {
    scrollToBottom();
  }, [allMessagesTerm]);

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="py-5 px-6 bg-white shadow-[0_1px_3px_0_rgb(0,0,0,0.05)] relative z-10">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          {/* App Title */}
          <div className="flex items-center gap-4">
            <Bot size={40} className="text-indigo-600" />
            <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-600 to-indigo-500 bg-clip-text text-transparent">
              Agentic Chatbot
            </h1>
          </div>

          {/* Chat History Select */}
          <SelectBoxHistory
            histories={selectedBox}
            historySelected={handleSelectChat}
          ></SelectBoxHistory>
        </div>
      </div>

      {/* Chat Messages Area */}
      <div
        className="flex-1 overflow-y-auto bg-gray-50"
        ref={messagesContainerRef}
      >
        <div className="max-w-3xl mx-auto py-6 px-4 space-y-6">
          {allMessagesTerm.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-4 ${
                msg.sender === "user" ? "flex-row-reverse" : ""
              }`}
            >
              {/* Avatar */}
              <div
                className={`flex-shrink-0 ${
                  msg.sender === "user"
                    ? "bg-indigo-100"
                    : "bg-white border border-gray-200"
                } w-10 h-10 rounded-lg flex items-center justify-center shadow-sm`}
              >
                {msg.sender === "user" ? (
                  <User size={20} className="text-indigo-600" />
                ) : (
                  <Bot size={20} className="text-indigo-600" />
                )}
              </div>

              {/* Message Content */}
              <div
                className={`flex flex-col max-w-[80%] ${
                  msg.sender === "user" ? "items-end" : "items-start"
                }`}
              >
                <div
                  className={`px-4 py-3 rounded-lg ${
                    msg.sender === "user"
                      ? "bg-indigo-600 text-white"
                      : "bg-white border border-gray-200"
                  }`}
                >
                  {msg.sender === "system" ? (
                    <div className="prose prose-sm max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {msg.text}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap">{msg.text}</p>
                  )}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-4">
              {/* Bot Avatar */}
              <div className="flex-shrink-0 bg-white border border-gray-200 w-10 h-10 rounded-lg flex items-center justify-center shadow-sm">
                <Bot size={20} className="text-indigo-600" />
              </div>
              {/* Loading Message */}
              <div className="flex flex-col max-w-[80%] items-start">
                <div className="px-4 py-3 rounded-lg bg-white border border-gray-200">
                  <Spinner />
                </div>
              </div>
            </div>
          )}

          {isLoadingPDF && (
            <div className="flex gap-4 items-center">
              {/* Bot Avatar */}
              <div className="flex-shrink-0 bg-white border border-gray-200 w-10 h-10 rounded-lg flex items-center justify-center shadow-sm">
                <Bot size={20} className="text-indigo-600" />
              </div>

              {/* Loading Message */}
              <div className="flex flex-col max-w-[80%] items-start">
                <div className="px-4 py-3 rounded-lg bg-white border border-gray-200 flex items-center">
                  <Spinner />
                  <span> PDF loading...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} style={{ height: 0 }} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white shadow-[0_-1px_3px_0_rgb(0,0,0,0.05)] relative z-10">
        <div className="max-w-3xl mx-auto py-4 px-4">
          <div className="flex items-center gap-2">
            {/* PDF Upload Button */}
            <div className="relative">
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                className="hidden"
                id="pdf-upload"
              />
              <label
                htmlFor="pdf-upload"
                className={`p-2.5 rounded-xl bg-gray-50 hover:bg-gray-100 cursor-pointer transition-all flex items-center justify-center shadow-sm
                  ${pdfPath ? "text-green-500" : "text-gray-500"}`}
                title="Upload PDF"
              >
                <FileUp size={20} />
              </label>
            </div>

            <div className="flex-1">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Hỏi bất kỳ điều gì"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={handleKeyPress}
                  className="w-full px-4 py-2.5 text-gray-700 bg-white border border-gray-200 rounded-xl focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 transition-all outline-none shadow-sm"
                />
              </div>
            </div>

            <button
              onClick={handleSendMessage}
              className={`p-2.5 rounded-xl transition-all ${
                message.trim()
                  ? "bg-indigo-600 hover:bg-indigo-700 text-white shadow-md hover:shadow-lg"
                  : "bg-gray-100 text-gray-400 shadow-sm"
              }`}
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
