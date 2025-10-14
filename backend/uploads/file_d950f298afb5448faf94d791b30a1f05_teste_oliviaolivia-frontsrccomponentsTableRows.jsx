import React from 'react';
import { TableRow, TableCell, TextField } from '@mui/material';

const TableRows = ({ data, sectionKey, formData, setFormData }) => (
  <>
    {data &&
      Object.entries(data)
        .filter(([key]) => !key.startsWith('_'))
        .map(([key, value], index) => (
          <TableRow key={`${sectionKey}-${index}`}>
            <TableCell>{key}</TableCell>
            <TableCell>
              <TextField
                fullWidth
                variant='outlined'
                value={value}
                onChange={e =>
                  setFormData({
                    ...formData,
                    [sectionKey]: {
                      ...data,
                      [key]: e.target.value
                    }
                  })
                }
              />
            </TableCell>
          </TableRow>
        ))}
  </>
);

export default TableRows;
