
import React from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle,
  DialogDescription,
  DialogFooter
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Circle, MapPin, Info, Calendar } from 'lucide-react';

interface CameraDetailDialogProps {
  camera: {
    id: string;
    name: string;
    location: string;
    imageUrl: string;
    status: 'online' | 'offline';
    vehicleCount?: number;
  } | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const CameraDetailDialog: React.FC<CameraDetailDialogProps> = ({ 
  camera, 
  open, 
  onOpenChange 
}) => {
  if (!camera) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {camera.name}
            <Badge 
              variant={camera.status === 'online' ? "default" : "destructive"}
              className="flex items-center gap-1"
            >
              <Circle className={`h-2 w-2 ${camera.status === 'online' ? 'fill-white' : 'fill-destructive-foreground'}`} />
              {camera.status === 'online' ? 'Live' : 'Offline'}
            </Badge>
          </DialogTitle>
          <DialogDescription className="flex items-center gap-1">
            <MapPin className="h-3 w-3" />
            {camera.location}
          </DialogDescription>
        </DialogHeader>
        
        <div className="relative aspect-video rounded-md overflow-hidden">
          <img 
            src={camera.imageUrl} 
            alt={`Feed from ${camera.name}`} 
            className="w-full h-full object-cover"
          />
          {camera.status === 'online' && <div className="scanline"></div>}
          <div className="absolute top-2 left-2 bg-black/50 text-white px-2 py-1 rounded text-xs">
            {new Date().toLocaleTimeString()}
          </div>
          {camera.vehicleCount !== undefined && (
            <div className="absolute bottom-2 right-2 bg-primary/80 text-primary-foreground px-2 py-1 rounded text-xs">
              Vehicles: {camera.vehicleCount}
            </div>
          )}
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-2">
          <div className="bg-secondary/30 rounded-md p-4">
            <h3 className="text-sm font-medium flex items-center gap-1 mb-2">
              <Info className="h-3 w-3" /> Camera Details
            </h3>
            <p className="text-xs text-muted-foreground mb-1">Camera ID: {camera.id}</p>
            <p className="text-xs text-muted-foreground mb-1">Resolution: 1080p HD</p>
            <p className="text-xs text-muted-foreground">Frame Rate: 30fps</p>
          </div>
          
          <div className="bg-secondary/30 rounded-md p-4">
            <h3 className="text-sm font-medium flex items-center gap-1 mb-2">
              <Calendar className="h-3 w-3" /> Activity Log
            </h3>
            <p className="text-xs text-muted-foreground mb-1">
              Last Maintenance: {new Date(Date.now() - 1000 * 60 * 60 * 24 * 14).toLocaleDateString()}
            </p>
            <p className="text-xs text-muted-foreground mb-1">
              Last Calibrated: {new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toLocaleDateString()}
            </p>
            <p className="text-xs text-muted-foreground">
              Uptime: 99.7%
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Close</Button>
          <Button>View Full Analytics</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default CameraDetailDialog;
