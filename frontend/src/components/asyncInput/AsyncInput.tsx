import Autocomplete from '@mui/material/Autocomplete';
import CircularProgress from '@mui/material/CircularProgress';
import TextField from '@mui/material/TextField';
import { useEffect } from 'react';

import { useMainStore } from '@store/main';

export function AsyncInput<I>(props: {
  value: I | null;
  onChange: (value: I) => void;
  items: I[] | null;
  getItems: () => Promise<I[]>;
  label: string;
  nameColumn?: keyof I;
}) {
  const nameColumn = (props.nameColumn ?? 'name') as keyof I;
  const isLoading = useMainStore((state) => state.isLoading);

  useEffect(() => {
    if (props.value === null) {
      props.getItems().then((data) => {
        if (data.length > 0) {
          props.onChange(data[0] as I);
        }
      });
    }
  }, [props.items]);

  const handleOpen = async () => {
    await props.getItems();
  };

  if (props.value === null) return null;
  return (
    <Autocomplete
      options={props.items ?? [props.value]}
      getOptionLabel={(option) => (option as I)[nameColumn] as string}
      value={props.value}
      onOpen={handleOpen}
      getOptionKey={(option) => (option as unknown as { id: number }).id}
      onChange={(_, v) => props.onChange(v as I)}
      disableClearable
      renderInput={(params) => (
        <TextField
          {...params}
          label={props.label}
          slotProps={{
            input: {
              ...params.InputProps,
              endAdornment: (
                <>
                  {isLoading ? <CircularProgress color="inherit" size={20} /> : null}
                  {params.InputProps.endAdornment}
                </>
              ),
            },
          }}
        />
      )}
    />
  );
}
