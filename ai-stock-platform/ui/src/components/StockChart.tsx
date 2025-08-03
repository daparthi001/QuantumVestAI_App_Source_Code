import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface StockPoint {
  time: string;
  price: number;
}

interface StockChartProps {
  /** Array of {time, price} pairs */
  data: StockPoint[];
}

/**
 * Simple line chart for displaying stock price history.
 * Uses Recharts under the hood for responsiveness.
 */
const StockChart: React.FC<StockChartProps> = ({ data }) => (
  <div style={{ width: '100%', height: 300 }}>
    <ResponsiveContainer>
      <LineChart data={data}>
        <XAxis dataKey="time" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="price" stroke="#8884d8" dot={false} />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

export default StockChart;

