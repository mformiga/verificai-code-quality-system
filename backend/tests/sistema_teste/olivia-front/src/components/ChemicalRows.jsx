import React from 'react';
import { TableRow, TableCell, TextField } from '@mui/material';

const ChemicalRows = ({ data, formData, setFormData }) => {
  if (!data) return null;

  const entries = Object.entries(data).filter(
    ([key]) => !key.endsWith(' - Incerteza') && !key.startsWith('_')
  );

  const handleChange = (label, isUncertainty) => e => {
    const newValue = e.target.value;
    const targetKey = isUncertainty ? `${label} - Incerteza` : label;
    setFormData({
      ...formData,
      quimico: {
        ...data,
        [targetKey]: newValue
      }
    });
  };

  return (
    <>
      {entries.map(([label, value], index) => {
        const uncertaintyKey = `${label} - Incerteza`;
        const uncertaintyValue = data[uncertaintyKey] ?? '';

        return (
          <TableRow key={`quimico-${index}`}>
            <TableCell>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span
                  style={{
                    fontSize: 12,
                    color: 'rgba(0,0,0,0.6)',
                    marginBottom: 4
                  }}>
                  {label}
                </span>
                <TextField
                  fullWidth
                  variant='outlined'
                  size='small'
                  value={value ?? ''}
                  onChange={handleChange(label, false)}
                />
              </div>
            </TableCell>
            <TableCell>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span
                  style={{
                    fontSize: 12,
                    color: 'rgba(0,0,0,0.6)',
                    marginBottom: 4
                  }}>
                  Incerteza
                </span>
                <TextField
                  fullWidth
                  variant='outlined'
                  size='small'
                  value={uncertaintyValue}
                  onChange={handleChange(label, true)}
                />
              </div>
            </TableCell>
          </TableRow>
        );
      })}
    </>
  );
};

export default ChemicalRows;
