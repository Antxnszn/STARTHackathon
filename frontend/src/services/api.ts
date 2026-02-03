import type { Project, ProjectCreateRequest, ProjectListResponse, AnalysisResultResponse, EUDRReportResponse } from '../types';

const API_BASE_URL = '/api'; // Using Vite proxy

export const api = {
    getProjects: async (): Promise<ProjectListResponse> => {
        try {
            const response = await fetch(`${API_BASE_URL}/projects`);
            if (!response.ok) throw new Error('Failed to fetch projects');
            return await response.json();
        } catch (error) {
            // Fallback for demo/development if backend not running
            console.warn("Backend not reachable, returning mock data", error);
            return { projects: [], total: 0 };
        }
    },

    createProject: async (project: ProjectCreateRequest): Promise<Project> => {
        const response = await fetch(`${API_BASE_URL}/projects`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(project),
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const detail = errorData.detail;
            if (Array.isArray(detail)) {
                // Pydantic validation error format
                const messages = detail.map((e: any) => `${e.loc?.join('.')}: ${e.msg}`).join(', ');
                throw new Error(`Validación fallida: ${messages}`);
            }
            throw new Error(detail || 'Failed to create project');
        }
        return await response.json();
    },

    getProject: async (id: string): Promise<Project> => {
        const response = await fetch(`${API_BASE_URL}/projects/${id}`);
        if (!response.ok) throw new Error('Failed to fetch project');
        return await response.json();
    },

    uploadGeoJSON: async (projectId: string, file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(`${API_BASE_URL}/projects/${projectId}/upload`, {
            method: 'POST',
            body: formData,
        });
        if (!response.ok) throw new Error('Failed to upload GeoJSON');
        return await response.json();
    },

    analyzeProject: async (projectId: string): Promise<AnalysisResultResponse> => {
        const response = await fetch(`${API_BASE_URL}/projects/${projectId}/analyze`, {
            method: 'POST',
        });
        if (!response.ok) throw new Error('Failed to analyze project');
        return await response.json();
    },

    getReport: async (projectId: string): Promise<EUDRReportResponse> => {
        const response = await fetch(`${API_BASE_URL}/projects/${projectId}/report`);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Failed to get report');
        }
        return await response.json();
    },

    // Helper to check backend health
    checkHealth: async (): Promise<boolean> => {
        try {
            const res = await fetch('/health');
            return res.ok;
        } catch {
            return false;
        }
    }
};

