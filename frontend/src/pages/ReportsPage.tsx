import { useState } from 'react';
import { FileText, Download, CheckCircle, XCircle, Clock, Eye } from 'lucide-react';
import type { Project, EUDRReportResponse } from '../types';
import { api } from '../services/api';

interface ReportsPageProps {
  projects: Project[];
}

export default function ReportsPage({ projects }: ReportsPageProps) {
  const [selectedReport, setSelectedReport] = useState<EUDRReportResponse | null>(null);
  const [loadingReportId, setLoadingReportId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Filter to only show projects that have been processed
  const processedProjects = projects.filter(p => 
    p.status === 'COMPLIANT' || p.status === 'NON_COMPLIANT' || p.status === 'ERROR'
  );

  const handleViewReport = async (project: Project) => {
    if (project.status !== 'COMPLIANT') {
      setError('Los reportes solo están disponibles para proyectos conformes.');
      return;
    }

    setLoadingReportId(project.id);
    setError(null);
    try {
      const report = await api.getReport(project.id);
      setSelectedReport(report);
    } catch (e: any) {
      setError(e.message || 'Error al obtener el reporte');
    } finally {
      setLoadingReportId(null);
    }
  };

  const handleDownloadReport = async (project: Project) => {
    if (project.status !== 'COMPLIANT') return;
    
    setLoadingReportId(project.id);
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
      setError(e.message || 'Error al descargar el reporte');
    } finally {
      setLoadingReportId(null);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLIANT':
        return <CheckCircle className="w-5 h-5 text-emerald-400" />;
      case 'NON_COMPLIANT':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'ERROR':
        return <XCircle className="w-5 h-5 text-orange-400" />;
      default:
        return <Clock className="w-5 h-5 text-yellow-400" />;
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'COMPLIANT':
        return 'Conforme';
      case 'NON_COMPLIANT':
        return 'No Conforme';
      case 'ERROR':
        return 'Error';
      default:
        return status;
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#f5f5f0] mb-2">Reportes EUDR</h1>
        <p className="text-[#a8bba8]">
          Visualiza y descarga los reportes de conformidad para tus proyectos analizados.
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
          {error}
          <button onClick={() => setError(null)} className="ml-4 underline">Cerrar</button>
        </div>
      )}

      {processedProjects.length === 0 ? (
        <div className="text-center py-16">
          <FileText className="w-16 h-16 text-[#3e663e] mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-[#a8bba8] mb-2">No hay reportes disponibles</h2>
          <p className="text-[#6b8a6b]">
            Los reportes aparecerán aquí después de analizar tus parcelas en el Dashboard.
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {processedProjects.map(project => (
            <div
              key={project.id}
              className="bg-[#1a2e1a] border border-[#2d4a2d] rounded-xl p-6 hover:border-[#3e663e] transition-all"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {getStatusIcon(project.status)}
                  <div>
                    <h3 className="font-bold text-[#f5f5f0]">{project.name}</h3>
                    <p className="text-sm text-[#a8bba8]">{project.organization_name}</p>
                  </div>
                </div>
                
                <div className="flex items-center gap-6">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    project.status === 'COMPLIANT' 
                      ? 'bg-emerald-900/50 text-emerald-300 border border-emerald-700'
                      : project.status === 'NON_COMPLIANT'
                      ? 'bg-red-900/50 text-red-300 border border-red-700'
                      : 'bg-orange-900/50 text-orange-300 border border-orange-700'
                  }`}>
                    {getStatusLabel(project.status)}
                  </span>
                  
                  {project.status === 'COMPLIANT' && (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleViewReport(project)}
                        disabled={loadingReportId === project.id}
                        className="flex items-center gap-2 px-4 py-2 bg-[#243b24] hover:bg-[#2d4a2d] text-[#f5f5f0] rounded-lg transition-all disabled:opacity-50"
                      >
                        <Eye className="w-4 h-4" />
                        Ver
                      </button>
                      <button
                        onClick={() => handleDownloadReport(project)}
                        disabled={loadingReportId === project.id}
                        className="flex items-center gap-2 px-4 py-2 bg-[#fbbf24] hover:bg-[#f59e0b] text-[#1a2e1a] font-bold rounded-lg transition-all disabled:opacity-50"
                      >
                        <Download className="w-4 h-4" />
                        Descargar
                      </button>
                    </div>
                  )}
                  
                  {project.status === 'NON_COMPLIANT' && (
                    <span className="text-sm text-[#6b8a6b]">Reporte no disponible</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Report Preview Modal */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-[#1a2e1a] border border-[#2d4a2d] rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-[#2d4a2d] flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-[#f5f5f0]">Reporte EUDR</h2>
                <p className="text-sm text-[#fbbf24]">{selectedReport.greenpass_reference}</p>
              </div>
              <button
                onClick={() => setSelectedReport(null)}
                className="text-[#a8bba8] hover:text-[#f5f5f0] text-2xl"
              >
                ×
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
              {/* Header Section */}
              <div className="mb-6">
                <h3 className="text-sm font-bold text-[#fbbf24] uppercase mb-3">Información del Operador</h3>
                <div className="grid grid-cols-2 gap-4 bg-[#243b24] p-4 rounded-lg">
                  <div>
                    <p className="text-xs text-[#6b8a6b]">Nombre</p>
                    <p className="text-[#f5f5f0]">{selectedReport.header.operator.name}</p>
                  </div>
                  <div>
                    <p className="text-xs text-[#6b8a6b]">EORI</p>
                    <p className="text-[#f5f5f0]">{selectedReport.header.operator.eori}</p>
                  </div>
                  <div>
                    <p className="text-xs text-[#6b8a6b]">Mercado Destino</p>
                    <p className="text-[#f5f5f0]">{selectedReport.header.destination_market}</p>
                  </div>
                  <div>
                    <p className="text-xs text-[#6b8a6b]">Referencia</p>
                    <p className="text-[#f5f5f0]">{selectedReport.header.reference_number}</p>
                  </div>
                </div>
              </div>

              {/* Commodity Section */}
              <div className="mb-6">
                <h3 className="text-sm font-bold text-[#fbbf24] uppercase mb-3">Producto</h3>
                <div className="grid grid-cols-2 gap-4 bg-[#243b24] p-4 rounded-lg">
                  <div>
                    <p className="text-xs text-[#6b8a6b]">Código HS</p>
                    <p className="text-[#f5f5f0]">{selectedReport.commodity.hs_code}</p>
                  </div>
                  <div>
                    <p className="text-xs text-[#6b8a6b]">Nombre Comercial</p>
                    <p className="text-[#f5f5f0]">{selectedReport.commodity.trade_name}</p>
                  </div>
                  <div>
                    <p className="text-xs text-[#6b8a6b]">Nombre Científico</p>
                    <p className="text-[#f5f5f0]">{selectedReport.commodity.scientific_name}</p>
                  </div>
                  <div>
                    <p className="text-xs text-[#6b8a6b]">Cantidad</p>
                    <p className="text-[#f5f5f0]">{selectedReport.commodity.quantity.amount} {selectedReport.commodity.quantity.unit}</p>
                  </div>
                </div>
              </div>

              {/* Compliance Section */}
              <div className="mb-6">
                <h3 className="text-sm font-bold text-[#fbbf24] uppercase mb-3">Estado de Conformidad</h3>
                <div className="bg-[#243b24] p-4 rounded-lg">
                  <div className="flex items-center gap-3 mb-4">
                    <CheckCircle className="w-6 h-6 text-emerald-400" />
                    <span className="text-[#f5f5f0] font-bold">Libre de Deforestación Post-2020</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs text-[#6b8a6b]">Área Analizada</p>
                      <p className="text-[#f5f5f0]">{selectedReport.compliance.audit_metadata.area_hectares.toFixed(2)} ha</p>
                    </div>
                    <div>
                      <p className="text-xs text-[#6b8a6b]">Alertas de Deforestación</p>
                      <p className="text-[#f5f5f0]">{selectedReport.compliance.audit_metadata.deforestation_alerts}</p>
                    </div>
                    <div>
                      <p className="text-xs text-[#6b8a6b]">Riesgo Hídrico</p>
                      <p className="text-[#f5f5f0]">{selectedReport.compliance.audit_metadata.water_risk_assessment}</p>
                    </div>
                    <div>
                      <p className="text-xs text-[#6b8a6b]">Huella de Carbono</p>
                      <p className="text-[#f5f5f0]">{selectedReport.compliance.audit_metadata.carbon_footprint_tonnes.toFixed(2)} t CO₂e</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Meta Section */}
              <div className="text-xs text-[#6b8a6b] flex justify-between">
                <span>Motor: {selectedReport.compliance.audit_metadata.engine}</span>
                <span>Generado: {new Date(selectedReport.generated_at).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
