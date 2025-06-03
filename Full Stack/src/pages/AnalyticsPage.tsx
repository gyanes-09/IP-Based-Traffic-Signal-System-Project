
import React from 'react';
import { Car, AlertTriangle, TrendingUp, Clock } from 'lucide-react';
import StatCard from '@/components/StatCard';
import TrafficChart from '@/components/TrafficChart';
import { hourlyTrafficData, trafficViolationTypes } from '@/utils/mock-data';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

const AnalyticsPage = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Traffic Analytics</h1>
        <p className="text-muted-foreground">
          Real-time traffic monitoring and violation reports
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Total Vehicles Today"
          value="1,248"
          description="Across all monitored areas"
          icon={<Car className="h-4 w-4" />}
          trend={{ value: 12, isPositive: true }}
        />
        <StatCard 
          title="Traffic Violations"
          value="142"
          description="11% of total traffic"
          icon={<AlertTriangle className="h-4 w-4" />}
          trend={{ value: 5, isPositive: false }}
        />
        <StatCard 
          title="Peak Traffic Time"
          value="5:00 PM"
          description="145 vehicles recorded"
          icon={<Clock className="h-4 w-4" />}
        />
        <StatCard 
          title="Traffic Growth"
          value="8.3%"
          description="Compared to last week"
          icon={<TrendingUp className="h-4 w-4" />}
          trend={{ value: 8.3, isPositive: true }}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <TrafficChart data={hourlyTrafficData} type="line" />
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Violation Breakdown</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {trafficViolationTypes.map((violation) => (
              <div key={violation.type} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>{violation.type}</span>
                  <span className="font-medium">{violation.count} ({violation.percentage}%)</span>
                </div>
                <Progress value={violation.percentage} className="h-2" />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Traffic Comparison</CardTitle>
          </CardHeader>
          <CardContent className="h-[300px]">
            <TrafficChart data={hourlyTrafficData} type="bar" />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AnalyticsPage;
