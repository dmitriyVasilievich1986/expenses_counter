/**
 * MUI X line chart that plots paid price per transaction date for a single product.
 * Fetches recent transactions server-side and tints the series by the latest price move (up / down / flat).
 */

import { Typography } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { LineChart } from '@mui/x-charts/LineChart';

import type { TransactionType } from '@store/transaction/types';

/**
 * Renders transaction prices over time for `productId`, or a “No data available” message when there are zero or one points.
 *
 * @param {object} props - Component props.
 * @param {number} props.productId - Product whose transactions are loaded and charted.
 * @param {boolean | undefined} props.removeLabels - When true (default), hides axes, legend, highlights, and tooltips for a compact sparkline-style chart.
 * @returns {JSX.Element} Line chart or empty-state typography.
 */
export function ProductPriceChart({
  data,
  removeLabels = true,
}: {
  data: TransactionType[] | null;
  removeLabels?: boolean;
}) {
  const theme = useTheme();

  if (data === null || data.length <= 1) {
    return (
      <Typography variant="body1" textAlign="center">
        No data available
      </Typography>
    );
  }

  const prices = data.map((item) => item.price);
  // red for uprising, green for falling, blue for flat
  // that should show that growing prices are bad and falling prices are good
  let lineColor = theme.palette.primary.main;
  const last = prices[prices.length - 1];
  const previous = prices[prices.length - 2];
  if (last > previous) {
    lineColor = theme.palette.error.main;
  } else if (last < previous) {
    lineColor = theme.palette.success.main;
  }

  const stripChrome = removeLabels;

  return (
    <LineChart
      hideLegend={stripChrome}
      axisHighlight={stripChrome ? { x: 'none', y: 'none' } : undefined}
      margin={stripChrome ? { top: 4, right: 4, bottom: 4, left: 4 } : undefined}
      slotProps={stripChrome ? { tooltip: { trigger: 'none' as const } } : undefined}
      xAxis={[
        {
          data: data.map((item) => item.date),
          scaleType: 'point',
          ...(stripChrome ? { position: 'none' as const } : {}),
        },
      ]}
      yAxis={[
        stripChrome
          ? { position: 'none' as const }
          : {
              valueFormatter: (value: number) => value.toString(),
            },
      ]}
      series={[
        {
          data: prices,
          showMark: false,
          color: lineColor,
        },
      ]}
    />
  );
}
