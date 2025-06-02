import { MoreVertical, ChevronLast, ChevronFirst } from "lucide-react";
import { createContext, useState } from "react";

interface SidebarContextType {
  expanded: boolean;
}

export const SidebarContext = createContext<SidebarContextType>({ expanded: true });

const Sidebar = ({ children }: any) => {
  const [expanded, setExpanded] = useState(true);
  return (
    <aside className={`${expanded ? "w-[280px]" : "w-20"} h-screen transition-all duration-300 relative`}>
      <nav className="h-full flex flex-col bg-white shadow-[4px_0_10px_-3px_rgb(0,0,0,0.05)] z-10">
        {/* Header */}
        <div className="p-4 pb-4 flex justify-between items-center border-b border-gray-100">
          <img
            src="./logo_tma.jfif"
            className={`overflow-hidden transition-all ${
              expanded ? "w-36" : "w-0"
            }`}
            alt=""
          />
          <button
            onClick={() => setExpanded((curr) => !curr)}
            className="p-2 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors"
          >
            {expanded ? <ChevronFirst size={20} /> : <ChevronLast size={20} />}
          </button>
        </div>

        {/* Menu Items */}
        <SidebarContext.Provider value={{ expanded }}>
          <ul className="flex-1 px-3 py-3">{children}</ul>
        </SidebarContext.Provider>

        {/* Profile */}
        <div className="border-t border-gray-100 flex p-3">
          <img
            src="https://ui-avatars.com/api/?background=c7d2fe&color=3730a3&bold=true"
            alt=""
            className="w-10 h-10 rounded-lg shadow-sm"
          />
          <div
            className={`
              flex justify-between items-center
              overflow-hidden transition-all ${expanded ? "w-52 ml-3" : "w-0"}
          `}
          >
            <div className="leading-4">
              <h4 className="font-semibold text-gray-700">Quỳnh Bùi</h4>
              <span className="text-xs text-gray-600">quynhbui@gmail.com</span>
            </div>
            <MoreVertical size={20} className="text-gray-500 hover:text-gray-700 cursor-pointer" />
          </div>
        </div>
      </nav>
    </aside>
  );
};

export default Sidebar;
