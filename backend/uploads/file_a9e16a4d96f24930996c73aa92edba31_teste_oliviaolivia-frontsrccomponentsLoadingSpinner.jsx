import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

const LoadingSpinner = ({ message }) => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: '#f5f5f5',
      padding: 4,
    }}
  >
    <CircularProgress size={60} sx={{ mt: 4 }} />
    <Typography variant='body1' align='center' sx={{ mt: 2 }}>
      {message}
    </Typography>
  </Box>
);

export default LoadingSpinner;
