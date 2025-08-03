import React from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface PortfolioPoint {
  name: string;
  risk: number;
  return: number;
  /** optional size of the holding to scale the scatter point */
  size?: number;
}

interface PortfolioHeatmapProps {
  /** Data representing portfolio positions */
  data: PortfolioPoint[];
}

/**
 * Visualizes portfolio positions on a risk-return scatter plot.
 * Each point can optionally have a size to indicate allocation.
 */
const PortfolioHeatmap: React.FC<PortfolioHeatmapProps> = ({ data }) => (
  <div style={{ width: '100%', height: 300 }}>
    <ResponsiveContainer>
      <ScatterChart>
        <XAxis type="number" dataKey="risk" name="Risk" />
        <YAxis type="number" dataKey="return" name="Return" />
        <ZAxis type="number" dataKey="size" range={[60, 400]} name="Size" />
        <Tooltip cursor={{ strokeDasharray: '3 3' }} />
        <Scatter data={data} fill="#82ca9d" />
      </ScatterChart>
    </ResponsiveContainer>
  </div>
);

export default PortfolioHeatmap;

