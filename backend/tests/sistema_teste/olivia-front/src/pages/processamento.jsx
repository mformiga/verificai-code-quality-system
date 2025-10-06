import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Button
} from '@mui/material';
import { Worker, Viewer } from '@react-pdf-viewer/core';
import { selectionModePlugin } from '@react-pdf-viewer/selection-mode';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';
import BasePage from '../components/BasePage';
import LoadingSpinner from '../components/LoadingSpinner';
import TableRows from '../components/TableRows';
import ChemicalRows from '../components/ChemicalRows';
import apiClient, {
  getApiResponse,
  saveApiResponse
} from '../services/apiClient';

const Processamento = () => {
  const router = useRouter();
  const defaultLayoutPluginInstance = defaultLayoutPlugin();
  const selectionModePluginInstance = selectionModePlugin({
    selectionMode: 'hand'
  });
  const laudo = getApiResponse('laudo');
  const [formData, setFormData] = useState({});
  const tableContainerRef = useRef(null);
  const [tableHeight, setTableHeight] = useState(null);
  const [onprogress, setOnprogress] = useState(false);

  useEffect(() => {
    const response = getApiResponse('extract-pdf-data');
    setFormData(response);
  }, []);

  useEffect(() => {
    if (tableContainerRef.current) {
      setTableHeight(tableContainerRef.current.clientHeight);
    }
  }, [formData]);

  const handleSave = async () => {
    try {
      const body = {
        lpco: getApiResponse('lpco'),
        chem_data: JSON.stringify(formData),
        sub: JSON.parse(localStorage.getItem('user')).sub
      };
      setOnprogress(true);
      const response = await apiClient.post('/api/data-processing', body, {
        headers: { 'Content-Type': 'application/json' }
      });
      saveApiResponse('data-processing', response.data);
      setOnprogress(false);
      router.push('/resultado');
    } catch (error) {
      console.error('Erro ao salvar dados:', error);
    }
  };

  return (
    <BasePage title='Processamento'>
      {onprogress ? (
        <LoadingSpinner message='Aguarde um momento enquanto nossa IA está processando...' />
      ) : (
        <>
          <Typography variant='body1' align='center' sx={{ mt: 2, mb: 2 }}>
            Analise os dados extraídos pela OlivIA. Altere se achar necessário e
            no final da tabela clique no botão de salvar para que seja criado o
            pdf com os dados processados.<br></br>
            <b>Documento gerado por IA - Precisa ser revisado por um humano</b>
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={8} md={8} lg={8}>
              <Paper
                elevation={3}
                style={{ width: '100%' }}
                ref={tableContainerRef}>
                <Worker workerUrl='https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js'>
                  <div>
                    <Viewer
                      defaultScale={1.5}
                      fileUrl={laudo}
                      plugins={[
                        defaultLayoutPluginInstance,
                        selectionModePluginInstance
                      ]}
                    />
                  </div>
                </Worker>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={4} md={4} lg={4}>
              <Paper
                elevation={3}
                style={{
                  padding: '16px',
                  height: 'calc(100vh - 30vh)',
                  overflowY: 'auto',
                  position: 'fixed',
                  zIndex: 1300
                }}>
                <Button
                  variant='contained'
                  color='primary'
                  onClick={handleSave}
                  style={{ marginBottom: '16px' }}
                  fullWidth>
                  Salvar Dados
                </Button>
                {/* Cabeçalho */}
                <Typography variant='h6' sx={{ mt: 2, mb: 1 }}>
                  Dados da Amostra
                </Typography>
                <TableContainer>
                  <Table size='small'>
                    <TableHead>
                      <TableRow>
                        <TableCell>Campo</TableCell>
                        <TableCell>Valor</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRows
                        data={formData.cabecalho}
                        sectionKey='cabecalho'
                        formData={formData}
                        setFormData={setFormData}
                      />
                    </TableBody>
                  </Table>
                </TableContainer>
                {/* Dados Químicos */}
                <Typography variant='h6' sx={{ mt: 3, mb: 1 }}>
                  Resultados dos Ensaios
                </Typography>
                <TableContainer>
                  <Table size='small'>
                    <TableHead>
                      <TableRow></TableRow>
                    </TableHead>
                    <TableBody>
                      <ChemicalRows
                        data={formData.quimico}
                        formData={formData}
                        setFormData={setFormData}
                      />
                    </TableBody>
                  </Table>
                </TableContainer>
              </Paper>
            </Grid>
          </Grid>
        </>
      )}
    </BasePage>
  );
};

export default Processamento;
