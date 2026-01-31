import TextField from '@mui/material/TextField';
import { useMemo, useState } from 'react';

import { useMainStore } from '@store/main';

export function Input(props: { label: string; name: string; defaultValue?: string | null }) {
  const [value, setValue] = useState<string>(props.defaultValue ?? '');
  const isLoading = useMainStore((state) => state.isLoading);
  const isChanged = useMemo(
    () => props.defaultValue && value !== props.defaultValue,
    [props.defaultValue, value]
  );

  return (
    <TextField
      label={props.label}
      name={props.name}
      value={value}
      onChange={(e) => setValue(e.target.value)}
      fullWidth
      disabled={isLoading}
      color={isChanged ? 'warning' : 'primary'}
      focused={isChanged ? true : undefined}
    />
  );
}
