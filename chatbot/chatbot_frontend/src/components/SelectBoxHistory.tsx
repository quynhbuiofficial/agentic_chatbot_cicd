import { useState, useRef, useEffect } from "react";
import { History } from "lucide-react"; // hoặc react-icons

interface LabelHistory {
  id: string;
  text: string;
  sectionId: string;
}
interface Histories {
  histories: LabelHistory[];
  historySelected: (sectionId: string) => void;
}

const SelectBoxHistory = ({ histories, historySelected }: Histories) => {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState("New Chat");
  const wrapperRef = useRef<HTMLFormElement>(null);

  // console.log("histories: ", histories);
  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <form
      ref={wrapperRef}
      className="relative flex items-center gap-3 bg-gray-50 px-4 py-3 rounded-xl w-64 border border-gray-200 shadow-sm group hover:border-indigo-300 transition-all"
    >
      <History
        size={20}
        className="text-gray-400 group-hover:text-indigo-500"
      />

      <div className="relative w-full">
        {/* Trigger */}
        <div
          onClick={() => setOpen(!open)}
          className="cursor-pointer text-gray-600 text-base font-medium"
        >
          <span className="block truncate overflow-hidden whitespace-nowrap">
            {selected}
          </span>
        </div>

        {/* Dropdown */}
        {open && (
          <ul className="absolute z-10 mt-2 w-full bg-white border border-gray-200 rounded-lg shadow">
            {histories.map((history, idx) => (
              <li
                key={history.id + idx}
                onClick={() => {
                  setSelected(history.text);
                  setOpen(false);
                  historySelected(history.sectionId); // gửi id ra ngoài
                }}
                className="cursor-pointer select-none px-4 py-2 hover:bg-gray-100 text-gray-700"
              >
                <span className="block truncate overflow-hidden whitespace-nowrap">
                  {history.text}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Chevron icon */}
      <div className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2">
        <svg
          className="h-4 w-4 text-gray-400"
          viewBox="0 0 20 20"
          fill="currentColor"
        >
          <path
            fillRule="evenodd"
            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
            clipRule="evenodd"
          />
        </svg>
      </div>
    </form>
  );
};

export default SelectBoxHistory;
