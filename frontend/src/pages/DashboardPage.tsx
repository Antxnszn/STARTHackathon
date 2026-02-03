import { useState } from 'react';
import StatsGrid from '../components/StatsGrid';
import MapComponent from '../components/MapComponent';
import ParcelList from '../components/ParcelList';
import ParcelModal from '../components/ParcelModal';
import type { Project, AnalysisResultResponse } from '../types';
import { api } from '../services/api';

interface DashboardPageProps {
  projects: Project[];
  onProjectsChange: () => void;
}

export default function DashboardPage({ projects, onProjectsChange }: DashboardPageProps) {
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResultResponse | null>(null);
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false);

  const handleSelectProject = async (project: Project) => {
    setSelectedProject(project);
    setIsLoadingAnalysis(true);
    setAnalysis(null);
    try {
      const result = await api.analyzeProject(project.id);
      setAnalysis(result);
    } catch (e) {
      console.error("Failed to load analysis", e);
    } finally {
      setIsLoadingAnalysis(false);
    }
  };

  const handlePolygonComplete = async (coords: any[]) => {
    const pName = prompt("Nombre del nuevo predio (mínimo 3 caracteres):");
    if (!pName) return;
    if (pName.length < 3) {
      alert("El nombre debe tener al menos 3 caracteres");
      return;
    }

    try {
      const newProject = await api.createProject({
        name: pName,
        organization_name: "Demo Corp",
        organization_eori: "MX123456789012"
      });
      
      const geoJson = {
        type: "FeatureCollection",
        features: [
          {
            type: "Feature",
            properties: {},
            geometry: {
              type: "Polygon",
              coordinates: [coords.map((c: any) => [c.lng, c.lat])]
            }
          }
        ]
      };
      
      const blob = new Blob([JSON.stringify(geoJson)], { type: 'application/json' });
      const file = new File([blob], "parcel.geojson");
      
      await api.uploadGeoJSON(newProject.id, file);
      await api.analyzeProject(newProject.id);
      
      onProjectsChange();
      
    } catch (e: any) {
      console.error("Error creating project", e);
      alert(e.message || "Error al crear el proyecto. Asegúrate que el backend esté corriendo.");
    }
  };

  const handleGeoJSONUpload = async (file: File) => {
    const pName = prompt("Nombre del nuevo predio (mínimo 3 caracteres):");
    if (!pName) return;
    if (pName.length < 3) {
      alert("El nombre debe tener al menos 3 caracteres");
      return;
    }

    try {
      const newProject = await api.createProject({
        name: pName,
        organization_name: "Demo Corp",
        organization_eori: "MX123456789012"
      });

      await api.uploadGeoJSON(newProject.id, file);
      await api.analyzeProject(newProject.id);
      onProjectsChange();

      alert(`Proyecto "${pName}" creado exitosamente!`);
    } catch (e: any) {
      console.error("Error creating project from GeoJSON", e);
      alert(e.message || "Error al crear el proyecto. Asegúrate que el backend esté corriendo en puerto 8001.");
    }
  };

  return (
    <>
      <StatsGrid />
      
      <div className="px-8 pb-8 flex gap-6 flex-col md:flex-row">
        <MapComponent onPolygonComplete={handlePolygonComplete} onGeoJSONUpload={handleGeoJSONUpload} />
        <ParcelList projects={projects} onSelectProject={handleSelectProject} />
      </div>

      {selectedProject && (
        <ParcelModal 
          project={selectedProject} 
          analysis={analysis} 
          onClose={() => setSelectedProject(null)}
          isLoadingAnalysis={isLoadingAnalysis}
        />
      )}
    </>
  );
}
