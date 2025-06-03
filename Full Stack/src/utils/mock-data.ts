
export const cameraFeeds = [
  {
    id: 'CAM-001',
    name: 'Main Intersection',
    location: 'Junction Ave & Central Blvd',
    imageUrl: 'https://images.unsplash.com/photo-1617469165786-8007eda3caa7?q=80&w=2070&auto=format&fit=crop',
    status: 'online',
    vehicleCount: 45
  },
  {
    id: 'CAM-002',
    name: 'Highway Entrance',
    location: 'I-95 North Entrance',
    imageUrl: 'https://images.unsplash.com/photo-1566139884361-30b1d4b29450?q=80&w=1887&auto=format&fit=crop',
    status: 'online',
    vehicleCount: 78
  },
  {
    id: 'CAM-003',
    name: 'Downtown Plaza',
    location: 'City Center Mall',
    imageUrl: 'https://images.unsplash.com/photo-1579105728744-9d8bd14b66a5?q=80&w=2080&auto=format&fit=crop',
    status: 'offline'
  },
  {
    id: 'CAM-004',
    name: 'School Zone',
    location: 'Lincoln Elementary',
    imageUrl: 'https://images.unsplash.com/photo-1543465077-db45d34b88a5?q=80&w=2065&auto=format&fit=crop',
    status: 'online',
    vehicleCount: 12
  },
  {
    id: 'CAM-005',
    name: 'Bridge Crossing',
    location: 'River Way Bridge',
    imageUrl: 'https://images.unsplash.com/photo-1577432155504-b4a900341278?q=80&w=1925&auto=format&fit=crop',
    status: 'online',
    vehicleCount: 31
  },
  {
    id: 'CAM-006',
    name: 'Industrial Park',
    location: 'Commerce District',
    imageUrl: 'https://images.unsplash.com/photo-1612708332305-bc3d978d92a0?q=80&w=1887&auto=format&fit=crop',
    status: 'online',
    vehicleCount: 23
  }
];

export const hourlyTrafficData = [
  { name: '09:00', vehicles: 65, violations: 5 },
  { name: '10:00', vehicles: 78, violations: 8 },
  { name: '11:00', vehicles: 90, violations: 12 },
  { name: '12:00', vehicles: 95, violations: 9 },
  { name: '13:00', vehicles: 110, violations: 15 },
  { name: '14:00', vehicles: 102, violations: 10 },
  { name: '15:00', vehicles: 118, violations: 13 },
  { name: '16:00', vehicles: 135, violations: 20 },
  { name: '17:00', vehicles: 145, violations: 24 },
  { name: '18:00', vehicles: 120, violations: 18 },
  { name: '19:00', vehicles: 100, violations: 12 },
  { name: '20:00', vehicles: 85, violations: 8 }
];

export const trafficViolationTypes = [
  { type: 'Speeding', count: 243, percentage: 42 },
  { type: 'Red Light', count: 156, percentage: 27 },
  { type: 'Improper Lane Change', count: 98, percentage: 17 },
  { type: 'No Turn Signal', count: 54, percentage: 9 },
  { type: 'Other', count: 28, percentage: 5 }
];
