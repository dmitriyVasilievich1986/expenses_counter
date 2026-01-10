import Autocomplete from '@mui/material/Autocomplete';
import CircularProgress from '@mui/material/CircularProgress';
import TextField from '@mui/material/TextField';
import { useEffect } from 'react';

import { useCategoryAPIClient } from '@services/apiClient';
import { useCategoryStore } from '@store/category';
import type { CategorySimpleType } from '@store/category';
import { useMainStore } from '@store/main';

export function CategoryInput(props: {
  value: CategorySimpleType | null;
  onChange: (value: CategorySimpleType) => void;
}) {
  const categories = useCategoryStore((state) => state.categories);
  const isLoading = useMainStore((state) => state.isLoading);

  const { getCategories } = useCategoryAPIClient();

  useEffect(() => {
    if (props.value === null) {
      getCategories().then((newCategories) => {
        props.onChange(newCategories[0]);
      });
    }
  }, [categories]);

  const handleOpen = async () => {
    await getCategories();
  };

  if (props.value === null) return null;
  return (
    <Autocomplete
      options={categories ?? [props.value]}
      getOptionLabel={(option) => (option as CategorySimpleType).name}
      value={props.value}
      onOpen={handleOpen}
      onChange={(_, v) => props.onChange(v as CategorySimpleType)}
      renderInput={(params) => (
        <TextField
          name="categoryId"
          {...params}
          label="Category"
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
