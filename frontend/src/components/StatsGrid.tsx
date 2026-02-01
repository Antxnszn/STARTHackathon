import { TrendingDown } from 'lucide-react';

export default function StatsGrid() {
  // TODO: These should be fetched from the backend based on actual project data
  // For now, show placeholder values to indicate no data available
  return (
    <div className="grid grid-cols-4 gap-4 px-8 mb-6">
      <div className="bg-[#243b24] p-4 rounded border border-[#2d4a2d]">
        <p className="text-[10px] text-[#a8bba8] uppercase font-bold mb-1">Valor en Riesgo</p>
        <div className="flex justify-between items-end">
          <span className="text-2xl font-mono font-bold text-bone-white/50">--</span>
          <span className="text-xs text-[#a8bba8] font-mono">sin datos</span>
        </div>
      </div>
      <div className="bg-[#243b24] p-4 rounded border border-[#2d4a2d]">
        <p className="text-[10px] text-[#a8bba8] uppercase font-bold mb-1">Multas Evitadas</p>
        <div className="flex justify-between items-end">
          <span className="text-2xl font-mono font-bold text-bone-white/50">--</span>
          <span className="text-xs text-[#a8bba8] font-mono">sin datos</span>
        </div>
      </div>
      <div className="bg-[#243b24] p-4 rounded border border-[#2d4a2d]">
        <p className="text-[10px] text-[#a8bba8] uppercase font-bold mb-1">Certificación</p>
        <div className="flex justify-between items-end">
          <span className="text-2xl font-mono font-bold text-bone-white/50">0/0</span>
          <span className="text-xs text-[#a8bba8] font-mono">--</span>
        </div>
      </div>
      <div className="bg-[#243b24] p-4 rounded border border-[#2d4a2d]">
        <p className="text-[10px] text-[#a8bba8] uppercase font-bold mb-1">Huella CO2e</p>
        <div className="flex justify-between items-end">
          <span className="text-2xl font-mono font-bold text-bone-white/50">--</span>
          <TrendingDown className="text-[#a8bba8] w-4 h-4" />
        </div>
      </div>
    </div>
  );
}
