import { Settings, MessageSquare } from "lucide-react";
import { useState } from "react";
import Sidebar from "./components/Sidebar";
import SidebarItem from "./components/SidebarItem";
import ChatInterface from "./components/ChatInterface";
import AddKnowledgeInterface from "./components/AddKnowledgeInterface";

const App = () => {
  const [activeInterface, setActiveInterface] = useState<'chat' | 'knowledge'>('chat');

  return (
    <div className="flex h-screen bg-white">
      <Sidebar>
        <SidebarItem
          icon={<MessageSquare size={25} />}
          text="Play with ChatBot"
          active={activeInterface === 'chat'}
          changePage={() => setActiveInterface('chat')}
        />
        <SidebarItem
          icon={<Settings size={25} />}
          text="Add knowledge to chatbot"
          active={activeInterface === 'knowledge'}
          changePage={() => setActiveInterface('knowledge')}
        />
      </Sidebar>
      <div className="flex-1">
        {activeInterface === 'chat' ? <ChatInterface /> : <AddKnowledgeInterface />}
      </div>
    </div>
  );
};

export default App;
