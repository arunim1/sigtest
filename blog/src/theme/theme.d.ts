// blog/src/theme/theme.d.ts

import { PaletteOptions, Palette } from '@mui/material/styles/createPalette';
import { Shadows } from '@mui/material/styles/shadows';

declare module '@mui/material/styles' {
  interface ColorRange {
    50: string;
    100: string;
    200: string;
    300: string;
    400: string;
    500: string;
    600: string;
    700: string;
    800: string;
    900: string;
  }

  interface PaletteColor extends ColorRange {}

  interface PaletteOptions extends Partial<Palette> {
    baseShadow?: string;
  }

  interface Theme {
    vars?: {
      palette: Palette & {
        background: {
          defaultChannel: number;
        };
      };
      shape: Theme['shape'];
      shadows: Shadows;
    };
  }

  interface ThemeOptions {
    vars?: {
      palette?: PaletteOptions & {
        background?: {
          defaultChannel?: number;
        };
      };
      shape?: Theme['shape'];
      shadows?: Shadows;
    };
  }

  interface CustomShadows extends Shadows {}
}