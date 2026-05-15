/**
 * MUI `Avatar` wrapper: shows `src` when loadable, otherwise the first two uppercase letters of `label`.
 *
 * @module components/avatar/Avatar
 */

import { default as MuiAvatar } from '@mui/material/Avatar';
import { useState } from 'react';

/**
 * Renders a user avatar from a photo URL or, on missing URL or load error, from `label` initials.
 *
 * @param props - Component props.
 * @param props.src - Optional image URL; initials are shown when omitted or when the image fails to load.
 * @param props.label - Source for fallback initials (first two characters, uppercased).
 * @returns A Material UI `Avatar` element.
 */
export function Avatar(props: { src?: string | null; label: string }) {
  const [failed, setFailed] = useState(false);

  if (failed || !props.src) {
    return <MuiAvatar aria-label="avatar">{props.label.slice(0, 2).toUpperCase()}</MuiAvatar>;
  }
  return <MuiAvatar src={props.src} onError={() => setFailed(true)} aria-label="avatar" />;
}
