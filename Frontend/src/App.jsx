import React, { useState } from 'react';
import LoginPage from './components/LoginPage';
import LiveFeedPage from './components/LiveFeedPage';
import VehicleCountPage from './components/VehicleCountPage';

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentPage, setCurrentPage] = useState(1); // 1: Login, 2: Live Feed, 3: Vehicle Count

  const handleLogin = () => {
    setIsAuthenticated(true);
    setCurrentPage(2);
  };

  const goToNextPage = () => {
    setCurrentPage((prev) => prev + 1);
  };

  return (
    <div>
      {currentPage === 1 && <LoginPage onLogin={handleLogin} />}
      {currentPage === 2 && <LiveFeedPage goToVehicleCountPage={goToNextPage} />}
      {currentPage === 3 && <VehicleCountPage />}
    </div>
  );
};

export default App;