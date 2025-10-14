import React from 'react';
import InputMask from 'react-input-mask';
import { TextField } from '@mui/material';

const MaskedInput = ({ value, onChange }) => {
  return (
    <InputMask
      mask='* 99 99999999'
      value={value}
      onChange={onChange}
      alwaysShowMask={false}>
      {inputProps => (
        <TextField {...inputProps} label='LPCO' variant='outlined' fullWidth />
      )}
    </InputMask>
  );
};

export default MaskedInput;
