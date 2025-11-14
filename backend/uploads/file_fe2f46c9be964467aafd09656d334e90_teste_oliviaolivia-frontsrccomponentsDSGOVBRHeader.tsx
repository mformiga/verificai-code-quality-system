import { useState } from 'react';
import Image from 'next/image';
import {
  AppBar,
  Box,
  Container,
  IconButton,
  Button,
  Link,
  Typography,
  InputBase
} from '@mui/material';

export interface QuickLink {
  label: string;
  href: string;
  icon?: React.ReactNode;
}
export interface SystemFunction {
  label: string;
  onClick: () => void;
  icon?: React.ReactNode;
}
export interface BRHeaderProps {
  logoSrc?: string;
  sign?: string;
  title: string;
  subtitle?: string;
  quickLinks?: QuickLink[];
  systemFunctions?: SystemFunction[];
  showSearch?: boolean;
  onSearch?: (v: string) => void;
  onLogin?: () => void;
  onMenu?: () => void;
}

export function BRHeader({
  logoSrc,
  sign,
  title,
  subtitle,
  quickLinks = [],
  systemFunctions = [],
  showSearch = false,
  onSearch,
  onLogin,
  onMenu
}: BRHeaderProps) {
  const [searchValue, setSearchValue] = useState('');

  return (
    <AppBar
      position='static'
      elevation={0}
      color='default'
      sx={{
        backgroundColor: 'background.default',
        boxShadow: '0 1px 6px rgba(0,0,0,.16)',
        py: 0.5,
        fontFamily: 'var(--font-family-base, Arial, sans-serif)'
      }}>
      <Container
        maxWidth={false}
        sx={{ maxWidth: 1360, mx: 'auto', width: '100%', px: 4 }}>
        {/* ───────── Linha superior ───────── */}
        <Box
          sx={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 2
          }}>
          {/* logo + título */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {logoSrc && (
              <Image
                src={logoSrc}
                alt='Ministério da Agricultura e Pecuária'
                width={166}
                height={40}
                priority
                style={{ 
                  marginRight: '-10px', 
                  objectFit: 'contain',
                }}
              />
            )}
            {/* separador vertical */}
            <Box sx={{ height: 32, borderLeft: '1px solid #dcdcdc' }} />
            {/* título e ícone */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Typography
                sx={{ 
                  fontSize: '1.5rem', 
                  fontWeight: 400, 
                  color: '#222',
                }}>
                {title}
              </Typography>
              <Image
                src="/assets/icon-desenvolvimento.png"
                alt="Ícone de Desenvolvimento"
                width={150}
                height={23}
                priority
                style={{ objectFit: 'contain' }}
              />
            </Box>
          </Box>

          {subtitle && (
            <Typography
              sx={{ fontSize: '1rem', fontWeight: 500, color: '#666' }}>
              {subtitle}
            </Typography>
          )}

          {/* links rápidos e ações */}
          <Box
            sx={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: 1,
              mr: 0
            }}>
            {quickLinks.length > 0 && (
              <Box
                component='nav'
                sx={{
                  display: 'flex',
                  gap: 2,
                  justifyContent: 'end'
                }}>
                {quickLinks.map(l => (
                  <Link
                    key={l.label}
                    href={l.href}
                    underline='hover'
                    sx={{
                      color: '#1351B4',
                      fontWeight: 500,
                      '&:hover': { textDecoration: 'underline' }
                    }}>
                    {l.label}
                  </Link>
                ))}
              </Box>
            )}
            {/* Barra vertical separadora */}
            <Box sx={{ height: 32, borderLeft: '1px solid #dcdcdc' }} />
            {/* Ações (logout) */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {systemFunctions.map(fn => (
                <IconButton
                  key={fn.label}
                  size='small'
                  aria-label={fn.label}
                  onClick={fn.onClick}
                  sx={{
                    width: 32,
                    height: 32,
                    color: '#1351B4',
                    '& svg, & i': { fontSize: 18 }
                  }}>
                  {fn.icon}
                </IconButton>
              ))}
            </Box>
          </Box>
        </Box>
      </Container>
    </AppBar>
  );
}
