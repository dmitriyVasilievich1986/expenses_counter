import { LineChart } from '@mui/x-charts/LineChart';
import { useEffect, useState } from 'react';

import { useStatisticsAPIClient } from '@services/apiClient/statistics';

export function SpendingsGroupedByMonth() {
  const [data, setData] = useState<{ month: string; spendings: number }[] | null>(null);
  const { getSpendingsGroupedByMonth } = useStatisticsAPIClient();

  useEffect(() => {
    if (data === null) {
      getSpendingsGroupedByMonth().then((response) => {
        setData(response);
      });
    }
  }, [data]);

  if (data === null) {
    return <div>Loading...</div>;
  }
  return (
    <LineChart
      xAxis={[
        {
          data: data.map((item) => item.month),
          scaleType: 'point',
        },
      ]}
      yAxis={[
        {
          valueFormatter: (value: number) => {
            if (value >= 1000) {
              return `${(value / 1000).toFixed(0)}k`;
            }
            return value.toString();
          },
        },
      ]}
      series={[
        {
          data: data.map((item) => item.spendings),
          label: 'Spendings',
        },
      ]}
    />
  );
}
