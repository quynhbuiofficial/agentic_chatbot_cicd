import { ReactNode, useContext } from "react";
import { SidebarContext } from "./Sidebar";

interface Props {
  icon: ReactNode;
  text: string;
  active: boolean;
  changePage: () => void;
}

const SidebarItem = ({ icon, text, active, changePage }: Props) => {
  const { expanded } = useContext(SidebarContext);
  return (
    <li
      onClick={changePage}
      className={`
        relative flex items-center py-2.5 px-3 my-1
        font-medium rounded-lg cursor-pointer
        transition-colors group
        ${
          active
            ? "bg-indigo-50 text-indigo-600"
            : "hover:bg-gray-50 text-gray-600"
        }
    `}
    >
      <div className="flex items-center">
        <div className={active ? "text-indigo-600" : "text-gray-500"}>{icon}</div>
        <span 
          className={`overflow-hidden transition-all ${
            expanded ? "w-52 ml-3" : "w-0"
          }`}
        >
          {text}
        </span>
      </div>
      
      {!expanded && (
        <div
          className={`
          absolute left-full rounded-md px-2 py-2 ml-6 
          bg-indigo-50 text-indigo-600 text-sm whitespace-nowrap
          invisible opacity-20 -translate-x-3 transition-all
          group-hover:visible group-hover:opacity-100 group-hover:translate-x-0
        `}
        >
          {text}
        </div>
      )}
    </li>
  );
};

export default SidebarItem;

