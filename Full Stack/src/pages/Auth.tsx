
import React from 'react';
import AuthForm from '../components/AuthForm';

const Auth = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-background to-muted p-4">
      <div className="w-full max-w-md mb-8 text-center">
        <h1 className="text-4xl font-bold text-primary mb-2">Traffic Signal Control</h1>
        <p className="text-muted-foreground">Advanced Traffic Monitoring System</p>
      </div>
      <AuthForm />
      <div className="mt-8 text-center text-sm text-muted-foreground">
        <p>© 2025 Traffic Signal Control. All rights reserved.</p>
      </div>
    </div>
  );
};

export default Auth;
