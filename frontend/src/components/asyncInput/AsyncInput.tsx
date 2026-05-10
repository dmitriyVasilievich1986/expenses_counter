import KeyboardDoubleArrowRightIcon from '@mui/icons-material/KeyboardDoubleArrowRight';
import Autocomplete, { type AutocompleteRenderInputParams } from '@mui/material/Autocomplete';
import CircularProgress from '@mui/material/CircularProgress';
import Fab from '@mui/material/Fab';
import TextField from '@mui/material/TextField';
import { useState } from 'react';
import { useNavigate } from 'react-router';

import type { PaginationMetadata } from '@services/apiClient/types';
import { useMainStore } from '@store/main';

import type { SxProps, Theme } from '@mui/material/styles';

/**
 * MUI Autocomplete that fetches every page from `getItems` the first time the dropdown opens,
 * then keeps options in parent state via `setItems`. Optionally shows a FAB that navigates to
 * `link`/`id` when both are set.
 *
 * @template I - Row type; must be an object with numeric `id` (option keys) and a string label
 *   field (default `name`, or `nameColumn`).
 */
export function AsyncInput<I extends object>(props: {
  value: I | null;
  onChange: (value: I) => void;
  items: I[] | null;
  getItems: (limit: number, offset: number) => Promise<{ data: I[]; metadata: PaginationMetadata }>;
  setItems: (items: I[]) => void;
  label: string;
  nameColumn?: keyof I;
  link?: string;
  sx?: SxProps<Theme>;
  disableClearable?: boolean;
}) {
  const [isLoadingAllItems, setIsLoadingAllItems] = useState<boolean>(false);

  const nameColumn = (props.nameColumn ?? 'name') as keyof I;
  const isLoading = useMainStore((state) => state.isLoading);
  const navigate = useNavigate();

  /** Loads all pages into `items` once when the list is opened and `items` is still null. */
  const openHandler = async () => {
    if (props.items !== null || isLoadingAllItems) return;

    setIsLoadingAllItems(true);
    try {
      let total = 1000;
      const items: I[] = [];
      while (total > items.length) {
        const { data, metadata } = await props.getItems(100, items.length);
        items.push(...data);
        total = metadata.total;
      }
      props.setItems(items);
    } catch (error) {
      console.error(error);
      props.setItems([] as I[]);
    } finally {
      setIsLoadingAllItems(false);
    }
  };

  /** End adornment: global/store loading spinner, optional navigate FAB, then Autocomplete defaults. */
  const EndAdornment = (params: AutocompleteRenderInputParams) => {
    if (isLoading || isLoadingAllItems) {
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

  return (
    <Autocomplete
      options={props.items ?? (!props.value ? [] : [props.value])}
      getOptionLabel={(option) => (option as I)[nameColumn] as string}
      loading={isLoadingAllItems}
      onOpen={openHandler}
      value={props.value ?? undefined}
      getOptionKey={(option) => (option as unknown as { id: number }).id}
      onChange={(_, v) => props.onChange(v as I)}
      disableClearable={props.disableClearable ?? false}
      sx={props.sx}
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
