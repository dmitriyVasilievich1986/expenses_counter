import CircularProgress from '@mui/material/CircularProgress';
import { useMainStore } from '@store/main';
import Button from '@mui/material/Button';

export function SubmitButton(props: {
  disabled?: boolean;
  variant?: 'create' | 'update' | 'delete';
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}) {
  const isLoading = useMainStore((state) => state.isLoading);

  const getVariant = () => {
    switch (props.variant) {
      case 'create':
        return 'primary';
      case 'update':
        return 'secondary';
      case 'delete':
        return 'error';
    }
  };

  const getButtonText = () => {
    switch (props.variant) {
      case 'create':
        return 'Create';
      case 'update':
        return 'Update';
      case 'delete':
        return 'Delete';
    }
  };

  if (isLoading) {
    return <CircularProgress size={20} />;
  }
  return (
    <Button
      variant="contained"
      color={getVariant()}
      disabled={props.disabled}
      onClick={props.onClick}
    >
      {getButtonText()}
    </Button>
  );
}
