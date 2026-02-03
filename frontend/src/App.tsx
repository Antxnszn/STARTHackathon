import { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import DashboardPage from './pages/DashboardPage';
import ReportsPage from './pages/ReportsPage';
import type { Project } from './types';
import { api } from './services/api';

function App() {
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    const data = await api.getProjects();
    setProjects(data.projects);
  };

  return (
    <div className="overflow-hidden h-screen flex bg-forest-deep text-bone-white font-sans">
      <Sidebar />
      <main className="flex-1 flex flex-col overflow-y-auto h-screen">
        <Header />
        <Routes>
          <Route 
            path="/" 
            element={
              <DashboardPage 
                projects={projects} 
                onProjectsChange={loadProjects} 
              />
            } 
          />
          <Route 
            path="/reports" 
            element={<ReportsPage projects={projects} />} 
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
