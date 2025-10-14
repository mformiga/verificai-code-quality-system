import React from 'react';
import { Box, Typography, styled } from '@mui/material';
import AppHeader from './AppHeader';
import PrivateRoute from './PrivateRoute';

const BasePage = ({ title, children }) => {
  const Title = styled(Typography)(() => ({
    margin: '20px'
  }));
  return (
    <PrivateRoute>
      <Box sx={{ minHeight: '100vh', backgroundColor: '#f5f5f5', padding: 0 }}>
        <AppHeader />
        <Box sx={{ p: 2, pt: 0 }}>
          <Title variant='h4' align='center'>
            {title}
          </Title>
          {children}
        </Box>
      </Box>
    </PrivateRoute>
  );
};

export default BasePage;
