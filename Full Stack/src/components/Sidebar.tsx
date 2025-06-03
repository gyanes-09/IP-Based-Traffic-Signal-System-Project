
import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import { Camera, BarChart3, LogOut } from 'lucide-react';

const Sidebar = () => {
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleLogout = () => {
    localStorage.removeItem('isAuthenticated');
    toast({
      title: "Logged Out",
      description: "You have been successfully logged out",
    });
    navigate('/');
  };

  return (
    <div className="h-full w-64 border-r bg-sidebar text-sidebar-foreground">
      <div className="flex h-16 items-center px-4 border-b border-sidebar-border">
        <h2 className="text-xl font-semibold">Traffic Signal Control</h2>
      </div>
      <nav className="space-y-1 p-4">
        <NavLink
          to="/cameras"
          className={({ isActive }) =>
            `flex items-center space-x-3 px-3 py-2 rounded-md transition-colors ${
              isActive
                ? "bg-sidebar-accent text-sidebar-accent-foreground"
                : "hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
            }`
          }
        >
          <Camera className="h-5 w-5" />
          <span>Camera Feeds</span>
        </NavLink>
        <NavLink
          to="/analytics"
          className={({ isActive }) =>
            `flex items-center space-x-3 px-3 py-2 rounded-md transition-colors ${
              isActive
                ? "bg-sidebar-accent text-sidebar-accent-foreground"
                : "hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
            }`
          }
        >
          <BarChart3 className="h-5 w-5" />
          <span>Traffic Analytics</span>
        </NavLink>
      </nav>
      <div className="absolute bottom-4 w-64 px-4">
        <Button
          variant="ghost"
          className="w-full flex items-center justify-start space-x-3 text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
          onClick={handleLogout}
        >
          <LogOut className="h-5 w-5" />
          <span>Logout</span>
        </Button>
      </div>
    </div>
  );
};

export default Sidebar;
