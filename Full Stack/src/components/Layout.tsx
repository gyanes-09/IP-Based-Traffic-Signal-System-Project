
import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  
  useEffect(() => {
    const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
    const isAuthPage = location.pathname === '/';
    
    if (!isAuthenticated && !isAuthPage) {
      navigate('/');
    }
    
    if (isAuthenticated && isAuthPage) {
      navigate('/cameras');
    }
  }, [navigate, location.pathname]);

  // Don't show sidebar on auth page
  if (location.pathname === '/') {
    return <div className="min-h-screen bg-background">{children}</div>;
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-6">
        {children}
      </main>
    </div>
  );
};

export default Layout;
