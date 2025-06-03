import React from 'react';
import { BarChart3, Camera, ChevronRight } from 'lucide-react';
import axios from 'axios';

const LiveFeedPage = ({ goToVehicleCountPage }) => {
  const handleLogout = async () => {
    try {
      await axios.post('http://localhost:5000/api/auth/logout');
      window.location.reload(); // Reload the page to reset the state
    } catch (error) {
      console.error('Logout failed', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="container mx-auto px-4 py-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Camera className="w-6 h-6" /> Live Traffic Feed
          </h1>
          <div className="flex items-center gap-4">
            <button
              onClick={goToVehicleCountPage}
              className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition duration-300"
            >
              <BarChart3 className="w-5 h-5" />
              View Statistics
              <ChevronRight className="w-4 h-4" />
            </button>
            <button
              onClick={handleLogout}
              className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition duration-300"
            >
              Logout
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {[1, 2, 3, 4].map((camera) => (
            <div key={camera} className="bg-gray-800 rounded-xl overflow-hidden">
              <div className="aspect-video bg-black relative">
                <img
                  src={`https://images.unsplash.com/photo-1494783367193-149034c05e8f?auto=format&fit=crop&w=800&q=80`}
                  alt={`Traffic Camera ${camera}`}
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-4 left-4 bg-red-500 px-2 py-1 rounded text-sm text-white flex items-center gap-1">
                  <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                  LIVE
                </div>
              </div>
              <div className="p-4">
                <h3 className="text-lg font-semibold text-white mb-2">Camera {camera}</h3>
                <p className="text-gray-400">Intersection {camera} - Main Street</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LiveFeedPage;