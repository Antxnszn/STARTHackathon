import { X, TreeDeciduous, Droplets, FileCheck, Download } from 'lucide-react';
import type { Project, AnalysisResultResponse } from '../types';

interface ParcelModalProps {
  project: Project | null;
  analysis: AnalysisResultResponse | null;
  onClose: () => void;
  isLoadingAnalysis: boolean;
}

export default function ParcelModal({ project, analysis, onClose, isLoadingAnalysis }: ParcelModalProps) {
  if (!project) return null;

  const isApproved = project.status === 'COMPLIANT';
  const isBlocked = project.status === 'NON_COMPLIANT';

  let headerColor = 'bg-emerald-500';
  let badgeClass = 'bg-emerald-900/30 text-emerald-400 border border-emerald-500/50';
  let badgeText = 'APROBADO';
  let forestIconColor = 'text-emerald-400';
  
  if (isBlocked) {
    headerColor = 'bg-red-500';
    badgeClass = 'bg-red-900/30 text-red-400 border border-red-500/50';
    badgeText = 'BLOQUEADO';
    forestIconColor = 'text-red-400';
  } else if (!isApproved && !isBlocked) {
      headerColor = 'bg-amber-500';
      badgeClass = 'bg-amber-900/30 text-amber-400 border border-amber-500/50';
      badgeText = project.status;
      forestIconColor = 'text-amber-400';
  }

  const alerts = analysis?.deforestation.alerts_count ?? 0;
  const risk = analysis?.water.risk_level ?? 'N/A';
  const co2 = analysis?.carbon.estimated_co2e_tonnes ?? 0;

  return (
    <div className="modal-overlay fixed inset-0 z-[2000] flex items-center justify-center p-4">
      <div className="bg-[#1a2e1a] border border-[#2d4a2d] w-full max-w-2xl rounded shadow-2xl overflow-hidden relative">
        <div className={`h-1.5 w-full ${headerColor}`}></div>
        <div className="p-8">
          <div className="flex justify-between items-start mb-6">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <h2 className="text-2xl font-bold text-bone-white">{project.name}</h2>
                <span className={`${badgeClass} px-2 py-0.5 rounded text-[10px] font-bold uppercase`}>
                  {badgeText}
                </span>
              </div>
              <p className="text-[#a8bba8] text-xs font-mono tracking-tight">
                {project.id} | {project.commodity_code}
              </p>
            </div>
            <button onClick={onClose} className="text-[#a8bba8] hover:text-white transition-colors">
              <X className="w-6 h-6" />
            </button>
          </div>

          {isLoadingAnalysis ? (
             <div className="py-12 text-center text-[#a8bba8] animate-pulse">Cargando análisis...</div>
          ) : (
            <>
            <div className="grid grid-cols-2 gap-6 mb-8">
                <div className="space-y-4">
                <div className="bg-[#243b24] p-4 rounded border border-[#2d4a2d]">
                    <p className="text-[9px] uppercase font-bold text-[#fbbf24] mb-2 tracking-widest">Capa Forestal</p>
                    <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-bone-white">
                        <TreeDeciduous className={`w-5 h-5 ${forestIconColor}`} />
                        <span className="text-sm">Alertas Global Forest</span>
                    </div>
                    <span className="font-mono text-sm text-bone-white">{alerts}</span>
                    </div>
                </div>
                <div className="bg-[#243b24] p-4 rounded border border-[#2d4a2d]">
                    <p className="text-[9px] uppercase font-bold text-[#fbbf24] mb-2 tracking-widest">Capa Hídrica</p>
                    <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-bone-white">
                        <Droplets className="w-5 h-5 text-blue-400" />
                        <span className="text-sm">Estrés Aqueduct</span>
                    </div>
                    <span className="font-mono text-sm text-bone-white">{risk}</span>
                    </div>
                </div>
                </div>
                <div className={`p-4 rounded border ${isBlocked ? 'border-red-500/50 bg-red-900/20' : 'border-emerald-500/30 bg-emerald-900/10'} flex flex-col justify-center text-center`}>
                <p className={`text-[9px] uppercase font-bold ${isBlocked ? 'text-red-400' : 'text-emerald-400'} mb-2`}>Estatus Secuestro Carbono</p>
                <p className={`text-3xl font-mono font-bold ${isBlocked ? 'text-red-400' : 'text-emerald-400'}`}>{co2}</p>
                <p className={`text-[10px] ${isBlocked ? 'text-red-400/80' : 'text-emerald-400/80'}`}>tCO2e Almacenadas</p>
                </div>
            </div>

            <div className="flex gap-3 pt-6 border-t border-[#2d4a2d]">
                <button className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-[#1a2e1a] font-bold py-3 rounded flex items-center justify-center gap-2 transition-all">
                <FileCheck className="w-5 h-5" /> Generar Pasaporte
                </button>
                <button className="flex-1 border border-[#2d4a2d] hover:bg-[#243b24] font-bold py-3 rounded flex items-center justify-center gap-2 transition-all text-bone-white">
                <Download className="w-5 h-5" /> JSON TRACES NT
                </button>
            </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
