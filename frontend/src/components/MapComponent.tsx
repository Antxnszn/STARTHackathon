import { useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polygon, Polyline, CircleMarker, useMapEvents } from 'react-leaflet';
import { Layers, RefreshCcw, Upload } from 'lucide-react';
import type { LatLngExpression, LatLng } from 'leaflet';
import L from 'leaflet';

const AVOCADO_LAT_LNG: LatLngExpression = [19.514082266075157, -101.85155289489319];

interface MapComponentProps {
  onPolygonComplete?: (coords: LatLng[]) => void;
  onGeoJSONUpload?: (file: File) => void;
}

function DrawingLayer({ onPolygonComplete, points, setPoints, polygon, setPolygon }: any) {
  useMapEvents({
    click(e) {
      if (polygon) return; // Already drawn

      const newPoints = [...points, e.latlng];
      setPoints(newPoints);

      if (newPoints.length >= 3) {
        const first = newPoints[0];
        const last = e.latlng;
        // Simple distance check (approximate)
        const dist = first.distanceTo(last);

        if (dist < 40) {
           // Close the polygon
           const finalPolygon = [...newPoints];
           finalPolygon[finalPolygon.length - 1] = first; // Snap to start
           setPolygon(finalPolygon);
           onPolygonComplete?.(finalPolygon);
        }
      }
    },
  });

  return null;
}

export default function MapComponent({ onPolygonComplete, onGeoJSONUpload }: MapComponentProps) {
  const [points, setPoints] = useState<LatLng[]>([]);
  const [polygon, setPolygon] = useState<LatLng[] | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const resetMap = () => {
    setPoints([]);
    setPolygon(null);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Read file to display polygon on map
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const geojson = JSON.parse(e.target?.result as string);
        // Extract coordinates from GeoJSON
        let coords: LatLng[] = [];
        
        const feature = geojson.features?.[0] || geojson;
        const geometry = feature.geometry || feature;
        
        if (geometry.type === 'Polygon') {
          // GeoJSON is [lng, lat], Leaflet wants [lat, lng]
          coords = geometry.coordinates[0].map((c: number[]) => 
            L.latLng(c[1], c[0])
          );
        }
        
        if (coords.length > 0) {
          setPolygon(coords);
          setPoints(coords);
        }
      } catch (err) {
        console.error('Error parsing GeoJSON:', err);
        alert('Error al leer el archivo GeoJSON');
      }
    };
    reader.readAsText(file);

    // Also call the upload callback
    if (onGeoJSONUpload) {
      onGeoJSONUpload(file);
    }
  };

  return (
    <div className="flex-[2] bg-[#243b24] rounded-lg border border-[#2d4a2d] overflow-hidden flex flex-col relative h-[500px]">
      <div className="p-3 border-b border-[#2d4a2d] flex justify-between items-center bg-[#1a2e1a]">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-[#f5f5f0]">
          <Layers className="text-[#fbbf24] w-4 h-4" />
          Control Geoespacial de Predios
        </div>
        <div className="flex items-center gap-2">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".geojson,.json"
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="text-[10px] bg-[#fbbf24] text-black px-2 py-1 rounded hover:bg-[#fcd34d] flex items-center gap-1 transition-all font-bold"
          >
            <Upload className="w-3 h-3" /> Subir GeoJSON
          </button>
          <button
            onClick={resetMap}
            className="text-[10px] bg-[#2d4a2d] px-2 py-1 rounded hover:bg-[#3e663e] flex items-center gap-1 transition-all text-bone-white"
          >
            <RefreshCcw className="w-3 h-3" /> Reiniciar
          </button>
        </div>
      </div>

      <MapContainer
        center={AVOCADO_LAT_LNG}
        zoom={14}
        zoomControl={false}
        className="flex-grow w-full h-full"
        id="map"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
          className="dark-map-tiles"
        />
        <Marker position={AVOCADO_LAT_LNG}>
          <Popup>
            <b>Huerta La Ladera</b><br />Tingambato, Mich.
          </Popup>
        </Marker>

        <DrawingLayer
          points={points}
          setPoints={setPoints}
          polygon={polygon}
          setPolygon={setPolygon}
          onPolygonComplete={onPolygonComplete}
        />

        {points.map((pt, idx) => (
          !polygon && <CircleMarker key={idx} center={pt} radius={3} pathOptions={{ color: '#fbbf24', fillColor: '#fbbf24', fillOpacity: 1 }} />
        ))}

        {!polygon && points.length > 1 && (
            <Polyline positions={points} pathOptions={{ color: '#fbbf24', dashArray: '5, 5' }} />
        )}

        {polygon && (
           <Polygon positions={polygon} pathOptions={{ color: '#10b981', fillColor: '#10b981', fillOpacity: 0.4 }} />
        )}

      </MapContainer>

      <div className="absolute bottom-4 left-4 z-[1000] p-2 bg-[#1a2e1a]/90 border border-[#2d4a2d] rounded text-[9px] font-mono text-[#a8bba8]">
        COORD: 19.51, -101.85 | SAT: SENTINEL-2 | CLIC PARA TRAZAR POLÍGONO
      </div>
    </div>
  );
}
