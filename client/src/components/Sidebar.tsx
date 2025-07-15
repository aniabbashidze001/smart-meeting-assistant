import { NavLink } from "react-router-dom";

const navItems = [
  { label: "Dashboard", path: "/dashboard", icon: "📊" },
  { label: "Upload Meeting", path: "/upload", icon: "🎙️" },
  { label: "Summary", path: "/summary", icon: "📝" },
  { label: "Search", path: "/search", icon: "🔍" },
  { label: "Visuals", path: "/visuals", icon: "🖼️" },
  { label: "Calendar", path: "/calendar", icon: "🗓️" },
];

export default function Sidebar() {
  return (
    <div className="w-64 h-full bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 text-white shadow-lg p-4">
      <h2 className="text-2xl font-extrabold mb-8 text-gradient bg-gradient-to-r from-blue-400 via-pink-400 to-purple-500 bg-clip-text text-transparent">
        Assistant Menu
      </h2>
      <nav className="space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2 rounded-lg transition-all duration-200 ${
                isActive
                  ? "bg-gradient-to-r from-blue-600 to-purple-600 font-bold shadow-md"
                  : "hover:bg-gray-700 hover:shadow"
              }`
            }
          >
            <span className="text-lg">{item.icon}</span>
            <span className="text-sm">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
