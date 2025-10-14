import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  MenuItem,
  Select,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import BasePage from '../components/BasePage';
import { useAuth } from '../context/AuthContext';
import { useRouter } from 'next/router';

const PromptsEditor = () => {
  const { loading } = useAuth();
  const router = useRouter();
  if (loading) return null;

  // Estado para armazenar os prompts e suas versões
  const [prompts, setPrompts] = useState([
    {
      id: 1,
      nome: 'Prompt para extração de propriedades físicas do Azeite',
      texto: `como podem ser classificados os (resultados) dos seguintes parâmetros sem os limites, de forma precisa e eficiente. Deve seguir os nomes sugeridos abaixo. Se o parâmetro não estiver presente tabela, por favor não fornecer nenhum valor para esse parâmetro. Além disso, Dizer GRUPO como: Azeite_de_Oliva_Virgem ou Azeite_de_Oliva ou Azeite_de_Oliva_Refinado ou Óleo_de_Bagaço_de_Oliva ou Óleo_de_Bagaço_de_Oliva_ Refinado. Para os parâmetros cis e trans (como "C16:1 (%) Palmitoléico trans" e "C16:1 (%) Palmitoléico cis"), nunca combine ou atribua seus valores ao parâmetro genérico "C16:1 (%) Palmitoléico".O modelo deve retornar um arquivo em JSON. Certifique-se de que a estrutura JSON está bem formatada e consistente com os dados fornecidos. Por exemplo, {"GRUPO": "Azeite_de_Oliva_Virgem",  "Acidez Livre (%)": 0.38, "C16:1 (%) Palmitoléico trans": 0.23, "C16:1 (%) Palmitoléico cis":0.40}.
GRUPO
Acidez Livre (%)
Índice de Peróxidos (mEq/kg)
Ext. Específica em UV K270
Ext. Específica em UV Delta K
Ext. Específica em UV K232
Mediana do defeito (Md)
Mediana do frutado (Mf)
Estigmastadienos (mg/kg)
Ceras (mg/kg)
Diferença do ECN 42
18:1t (%) Oléico trans
18:2t + 18:3t (%) trans
C14:0 (%) Mirístico
C16:0 (%) Palmítico
C16:1 (%) Palmitoléico trans
C16:1 (%) Palmitoléico cis
C16:1 (%) Palmitoléico
C17:0 (%) Margárico
C17:1 (%) Cis-Heptadecenóico
C18:0 (%) Esteárico
C18:1 (%) Oléico
C18:2 (%) Linoléico
C18:3 (%) Linolênico
C20:0 (%) Araquídico
C20:1 (%) Gadoléico
C22:0 (%) Behênico
C24:0 (%) Lignocérico
Colesterol (%)
Brassicasterol (%)
Campesterol   (%)
Estigmasterol  (%)
Delta-7-estigmastenol  (%)
Eritrodiol e Uvaol  (%)
Esteróis Totais  (mg/kg)
Monopalmitato de 2-glicerilo (%)
Impurezas Insoluveis (%)
Índice de refração`,
      resultado: '',
      versoes: [
        `como podem ser classificados os (resultados) dos seguintes parâmetros sem os limites, de forma precisa e eficiente. Deve seguir os nomes sugeridos abaixo. Se o parâmetro não estiver presente tabela, por favor não fornecer nenhum valor para esse parâmetro. Além disso, Dizer GRUPO como: Azeite_de_Oliva_Virgem ou Azeite_de_Oliva ou Azeite_de_Oliva_Refinado ou Óleo_de_Bagaço_de_Oliva ou Óleo_de_Bagaço_de_Oliva_ Refinado. Para os parâmetros`,
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque metus est, pulvinar vitae varius pellentesque, volutpat in dolor. Quisque libero.'
      ]
    },
    {
      id: 2,
      nome: 'Prompt para extração de informações gerais do Laudo',
      texto:
        'com base no Laudo extrair as informações para os atributos Laboratório, País, Número Relatório, Número Amostra, Data Recepção, Data Envase, Produto, Marca, Safra, Número do Lote, Cliente, Tipo (Único, Virgem, Extra Virgem, Óleo de Bagaço, Azeite Refinado, Lampante) de forma precisa e eficiente em português. Se esses atributos não estiver presente no Laudo, por favor não fornecer nenhuma informação para o atributo. O modelo deve retornar um arquivo em JSON. Certifique-se de que a estrutura JSON está bem formatada e consistente com os dados fornecidos. Por exemplo, {"Laboratório": "Laboratorio Tecnológico del Uruguay", "País": "Uruguai"}',
      resultado: '',
      versoes: [
        'com base no Laudo extrair as informações para os atributos Laboratório, País, Número Relatório, Número Amostra, Data Recepção, Data Envase, Produto, Marca, Safra, Número do Lote, Cliente, Tipo (Único, Virgem, Extra Virgem, Óleo de Bagaço, Azeite Refinado, Lampante) de forma precisa e eficiente em português. Se esses atributos não estiver presente no Laudo, por favor não fornecer nenhuma informação para o atributo. O modelo deve retornar um arquivo em JSON. Certifique-se de que a estrutura JSON está bem formatada e consistente com os dados fornecidos. Por exemplo, {"Laboratório": "Laboratorio Tecnológico del Uruguay", "País": "Uruguai"}',
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque metus est, pulvinar vitae varius pellentesque, volutpat in dolor. Quisque libero.'
      ]
    }
  ]);

  const [testando, setTestando] = useState(false);
  const [dialogExcludeOpen, setDialogExcludeOpen] = useState(false);
  const [dialogOficialOpen, setDialogOficialOpen] = useState(false);
  const [selectedPromptId, setSelectedPromptId] = useState(null);
  const [selectedVersionIndex, setSelectedVersionIndex] = useState(null);

  // Atualiza o texto do prompt
  const handlePromptChange = (id, novoTexto) => {
    setPrompts(
      prompts.map(p => (p.id === id ? { ...p, texto: novoTexto } : p))
    );
  };

  // Salva a versão atual do prompt
  const salvarVersao = id => {
    setPrompts(
      prompts.map(p =>
        p.id === id ? { ...p, versoes: [...p.versoes, p.texto] } : p
      )
    );
  };

  // Restaura uma versão anterior do prompt
  const restaurarVersao = (id, versaoIndex) => {
    setPrompts(
      prompts.map(p =>
        p.id === id ? { ...p, texto: p.versoes[versaoIndex] } : p
      )
    );
  };

  // Abre o diálogo de confirmação
  const handleExcluirVersao = (promptId, versaoIndex) => {
    setSelectedPromptId(promptId);
    setSelectedVersionIndex(versaoIndex);
    setDialogExcludeOpen(true);
  };

  const handleVersaoOficial = (promptId, versaoIndex) => {
    setSelectedPromptId(promptId);
    setSelectedVersionIndex(versaoIndex);
    setDialogOficialOpen(true);
  };

  // Confirma e remove a versão selecionada
  const confirmarExclusao = () => {
    setPrompts(
      prompts.map(p =>
        p.id === selectedPromptId
          ? {
              ...p,
              versoes: p.versoes.filter(
                (_, index) => index !== selectedVersionIndex
              )
            }
          : p
      )
    );
    setDialogExcludeOpen(false);
  };
  const confirmarOficial = () => {
    // Encontrar o objeto com o id correspondente
    const item = prompts.find(item => item.id === selectedPromptId);

    if (item && item.versoes[selectedVersionIndex]) {
      // Remover a versão do índice e colocá-la na primeira posição
      const versaoMovida = item.versoes.splice(selectedVersionIndex, 1)[0];
      item.versoes.unshift(versaoMovida);
      setPrompts(prompts.map(p => (p.id === selectedPromptId ? item : p)));
    }
    setDialogOficialOpen(false);
  };

  // Testa um prompt (simulação, sem backend)
  const testarPrompt = async id => {
    setTestando(true);
    const promptSelecionado = prompts.find(p => p.id === id);

    // Simulação de resposta da IA
    setTimeout(() => {
      setPrompts(
        prompts.map(p =>
          p.id === id ? { ...p, resultado: `Resposta gerada: ${p.texto}` } : p
        )
      );
      setTestando(false);
    }, 1000);
  };

  return (
    <BasePage title='Editor de Prompts'>
      <Typography variant='h6' gutterBottom>
        Dados do Processo para realização dos testes
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, marginBottom: 3 }}>
        <TextField label='LPCO' variant='outlined' fullWidth />
        <TextField
          type='file'
          fullWidth
          label='Laudo'
          variant='outlined'
          slotProps={{
            htmlInput: { accept: '.pdf' },
            inputLabel: { shrink: true }
          }}
        />
      </Box>
      {prompts.map(prompt => (
        <Paper key={prompt.id} sx={{ padding: 2, marginBottom: 2 }}>
          <Typography variant='h6'>{prompt.nome}</Typography>
          <TextField
            fullWidth
            multiline
            minRows={3}
            variant='outlined'
            value={prompt.texto}
            onChange={e => handlePromptChange(prompt.id, e.target.value)}
            sx={{ marginBottom: 2 }}
          />
          <Button
            variant='contained'
            color='primary'
            onClick={() => testarPrompt(prompt.id)}
            disabled={testando}
            sx={{ marginRight: 1 }}>
            Testar Prompt
          </Button>
          <Button
            variant='outlined'
            color='secondary'
            onClick={() => salvarVersao(prompt.id)}>
            Salvar Versão
          </Button>

          {/* Select para listar versões anteriores */}
          {prompt.versoes.length > 0 && (
            <Box sx={{ display: 'flex', gap: 2, marginTop: 1 }}>
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center'
                }}>
                <Typography variant='body2' align='center'>
                  <strong>Versões Salvas:</strong>
                </Typography>
              </Box>
              <Select
                displayEmpty
                value={prompt.versoes.indexOf(prompt.texto)}
                onChange={e => restaurarVersao(prompt.id, e.target.value)}
                sx={{ marginTop: 1 }}>
                <MenuItem value={-1} disabled>
                  Selecionar uma versão
                </MenuItem>
                {prompt.versoes.map((versao, index) => (
                  <MenuItem
                    key={index}
                    value={index}
                    onClick={() => setSelectedVersionIndex(index)}>
                    Versão {index + 1}: {versao.substring(0, 30)}...
                  </MenuItem>
                ))}
              </Select>

              {/* Botão para excluir a versão selecionada */}
              <Button
                variant='outlined'
                color='error'
                sx={{ marginTop: 1 }}
                disabled={prompt.versoes.length <= 1}
                onClick={() =>
                  handleExcluirVersao(prompt.id, selectedVersionIndex)
                }>
                Excluir Versão
              </Button>
              {/* Botão para excluir a versão selecionada */}
              <Button
                variant='outlined'
                color='success'
                sx={{ marginTop: 1 }}
                disabled={prompt.versoes.length <= 1}
                onClick={() =>
                  handleVersaoOficial(prompt.id, selectedVersionIndex)
                }>
                Ativar Versão
              </Button>
            </Box>
          )}
          <Box
            sx={{
              marginTop: 2,
              padding: 1,
              backgroundColor: '#f5f5f5',
              borderRadius: 1
            }}>
            <Typography variant='body1'>
              <strong>Versão Ativa: </strong>
              {prompt.versoes[0]}
            </Typography>
          </Box>
          {/* Mostra o resultado do teste se existir */}
          {prompt.resultado && (
            <Box
              sx={{
                marginTop: 2,
                padding: 1,
                backgroundColor: '#f5f5f5',
                borderRadius: 1
              }}>
              <Typography variant='body1'>
                <strong>Resultado:</strong>
              </Typography>
              <Typography variant='body2'>{prompt.resultado}</Typography>
            </Box>
          )}
        </Paper>
      ))}
      {/* Diálogo de confirmação para excluir versão */}
      <Dialog
        open={dialogExcludeOpen}
        onClose={() => setDialogExcludeOpen(false)}>
        <DialogTitle>Confirmar Exclusão</DialogTitle>
        <DialogContent>
          <Typography>
            Tem certeza que deseja excluir esta versão? Esta ação não pode ser
            desfeita.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogExcludeOpen(false)} color='secondary'>
            Cancelar
          </Button>
          <Button onClick={confirmarExclusao} color='error' variant='contained'>
            Excluir
          </Button>
        </DialogActions>
      </Dialog>
      <Dialog
        open={dialogOficialOpen}
        onClose={() => setDialogOficialOpen(false)}>
        <DialogTitle>Oficializar versão</DialogTitle>
        <DialogContent>
          <Typography>
            Tem certeza que deseja tornar esta versão oficial?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOficialOpen(false)} color='secondary'>
            Cancelar
          </Button>
          <Button
            onClick={confirmarOficial}
            color='success'
            variant='contained'>
            Sim
          </Button>
        </DialogActions>
      </Dialog>
    </BasePage>
  );
};

export default PromptsEditor;
