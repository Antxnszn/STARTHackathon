import { Link, useLocation } from 'react-router-dom';
import { ShieldCheck, LayoutDashboard, Map as MapIcon, Shield, FileText } from 'lucide-react';

export default function Sidebar() {
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;
  
  const linkClass = (path: string) => 
    isActive(path)
      ? "flex items-center gap-3 px-4 py-3 rounded bg-[#B5CC50] text-[#1a2e1a] font-bold shadow-lg"
      : "flex items-center gap-3 px-4 py-3 rounded text-[#a8bba8] hover:bg-[#243b24] hover:text-[#f5f5f0] transition-all";

  return (
    <aside className="w-64 bg-[#121f12] border-r border-[#2d4a2d] flex flex-col shrink-0 h-screen">
      <div className="p-6">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-8 h-8 rounded flex items-center justify-center">
            <img src="/greenpass.png" alt="GreenPass Logo" className="w-6 h-6" />
          </div>
          <span className="text-xl font-bold tracking-tighter text-bone-white">
            GREEN<span className="text-[#C7DE6A]">PASS</span>
          </span>
        </div>

        <nav className="space-y-1">
          <Link to="/" className={linkClass("/")}>
            <LayoutDashboard className="w-5 h-5" /> Dashboard
          </Link>
          <Link to="/geo" className={linkClass("/geo")}>
            <MapIcon className="w-5 h-5" /> Geo-Monitoreo
          </Link>
          <Link to="/certification" className={linkClass("/certification")}>
            <Shield className="w-5 h-5" /> Certificación
          </Link>
          <Link to="/reports" className={linkClass("/reports")}>
            <FileText className="w-5 h-5" /> Reportes
          </Link>
        </nav>
      </div>

      <div className="mt-auto p-6 space-y-4">
        <div className="bg-[#243b24] p-3 rounded border border-[#2d4a2d]">
          <p className="text-[10px] text-[#B5CC50] font-bold uppercase mb-1">
            Estatus del Sistema
          </p>
          <div className="flex items-center gap-2 text-[11px] text-[#a8bba8]">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            Sentinel API: Online
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-[#3e663e] border border-[#B5CC50] flex items-center justify-center text-xs font-bold text-white">
            JD
          </div>
          <div className="text-[11px]">
            <p className="font-bold text-[#f5f5f0]">Juan Delgado</p>
            <p className="text-[#a8bba8]">Director Ops</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
