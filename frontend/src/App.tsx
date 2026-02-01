import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import StatsGrid from './components/StatsGrid';
import MapComponent from './components/MapComponent';
import ParcelList from './components/ParcelList';
import ParcelModal from './components/ParcelModal';
import type { Project, AnalysisResultResponse } from './types';
import { api } from './services/api';

function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResultResponse | null>(null);
  const [isLoadingAnalysis, setIsLoadingAnalysis] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    const data = await api.getProjects();
    // If no projects from backend, use mock data for demo if needed, or just empty
    if (data.projects.length === 0) {
        // Optional: Inject mock data if backend returns empty
    }
    setProjects(data.projects);
  };

  const handleSelectProject = async (project: Project) => {
    setSelectedProject(project);
    setIsLoadingAnalysis(true);
    setAnalysis(null);
    try {
      // Try to get existing analysis result
      // Backend doesn't have a direct "get analysis" endpoint, but "analyze" runs it.
      // Ideally we should store analysis result in project or have a getter.
      // For now, we'll re-run analyze or simulate it. 
      // If status is COMPLIANT, usually data is there.
      // Let's assume re-running analyze is cheap or idempotent.
      const result = await api.analyzeProject(project.id);
      setAnalysis(result);
    } catch (e) {
      console.error("Failed to load analysis", e);
    } finally {
      setIsLoadingAnalysis(false);
    }
  };

  const handlePolygonComplete = async (coords: any[]) => {
      // In a real app, we would prompt for project details here.
      // For this MVP/Demo, we could auto-create a project or log it.
      // We'll create a dummy project for demonstration.
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
          
          // Create GeoJSON Polygon
          const geoJson = {
              type: "FeatureCollection",
              features: [
                  {
                      type: "Feature",
                      properties: {},
                      geometry: {
                          type: "Polygon",
                          coordinates: [coords.map((c: any) => [c.lng, c.lat])] // Leaflet is lat,lng -> GeoJSON lng,lat
                      }
                  }
              ]
          };
          
          // Need to handle file upload or direct JSON upload. 
          // Our API expects file upload. We can create a File object.
          const blob = new Blob([JSON.stringify(geoJson)], { type: 'application/json' });
          const file = new File([blob], "parcel.geojson");
          
          await api.uploadGeoJSON(newProject.id, file);
          await api.analyzeProject(newProject.id);
          
          await loadProjects();
          
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
      await loadProjects();

      alert(`Proyecto "${pName}" creado exitosamente!`);
    } catch (e: any) {
      console.error("Error creating project from GeoJSON", e);
      alert(e.message || "Error al crear el proyecto. Asegúrate que el backend esté corriendo en puerto 8001.");
    }
  };

  return (
    <div className="overflow-hidden h-screen flex bg-forest-deep text-bone-white font-sans">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-y-auto h-screen">
        <Header />
        <StatsGrid />
        
        <div className="px-8 pb-8 flex gap-6 flex-col md:flex-row">
          <MapComponent onPolygonComplete={handlePolygonComplete} onGeoJSONUpload={handleGeoJSONUpload} />
          <ParcelList projects={projects} onSelectProject={handleSelectProject} />
        </div>
      </main>

      {selectedProject && (
        <ParcelModal 
            project={selectedProject} 
            analysis={analysis} 
            onClose={() => setSelectedProject(null)}
            isLoadingAnalysis={isLoadingAnalysis}
        />
      )}
    </div>
  );
}

export default App;
