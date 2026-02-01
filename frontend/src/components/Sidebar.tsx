import { ShieldCheck, LayoutDashboard, Map as MapIcon, Shield, FileText } from 'lucide-react';

export default function Sidebar() {
  return (
    <aside className="w-64 bg-[#121f12] border-r border-[#2d4a2d] flex flex-col shrink-0 h-screen">
      <div className="p-6">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-8 h-8 bg-[#fbbf24] rounded flex items-center justify-center">
            <ShieldCheck className="text-[#1a2e1a] w-5 h-5" />
          </div>
          <span className="text-xl font-bold tracking-tighter text-bone-white">
            GREEN<span className="text-[#fbbf24]">PASS</span>
          </span>
        </div>

        <nav className="space-y-1">
          <a
            href="#"
            className="flex items-center gap-3 px-4 py-3 rounded bg-[#fbbf24] text-[#1a2e1a] font-bold shadow-lg"
          >
            <LayoutDashboard className="w-5 h-5" /> Dashboard
          </a>
          <a
            href="#"
            className="flex items-center gap-3 px-4 py-3 rounded text-[#a8bba8] hover:bg-[#243b24] hover:text-[#f5f5f0] transition-all"
          >
            <MapIcon className="w-5 h-5" /> Geo-Monitoreo
          </a>
          <a
            href="#"
            className="flex items-center gap-3 px-4 py-3 rounded text-[#a8bba8] hover:bg-[#243b24] hover:text-[#f5f5f0] transition-all"
          >
            <Shield className="w-5 h-5" /> Certificación
          </a>
          <a
            href="#"
            className="flex items-center gap-3 px-4 py-3 rounded text-[#a8bba8] hover:bg-[#243b24] hover:text-[#f5f5f0] transition-all"
          >
            <FileText className="w-5 h-5" /> Reportes
          </a>
        </nav>
      </div>

      <div className="mt-auto p-6 space-y-4">
        <div className="bg-[#243b24] p-3 rounded border border-[#2d4a2d]">
          <p className="text-[10px] text-[#fbbf24] font-bold uppercase mb-1">
            Estatus del Sistema
          </p>
          <div className="flex items-center gap-2 text-[11px] text-[#a8bba8]">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            Sentinel API: Online
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-[#3e663e] border border-[#fbbf24] flex items-center justify-center text-xs font-bold text-white">
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
