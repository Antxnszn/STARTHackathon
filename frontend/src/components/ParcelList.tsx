import { TreeDeciduous, Droplets } from 'lucide-react';
import type { Project } from '../types';

interface ParcelListProps {
  projects: Project[];
  onSelectProject: (project: Project) => void;
}

export default function ParcelList({ projects, onSelectProject }: ParcelListProps) {
  return (
    <div className="flex-1 bg-[#243b24] rounded-lg border border-[#2d4a2d] flex flex-col overflow-hidden h-[500px]">
      <div className="p-4 border-b border-[#2d4a2d] bg-[#1a2e1a]">
        <h3 className="text-xs font-bold uppercase tracking-widest text-[#f5f5f0]">Filtro de Semáforo</h3>
      </div>
      <div className="flex-grow overflow-y-auto p-4 space-y-3" id="parcelList">
        {projects.map((p) => {
          const isApproved = p.status === 'COMPLIANT';
          const isBlocked = p.status === 'NON_COMPLIANT';

          let statusColor = 'text-[#fbbf24] border-[#fbbf24]/30'; // Default/Processing
          if (isApproved) statusColor = 'text-emerald-400 border-emerald-500/30';
          if (isBlocked) statusColor = 'text-red-400 border-red-500/30';

          return (
            <div
              key={p.id}
              onClick={() => onSelectProject(p)}
              className="p-3 bg-[#1a2e1a] border border-[#2d4a2d] rounded cursor-pointer hover:border-[#fbbf24] transition-all group"
            >
              <div className="flex justify-between items-center mb-1">
                <span className="text-[9px] font-mono text-[#fbbf24]">{p.id.substring(0, 8)}...</span>
                <span className={`text-[8px] font-bold px-1.5 py-0.5 rounded border ${statusColor}`}>
                  {p.status}
                </span>
              </div>
              <p className="text-xs font-bold group-hover:text-[#fbbf24] transition-colors text-bone-white">{p.name}</p>
              <div className="flex gap-3 mt-2 text-[9px] text-[#a8bba8]">
                 {/* Mocking alerts/stress for list view as defined in Front.html but using Project type */}
                <span className="flex items-center gap-1">
                  <TreeDeciduous className="w-3 h-3" />
                   -- Alt
                </span>
                <span className="flex items-center gap-1">
                  <Droplets className="w-3 h-3" />
                   -- Stress
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
