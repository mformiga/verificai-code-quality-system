import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Grid2 } from '@mui/material';
import BasePage from '../components/BasePage';
import VerifiedIcon from '@mui/icons-material/Verified';
import { getApiResponse } from '../services/apiClient';

const Resultado = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    const response = getApiResponse('data-processing');
    setData(response);
  }, []);
  return (
    <BasePage title='Classificação de azeite'>
      <Box
        sx={{
          backgroundColor: '#f5f5f5',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center'
        }}>
        <Box
          sx={{
            padding: 2,
            backgroundColor: '#ffffff',
            borderRadius: 3,
            boxShadow: 10
          }}>
          <Typography
            variant='body1'
            gutterBottom
            id='text-result'
            sx={{ display: 'flex', alignItems: 'center' }}>
            <VerifiedIcon color='success' />

            {data ? (
              <span>
                O PDF gerado pela IA está salvo no nosso bucket do MinIO com o
                nome "{data.laudo}". Caso queria ver outros resultados pode
                acessar o menu "Histórico de processamento".
              </span>
            ) : (
              <span>Aguardando resultado</span>
            )}
          </Typography>
        </Box>

        <Grid2
          container
          spacing={3}
          sx={{ mt: 5, maxWidth: 800, alignItems: 'center' }}>
          <Grid2 item xs={12} sm={6}>
            <Button
              variant='contained'
              color='primary'
              fullWidth
              onClick={() =>
                window.open(
                  `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/laudo/${data.laudo}`,
                  '_blank'
                )
              }>
              Baixar PDF
            </Button>
          </Grid2>
        </Grid2>
      </Box>
    </BasePage>
  );
};

export default Resultado;
