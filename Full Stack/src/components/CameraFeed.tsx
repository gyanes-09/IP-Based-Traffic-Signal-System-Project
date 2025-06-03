import React, { useState } from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Settings, Circle } from 'lucide-react';
import CameraDetailDialog from './CameraDetailDialog';

interface CameraFeedProps {
  id: string;
  name: string;
  location: string;
  imageUrl: string;
  status: 'online' | 'offline';
  vehicleCount?: number;
}

const CameraFeed: React.FC<CameraFeedProps> = ({ 
  id, 
  name, 
  location, 
  imageUrl, 
  status, 
  vehicleCount 
}) => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  
  const handleCardClick = () => {
    setIsDialogOpen(true);
  };
  
  return (
    <>
      <Card 
        className="overflow-hidden transition-all hover:shadow-lg cursor-pointer" 
        onClick={handleCardClick}
      >
        <CardHeader className="p-4 pb-0 flex justify-between items-start">
          <div>
            <CardTitle className="text-lg font-medium">{name}</CardTitle>
            <p className="text-sm text-muted-foreground">{location}</p>
          </div>
          <div className="flex items-center space-x-2">
            <Badge 
              variant={status === 'online' ? "default" : "destructive"}
              className="flex items-center gap-1"
            >
              <Circle className={`h-2 w-2 ${status === 'online' ? 'fill-white' : 'fill-destructive-foreground'}`} />
              {status === 'online' ? 'Live' : 'Offline'}
            </Badge>
            <button 
              className="text-muted-foreground hover:text-foreground transition-colors"
              onClick={(e) => {
                e.stopPropagation(); // Prevent card click
              }}
            >
              <Settings className="h-4 w-4" />
            </button>
          </div>
        </CardHeader>
        <CardContent className="p-4">
          <div className="relative camera-feed aspect-video rounded-md overflow-hidden">
            <img 
              src={imageUrl} 
              alt={`Feed from ${name}`} 
              className="w-full h-full object-cover"
            />
            {status === 'online' && <div className="scanline"></div>}
            <div className="absolute top-2 left-2 bg-black/50 text-white px-2 py-1 rounded text-xs">
              {new Date().toLocaleTimeString()}
            </div>
            {vehicleCount !== undefined && (
              <div className="absolute bottom-2 right-2 bg-primary/80 text-primary-foreground px-2 py-1 rounded text-xs">
                Vehicles: {vehicleCount}
              </div>
            )}
          </div>
        </CardContent>
        <CardFooter className="px-4 py-2 bg-secondary/50 text-xs flex justify-between">
          <span>ID: {id}</span>
          <span>Updated: {new Date().toLocaleString()}</span>
        </CardFooter>
      </Card>
      
      <CameraDetailDialog
        camera={{ id, name, location, imageUrl, status, vehicleCount }}
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
      />
    </>
  );
};

export default CameraFeed;
