import { useState, useEffect } from 'react';
import { Box, Button, Typography, Paper, Container } from '@mui/material';
import Image from 'next/image';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const { loginWithGovBr, authError, clearAuthError } = useAuth();
  const [erro, setErro] = useState('');
  useEffect(() => {
    if (authError) {
      setErro(authError);
    }
  }, [authError]);
  const handleLogin = async e => {
    e.preventDefault();
    try {
      clearAuthError();
      setErro('');
      await loginWithGovBr();
    } catch (err) {
      setErro('Falha no login');
    }
  };
  return (
    <Container maxWidth='sm' sx={{ mt: 8, mb: 4 }}>
      <Box display='flex' justifyContent='center' mb={3}>
        <Image
          src='/assets/logo-ministerio-agricultura.png'
          alt='logo-ministerio-agricultura'
          width={600}
          height={175}
          style={{
            maxHeight: 150,
            height: 'auto',
            width: '100%',
            objectFit: 'contain'
          }}
          priority
        />
      </Box>

      <Button
        variant='contained'
        fullWidth
        onClick={handleLogin}
        sx={{
          borderRadius: '20px',
          backgroundColor: '#1a3dc1',
          color: 'white',
          py: 1.5,
          mb: 2,
          fontWeight: 'bold'
        }}>
        ENTRAR COM O GOV.BR
      </Button>
      {erro && <p style={{ color: 'red' }}>{erro}</p>}

      <Paper
        elevation={2}
        sx={{
          borderRadius: '16px',
          padding: 3,
          textAlign: 'center'
        }}>
        <Typography variant='subtitle1' fontWeight='bold' gutterBottom>
          Bem-vindo(a)
        </Typography>

        <div>
          <p>
            Caso não tenha login no ambiente de hml faça o cadastro aqui
            <br />
            <a
              href='https://sso.staging.acesso.gov.br/'
              target='_blank'
              rel='noopener noreferrer'>
              https://sso.staging.acesso.gov.br/
            </a>
          </p>
          <p>Utilize os seguiuntes dados para criação do cadastro:</p>
          <p>
            Nome da mãe: MAMÃE
            <br />
            Data de nascimento: 01/01/1980
          </p>
        </div>
      </Paper>
    </Container>
  );
};

export default Login;
