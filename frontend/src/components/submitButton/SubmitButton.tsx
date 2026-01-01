import CircularProgress from '@mui/material/CircularProgress';
import { useMainStore } from '@store/main';
import Button from '@mui/material/Button';

export function SubmitButton(props: { disabled?: boolean; isSubmit?: boolean }) {
  const isLoading = useMainStore((state) => state.isLoading);

  if (isLoading) {
    return <CircularProgress size={20} />;
  }
  return (
    <Button
      type="submit"
      variant="contained"
      color={props.isSubmit ? 'primary' : 'secondary'}
      disabled={props.disabled}
    >
      {props.isSubmit ? 'Create' : 'Update'}
    </Button>
  );
}
