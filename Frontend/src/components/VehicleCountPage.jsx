import React from 'react';
import { Car, TrendingUp, Clock, AlertTriangle } from 'lucide-react';

const VehicleCountPage = () => {
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold mb-8 flex items-center gap-2">
          <Car className="w-6 h-6" /> Traffic Analytics Dashboard
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {[
            { icon: Car, title: 'Total Vehicles', value: '1,234', change: '+12%' },
            { icon: TrendingUp, title: 'Peak Hour Traffic', value: '456', change: '+8%' },
            { icon: Clock, title: 'Avg. Wait Time', value: '2.5 min', change: '-5%' },
            { icon: AlertTriangle, title: 'Incidents', value: '3', change: '+1' },
          ].map((stat, index) => (
            <div key={index} className="bg-gray-800 rounded-xl p-6">
              <div className="flex items-start justify-between">
                <div>
                  <stat.icon className="w-8 h-8 text-blue-400 mb-4" />
                  <h3 className="text-gray-400 text-sm">{stat.title}</h3>
                  <p className="text-2xl font-bold mt-1">{stat.value}</p>
                </div>
                <span className={`text-sm ${stat.change.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
                  {stat.change}
                </span>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gray-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">Hourly Traffic Distribution</h3>
            <div className="h-64 flex items-end justify-between gap-2">
              {[...Array(24)].map((_, i) => {
                const height = Math.random() * 100;
                return (
                  <div key={i} className="flex-1">
                    <div
                      className="bg-blue-500 hover:bg-blue-400 transition-all duration-300"
                      style={{ height: `${height}%` }}
                    ></div>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 flex justify-between text-sm text-gray-400">
              <span>00:00</span>
              <span>12:00</span>
              <span>23:59</span>
            </div>
          </div>

          <div className="bg-gray-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">Vehicle Types Distribution</h3>
            <div className="space-y-4">
              {[
                { type: 'Cars', percentage: 65 },
                { type: 'Trucks', percentage: 20 },
                { type: 'Motorcycles', percentage: 10 },
                { type: 'Others', percentage: 5 },
              ].map((vehicle) => (
                <div key={vehicle.type}>
                  <div className="flex justify-between mb-1">
                    <span>{vehicle.type}</span>
                    <span>{vehicle.percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${vehicle.percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VehicleCountPage;