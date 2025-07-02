import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import { ReactNode } from "react";

type LayoutProps = {
  children: ReactNode;
};

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      <Sidebar />
      <div className="flex flex-col flex-grow backdrop-blur-xl">
        <Topbar />
        <main className="p-6 flex-grow overflow-y-auto bg-white/5 rounded-tl-3xl shadow-inner">
          {children}
        </main>
      </div>
    </div>
  );
}
