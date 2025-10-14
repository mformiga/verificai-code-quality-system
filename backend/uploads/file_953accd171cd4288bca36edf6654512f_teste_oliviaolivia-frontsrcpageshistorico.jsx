import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Container,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  TextField
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/CloudDownload';
import BasePage from '../components/BasePage';
import apiClient from '../services/apiClient';

const formatDate = isoString => {
  const date = new Date(isoString);

  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();

  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return `${day}/${month}/${year} - ${hours}h${minutes}`;
};

const Historico = () => {
  const [laudos, setLaudos] = useState([]);
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await apiClient.get('/api/laudo/historico', {
          headers: {
            'ngrok-skip-browser-warning': 'true'
          }
        });
        setLaudos(response.data);
      } catch (error) {
        console.error('Erro ao buscar laudos:', error);
      }
    };
    fetchData();
  }, []);

  const [searchTerm, setSearchTerm] = useState('');
  const filteredLaudos = laudos.filter(laudo =>
    laudo.lpco.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <BasePage title='Laudos Processados'>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: '#f5f5f5',
          padding: 4
        }}>
        <Container
          maxWidth='md'
          sx={{
            padding: 2,
            backgroundColor: '#ffffff',
            borderRadius: 3,
            boxShadow: 10
          }}>
          <Typography align='center' variant='h6' gutterBottom>
            Histórico de Laudos Processados
          </Typography>

          <TextField
            fullWidth
            label='Pesquisar pelo número do LPCO'
            variant='outlined'
            size='small'
            sx={{ mb: 2 }}
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
          />

          {filteredLaudos.length > 0 ? (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <strong>Número do LPCO</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Usuário</strong>
                    </TableCell>
                    <TableCell>
                      <strong>Data de Processamento</strong>
                    </TableCell>
                    <TableCell align='center'>
                      <strong>Laudo Enviado</strong>
                    </TableCell>
                    <TableCell align='center'>
                      <strong>Laudo Gerado</strong>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredLaudos.map(laudo => (
                    <TableRow key={laudo.id}>
                      <TableCell>{laudo.lpco}</TableCell>
                      <TableCell>{laudo.clienteNome}</TableCell>
                      <TableCell>{formatDate(laudo.criacao)}</TableCell>
                      <TableCell align='center'>
                        {laudo.laudoEnviado ? (
                          <IconButton
                            color='primary'
                            href={laudo.laudoEnviado}
                            target='_blank'
                            rel='noopener noreferrer'
                            onClick={() =>
                              window.open(
                                `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/laudo/${laudo.laudoEnviado}`,
                                '_blank'
                              )
                            }>
                            <DownloadIcon />
                          </IconButton>
                        ) : null}
                      </TableCell>
                      <TableCell align='center'>
                        {laudo.laudoProcessado ? (
                          <IconButton
                            color='primary'
                            href={laudo.laudoProcessado}
                            target='_blank'
                            rel='noopener noreferrer'
                            onClick={() =>
                              window.open(
                                `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/laudo/${laudo.laudoProcessado}`,
                                '_blank'
                              )
                            }>
                            <DownloadIcon />
                          </IconButton>
                        ) : null}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Typography align='center' sx={{ mt: 2, color: 'gray' }}>
              Nenhum laudo encontrado.
            </Typography>
          )}
        </Container>
      </Box>
    </BasePage>
  );
};

export default Historico;
