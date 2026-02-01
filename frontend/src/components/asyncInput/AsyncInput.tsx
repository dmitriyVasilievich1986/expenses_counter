import KeyboardDoubleArrowRightIcon from '@mui/icons-material/KeyboardDoubleArrowRight';
import Autocomplete, { type AutocompleteRenderInputParams } from '@mui/material/Autocomplete';
import CircularProgress from '@mui/material/CircularProgress';
import Fab from '@mui/material/Fab';
import TextField from '@mui/material/TextField';
import { useEffect } from 'react';
import { useNavigate } from 'react-router';

import { useMainStore } from '@store/main';

export function AsyncInput<I extends object>(props: {
  value: I | null;
  onChange: (value: I) => void;
  items: I[] | null;
  getItems: () => Promise<I[]>;
  label: string;
  nameColumn?: keyof I;
  link?: string;
}) {
  const nameColumn = (props.nameColumn ?? 'name') as keyof I;
  const isLoading = useMainStore((state) => state.isLoading);
  const navigate = useNavigate();

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

  const EndAdornment = (params: AutocompleteRenderInputParams) => {
    if (isLoading) {
      return <CircularProgress color="inherit" size={20} />;
    }
    const valueId =
      props.value && 'id' in props.value ? (props.value as unknown as { id: string }).id : null;
    return (
      <>
        {props.link && valueId && (
          <Fab color="primary" size="small" onClick={() => navigate(`${props.link}/${valueId}`)}>
            <KeyboardDoubleArrowRightIcon />
          </Fab>
        )}
        {params.InputProps.endAdornment}
      </>
    );
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
              endAdornment: <EndAdornment {...params} />,
            },
          }}
        />
      )}
    />
  );
}
