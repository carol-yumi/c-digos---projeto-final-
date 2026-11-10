# Parte 1 - resultado real

Observacoes: 51056; empresas: 471; meses: 242.
Periodo: 2006-03-31 a 2026-09-30.
Variaveis do artigo com valores: 61 de 97.
Variaveis sem valores: 36. Elas nao foram preenchidas nem incluidas na lista de treino.
EV selecionado: liquida; atraso assumido: 3 meses.

Este e um painel real brasileiro ADAPTADO. Nao e uma reproducao exata das 97 variaveis americanas.
As formulas foram implementadas, mas as entradas ausentes continuam ausentes. Consulte dicionario_variaveis.csv.
FF49 nao e substituido pela classificacao atual. Os alvos, o dicionario e a lista de features precisam ser usados juntos.

Amostra do artigo: cerca de 1,81 milhao de observacoes, mercado americano, 1980-2019. O painel brasileiro tem
outra cobertura e periodo, de modo que a diferenca de tamanho nao prova por si so erro de filtro.

Pontos pendentes: equivalencias contabeis, contas vazias nas exportacoes, FF49 historico, sinais e periodos
suspeitos de custos e moedas originais entre fontes. As datas de divulgacao e revisoes historicas nao foram observadas:
os tres meses sao a HIPOTESE do guia. CNPJ atual auxilia o agrupamento, mas mudancas historicas de identificadores
precisam de conferencia. CNPJs ausentes ou invalidos permanecem com identificador do proprio ticker; zeros nao agrupam empresas.

Nao foi aplicado winsor nem preenchimento estatistico. As aproximacoes contabeis estao no dicionario.
Arquivos de origem permanecem preservados. O script nao treinou modelos nem executou as Partes 2, 3 ou 4.
