import { UploadCloud, Download } from 'lucide-react';

export default function Header() {
  return (
    <header className="p-8 pb-4 flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold text-bone-white">Resumen Ejecutivo</h1>
        <p className="text-[#a8bba8] text-sm">Validación de cumplimiento EUDR v1.2</p>
      </div>
      <div className="flex gap-3">
        <button className="flex items-center gap-2 bg-[#2d4a2d] hover:bg-[#385c38] px-4 py-2 rounded text-sm border border-[#3e663e] transition-all text-bone-white">
          <UploadCloud className="w-4 h-4" /> Ingesta GeoJSON
        </button>
        <button className="flex items-center gap-2 bg-[#B5CC50] hover:bg-[#f59e0b] text-[#1a2e1a] px-4 py-2 rounded text-sm font-bold transition-all">
          <Download className="w-4 h-4" /> Reporte Consolidado
        </button>
      </div>
    </header>
  );
}
