import { useState } from 'react';
import { X, TreeDeciduous, Droplets, FileCheck, Download, Loader2 } from 'lucide-react';
import type { Project, AnalysisResultResponse } from '../types';
import { api } from '../services/api';

interface ParcelModalProps {
  project: Project | null;
  analysis: AnalysisResultResponse | null;
  onClose: () => void;
  isLoadingAnalysis: boolean;
}

export default function ParcelModal({ project, analysis, onClose, isLoadingAnalysis }: ParcelModalProps) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

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

  const handleDownloadReport = async () => {
    if (!isApproved) {
      setDownloadError('El reporte solo está disponible para proyectos conformes.');
      return;
    }

    setIsDownloading(true);
    setDownloadError(null);
    
    try {
      const report = await api.getReport(project.id);
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `eudr-report-${report.greenpass_reference}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setDownloadError(e.message || 'Error al descargar el reporte');
    } finally {
      setIsDownloading(false);
    }
  };

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
                    <p className="text-[9px] uppercase font-bold text-[#B5CC50] mb-2 tracking-widest">Capa Forestal</p>
                    <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-bone-white">
                        <TreeDeciduous className={`w-5 h-5 ${forestIconColor}`} />
                        <span className="text-sm">Alertas Global Forest</span>
                    </div>
                    <span className="font-mono text-sm text-bone-white">{alerts}</span>
                    </div>
                </div>
                <div className="bg-[#243b24] p-4 rounded border border-[#2d4a2d]">
                    <p className="text-[9px] uppercase font-bold text-[#B5CC50] mb-2 tracking-widest">Capa Hídrica</p>
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

            {downloadError && (
              <div className="mb-4 p-3 bg-red-900/30 border border-red-700 rounded text-red-300 text-sm">
                {downloadError}
              </div>
            )}

            <div className="flex gap-3 pt-6 border-t border-[#2d4a2d]">
                <button 
                  className={`flex-1 font-bold py-3 rounded flex items-center justify-center gap-2 transition-all ${
                    isApproved 
                      ? 'bg-emerald-600 hover:bg-emerald-500 text-[#1a2e1a]' 
                      : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  }`}
                  disabled={!isApproved}
                >
                <FileCheck className="w-5 h-5" /> Generar Pasaporte
                </button>
                <button 
                  onClick={handleDownloadReport}
                  disabled={!isApproved || isDownloading}
                  className={`flex-1 font-bold py-3 rounded flex items-center justify-center gap-2 transition-all ${
                    isApproved 
                      ? 'border border-[#B5CC50] hover:bg-[#B5CC50] hover:text-[#1a2e1a] text-[#B5CC50]' 
                      : 'border border-[#2d4a2d] text-gray-500 cursor-not-allowed'
                  }`}
                >
                  {isDownloading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Download className="w-5 h-5" />
                  )}
                  JSON TRACES NT
                </button>
            </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
