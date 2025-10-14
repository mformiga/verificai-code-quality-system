import React, { useState } from 'react';
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Button,
  Paper,
  Typography
} from '@mui/material';
import { useRouter } from 'next/navigation';
import BasePage from '../components/BasePage';
import MaskedInput from '../components/MaskedInput';
import LoadingSpinner from '../components/LoadingSpinner';
import apiClient, { saveApiResponse } from '../services/apiClient';
const Arquivos = () => {
  const router = useRouter();
  const [numeroLPCO, setNumeroLPCO] = useState('');
  const [laudo, setLaudo] = useState(null);
  const [onprogress, setOnprogress] = useState(false);

  const handleChange = event => {
    setNumeroLPCO(event.target.value);
  };

  const validateFields = () => numeroLPCO && laudo;

  const saveToBase64 = file => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = error => reject(error);
    });
  };

  const handleSubmit = async () => {
    if (validateFields()) {
      try {
        const base64 = await saveToBase64(laudo);
        saveApiResponse('laudo', base64);
        const formData = new FormData();
        formData.append('lpco', numeroLPCO);
        formData.append('laudo', laudo);
        formData.append('sub', JSON.parse(localStorage.getItem('user')).sub);
        setOnprogress(true);
        const response = await apiClient.post(
          '/api/extract-pdf-data',
          formData
        );
        saveApiResponse('lpco', numeroLPCO);
        saveApiResponse('extract-pdf-data', response.data);
        setOnprogress(false);
        router.push('/processamento');
      } catch (error) {
        console.error('Erro ao enviar dados para a API:', error);
      }
    }
  };

  return (
    <BasePage title='Envio do Laudo'>
      {onprogress ? (
        <LoadingSpinner message='Aguarde um momento enquanto nossa IA está processando...' />
      ) : (
        <>
          <TableContainer component={Paper} sx={{ mt: 4 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell></TableCell>
                  <TableCell></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                <TableRow key={1}>
                  <TableCell>Número LPCO</TableCell>
                  <TableCell>
                    <MaskedInput
                      value={numeroLPCO}
                      onChange={handleChange}
                      label='lpco'
                    />
                  </TableCell>
                </TableRow>
                <TableRow key={2}>
                  <TableCell>PDF do Laudo</TableCell>
                  <TableCell>
                    <TextField
                      type='file'
                      fullWidth
                      slotProps={{
                        htmlInput: { accept: '.pdf' },
                        inputLabel: { shrink: true }
                      }}
                      onChange={e => setLaudo(e.target.files[0] || null)}
                    />
                  </TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </TableContainer>

          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Button
              variant='contained'
              color='primary'
              sx={{ padding: '12px', fontSize: '16px', width: '50%' }}
              onClick={handleSubmit}>
              Enviar para IA
            </Button>
          </Box>
        </>
      )}
    </BasePage>
  );
};

export default Arquivos;
