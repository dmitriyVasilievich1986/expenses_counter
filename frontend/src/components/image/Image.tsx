import StorefrontIcon from '@mui/icons-material/Storefront';
import { useState } from 'react';

/**
 * Props for {@link Image}.
 */
export type ImageProps = {
  /** Image URL; when missing or after a load error, a storefront icon is shown instead. */
  src?: string | null;
  /** Passed to the underlying `img` or icon `sx` width. */
  width?: number | string;
  /** Passed to the underlying `img` or icon `sx` height. */
  height?: number | string;
};

/**
 * Renders a lazy-loaded image, or a Material UI storefront icon if `src` is absent
 * or the image fails to load (`onError`).
 */
export function Image(props: ImageProps) {
  const [failed, setFailed] = useState(false);

  if (!props.src || failed) {
    return <StorefrontIcon sx={{ width: props.width, height: props.height }} />;
  }

  return (
    <img
      src={props.src}
      loading="lazy"
      style={{ width: props.width, height: props.height }}
      onError={() => setFailed(true)}
    />
  );
}
