import { createTheme } from '@mui/material/styles';
import { colors } from '@/styles/tokens/colors';
import { typography } from '@/styles/tokens/typography';
import { spacing } from '@/styles/tokens/spacing';

export const dsgovTheme = createTheme({
  palette: {
    primary: { main: colors.primary, contrastText: colors.background },
    secondary: { main: colors.secondary, contrastText: colors.foreground },
    success: { main: colors.success, contrastText: colors.background },
    error: { main: colors.danger, contrastText: colors.background },
    warning: { main: colors.warning, contrastText: colors.foreground },
    info: { main: colors.info, contrastText: colors.background },
    background: { default: colors.background },
    text: { primary: colors.foreground }
  },
  typography: {
    fontFamily: typography.fontFamily,
    fontSize: 14,
    fontWeightRegular: typography.fontWeight.regular,
    fontWeightMedium: typography.fontWeight.semiBold,
    fontWeightBold: typography.fontWeight.bold
  },
  spacing: spacing.md,
  shape: { borderRadius: 0 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '100em',
          textTransform: 'none',
          fontWeight: typography.fontWeight.semiBold
        }
      }
    }
  }
});
