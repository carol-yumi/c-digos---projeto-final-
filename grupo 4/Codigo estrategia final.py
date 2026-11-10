"""
================================================================================================
ARBITRAGEM ESTATÍSTICA POR PCA EM AÇÕES BRASILEIRAS (Avellaneda & Lee, 2010) — 2010 A 2025
================================================================================================

O QUE ESTE ARQUIVO FAZ
    Simula, pregão a pregão (pregão = dia em que a bolsa funcionou), a estratégia da entrega
    parcial do grupo (Seções 2 a 6):
    1. todo dia escolhe as até 100 ações mais negociadas (o "universo"), só com dados até a
       véspera;
    2. para cada ação, monta uma "cópia" feita de movimentos comuns do mercado (os "fatores",
       achados por PCA) e mede quanto a ação se afastou da cópia (o "s-score");
    3. compra a ação que ficou barata demais em relação à cópia e vende a descoberto a que ficou
       cara demais; fecha quando ela volta para perto do normal (ou no stop de perda);
    4. faz a contabilidade completa: custos, aluguel das vendas a descoberto e CDI do caixa.
    Os termos técnicos estão explicados no PEQUENO DICIONÁRIO, mais abaixo.

O QUE VOCÊ PRECISA
    Python 3 com as bibliotecas pandas, numpy, matplotlib e openpyxl. Se faltar alguma:
        pip install pandas numpy matplotlib openpyxl

COMO RODAR
    Deixe a pasta "dados" (4 planilhas do Economatica) ao lado deste arquivo e rode:
        python estrategia.py
    Leva de um a quatro minutos, conforme o computador (ler as planilhas é a parte mais lenta).
    A tela mostra uma linha de progresso por ano.

O QUE SAI
    Na tela, nesta ordem (só o essencial; os detalhes ficam na planilha):
      1. resumo da limpeza (os 5 números mais importantes);
      2. progresso da estratégia, uma linha por ano;
      3. os 5 maiores e os 5 menores retornos diários (acima de 40%, para cima ou para baixo)
         das ações que já estiveram no universo, com o dia em que aconteceram;
      4. resultados ano a ano, resultado acumulado e conferência da contabilidade.
    Na pasta "resultados" (criada ao lado deste arquivo):
      - resultados.xlsx, com as abas:
          ano_a_ano ......... uma linha por ano (retorno, CDI, Sharpe, queda máxima...);
          acumulado ......... o período inteiro, mais a conferência da contabilidade;
          operacoes ......... uma linha por operação (entrada, saída, resultado, motivo);
          diario ............ uma linha por pregão (patrimônio, caixa, juros, custos...);
          limpeza ........... o relatório de limpeza completo e as conferências de viés;
          retornos_grandes .. a lista completa dos retornos diários acima de 40%;
          ajustes_grandes ... a lista completa dos dias de ajuste grande do Economatica;
      - patrimonio.png: patrimônio da estratégia contra o CDI (base 100), com e sem os custos
        de transação;
      - acao_mais_operada.png: o preço da ação que mais operamos, marcando onde abrimos cada
        posição (compra ou venda), onde fechamos e o período em que ficamos posicionados, com
        a volatilidade da ação e o retorno só das operações nela (também mostrados na tela).

COMO O ARQUIVO ESTÁ ORGANIZADO (4 partes, nesta ordem)
    PARTE 1 — LEITURA DOS DADOS ......... lê e confere as 4 planilhas
    PARTE 2 — LIMPEZA DOS DADOS ......... calendário, preços sem negócio, tipos de ativo,
                                          retornos e correção das cisões mal ajustadas
    PARTE 3 — APLICAÇÃO DA ESTRATÉGIA ... universo, sinal (s-score), operações e contabilidade
    PARTE 4 — RESULTADOS ................ ano a ano, acumulado, planilha e gráfico
    Por onde começar a ler: main(), no fim do arquivo, e depois o "Roteiro" no início de cada
    parte (diz qual função chama qual). Toda função começa com um texto "Recebe / Faz / Devolve".

PEQUENO DICIONÁRIO (termos técnicos usados no código, explicados em palavras)
    Pregão ............. dia em que a bolsa funcionou e houve negócios.
    Venda a descoberto . vender uma ação que não temos: pegamos emprestada de quem tem, vendemos
                         hoje e recompramos depois para devolver. Ganha se o preço CAIR.
    Aluguel ............ taxa paga a quem nos emprestou a ação vendida a descoberto (aqui, 2% ao
                         ano sobre o valor da posição).
    CDI ................ taxa de juros de um dia entre bancos; é o rendimento "sem risco" de
                         referência no Brasil. O caixa da estratégia rende CDI, e o CDI é a taxa
                         livre de risco (rf) usada no Sharpe.
    Preço ajustado ..... preço histórico recalculado para que dividendos, desdobramentos e
                         grupamentos não apareçam como saltos falsos. Ex.: uma ação de R$ 10 paga
                         R$ 1 de dividendo e passa a valer R$ 9, mas o acionista não perdeu nada
                         (tem 9 + 1 = 10). O ajuste multiplica os preços anteriores por 9/10 = 0,9:
                         o R$ 10 vira R$ 9 e o retorno do dia sai 0%, e não -10%.
    Desdobramento ...... cada ação vira várias (2 por 1: quem tinha 1 ação de R$ 20 passa a ter
                         2 de R$ 10; ninguém ganha nem perde). Grupamento é o contrário (10 ações
                         de R$ 0,10 viram 1 de R$ 1). Bonificação: a empresa dá ações novas aos
                         acionistas (10%: quem tem 10 ações ganha mais 1).
    ON, PN e unit ...... classes de ação da mesma empresa: ON (ordinária, final 3) dá direito a
                         voto; PN (preferencial, finais 4 a 8) tem preferência nos dividendos;
                         unit (final 11) é um pacote de ações negociado como um papel só (ex.:
                         1 unit da AES Tietê = 1 ON + 4 PN; por isso o preço dela fica perto da
                         soma dos preços das ações do pacote).
    Cisão .............. a empresa se divide em duas; o acionista recebe ações da nova empresa.
    BDR ................ certificado negociado na bolsa brasileira que representa ação de uma
                         empresa estrangeira. Não faz parte deste estudo.
    Viés de sobrevivência  testar só com as empresas que existem hoje. As que quebraram ou foram
                         compradas ficam de fora, e o passado parece melhor do que foi.
    PCA ................ (Análise de Componentes Principais) técnica que resume os movimentos de
                         muitas ações em poucos movimentos comuns, os "fatores" (ex.: "a bolsa
                         toda subiu", "os bancos caíram").
    Autovetor e autovalor  na PCA, cada fator é um autovetor (a "receita": quanto de cada ação
                         entra no fator), e o autovalor dele diz quanto da oscilação total das
                         ações esse fator explica.
    Regressão .......... conta que acha a combinação dos fatores que melhor imita uma ação (a que
                         deixa os menores erros ao quadrado: "mínimos quadrados").
    Resíduo ............ o erro da regressão em cada dia: retorno da ação - retorno da cópia.
    AR(1) .............. modelo em que o valor de amanhã depende só do de hoje:
                         X(amanhã) = a + b × X(hoje) + choque. Se 0 < b < 1, X tende a voltar
                         para um nível de equilíbrio.
    κ (kappa) .......... velocidade dessa volta, medida por ano. κ maior = volta mais rápida.
    s-score ............ quantas "oscilações típicas" a ação está longe do seu equilíbrio em
                         relação à cópia. s = +2: cara (candidata a venda); s = -2: barata
                         (candidata a compra).
    Stop ............... fechar uma operação que já perdeu 5% do valor aplicado.
    Quarentena ......... depois de um stop, a ação fica 10 pregões sem poder ser reaberta.
    Sharpe ............. (retorno da estratégia - CDI) ÷ desvio-padrão dos retornos da estratégia:
                         quanto se ganhou ACIMA do CDI por unidade de oscilação (risco).
                         Negativo = rendeu menos que o CDI. Ex.: retorno de 12%, CDI de 10% e
                         desvio de 2% -> (12 - 10) / 2 = 1,0.
    Queda máxima ....... o pior tombo do patrimônio desde um pico (ex.: de 120 para 90 = -25%).

POR QUE TANTO CUIDADO COM "VER O FUTURO" E COM VIÉS DE SOBREVIVÊNCIA
    A base foi exportada HOJE, com o período inteiro (2009–2025). Ela "sabe" coisas que o
    investidor da época não sabia. Qualquer decisão tomada com essa informação deixa o teste
    diferente (em geral, melhor) do que teria sido na vida real. Os cuidados, um a um (cada um
    também está explicado junto do trecho que o aplica, indicado entre colchetes):

    (1) EMPRESAS CANCELADAS FICAM. Na base, 402 tickers (377 deles do tipo de ação usado no
        estudo) param de negociar antes de dez/2025: foram incorporados, fecharam o capital ou
        quebraram (ex.: OGXP3, da OGX, em recuperação judicial desde 2013, com último negócio
        em 10/01/2019). Nenhum é retirado.
        Se fossem retirados, o teste usaria só as empresas que sobreviveram até 2025 (viés de
        sobrevivência). Se a estratégia tem posição numa ação que para de negociar, a posição
        é encerrada no último preço negociado. [Parte 2: escolher_tickers;
        Parte 3: motivo_para_fechar]

    (2) O PREÇO AJUSTADO "SABE O FUTURO". A cada novo dividendo, desdobramento ou grupamento, o
        Economatica recalcula TODO o histórico ajustado. Então o preço ajustado de 2016 que
        vemos hoje já embute os proventos pagos de 2016 a 2025. Os RETORNOS diários continuam
        certos (os preços antigos são multiplicados todos pelo mesmo número, e a razão entre
        dois deles não muda), mas o NÍVEL em R$ não é o que estava na tela naquele dia.
        Exemplos da própria base:
          - PETR4 em 26/01/2016: negociada a R$ 4,20; o ajustado de hoje mostra R$ 0,99.
            Com o ajustado, o filtro "preço >= R$ 1" barraria a PETR4 em 2016 por causa de
            proventos pagos anos depois.
          - OGXP3 em 2013: negociada entre R$ 5,36 e R$ 0,13; o ajustado mostra entre R$ 536
            e R$ 13 (um grupamento posterior, de 100 ações em 1, multiplicou o histórico por
            100). Com o ajustado, a OGX passaria no filtro de R$ 1 quando valia centavos.
        Regra do código: o ajustado só serve para calcular RETORNOS; o filtro de R$ 1 usa o
        preço NÃO ajustado, o que de fato apareceu na tela. [Parte 3: preparar_regras_do_universo]

    (3) O TICKER É O DE HOJE, PARA TODO O HISTÓRICO. A base mostra o código atual da ação em
        todas as datas (ex.: a B3 aparece como B3SA3 desde 2009, quando o código era BVMF3).
        O tipo do papel é lido pelo final do ticker (3 = ON, 4 = PN, 11 = unit, 32 a 39 =
        BDR), e esse final também é o de hoje. Casos em que a regra do final erraria:
          - GOLL54 e AZUL54 são as PNs da GOL e da Azul (eram GOLL4 e AZUL4; o "54" só surgiu
            em reorganizações de 2025). Pela regra do final, seriam descartadas em TODAS as
            datas, e GOL e Azul sumiriam do teste inteiro por causa de um código criado em
            2025: informação do futuro decidindo o passado. Por isso estão numa lista de
            EXCEÇÕES ACEITAS.
          - DUFB11 era um BDR (da Dufry South America) com o código antigo "11" (parou em
            19/04/2010; no dia seguinte estreou o DAGB33, o BDR que o substituiu). Pela regra
            do final, passaria por unit brasileira. Por isso está numa lista de EXCEÇÕES
            EXCLUÍDAS, junto com PPLA11 e TARP11: o "11" também parece unit brasileira, mas
            são pacotes de BDRs de empresas estrangeiras.
        O ticker de hoje também engana na regra 3 do universo ("uma classe por empresa"). A
        base não tem cadastro de empresas, então "empresa" = 4 primeiras letras do ticker
        (PETR3 e PETR4 -> PETR: só a mais negociada das duas entra no universo). Quando só UMA
        das classes de uma empresa mudou de código, a mesma empresa aparece com duas "4 letras":
          - Ambev: em 11/11/2013 cada ação da antiga Cia. de Bebidas (AMBV3 ou AMBV4) virou 5
            ABEV3. A base mostra o histórico da ON com o código novo (ABEV3, desde 2009) e o da
            PN com o antigo (AMBV4, até 08/11/2013). Pelas 4 letras, ABEV e AMBV seriam duas
            empresas, e as duas classes da Ambev ficariam JUNTAS no universo em 953 pregões:
            a mesma empresa contada duas vezes.
          - TIM: a ON aparece com o código de hoje (TIMS3, desde 2009; até 2011 era TCSL3) e a
            PN com o antigo (TCSL4, até 02/08/2011). Juntas no universo em 388 pregões.
          - AES Tietê: a unit aparece com o código de hoje (AESB3; de 2016 a 2021 era TIET11)
            e a ON e a PN com os antigos (TIET3 e TIET4, até 26/03/2021). Cada unit era um
            pacote de 1 TIET3 + 4 TIET4, então valia quase a soma do pacote. Em 01/06/2020:
            3,07 + 4 x 2,69 = R$ 13,83, quase o preço da AESB3 (R$ 13,74): é a mesma empresa.
          - Via Varejo (hoje Casas Bahia): a ON aparece com o código de hoje (BHIA3; era
            VVAR3) e a unit e a PN com os antigos (VVAR11 e VVAR4, até 23/11/2018). Cada unit
            era 1 ON + 2 PN. Em 22/11/2018: 4,92 + 2 x 4,89 = R$ 14,70, quase o preço da VVAR11
            (R$ 14,75).
          A pequena diferença é normal: a unit e as ações do pacote são negociadas separadas.
          Esses dois últimos pares nunca ficaram juntos no universo (o resultado não muda), mas
          a regra tem de estar certa para qualquer dia.
        Por isso há uma lista explícita "mesma_empresa": ABEV3 conta como empresa AMBV, TIMS3
        como TCSL, AESB3 como TIET e BHIA3 como VVAR. Isso NÃO é informação do futuro: na
        época, todo investidor sabia que AMBV3 e AMBV4 eram da mesma empresa; o que vem do
        futuro é o código que a base mostra. [PARÂMETROS: excecoes_aceitas,
        excecoes_excluidas, mesma_empresa; Parte 2: classificar_ticker, codigo_da_empresa]

    (4) ALGUMAS CISÕES ESTÃO MAL AJUSTADAS NA BASE. Exemplo do Assaí: em 01/03/2021 o Pão de
        Açúcar (PCAR3) se dividiu, e cada PCAR3 recebeu 1 ação do Assaí (ASAI3). O Economatica
        tratou a ASAI3 recebida como se valesse R$ 14,70 (um preço teórico, de antes da
        estreia), mas ela estreou a R$ 71,40. Por isso o PCAR3 ajustado "cai"
        23,33 / (83,00 - 14,70) - 1 = -65,8% nesse dia, quando quem tinha PCAR3 ganhou +14,1%:
            na véspera: 1 PCAR3 a R$ 83,00                          = R$ 83,00
            no dia:     1 PCAR3 a R$ 23,33 + 1 ASAI3 a R$ 71,40     = R$ 94,73
            retorno:    94,73 / 83,00 - 1                           = +14,1%
        O mesmo tipo de erro (retorno da base, no dia da cisão, bem diferente do que o
        acionista ganhou) aparece em outras quatro cisões. As cinco corrigidas:
            ação    data          empresa nova (recebida)        na base    acionista
            EQTL3   25/08/2010    Redentor Energia (RDTR3)         -13,5%       +1,9%
            PRML3   03/12/2010    PortX (PRTX3)                    -40,7%       +3,8%
            MRVE3   21/12/2018    Log (LOGG3)                      +13,0%       +4,5%
            PCAR3   01/03/2021    Assaí (ASAI3)                    -65,8%      +14,1%
            PCAR3   23/08/2023    Grupo Éxito (BDR EXCO32)         -19,4%       +4,7%
        Para cada uma, o código troca o retorno desse único dia pelo do acionista, usando só
        preços da véspera e do próprio dia, lidos da planilha não ajustada. A única exceção é
        o BDR do Éxito, que não está na base: o preço dele foi digitado, com a fonte anotada.
        [PARÂMETROS: cisoes; Parte 2: corrigir_cisoes]
        Para ajudar o grupo a achar outros casos, a Parte 4 lista os dias em que o
        Economatica fez um ajuste grande no preço (só relatório; não decide nada). Dois casos
        suspeitos já estão anotados nos PARÂMETROS, sem correção, para o grupo conferir
        (BRAP4 em 17/12/2021 e AXIA3 em 22/12/2025).

    (5) NADA CALCULADO COM O PERÍODO INTEIRO DECIDE NADA. Ex. do que NÃO fazer: "usar só as
        ações que negociaram até 2025" ou "fechar a posição porque a ação nunca mais vai
        negociar". Em 2012 ninguém sabia disso. Por isso:
          - o universo do dia usa só dados até a VÉSPERA;
          - o sinal usa só dados até o fechamento do PRÓPRIO dia;
          - uma posição é fechada por falta de negócio só no dia em que o negócio de fato não
            aconteceu ("hoje não houve negócio"), nunca por "ela não volta mais".
        As contas que usam o período inteiro (tickers que nunca negociaram, empresas que
        pararam, dia de estreia de cada ticker, as duas listas informativas da Parte 4) só vão
        para relatórios ou não mudam nenhuma decisão; cada uma diz isso no próprio trecho.
        Para comprovar, o parâmetro "data_de_corte" roda tudo com a base cortada numa data,
        como se tivesse sido exportada naquele dia: os resultados antes do corte têm de sair
        idênticos aos da base inteira.
"""

import math
import re
import textwrap
import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")  # desenha o gráfico direto no arquivo, sem abrir janela
import matplotlib.pyplot as plt


# ==============================================================================================
# PARÂMETROS (todos num lugar só; os valores vêm da Tabela 4 da entrega parcial)
# ==============================================================================================
PASTA_DESTE_ARQUIVO = Path(__file__).resolve().parent

PARAMETROS = {
    # ---------------- Arquivos ----------------
    "pasta_dados": PASTA_DESTE_ARQUIVO / "Bases estrategia quant",
    "pasta_resultados": PASTA_DESTE_ARQUIVO / "resultados",
    "arquivo_precos_ajustados": "Precos 2009-2025.xlsx",
    "arquivo_precos_nao_ajustados": "Precos n ajust 2009-2025.xlsx",
    "arquivo_volume": "Volume 2009-2025.xlsx",
    "arquivo_ibov_cdi": "IBOV e CDI 2009-2025.xlsx",
    # Teste "sem futuro": se for uma data (ex.: "2021-02-26"), a base é cortada nessa data logo
    # depois da leitura, como se tivesse sido exportada naquele dia. None = base inteira.
    "data_de_corte": None,

    # ---------------- Período ----------------
    "primeiro_ano_de_operacao": 2010,  # 2009 só "aquece" as janelas de 252 pregões
    "pregoes_por_ano": 252,            # convenção brasileira para anualizar taxas e desvios

    # ---------------- Universo (Tabela 3) ----------------
    # "Volume mediano" = volume financeiro (R$) do dia do meio quando os 252 dias são postos em
    # ordem. Diferente da média, não é puxado por um único dia de volume gigante.
    "janela_universo": 252,            # regra 1: negociou em todos os 252 pregões anteriores
    "preco_minimo": 1.00,              # regra 2: último fechamento NÃO ajustado >= R$ 1
    "tamanho_maximo_universo": 100,    # regra 4: as 100 de maior volume mediano (N <= 100)

    # ---------------- Sinal (Seção 4) ----------------
    "janela_pca": 252,                 # pregões usados na PCA
    "variancia_minima_explicada": 0.55,  # K = menor nº de fatores que explica >= 55%
    "janela_regressao": 60,            # pregões da regressão da cópia e do AR(1)
    # κ mínimo: 252 / 30 = 8,4, ou seja, o afastamento tem de voltar, em média, em menos de
    # 30 pregões. Ações que voltam devagar demais não geram sinal.
    "kappa_minimo": 8.4,

    # ---------------- Operação (Tabela 2 e Seção 5.2) ----------------
    "s_para_abrir": 1.25,              # compra se s < -1,25; venda se s > +1,25
    "s_para_fechar_compra": -0.50,     # compra fecha se s > -0,50
    "s_para_fechar_venda": 0.75,       # venda fecha se s < +0,75
    "stop_de_perda": 0.05,             # fecha se a operação perde 5% do valor aplicado
    "pregoes_de_quarentena": 10,       # após o stop, a ação fica 10 pregões sem reabrir
    # "Ponta" = cada negócio: a abertura e, depois, o fechamento. Ex.: uma operação de
    # R$ 20.000 paga 0,001 x 20.000 = R$ 20 para abrir e, de novo, cerca de R$ 20 para fechar.
    "custo_por_ponta": 0.0010,
    # Aluguel cobrado por pregão (2% / 252) sobre o valor das posições vendidas a descoberto.
    # Ex.: venda de R$ 20.000 -> 20.000 x 0,02 / 252 = R$ 1,59 por pregão.
    "aluguel_ao_ano": 0.02,
    "patrimonio_inicial": 1_000_000.00,

    # ---------------- Tipos de ativo (armadilha do "ticker de hoje") ----------------
    # Final do ticker = o que vem depois dos 4 primeiros caracteres (código da empresa).
    # 3 = ordinária (ON), 4 a 8 = preferenciais (PN, PNA, PNB...), 11 = unit (pacote de ações).
    "finais_aceitos": ["3", "4", "5", "6", "7", "8", "11"],
    # BDRs são certificados de ações de empresas estrangeiras: não fazem parte do estudo.
    "finais_de_bdr": ["32", "33", "34", "35", "39"],
    # Exceções explícitas (ver o item (3) do texto do topo). O Economatica mostra o ticker de
    # HOJE em todas as datas; se a regra de final fosse aplicada sem exceções, a GOL e a Azul
    # sumiriam do teste inteiro só por causa de códigos criados em 2025 (informação do futuro
    # decidindo o passado), e o DUFB11, o PPLA11 e o TARP11, que são BDRs ou pacotes de BDRs,
    # passariam por units brasileiras.
    "excecoes_aceitas": {
        "GOLL54": "PN da GOL (era GOLL4); o código 54 veio da reorganização de 2025",
        "AZUL54": "PN da Azul (era AZUL4); o código 54 veio da reorganização de 2025",
    },
    "excecoes_excluidas": {
        "DUFB11": "BDR da Dufry South America com código antigo '11' (parou em 19/04/2010; "
                  "virou DAGB33 em 20/04/2010); não é ação brasileira",
        # PPLA11 e TARP11: o "11" parece unit brasileira, mas são units feitas de BDRs de
        # empresas estrangeiras. Nunca entram no universo (não mudam o resultado); ficam aqui
        # para a regra ser coerente com a do DUFB11.
        "PPLA11": "unit de BDRs da PPLA Participations (empresa estrangeira); não é ação "
                  "brasileira",
        "TARP11": "unit de BDRs da Tarpon (empresa estrangeira); não é ação brasileira",
    },
    # Mesma empresa com DOIS códigos de 4 letras (outro efeito do "ticker de hoje", item (3)
    # do texto do topo). A regra 3 do universo deixa só uma classe por empresa e reconhece a
    # empresa pelas 4 primeiras letras do ticker. Mas, como a base mostra o código de HOJE em
    # todas as datas, quando só uma das classes mudou de código a mesma empresa aparece como
    # duas "empresas" diferentes:
    #   - ABEV3: de 2009 a 2013 é a antiga AMBV3, a ON da Cia. de Bebidas das Américas (em
    #     11/11/2013 cada AMBV3 ou AMBV4 virou 5 ABEV3: na base, o ABEV3 não ajustado vai de
    #     R$ 87,00 para 87,00 / 5 = R$ 17,40). A AMBV4 (PN da mesma empresa) aparece com o
    #     código antigo. Sem esta correção, ABEV3 e AMBV4 ficavam JUNTAS no universo em 953
    #     pregões: a mesma empresa contada duas vezes.
    #   - TIMS3: até 2011 é a antiga TCSL3, a ON da TIM Participações; a PN (TCSL4, até
    #     02/08/2011) aparece com o código antigo. Ficavam juntas no universo em 388 pregões.
    #   - AESB3: de 2016 a 2021 é a antiga TIET11, a unit da AES Tietê (1 unit = 1 TIET3 +
    #     4 TIET4), e convive na base com TIET3 e TIET4 (até 26/03/2021). Prova, em
    #     01/06/2020: TIET3 + 4 x TIET4 = 3,07 + 4 x 2,69 = R$ 13,83, quase igual à AESB3
    #     (R$ 13,74).
    #   - BHIA3: é a ON da Via Varejo (antiga VVAR3, hoje Casas Bahia) e convive na base com a
    #     unit VVAR11 e a PN VVAR4 (até 23/11/2018; 1 unit = 1 ON + 2 PN). Prova, em
    #     22/11/2018: BHIA3 + 2 x VVAR4 = 4,92 + 2 x 4,89 = R$ 14,70, quase igual à VVAR11
    #     (R$ 14,75).
    #   (A diferença pequena é normal: a unit e as ações do pacote são negociadas separadas.)
    #   Esses dois pares nunca ficaram juntos no universo (o resultado não muda), mas a regra
    #   tem de estar certa para qualquer dia.
    # Não é informação do futuro: na época, todo investidor sabia que eram a mesma empresa.
    # Aqui: ticker -> código de empresa a usar no lugar das 4 primeiras letras.
    "mesma_empresa": {"ABEV3": "AMBV", "TIMS3": "TCSL", "AESB3": "TIET", "BHIA3": "VVAR"},

    # ---------------- Eventos societários mal ajustados na base ----------------
    # Cisão = a empresa se divide em duas e o acionista recebe ações da nova empresa. Em
    # algumas cisões o Economatica ajustou mal o preço (ver o item (4) do texto do topo), e o
    # retorno da base no dia não é o que o acionista ganhou. Para cada cisão abaixo, o código
    # troca o retorno daquele dia pelo do acionista. Em palavras: quem tinha 1 ação ontem tem,
    # hoje, essa ação mais as ações recebidas da empresa nova; então
    #     R = (ação hoje + ações recebidas por ação x ação recebida hoje) / ação ontem - 1
    # Os preços são os NÃO ajustados, LIDOS da base. A única exceção é quando a ação recebida
    # não está na base (o BDR do Éxito): aí o preço vai digitado em "preco_manual_recebida",
    # com a fonte comentada. Em cada item: os preços da conta (véspera e dia) e o resultado.
    "cisoes": [
        # Pão de Açúcar -> Assaí: 1 ASAI3 por PCAR3.
        # (23,33 + 1 x 71,40) / 83,00 - 1 = +14,1%   (na base: -65,8%)
        {"acao": "PCAR3", "data": "2021-03-01", "acao_recebida": "ASAI3",
         "acoes_recebidas_por_acao": 1.0},
        # Equatorial -> Redentor Energia: 1 RDTR3 por EQTL3.
        # (10,90 + 1 x 7,55) / 18,10 - 1 = +1,9%   (na base: -13,5%)
        {"acao": "EQTL3", "data": "2010-08-25", "acao_recebida": "RDTR3",
         "acoes_recebidas_por_acao": 1.0},
        # LLX (hoje Prumo, PRML3) -> PortX: 1 PRTX3 por PRML3.
        # (4,59 + 1 x 3,90) / 8,18 - 1 = +3,8%   (na base: -40,7%)
        {"acao": "PRML3", "data": "2010-12-03", "acao_recebida": "PRTX3",
         "acoes_recebidas_por_acao": 1.0},
        # MRV -> Log Commercial Properties: 0,07215075382 LOGG3 por MRVE3 (≈ 0,07215; ou seja,
        # cerca de 7 LOGG3 para cada 100 MRVE3).
        # (12,01 + 0,07215 x 17,50) / 12,70 - 1 = (12,01 + 1,26) / 12,70 - 1 = +4,5%
        # (na base: +13,0%)
        {"acao": "MRVE3", "data": "2018-12-21", "acao_recebida": "LOGG3",
         "acoes_recebidas_por_acao": 0.07215075382},
        # Pão de Açúcar -> Grupo Éxito: 1 BDR do Éxito (EXCO32) por PCAR3. O EXCO32 NÃO está
        # na base, então o preço dele vai à mão. É um preço APROXIMADO, tirado da notícia da
        # Suno de 23/08/2023, que diz duas coisas: o BDR "fechou em alta de 21,7%", e a máxima
        # do dia, R$ 15, correspondia a uma alta de 30,3%. Então:
        #   preço de referência (base das altas) = 15 / 1,303 ≈ R$ 11,51
        #   fechamento = 11,51 x 1,217 ≈ R$ 14,01
        # (6,56 + 1 x 14,01) / 19,65 - 1 ≈ +4,7%   (na base: -19,4%)
        {"acao": "PCAR3", "data": "2023-08-23", "acao_recebida": "EXCO32",
         "acoes_recebidas_por_acao": 1.0, "preco_manual_recebida": 14.01},
        # PARA O GRUPO CONFERIR (não corrigidos; só anotados aqui). Nos dois, o preço não
        # ajustado cai muito num dia em que o acionista recebeu outros papéis, e o ajustado da
        # base quase não se mexe; falta confirmar se o ajuste do Economatica está certo:
        #   - BRAP4 em 17/12/2021: a Bradespar devolveu capital aos acionistas pagando com
        #     ações da Vale (VALE3). Não ajustado: -58,5%; ajustado da base: +0,6%;
        #   - AXIA3 em 22/12/2025: estreia da AXIA7 no mesmo dia. Não ajustado: -22,5%;
        #     ajustado da base: -2,2%.
    ],

    # ---------------- Relatórios (só informativos: não decidem nada) ----------------
    "limite_retorno_grande": 0.40,     # lista retornos diários acima de 40% (para conferência)
    # Lista os dias em que a razão ajustado ÷ não ajustado mudou mais de 5% de um pregão para
    # o outro: dia em que o Economatica fez um ajuste grande (pista de cisão, desdobramento...).
    # Como ler e usar essa lista: ver listar_ajustes_grandes, na Parte 4.
    "limite_ajuste_grande": 0.05,

    # ---------------- Conferência das planilhas ----------------
    # Uma planilha de ações do Economatica tem centenas de tickers (aqui, 1.419). Se tiver
    # poucas colunas, provavelmente é outro arquivo no lugar errado (ex.: a de IBOV e CDI).
    "minimo_de_tickers": 100,
}


# ==============================================================================================
# PEQUENAS FERRAMENTAS DE TEXTO (formatação brasileira: vírgula decimal)
# ==============================================================================================
def numero_br(valor, casas=2):
    """Recebe um número; devolve o texto no formato brasileiro. Ex.: 1234.5 -> '1.234,50'."""
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return "-"
    texto = f"{valor:,.{casas}f}"  # formato americano: 1,234.50
    # Troca "," por "." e "." por ",". O "#" é um lugar provisório: sem ele, as vírgulas
    # viradas em ponto seriam viradas de volta em vírgula no passo seguinte.
    return texto.replace(",", "#").replace(".", ",").replace("#", ".")


def porcentagem_br(fracao, casas=2):
    """Recebe uma fração; devolve em %. Ex.: 0.0523 -> '5,23%'."""
    if fracao is None or (isinstance(fracao, float) and math.isnan(fracao)):
        return "-"
    return numero_br(100 * fracao, casas) + "%"


def reais_br(valor):
    """Recebe um valor em R$; devolve o texto. Ex.: 1500 -> 'R$ 1.500,00'."""
    return "R$ " + numero_br(valor, 2)


def data_br(data):
    """Recebe uma data; devolve 'dd/mm/aaaa'."""
    return pd.Timestamp(data).strftime("%d/%m/%Y")


def titulo(texto):
    """Imprime um título de seção na tela."""
    print("\n" + "=" * 100)
    print(texto)
    print("=" * 100)


def imprimir_paragrafo(texto, recuo=6):
    """Imprime um texto longo quebrado em linhas de até 100 caracteres, com recuo à esquerda."""
    print(textwrap.fill(texto, width=100, initial_indent=" " * recuo,
                        subsequent_indent=" " * recuo))


# ##############################################################################################
#
#                                 PARTE 1 — LEITURA DOS DADOS
#
# ##############################################################################################
# Roteiro: ler_todos_os_dados() (a última função desta parte) chama, em ordem:
#   ler_planilha_de_acoes() para o ajustado, o não ajustado e o volume -> ler_ibov_e_cdi()
#   -> juntar_pelo_nome_do_ticker() -> cortar_na_data() (só no teste sem futuro)
def extrair_ticker(texto_do_cabecalho):
    """
    Recebe: o texto de uma célula do cabeçalho do Economatica (tem várias linhas).
    Faz:    pega a ÚLTIMA linha, que é o código da ação (ticker).
    Devolve: o ticker.
    Ex.: "Fechamento\\najust p/ prov\\nEm moeda orig\\nPETR4" -> "PETR4"
    """
    return str(texto_do_cabecalho).splitlines()[-1].strip()


def conferir_que_arquivo_existe(caminho):
    """Para o programa com mensagem clara se o arquivo não existir."""
    if not caminho.exists():
        raise FileNotFoundError(
            f"\n\nARQUIVO NÃO ENCONTRADO: {caminho}\n"
            "Coloque as 4 planilhas do Economatica na pasta 'dados', ao lado deste arquivo.")


def ler_datas_e_numeros(caminho):
    """
    Recebe: o caminho de uma planilha do Economatica.
    Faz:    lê a PRIMEIRA aba (os nomes das abas variam de arquivo para arquivo), trata "-" como
            vazio, apaga linhas sem data (o Economatica deixa linhas vazias depois do fim) e põe
            a data como índice da tabela.
    Devolve: (tabela com uma linha por data, lista com os textos originais do cabeçalho).
    """
    conferir_que_arquivo_existe(caminho)
    # O cabeçalho é lido à parte, "cru" (header=None: a 1ª linha vem como dado, sem mexer).
    # Por quê: na leitura normal, se dois cabeçalhos forem iguais (o mesmo ticker em duas
    # colunas), o pandas renomeia o segundo para "...PETR4.1", e a repetição sumiria sem aviso
    # (o "PETR4.1" seria descartado mais tarde como "outro final"). Lido cru, o repetido
    # continua igual e é pego em ler_planilha_de_acoes.
    primeira_linha = pd.read_excel(caminho, sheet_name=0, header=None, nrows=1)
    cabecalhos = [str(celula) for celula in primeira_linha.iloc[0]]
    tabela = pd.read_excel(caminho, sheet_name=0, header=0, na_values=["-"])
    if len(cabecalhos) != tabela.shape[1]:   # trava: as duas leituras têm de ter as mesmas colunas
        raise ValueError(f"\n\nEm {caminho.name}, o cabeçalho tem {len(cabecalhos)} colunas e os "
                         f"dados têm {tabela.shape[1]}. A planilha parece estar fora do formato.")
    if cabecalhos[0].strip() != "Data":
        raise ValueError(f"\n\nEm {caminho.name}, a primeira coluna deveria ser 'Data', "
                         f"mas é '{cabecalhos[0]}'.")
    # 1ª coluna -> datas; o que não for data (linha vazia no fim) vira "NaT" (data vazia).
    datas = pd.to_datetime(tabela.iloc[:, 0], errors="coerce")
    tem_data = datas.notna()
    tabela = tabela.loc[tem_data].copy()                              # só linhas com data
    tabela.index = pd.DatetimeIndex(datas[tem_data], name="Data")     # a data vira o rótulo
    tabela = tabela.iloc[:, 1:]                                       # tira a coluna "Data"
    if tabela.index.has_duplicates or not tabela.index.is_monotonic_increasing:
        raise ValueError(f"\n\nEm {caminho.name}, as datas estão repetidas ou fora de ordem.")
    return tabela, cabecalhos[1:]


def converter_para_numeros(tabela, nome_do_arquivo):
    """
    Recebe: uma tabela lida e o nome do arquivo (para a mensagem de erro).
    Faz:    confere que todas as colunas são números (depois de "-" virar vazio). Se sobrar
            algum texto, para com erro mostrando exemplos.
    Devolve: a tabela em números decimais (float).
    """
    for coluna in tabela.columns:
        if not pd.api.types.is_numeric_dtype(tabela[coluna]):
            # Texto que não vira número (e não estava vazio) = valor estranho na planilha.
            nao_vira_numero = pd.to_numeric(tabela[coluna], errors="coerce").isna()
            estranhos = tabela[coluna][nao_vira_numero & tabela[coluna].notna()]
            exemplos = estranhos.head(3).tolist()
            raise ValueError(f"\n\nEm {nome_do_arquivo}, a coluna {coluna} tem valores que não "
                             f"são números: {exemplos}")
    return tabela.astype(float)


def ler_planilha_de_acoes(caminho, tipo, textos_obrigatorios, textos_proibidos,
                          minimo_de_tickers):
    """
    Recebe: o caminho de uma planilha de ações, o tipo esperado (ex.: "preços ajustados"),
            os textos que TODO cabeçalho deve ter e os que NÃO pode ter, e o número mínimo de
            tickers. Ex.: o ajustado tem "ajust p/ prov" e não tem "não aj"; o não ajustado
            tem "não aj"; o volume tem "Volume" e "em milhares".
    Faz:    três conferências, cada uma parando o programa com uma mensagem clara:
            1) a planilha tem mais de 100 tickers (uma de ações do Economatica tem centenas; se
               tiver 3 colunas, provavelmente é a de IBOV e CDI posta no lugar errado);
            2) o cabeçalho de cada coluna diz o TIPO certo de dado (detecta arquivo trocado, ex.:
               o não ajustado no lugar do ajustado);
            3) nenhum ticker aparece em duas colunas (com duas colunas "PETR4", não daria para
               saber qual é a certa).
            Depois troca cada cabeçalho longo pelo ticker.
    Devolve: tabela (datas × tickers) com números; "sem dado" vira vazio (NaN).
    """
    tabela, cabecalhos = ler_datas_e_numeros(caminho)
    tickers = [extrair_ticker(cabecalho) for cabecalho in cabecalhos]
    if len(tickers) <= minimo_de_tickers:
        raise ValueError(
            f"\n\nPLANILHA ERRADA? {caminho.name} foi lida como a planilha de {tipo}, mas tem só "
            f"{len(tickers)} colunas de ativos ({', '.join(tickers[:5])}).\nUma planilha de ações "
            f"do Economatica tem mais de {minimo_de_tickers}. Se aparecem IBOV e CDI, é a "
            "planilha de IBOV e CDI no lugar errado: confira os nomes dos arquivos nos PARÂMETROS.")
    for cabecalho in cabecalhos:
        faltam = [texto for texto in textos_obrigatorios if texto not in cabecalho]
        sobram = [texto for texto in textos_proibidos if texto in cabecalho]
        if faltam or sobram:
            # Para a mensagem: cada texto entre aspas ('Volume' e 'em milhares') e o cabeçalho
            # numa linha só (as quebras de linha da célula viram " | ").
            esperados = " e ".join(f"'{texto}'" for texto in textos_obrigatorios)
            proibidos = " nem ".join(f"'{texto}'" for texto in textos_proibidos)
            cabecalho_em_uma_linha = " | ".join(cabecalho.splitlines())
            raise ValueError(
                f"\n\nCABEÇALHO INESPERADO em {caminho.name}, lida como a planilha de {tipo}:\n"
                f"    {cabecalho_em_uma_linha}\n"
                f"Todo cabeçalho dessa planilha deveria ter {esperados} e não ter {proibidos}.\n"
                "Os arquivos podem estar trocados: confira os nomes dos arquivos nos PARÂMETROS.")
    tabela.columns = tickers
    if tabela.columns.has_duplicates:
        repetidos = sorted(set(tabela.columns[tabela.columns.duplicated()]))
        raise ValueError(
            f"\n\nTICKER REPETIDO em {caminho.name}: {', '.join(repetidos[:10])} aparece(m) em "
            "mais de uma coluna.\nNão dá para saber qual coluna é a certa; exporte a planilha de "
            "novo sem colunas repetidas.")
    return converter_para_numeros(tabela, caminho.name)


def ler_ibov_e_cdi(caminho):
    """
    Recebe: o caminho da planilha "IBOV e CDI".
    Faz:    confere pelo cabeçalho que a coluna 1 é o IBOV e a coluna 2 é o "CDI 252 dias"
            (taxa ANUAL em %, ex.: 13,62). A coluna "CDI ao dia" NÃO é usada: ela pode vir como
            fórmula do Excel, que o Python não calcula; recalculamos a taxa diária na Parte 2.
    Devolve: tabela com as colunas "ibov" e "cdi_anual_pct" (vazia nos dias sem expediente
             bancário).
    """
    tabela, cabecalhos = ler_datas_e_numeros(caminho)
    nomes = [extrair_ticker(c) for c in cabecalhos]
    if len(nomes) < 2 or nomes[0] != "IBOV" or nomes[1] != "CDI 252 dias":
        raise ValueError(f"\n\nEm {caminho.name}, esperava as colunas 'IBOV' e 'CDI 252 dias' "
                         f"nas posições 1 e 2, mas encontrei {nomes[:3]}.")
    tabela = tabela.iloc[:, :2]
    tabela.columns = ["ibov", "cdi_anual_pct"]
    return converter_para_numeros(tabela, caminho.name)


def juntar_pelo_nome_do_ticker(ajustados, nao_ajustados, volumes, ibov_cdi):
    """
    Recebe: as quatro tabelas lidas.
    Faz:    confere que as três planilhas de ações têm EXATAMENTE os mesmos tickers e que as
            quatro têm exatamente as mesmas datas; depois põe as colunas do não ajustado e do
            volume na mesma ordem do ajustado, ESCOLHENDO PELO NOME DO TICKER.
            Por quê: a planilha não ajustada vem com os tickers em outra ordem. Juntar pela
            posição da coluna misturaria ações (ex.: o preço da PETR4 iria parar na VALE3).
    Devolve: (ajustados, nao_ajustados, volumes) com colunas na mesma ordem.
    """
    tickers = set(ajustados.columns)
    for nome, tabela in [("não ajustados", nao_ajustados), ("volume", volumes)]:
        if set(tabela.columns) != tickers:
            faltam = sorted(tickers - set(tabela.columns))[:10]
            sobram = sorted(set(tabela.columns) - tickers)[:10]
            raise ValueError(f"\n\nOs tickers da planilha de {nome} não batem com os do preço "
                             f"ajustado. Faltam: {faltam}. Sobram: {sobram}.")
    for nome, tabela in [("não ajustados", nao_ajustados), ("volume", volumes),
                         ("IBOV e CDI", ibov_cdi)]:
        if not tabela.index.equals(ajustados.index):
            raise ValueError(f"\n\nAs datas da planilha de {nome} não batem com as do preço "
                             f"ajustado ({len(tabela)} contra {len(ajustados)} datas).")
    ordem = list(ajustados.columns)
    return ajustados, nao_ajustados[ordem], volumes[ordem]


def cortar_na_data(dados, data_de_corte):
    """
    Recebe: o dicionário de tabelas lidas e uma data.
    Faz:    apaga tudo DEPOIS da data, como se a base tivesse sido exportada naquele dia.
            Serve para o teste "sem futuro": se algum cálculo usasse dados posteriores, os
            resultados antes do corte mudariam.
    Devolve: o dicionário com as tabelas cortadas.
    """
    limite = pd.Timestamp(data_de_corte)
    return {nome: tabela.loc[:limite] for nome, tabela in dados.items()}


def ler_todos_os_dados(parametros):
    """
    Recebe: os parâmetros (onde estão os arquivos).
    Faz:    lê as 4 planilhas, confere cabeçalhos, tickers e datas, e junta tudo pelo nome.
    Devolve: dicionário com "precos_ajustados", "precos_nao_ajustados", "volumes" (em R$ mil,
             como vem da planilha) e "ibov_cdi".
    """
    pasta = Path(parametros["pasta_dados"])
    minimo = parametros["minimo_de_tickers"]
    print("Lendo as planilhas (de meio minuto a alguns minutos, conforme o computador)...")
    ajustados = ler_planilha_de_acoes(pasta / parametros["arquivo_precos_ajustados"],
                                      "preços ajustados", ["ajust p/ prov"], ["não aj"], minimo)
    nao_ajustados = ler_planilha_de_acoes(pasta / parametros["arquivo_precos_nao_ajustados"],
                                          "preços não ajustados", ["não aj"], ["ajust p/ prov"],
                                          minimo)
    # O volume tem de estar "em milhares": a Parte 2 multiplica por 1.000 para chegar em R$.
    volumes = ler_planilha_de_acoes(pasta / parametros["arquivo_volume"], "volume",
                                    ["Volume", "em milhares"], ["Fechamento"], minimo)
    ibov_cdi = ler_ibov_e_cdi(pasta / parametros["arquivo_ibov_cdi"])
    ajustados, nao_ajustados, volumes = juntar_pelo_nome_do_ticker(
        ajustados, nao_ajustados, volumes, ibov_cdi)
    dados = {"precos_ajustados": ajustados, "precos_nao_ajustados": nao_ajustados,
             "volumes": volumes, "ibov_cdi": ibov_cdi}
    if parametros["data_de_corte"] is not None:
        print(f"ATENÇÃO: base cortada em {data_br(parametros['data_de_corte'])} "
              "(teste sem futuro).")
        dados = cortar_na_data(dados, parametros["data_de_corte"])
    print(f"Lidos {numero_br(ajustados.shape[1], 0)} tickers e "
          f"{numero_br(len(dados['precos_ajustados']), 0)} datas "
          f"({data_br(dados['precos_ajustados'].index[0])} a "
          f"{data_br(dados['precos_ajustados'].index[-1])}).")
    return dados


# ##############################################################################################
#
#                                 PARTE 2 — LIMPEZA DOS DADOS
#
# ##############################################################################################
# Roteiro: limpar_dados() (a última função desta parte) chama, em ordem:
#   montar_calendario() -> limpar_precos_e_volumes() -> listar_estreias() (só relatório)
#   -> escolher_tickers() -> calcular_retornos() -> corrigir_cisoes()
#   -> calcular_fator_cdi_por_pregao() -> codigo_da_empresa() para cada ticker
# As funções menores logo abaixo são usadas por essas.
def anotar(relatorio, etapa, quantidade, explicacao):
    """Acrescenta uma linha ao relatório de limpeza (mostrado na tela e salvo no Excel)."""
    relatorio.append({"etapa": etapa, "quantidade": quantidade, "explicacao": explicacao})


def contar_casos(tabela_sim_nao):
    """
    Recebe: uma tabela de verdadeiro/falso (ex.: "este preço é <= 0?" para cada dia e ação).
    Faz:    conta quantos "verdadeiro" há na tabela inteira. O primeiro .sum() soma cada coluna
            (verdadeiro vale 1, falso vale 0); o segundo soma os totais das colunas.
    Devolve: o número de casos (inteiro).
    """
    return int(tabela_sim_nao.sum().sum())


def separar_codigo_e_final(ticker):
    """
    Recebe: um ticker, ex.: "PETR4", "TEND3-old", "GOLL54", "KLBN11".
    Faz:    tira o sufixo "-old"/"old" (que o Economatica põe em códigos antigos repetidos) e
            separa os 4 primeiros caracteres (código da empresa) do resto (o "final", que diz o
            tipo do papel).
    Devolve: (empresa, final). Ex.: "TEND3-old" -> ("TEND", "3"); "KLBN11" -> ("KLBN", "11").
    Limitação: não há cadastro de empresas na base, então "empresa" = 4 primeiros caracteres
    do ticker de HOJE. Isso pode errar de dois jeitos opostos:
      - duas empresas diferentes com as mesmas 4 letras em épocas diferentes: como uma
        substitui a outra no tempo, isso não costuma juntar duas empresas no mesmo dia;
      - a MESMA empresa com dois códigos diferentes, porque uma classe mudou de código e a
        outra não: a ABEV3 de 2009 a 2013 é a antiga AMBV3, mas a PN da mesma empresa aparece
        como AMBV4; a TIMS3 de 2009 a 2011 é a antiga TCSL3, e a PN aparece como TCSL4. Esse
        caso, que contaria a mesma empresa duas vezes no universo, é corrigido pela lista
        PARAMETROS["mesma_empresa"], aplicada em codigo_da_empresa (logo abaixo).
    """
    # Apaga "-old" ou "old" no FIM do texto ("-?" = hífen opcional; "$" = fim do texto).
    codigo = re.sub(r"-?old$", "", ticker, flags=re.IGNORECASE)
    return codigo[:4], codigo[4:]


def codigo_da_empresa(ticker, parametros):
    """
    Recebe: um ticker e os parâmetros.
    Faz:    devolve o código da empresa usado na regra 3 do universo (uma classe por empresa):
            normalmente as 4 primeiras letras do ticker; para os tickers da lista
            PARAMETROS["mesma_empresa"], o código indicado lá.
            Ex.: "PETR4" -> "PETR"; "ABEV3" -> "AMBV" (a mesma empresa da AMBV4, até 2013);
            "TIMS3" -> "TCSL" (a mesma empresa da TCSL4, até 2011).
    Devolve: o código da empresa (texto).
    """
    if ticker in parametros["mesma_empresa"]:
        return parametros["mesma_empresa"][ticker]
    return separar_codigo_e_final(ticker)[0]


def listar_estreias(volumes, pregoes):
    """
    Recebe: os volumes de TODOS os tickers (antes do filtro de tipo) e os pregões.
    Faz:    acha o dia do primeiro negócio de cada ticker ("estreia" na base). Ticker que já
            negociava no 1º pregão da base não conta (não dá para saber quando estreou).
            SÓ PARA O RELATÓRIO da Parte 4: uma cisão costuma vir com a estreia da empresa
            nova no mesmo dia (ex.: ASAI3 em 01/03/2021). Usa o período inteiro, mas não entra
            em decisão nenhuma.
    Devolve: dicionário data -> lista de tickers que estrearam nesse dia.
    """
    estreias = {}
    for ticker in volumes.columns:
        primeiro_negocio = volumes[ticker].first_valid_index()   # None se nunca negociou
        if primeiro_negocio is not None and primeiro_negocio > pregoes[0]:
            # setdefault cria a lista vazia na 1ª vez que a data aparece; depois só acrescenta.
            estreias.setdefault(primeiro_negocio, []).append(ticker)
    return estreias


def classificar_ticker(ticker, parametros):
    """
    Recebe: um ticker e os parâmetros.
    Faz:    aplica a regra de tipo de ativo, com as exceções explícitas.
    Devolve: o motivo da decisão (texto). Só "aceito..." significa que o ticker fica.
    """
    _, final = separar_codigo_e_final(ticker)
    if ticker in parametros["excecoes_excluidas"]:
        return "excluído por exceção explícita"
    if ticker in parametros["excecoes_aceitas"]:
        return "aceito por exceção explícita"
    if final in parametros["finais_aceitos"]:
        return "aceito (final 3, 4, 5, 6, 7, 8 ou 11)"
    if final in parametros["finais_de_bdr"]:
        return "BDR (final 32, 33, 34, 35 ou 39)"
    if final and final[-1].isalpha():
        return "final com letra (3B, 6B...: mercado de balcão)"
    return "outro final (ex.: 12, 13, 36)"


def apagar_precos_sem_negocio(precos, volumes):
    """
    Recebe: uma tabela de preços e a de volumes (com vazio onde não houve negócio).
    Faz:    apaga o preço nos dias em que a ação não teve negócio. Um preço sem negócio não
            foi negociado de verdade (ex.: o "preço teórico" do ASAI3 no dia anterior à estreia).
    Devolve: (preços limpos, quantos preços foram apagados).
    """
    sem_negocio = volumes.isna()
    apagados = contar_casos(precos.notna() & sem_negocio)
    # .where(condição) mantém o valor onde a condição vale e põe vazio (NaN) no resto.
    return precos.where(~sem_negocio), apagados


def calcular_retornos(precos_ajustados):
    """
    Recebe: preços AJUSTADOS (datas × tickers), já só com pregões.
    Faz:    R(t) = P(t) / P(t-1) - 1 entre pregões consecutivos. Fica vazio se faltar o preço
            de hoje ou de ontem (não repetimos preço velho, o que criaria retornos zero falsos).
            Ex.: 10,00 ontem e 10,50 hoje -> 10,50 / 10,00 - 1 = 0,05 = +5%.
            No código, .shift(1) empurra a tabela uma linha para baixo: na linha de hoje
            aparece o preço de ontem, e a divisão é feita linha a linha.
    Devolve: tabela de retornos (mesmo formato).
    Por que o AJUSTADO: ele já inclui dividendos, desdobramentos etc., então o retorno do dia é
    o ganho real do acionista. Já o NÍVEL em R$ do preço ajustado não entra em decisão nenhuma
    (o filtro de R$ 1 usa o não ajustado; ver a regra 2 do universo na Parte 3).
    """
    return precos_ajustados / precos_ajustados.shift(1) - 1


def formatar_proporcao(proporcao):
    """Recebe a proporção da cisão; devolve o texto. Ex.: 1.0 -> '1'; 0.07215075 -> '0,07215'."""
    if proporcao == int(proporcao):
        return numero_br(proporcao, 0)
    return numero_br(proporcao, 5)


def retorno_do_acionista_na_cisao(cisao, data, vespera, nao_ajustados, nome):
    """
    Recebe: uma cisão (da lista de parâmetros), a data dela, o pregão anterior (véspera), os
            preços NÃO ajustados e o nome da cisão (para as mensagens de erro).
    Faz:    calcula o que o acionista de fato ganhou no dia da cisão, com os preços que estavam
            na tela (não ajustados, lidos da base). Quem tinha 1 ação ontem tem, hoje, essa
            ação MAIS as ações recebidas da empresa nova. Logo:
                R = (ação hoje + ações recebidas por ação x ação recebida hoje) / ação ontem - 1
            Ex. do Assaí: (23,33 + 1 x 71,40) / 83,00 - 1 = 94,73 / 83,00 - 1 = +14,1%.
            Ex. da MRV: cada MRVE3 recebeu 0,07215 LOGG3, então
                (12,01 + 0,07215 x 17,50) / 12,70 - 1 = (12,01 + 1,26) / 12,70 - 1 = +4,5%.
            Se a ação recebida não está na base (ex.: o BDR do Éxito, EXCO32), usa o
            "preco_manual_recebida" dos parâmetros, que traz a fonte comentada.
            Para com erro se algum ticker ou preço necessário não estiver na base.
    Devolve: (R, preço da ação ontem, preço da ação hoje, preço da ação recebida hoje,
              True se o preço da recebida foi digitado à mão).
    """
    acao, recebida = cisao["acao"], cisao["acao_recebida"]
    preco_manual = cisao.get("preco_manual_recebida")   # None se não houver preço manual
    necessarios = [acao] if preco_manual is not None else [acao, recebida]
    for ticker in necessarios:
        if ticker not in nao_ajustados.columns:
            raise ValueError(f"\n\n{nome}: o ticker {ticker} não está na base limpa.\nSe for a "
                             "ação recebida e ela não estiver na base, informe o preço de "
                             "fechamento dela no dia em 'preco_manual_recebida' (PARÂMETROS, "
                             "lista 'cisoes'), com a fonte num comentário.")
    preco_ontem = nao_ajustados.at[vespera, acao]
    preco_hoje = nao_ajustados.at[data, acao]
    if preco_manual is not None:
        preco_recebida = float(preco_manual)
    else:
        preco_recebida = nao_ajustados.at[data, recebida]
    if np.isnan([preco_ontem, preco_hoje, preco_recebida]).any():
        raise ValueError(f"\n\n{nome}: faltam preços não ajustados na base (a ação na véspera "
                         "ou no dia, ou a ação recebida no dia). Confira a data em PARÂMETROS, "
                         "lista 'cisoes'.")
    retorno_correto = ((preco_hoje + cisao["acoes_recebidas_por_acao"] * preco_recebida)
                       / preco_ontem - 1)
    return retorno_correto, preco_ontem, preco_hoje, preco_recebida, preco_manual is not None


def corrigir_cisoes(retornos, ajustados, nao_ajustados, pregoes, parametros, relatorio):
    """
    Recebe: retornos, preços ajustados e não ajustados, pregões, parâmetros e o relatório.
    Faz:    corrige o retorno do dia de cada cisão da lista PARAMETROS["cisoes"].
            O problema (item (4) do texto do topo), no exemplo do Assaí: em 01/03/2021 cada
            PCAR3 recebeu 1 ASAI3. O Economatica descontou a ASAI3 por um preço teórico de
            R$ 14,70, mas ela estreou a R$ 71,40. Por isso o PCAR3 ajustado "cai" -65,8% no
            dia, quando o acionista, que passou a ter PCAR3 + ASAI3, ganhou +14,1%. O mesmo
            tipo de erro aparece nas outras cisões da lista (EQTL3, PRML3, MRVE3 e PCAR3 em
            2023; tabela no item (4) do texto do topo).
            A correção: trocar esse ÚNICO retorno pelo retorno do acionista, sem mexer em
            nenhum outro número.
            Por que isso é o mesmo que "multiplicar os preços ajustados anteriores à cisão por
            um fator" (a forma descrita na especificação do projeto): multiplicar todos os
            preços antigos pelo mesmo número não muda a razão entre eles, logo não muda nenhum
            retorno antigo; só muda o retorno do dia da cisão. O fator equivalente,
            P_aj(dia) / ((1 + R) x P_aj(véspera)) (0,2993 no Assaí), vai para o relatório.
            Trocar só o retorno tem uma vantagem: os retornos anteriores ficam idênticos, bit a
            bit, aos de uma base que termina antes da cisão (é o que o teste sem futuro confere).
            Não é viés do futuro: só usa preços da véspera e do próprio dia (no Éxito, o preço
            de fechamento do BDR no próprio dia, digitado porque não está na base).
            Se a data estiver fora da base (antes do 2º pregão ou depois do último), a correção
            é pulada e anotada: numa base cortada antes da cisão, ela ainda não aconteceu.
    Devolve: os retornos corrigidos.
    """
    retornos = retornos.copy()
    for cisao in parametros["cisoes"]:
        acao, recebida = cisao["acao"], cisao["acao_recebida"]
        data = pd.Timestamp(cisao["data"])
        nome = f"Cisão {acao} -> {recebida} em {data_br(data)}"
        if data <= pregoes[0] or data > pregoes[-1]:
            anotar(relatorio, nome, "pulada", "a data está fora da base (sem véspera ou depois "
                   "do último pregão): nada a corrigir")
            continue
        if data not in pregoes:
            raise ValueError(f"\n\n{nome}: a data não é um pregão da base (feriado ou fim de "
                             "semana?). Confira a data em PARÂMETROS, lista 'cisoes'.")
        vespera = pregoes[pregoes.get_loc(data) - 1]
        retorno_correto, preco_ontem, preco_hoje, preco_recebida, manual = (
            retorno_do_acionista_na_cisao(cisao, data, vespera, nao_ajustados, nome))
        retorno_da_base = retornos.at[data, acao]
        fator = ajustados.at[data, acao] / ((1 + retorno_correto) * ajustados.at[vespera, acao])
        retornos.at[data, acao] = retorno_correto
        origem = ("preços não ajustados da base, menos o da ação recebida, digitado à mão (ver "
                  "a fonte nos PARÂMETROS)" if manual else "preços não ajustados da base")
        anotar(relatorio, nome, porcentagem_br(retorno_correto, 1),
               f"retorno do dia: na base {porcentagem_br(retorno_da_base, 1)} -> corrigido "
               f"{porcentagem_br(retorno_correto, 1)} = ({numero_br(preco_hoje)} + "
               f"{formatar_proporcao(cisao['acoes_recebidas_por_acao'])} x "
               f"{numero_br(preco_recebida)}) / {numero_br(preco_ontem)} - 1 ({origem}); "
               f"equivale a multiplicar os preços ajustados anteriores por {numero_br(fator, 4)}")
    return retornos


def calcular_fator_cdi_por_pregao(cdi_anual_pct, pregoes):
    """
    Recebe: o CDI anual em % de TODAS as datas da planilha (inclusive dias sem pregão) e a
            lista de pregões.
    Faz:    0) lembrete: o CDI é a taxa de juros de um dia entre bancos. A planilha traz a taxa
               ANUAL de cada dia (ex.: 13,62% ao ano), na convenção de 252 dias úteis por ano;
            1) converte a taxa anual em diária: (1 + 13,62/100)^(1/252) - 1 ≈ 0,0507% ao dia
               (porque 252 dias rendendo 0,0507% compostos dão 13,62%); dia sem expediente
               bancário (CDI vazio) não rende nada (fator 1);
            2) junta os dias entre um pregão e o seguinte. A taxa do CDI de um dia remunera o
               dinheiro desse dia até o dia útil seguinte (é assim que o CDI funciona). Então,
               do fechamento do pregão anterior ao fechamento de hoje, o caixa rende as taxas
               de todos os dias úteis do pregão anterior (inclusive) até hoje (exclusive).
               Ex. (janeiro de 2011): 24/01 e 26/01 foram pregões e 25/01 (aniversário de São
               Paulo) foi feriado só da bolsa, com CDI normal: o pregão de 26/01 recebe as taxas
               de 24/01 e de 25/01.
               Isso também evita usar a taxa de hoje, que só é divulgada depois do fechamento.
    Devolve: série com o fator de crescimento do caixa em cada pregão (ex.: 1,000507).
    """
    fator_diario = ((1 + cdi_anual_pct / 100) ** (1 / 252)).fillna(1.0)
    fator_por_pregao = np.ones(len(pregoes))
    # Para cada data, o pregão que recebe a taxa é o primeiro pregão DEPOIS dela.
    # np.searchsorted diz em que posição cada data entraria na lista (em ordem) de pregões; com
    # side="right", uma data que é pregão cai na posição do pregão SEGUINTE.
    # Ex.: pregões [24/01, 26/01, 27/01] -> 24/01 vai para a posição 1 (26/01), 25/01 também
    # vai para a posição 1 (26/01) e 26/01 vai para a posição 2 (27/01).
    proximo_pregao = np.searchsorted(pregoes.values, fator_diario.index.values, side="right")
    for posicao, fator in zip(proximo_pregao, fator_diario.to_numpy()):
        if posicao < len(pregoes):  # datas depois do último pregão não entram
            fator_por_pregao[posicao] *= fator
    return pd.Series(fator_por_pregao, index=pregoes, name="fator_cdi")


def montar_calendario(volumes, relatorio, parametros):
    """
    Recebe: a tabela de volumes (todas as datas da planilha), o relatório e os parâmetros.
    Faz:    define os pregões: datas em que pelo menos uma ação teve negócio (volume > 0). As
            outras são feriados que o Economatica exporta mesmo assim. Saber se uma data é
            pregão usa só o volume daquele dia, conhecido no fechamento (não há futuro aqui).
            Para com erro se houver menos de 253 pregões (252 de janela + 1 para operar).
    Devolve: os pregões (lista de datas).
    """
    eh_pregao = (volumes > 0).any(axis=1)
    pregoes = volumes.index[eh_pregao]
    anotar(relatorio, "Datas na planilha", len(volumes), "dias úteis exportados")
    anotar(relatorio, "Datas sem nenhum negócio (feriados) - retiradas", int((~eh_pregao).sum()),
           "nenhuma ação negociou; não são pregões")
    anotar(relatorio, "Pregões", len(pregoes),
           f"de {data_br(pregoes[0])} a {data_br(pregoes[-1])}")
    minimo = max(parametros["janela_universo"], parametros["janela_pca"]) + 1
    if len(pregoes) < minimo:
        raise ValueError(f"\n\nDADOS CURTOS DEMAIS: há {len(pregoes)} pregões; são precisos "
                         f"pelo menos {minimo} (252 para as janelas + 1 para operar).")
    return pregoes


def limpar_precos_e_volumes(ajustados, nao_ajustados, volumes, relatorio):
    """
    Recebe: preços ajustados, não ajustados e volumes (em R$), já só nos pregões.
    Faz:    1) volume zero ou vazio = não houve negócio. Guardamos vazio (e não zero) para que
               as medianas de volume só usem dias com negócio;
            2) apaga os preços dos dias sem negócio;
            3) conta os dias com volume mas sem preço ajustado: para a estratégia esses dias
               ficam sem preço (como se a ação não tivesse negociado);
            4) apaga preços menores ou iguais a zero (não deveria haver nenhum).
    Devolve: (ajustados, nao_ajustados, volumes) limpos.
    """
    volumes = volumes.where(volumes > 0)
    ajustados, n_apagados_aj = apagar_precos_sem_negocio(ajustados, volumes)
    nao_ajustados, n_apagados_na = apagar_precos_sem_negocio(nao_ajustados, volumes)
    anotar(relatorio, "Preços ajustados em dia sem volume - apagados", n_apagados_aj,
           "preço sem negócio não foi negociado (ex.: preço teórico antes da estreia)")
    anotar(relatorio, "Preços não ajustados em dia sem volume - apagados", n_apagados_na,
           "mesmo motivo")
    volume_sem_preco = volumes.notna() & ajustados.isna()
    com_nao_ajustado = contar_casos(volume_sem_preco & nao_ajustados.notna())
    tickers_casos = ", ".join(volumes.columns[volume_sem_preco.any(axis=0)])
    anotar(relatorio, "Dias com volume mas sem preço ajustado", contar_casos(volume_sem_preco),
           f"o não ajustado tem preço em {com_nao_ajustado} deles; para a estratégia o dia fica "
           f"sem preço (tickers: {tickers_casos})")
    precos_invalidos = contar_casos(ajustados <= 0) + contar_casos(nao_ajustados <= 0)
    anotar(relatorio, "Preços menores ou iguais a zero - apagados", precos_invalidos,
           "preço de ação tem de ser positivo")
    return ajustados.where(ajustados > 0), nao_ajustados.where(nao_ajustados > 0), volumes


def escolher_tickers(volumes, pregoes, relatorio, parametros):
    """
    Recebe: volumes limpos (vazio = sem negócio), pregões, relatório e parâmetros.
    Faz:    1) descarta tickers que nunca negociaram. Isso usa o período inteiro, mas não muda
               nenhuma decisão: um ticker sem negócio nunca passaria na regra 1 do universo;
            2) aplica a regra de tipo de ativo, com as exceções explícitas (GOLL54, AZUL54,
               DUFB11), e mostra quantos saíram por cada motivo;
            3) conta os tickers que param de negociar antes do último mês da base (empresas
               canceladas, incorporadas, que fecharam o capital ou quebraram). Eles FICAM:
               tirá-los seria viés de sobrevivência (item (1) do texto do topo). Ex.: a OGXP3,
               com último negócio em 10/01/2019, fica; enquanto negociou, pôde entrar no
               universo como qualquer outra. A contagem é só para o relatório; nenhuma decisão
               usa "esta ação vai parar de negociar".
    Devolve: a lista de tickers que ficam para a estratégia.
    """
    negociou_alguma_vez = volumes.notna().any(axis=0)  # True se teve negócio em algum dia
    anotar(relatorio, "Tickers na planilha", len(volumes.columns), "")
    anotar(relatorio, "Tickers que nunca negociaram - descartados",
           int((~negociou_alguma_vez).sum()), "não afeta decisões: nunca passariam na regra 1")
    tickers = list(volumes.columns[negociou_alguma_vez])

    motivos = pd.Series({ticker: classificar_ticker(ticker, parametros) for ticker in tickers})
    for motivo, quantidade in motivos.value_counts().items():
        anotar(relatorio, f"Tipo de ativo: {motivo}", int(quantidade), "entre os que negociaram")
    for ticker, porque in parametros["excecoes_aceitas"].items():
        anotar(relatorio, f"Exceção aceita: {ticker}",
               "aceito" if ticker in tickers else "fora da base", porque)
    for ticker, porque in parametros["excecoes_excluidas"].items():
        anotar(relatorio, f"Exceção excluída: {ticker}",
               "excluído" if ticker in tickers else "fora da base", porque)
    ficam = [ticker for ticker in tickers if motivos[ticker].startswith("aceito")]
    anotar(relatorio, "Tickers que ficam para a estratégia", len(ficam), "")

    # Só para o relatório (não decide nada): data do último negócio de cada ticker.
    ultimo_negocio = pd.Series({ticker: volumes[ticker].last_valid_index() for ticker in tickers})
    inicio_ultimo_mes = pregoes[-1].replace(day=1)  # ex.: 30/12/2025 -> 01/12/2025
    pararam = ultimo_negocio < inicio_ultimo_mes
    anotar(relatorio, "Tickers que param antes do último mês da base - FICAM",
           int(pararam.sum()), f"empresas canceladas ou incorporadas (entre os que negociaram); "
           f"{int(pararam[ficam].sum())} deles passaram no filtro de tipo. Tirá-los seria viés "
           "de sobrevivência")
    return ficam


def limpar_dados(dados, parametros):
    """
    Recebe: o dicionário lido na Parte 1 e os parâmetros.
    Faz:    todas as limpezas, em ordem, anotando no relatório quantos casos cada uma afetou.
    Devolve: (dicionário com os dados limpos, relatório de limpeza). O dicionário tem:
             "pregoes", "precos_ajustados", "precos_nao_ajustados", "volumes" (em R$, vazio
             quando não houve negócio), "retornos" (já corrigidos das cisões), "fator_cdi" (por
             pregão), "empresas" (código da empresa de cada ticker, ver codigo_da_empresa) e
             "estreias" (dia do 1º negócio de cada ticker; só para o relatório da Parte 4).
    """
    relatorio = []
    volumes = dados["volumes"] * 1000  # a planilha vem em R$ MIL; passamos para R$
    pregoes = montar_calendario(volumes, relatorio, parametros)
    ajustados, nao_ajustados, volumes = limpar_precos_e_volumes(
        dados["precos_ajustados"].loc[pregoes], dados["precos_nao_ajustados"].loc[pregoes],
        volumes.loc[pregoes], relatorio)
    estreias = listar_estreias(volumes, pregoes)   # antes do filtro de tipo; só relatório
    tickers = escolher_tickers(volumes, pregoes, relatorio, parametros)
    ajustados, nao_ajustados = ajustados[tickers], nao_ajustados[tickers]
    volumes = volumes[tickers]

    retornos = corrigir_cisoes(calcular_retornos(ajustados), ajustados, nao_ajustados, pregoes,
                               parametros, relatorio)

    cdi_anual = dados["ibov_cdi"]["cdi_anual_pct"]
    fator_cdi = calcular_fator_cdi_por_pregao(cdi_anual, pregoes)
    anotar(relatorio, "Pregões sem CDI na planilha", int(cdi_anual.reindex(pregoes).isna().sum()),
           "nesses dias o caixa não rende")
    anotar(relatorio, "Dias com CDI mas sem pregão", int(cdi_anual.drop(pregoes).notna().sum()),
           "feriados só da bolsa: o CDI desses dias entra no pregão seguinte")

    empresas = pd.Series({ticker: codigo_da_empresa(ticker, parametros) for ticker in tickers})
    for ticker, empresa in parametros["mesma_empresa"].items():
        mesma = [outro for outro in tickers if empresas[outro] == empresa and outro != ticker]
        anotar(relatorio, f"Mesma empresa: {ticker} conta como {empresa}",
               "aplicado" if ticker in tickers else "fora da base",
               f"o ticker de hoje esconde que é a mesma empresa de {', '.join(mesma) or '-'}; "
               "a regra 3 do universo passa a deixar só uma classe dessa empresa")
    dados_limpos = {"pregoes": pregoes, "precos_ajustados": ajustados,
                    "precos_nao_ajustados": nao_ajustados, "volumes": volumes,
                    "retornos": retornos, "fator_cdi": fator_cdi, "empresas": empresas,
                    "estreias": estreias}
    return dados_limpos, relatorio


# ##############################################################################################
#
#                              PARTE 3 — APLICAÇÃO DA ESTRATÉGIA
#
# ##############################################################################################
# A IDEIA EM PALAVRAS. Ações parecidas andam juntas. Se nos últimos dias a ITUB4 subiu bem
# mais do que "aquilo que costuma explicar a ITUB4" (a bolsa, os bancos...), ela ficou cara em
# relação à sua cópia. A aposta é que essa diferença se desfaça: vende-se a ITUB4 a descoberto
# e espera-se a volta. A ação que ficou barata em relação à cópia é comprada.
#
# Roteiro: aplicar_estrategia() (a última função desta parte) percorre os pregões em ordem e,
# em cada um, chama:
#   escolher_universo_do_dia()     universo, só com dados até ONTEM ............... (3.1)
#   calcular_s_scores_do_dia()     PCA -> cópia -> placar -> AR(1) -> s-score ..... (3.2)
#   atualizar_posicoes_e_caixa()   passo 1: retorno do dia, aluguel, CDI do caixa . (3.3)
#   fazer_fechamentos()            passo 2: fecha o que tiver motivo
#   fazer_aberturas()              passo 3: abre compras e vendas novas
#   registrar_dia()                passo 4: guarda a linha do dia
#
# Convenção de nomes nesta parte: "hoje" é o NÚMERO do pregão (a posição dele na lista de
# pregões: 0 = 02/01/2009, 1 = 05/01/2009, ...), e "data" é a data desse pregão. Usamos o número
# porque as contas do dia a dia usam matrizes do numpy (bem mais rápidas que tabelas do pandas
# num laço de 4 mil dias), e matriz do numpy é lida por posição: retornos[hoje, coluna].
# ---------------------------------------- 3.1 Universo ----------------------------------------
def preparar_regras_do_universo(dados, parametros):
    """
    Recebe: dados limpos e parâmetros.
    Faz:    calcula, para todos os pregões de uma vez, o que as regras do universo precisam,
            olhando SEMPRE só para trás (até a véspera). As contas "rolling" (janela móvel)
            só usam o passado; o ".shift(1)" empurra tudo uma linha para baixo, para que a
            linha de hoje tenha só o que se sabia ATÉ ONTEM.
            Ex.: no pregão de 10/03/2015, a regra 1 olha os 252 pregões que terminam em
            09/03/2015. O próprio dia 10 nunca entra.
    Devolve: dicionário com três tabelas (pregões × tickers):
      "regra_1": True se negociou em TODOS os 252 pregões anteriores (ação nova só entra depois
                 de 252 pregões);
      "preco_nao_ajustado_ate_ontem": último fechamento NÃO AJUSTADO até a véspera (regra 2).
                 Por que o não ajustado (item (2) do texto do topo): o ajustado de uma data
                 antiga embute eventos que vieram depois. Ex.: em 26/01/2016 a PETR4 foi
                 negociada a R$ 4,20, mas o ajustado de hoje mostra R$ 0,99; com o ajustado, a
                 PETR4 seria barrada em 2016;
      "volume_mediano": volume financeiro mediano (em R$) nos 252 pregões anteriores
                 (regras 3 e 4).
    """
    janela = parametros["janela_universo"]

    # Regra 1. teve_negocio: 1 se a ação tem preço (houve negócio) no dia, 0 se não.
    teve_negocio = dados["precos_ajustados"].notna().astype(int)
    dias_com_negocio = teve_negocio.rolling(janela).sum()  # nos 252 pregões terminando HOJE
    dias_com_negocio_ate_ontem = dias_com_negocio.shift(1)  # ... terminando ONTEM
    regra_1 = dias_com_negocio_ate_ontem == janela

    # Regra 2. .ffill() repete o último preço negociado nos dias sem negócio ("ffill" = forward
    # fill, preencher para a frente); o .shift(1) faz a linha de hoje mostrar o de ontem.
    ultimo_preco_negociado = dados["precos_nao_ajustados"].ffill()
    preco_ate_ontem = ultimo_preco_negociado.shift(1)

    # Regras 3 e 4. Se faltar volume em algum dos 252 dias, a mediana fica vazia; isso não
    # atrapalha, porque nesse caso a ação já foi barrada pela regra 1.
    volume_mediano_ate_hoje = dados["volumes"].rolling(janela).median()
    volume_mediano = volume_mediano_ate_hoje.shift(1)

    return {"regra_1": regra_1, "preco_nao_ajustado_ate_ontem": preco_ate_ontem,
            "volume_mediano": volume_mediano}


def escolher_universo_do_dia(hoje, regras, tickers, empresas, parametros):
    """
    Recebe: o número do pregão de hoje, as regras (em matrizes numpy), os tickers e a empresa
            de cada ticker.
    Faz:    aplica as 4 regras da Tabela 3, em ordem, com dados até a véspera:
            1) negociou em todos os 252 pregões anteriores;
            2) último fechamento não ajustado até ontem >= R$ 1;
            3) uma classe por empresa: fica a de maior volume mediano (ex.: entre PETR3 e PETR4
               fica a mais negociada), para não contar a mesma empresa duas vezes. A empresa
               de cada ticker vem de codigo_da_empresa (Parte 2): as 4 primeiras letras, salvo
               os casos da lista "mesma_empresa" (ex.: ABEV3 e AMBV4 = a mesma empresa);
            4) entre as que sobram, as 100 de maior volume mediano.
            Empate de volume (raríssimo) é desfeito pela ordem alfabética, para o resultado não
            depender da ordem das colunas.
    Devolve: lista dos tickers do universo, em ordem alfabética.
    """
    # regras["..."][hoje] é a linha de hoje: um valor por ticker, na ordem de "tickers".
    passa_regra_2 = regras["preco_ate_ontem"][hoje] >= parametros["preco_minimo"]
    passa = regras["regra_1"][hoje] & passa_regra_2   # True/False por ticker
    # tickers[passa] pega só os tickers em que "passa" é True (o mesmo vale para as outras).
    candidatos = pd.DataFrame({"ticker": tickers[passa], "empresa": empresas[passa],
                               "volume_mediano": regras["volume_mediano"][hoje][passa]})
    # Do maior volume para o menor; em caso de empate, ordem alfabética.
    candidatos = candidatos.sort_values(["volume_mediano", "ticker"], ascending=[False, True])
    # Regra 3: de cada empresa fica a primeira linha, que é a de maior volume.
    candidatos = candidatos.drop_duplicates("empresa", keep="first")
    # Regra 4: as 100 primeiras, que são as de maior volume.
    candidatos = candidatos.head(parametros["tamanho_maximo_universo"])
    return sorted(candidatos["ticker"])


# ---------------------------------------- 3.2 Sinal -------------------------------------------
def calcular_fatores_pca(retornos_janela, parametros):
    """
    Recebe: matriz de retornos (252 pregões × ações), sem buracos.
    Faz:    a PCA da Seção 4.2. Em palavras: com 100 ações, há 100 séries que sobem e descem;
            a PCA procura os poucos "movimentos comuns" (fatores) que explicam a maior parte
            dessas oscilações, como "a bolsa toda subiu" ou "os bancos caíram". Passos:
            1) padroniza cada ação (tira a média e divide pelo desvio), para que as ações mais
               voláteis não dominem;
            2) calcula a matriz de correlação entre as ações (100 × 100: quanto cada par anda
               junto, de -1 a +1);
            3) acha os autovetores dessa matriz (cada um é um fator: diz quanto de cada ação
               entra nele) e os autovalores (quanto da oscilação total cada fator explica), e
               põe do maior para o menor;
            4) K = menor número de fatores que explica pelo menos 55% da oscilação total.
               Ex.: se explicam 40%, 10%, 7%, ... -> acumulado 40%, 50%, 57% -> K = 3;
            5) cada fator vira uma carteira com peso Q = autovetor ÷ desvio da ação (ação mais
               volátil recebe peso menor, porque o autovetor foi achado com retornos
               padronizados), e o retorno do fator num dia é a soma de Q x retorno das ações.
    Devolve: (retornos dos K fatores em cada pregão da janela [252 × K], K).
    Notação numpy usada: "@" é multiplicação de matrizes; ".T" é a matriz transposta (linhas
    viram colunas); "axis=0" faz a conta coluna a coluna, ou seja, uma vez para cada ação.
    """
    medias = retornos_janela.mean(axis=0)              # média de cada ação
    desvios = retornos_janela.std(axis=0, ddof=1)      # desvio de cada ação
    padronizados = (retornos_janela - medias) / desvios
    # Correlação = média dos produtos dos retornos padronizados (dividindo por n - 1).
    correlacao = padronizados.T @ padronizados / (len(retornos_janela) - 1)
    autovalores, autovetores = np.linalg.eigh(correlacao)  # vêm do menor para o maior
    ordem = np.argsort(autovalores)[::-1]                   # invertemos: do maior para o menor
    autovalores, autovetores = autovalores[ordem], autovetores[:, ordem]

    # K: a fração acumulada é 0,40, 0,50, 0,57... no exemplo acima. "fracao_acumulada >= 0,55"
    # dá [False, False, True, ...]; np.argmax devolve a posição do primeiro True (2, contando
    # do zero); somando 1, K = 3.
    fracao_acumulada = np.cumsum(autovalores) / autovalores.sum()
    passou_do_minimo = fracao_acumulada >= parametros["variancia_minima_explicada"]
    k = int(np.argmax(passou_do_minimo)) + 1

    # Pesos Q: cada coluna dos K primeiros autovetores dividida, linha a linha, pelo desvio da
    # ação daquela linha (o "[:, None]" transforma os desvios numa coluna para essa divisão).
    pesos_q = autovetores[:, :k] / desvios[:, None]
    retornos_dos_fatores = retornos_janela @ pesos_q   # em cada dia: soma de Q x retorno
    return retornos_dos_fatores, k


def calcular_placar(retornos_60, fatores_60):
    """
    Recebe: retornos das ações (60 × ações) e dos fatores (60 × K) nos últimos 60 pregões.
    Faz:    1) para cada ação, uma regressão: acha os números b0, b1, ..., bK que fazem
                   b0 + b1 F1 + ... + bK FK
               ficar o mais perto possível do retorno da ação nos 60 dias (mínimos quadrados:
               a soma dos erros ao quadrado é a menor possível). b0 é o intercepto (uma
               constante); b1 F1 + ... + bK FK é a "cópia" da ação feita com os fatores;
            2) resíduo de cada dia = retorno da ação - (b0 + cópia): o que a cópia não explica;
            3) placar = soma acumulada dos resíduos: X(1) = e1, X(2) = e1 + e2, ...
               Placar subindo = a ação vem rendendo mais que a cópia. Com intercepto, os 60
               resíduos somam zero, então o placar de hoje (o último) é sempre zero.
            Como todas as ações usam os mesmos fatores, uma única chamada do numpy resolve as
            regressões de todas as ações ao mesmo tempo.
    Devolve: matriz 60 × ações com o placar de cada ação em cada dia da janela.
    """
    # Coluna de 1s ao lado dos fatores: é ela que faz a regressão ter intercepto (b0).
    explicativas = np.column_stack([np.ones(len(fatores_60)), fatores_60])
    # lstsq = "least squares" (mínimos quadrados). Devolve os coeficientes b0..bK de cada ação.
    coeficientes = np.linalg.lstsq(explicativas, retornos_60, rcond=None)[0]
    residuos = retornos_60 - explicativas @ coeficientes
    return np.cumsum(residuos, axis=0)   # soma acumulada, dia a dia, para cada ação


def estimar_reversao(placar, parametros):
    """
    Recebe: o placar (60 × ações).
    Faz:    para cada ação, ajusta um AR(1) ao placar: uma regressão do placar de amanhã no
            de hoje, com os 59 pares (dia 1, dia 2), (dia 2, dia 3), ..., (dia 59, dia 60):
                X(amanhã) = a + b X(hoje) + choque
            Mínimos quadrados com uma variável só têm fórmula pronta:
                b = covariância(X hoje, X amanhã) / variância(X hoje)
                a = média(X amanhã) - b x média(X hoje)
            Se 0 < b < 1, o placar é puxado de volta para um equilíbrio: de um dia para o
            outro, sobra só a fração b do afastamento (com b = 0,90, depois de 10 dias sobram
            0,90^10 = 35% do afastamento). Do AR(1) saem:
              κ (velocidade de volta, por ano) = -252 ln b   (ex.: b = 0,90 -> κ = 26,6)
              m (nível de equilíbrio do placar) = a / (1 - b)
              σ_eq (tamanho típico das oscilações em torno de m) = raiz(Var(choque) / (1 - b²))
            Válida só se 0 < b < 1 e κ > 8,4 (volta média em menos de 30 pregões: 252/30 = 8,4).
            Var(choque) é a variância amostral comum (divide por n - 1).
    Devolve: (m, sigma_eq, valida): três vetores, uma posição por ação.
    """
    placar_hoje, placar_amanha = placar[:-1], placar[1:]   # dias 1 a 59 e dias 2 a 60
    media_hoje, media_amanha = placar_hoje.mean(axis=0), placar_amanha.mean(axis=0)
    afastamento = placar_hoje - media_hoje
    with np.errstate(divide="ignore", invalid="ignore"):  # placar parado daria 0/0
        b = ((afastamento * (placar_amanha - media_amanha)).sum(axis=0)
             / (afastamento ** 2).sum(axis=0))
    a = media_amanha - b * media_hoje
    choques = placar_amanha - (a + b * placar_hoje)        # o que o AR(1) não previu
    variancia_choque = choques.var(axis=0, ddof=1)
    b_entre_0_e_1 = np.isfinite(b) & (b > 0) & (b < 1)
    # Onde b não está entre 0 e 1, a ação já é inválida. Pomos 0,5 no lugar só para as
    # contas abaixo não darem erro (log de número negativo, divisão por zero); esses
    # resultados nunca são usados.
    b_seguro = np.where(b_entre_0_e_1, b, 0.5)
    kappa = -parametros["pregoes_por_ano"] * np.log(b_seguro)
    m = a / (1 - b_seguro)
    sigma_eq = np.sqrt(variancia_choque / (1 - b_seguro ** 2))
    valida = b_entre_0_e_1 & (kappa > parametros["kappa_minimo"]) & (sigma_eq > 0)
    return m, sigma_eq, valida


def calcular_s_scores_do_dia(hoje, universo, retornos, tem_preco, coluna_do_ticker, parametros):
    """
    Recebe: o número do pregão de hoje, o universo do dia, a matriz de retornos, a matriz
            "tem preço" e o mapa ticker -> coluna.
    Faz:    calcula o s-score das ações do universo com dados até o FECHAMENTO DE HOJE, na
            sequência PCA (252 pregões) -> cópia e placar (60 pregões) -> AR(1) -> s-score.
            Só entram ações com preço hoje (sem preço hoje não há retorno de hoje e a ação não
            pode ser negociada). A regra 1 garante os 251 retornos anteriores sem buracos.
            O s-score mede o afastamento de hoje em "oscilações típicas":
                s = (placar de hoje - m) / σ_eq
            Como o placar de hoje é sempre zero (ver calcular_placar), fica s = -m / σ_eq.
            Antes, tira-se de cada m a média dos m das ações válidas do dia (ajuste previsto
            na metodologia: o que é comum a todas as ações não é afastamento de nenhuma delas):
                s = -(m - média dos m das válidas do dia) / σ_eq
            Ex.: m = -0,02, média dos m = 0,00, σ_eq = 0,01 -> s = -(-0,02 - 0) / 0,01 = +2:
            o placar de hoje (zero) está acima do equilíbrio (-0,02), ou seja, a ação rendeu
            mais que a cópia e está CARA (candidata a venda).
    Devolve: (dicionário ticker -> s-score das ações válidas, K do dia).
    """
    janela, janela_reg = parametros["janela_pca"], parametros["janela_regressao"]
    acoes = [ticker for ticker in universo if tem_preco[hoje, coluna_do_ticker[ticker]]]
    colunas = [coluna_do_ticker[ticker] for ticker in acoes]
    # Linhas: os 252 pregões que terminam HOJE (o fim de um intervalo do Python não entra,
    # por isso o "+ 1"). Colunas: só as das ações escolhidas acima.
    retornos_janela = retornos[hoje - janela + 1: hoje + 1][:, colunas]
    if np.isnan(retornos_janela).any():  # trava de segurança: a regra 1 impede isso
        raise RuntimeError(f"Janela de retornos com buraco no pregão {hoje}.")
    # Ação com preço parado a janela toda (desvio zero) não pode ser padronizada.
    tem_variacao = retornos_janela.std(axis=0, ddof=1) > 0
    acoes = [ticker for ticker, ok in zip(acoes, tem_variacao) if ok]
    retornos_janela = retornos_janela[:, tem_variacao]
    if len(acoes) < 2:
        return {}, 0
    fatores, k = calcular_fatores_pca(retornos_janela, parametros)
    if k + 2 > janela_reg:  # regressão precisaria de mais dados que a janela (não ocorre)
        return {}, k
    # A cópia e o placar usam só os últimos 60 dos 252 pregões.
    placar = calcular_placar(retornos_janela[-janela_reg:], fatores[-janela_reg:])
    m, sigma_eq, valida = estimar_reversao(placar, parametros)
    if not valida.any():
        return {}, k
    s = -(m[valida] - m[valida].mean()) / sigma_eq[valida]
    acoes_validas = [ticker for ticker, ok in zip(acoes, valida) if ok]
    return dict(zip(acoes_validas, s.tolist())), k


# ------------------------------------- 3.3 Operações ------------------------------------------
# Como as coisas são guardadas (dicionários simples do Python):
#   posicao  = uma operação aberta: "ativo", "lado" ("compra" ou "venda"), "data_entrada",
#              "pregao_entrada", "s_entrada", "valor_aplicado" (R$ na abertura, fixo),
#              "valor_atual" (R$ no fechamento de hoje) e "custos" e "aluguel" pagos até agora;
#   carteira = "caixa" (R$), "posicoes" (ativo -> posicao) e "bloqueada_ate" (ativo -> último
#              pregão da quarentena).
def direcao(posicao):
    """Devolve +1 para compra e -1 para venda a descoberto (o sinal do ganho)."""
    return 1 if posicao["lado"] == "compra" else -1


def resultado_da_operacao(posicao):
    """
    Recebe: uma posição aberta.
    Faz:    resultado acumulado até agora = ganho de preço - custos pagos - aluguel pago.
            Ex.: compra de R$ 10.000 que hoje vale R$ 9.550, custo de entrada R$ 10 e sem
            aluguel -> (9.550 - 10.000) - 10 = -460 = -4,6% do valor aplicado (stop ainda não).
            Na venda a descoberto o ganho de preço tem o sinal trocado (direcao = -1): venda de
            R$ 10.000 que hoje vale R$ 9.500 -> -1 x (9.500 - 10.000) = +500 de ganho.
    Devolve: o resultado em R$.
    """
    ganho = direcao(posicao) * (posicao["valor_atual"] - posicao["valor_aplicado"])
    return ganho - posicao["custos"] - posicao["aluguel"]


def calcular_patrimonio(carteira):
    """
    Recebe: a carteira (caixa e posições).
    Faz:    patrimônio = caixa + valor das compras - valor das vendas a descoberto (as ações
            vendidas a descoberto são uma dívida: um dia teremos de recomprá-las).
            Ex. (sem custos): começamos com R$ 1.000.000 em caixa. Compramos R$ 10.000 de uma
            ação (o caixa cai para 990.000) e vendemos a descoberto R$ 10.000 de outra (o
            dinheiro da venda entra e o caixa volta a 1.000.000). Patrimônio = 1.000.000 +
            10.000 - 10.000 = R$ 1.000.000: abrir posições não cria nem destrói riqueza.
    Devolve: o patrimônio em R$.
    """
    return carteira["caixa"] + sum(direcao(p) * p["valor_atual"]
                                   for p in carteira["posicoes"].values())


def motivo_para_fechar(posicao, tem_preco_hoje, esta_no_universo, s_hoje, parametros):
    """
    Recebe: uma posição, se a ação tem preço hoje, se está no universo de hoje e o s-score de
            hoje (None se não houver s válido).
    Faz:    testa os motivos de fechamento NA ORDEM DE PRIORIDADE:
            1) "sem preço": a ação não negociou hoje. Fecha no último preço negociado. Só usamos
               o que se sabe hoje ("hoje não houve negócio"), nunca "ela não volta mais";
            2) "saiu do universo";
            3) "stop": resultado acumulado (com custo de entrada e aluguel) <= -5% do aplicado;
            4) "sinal": compra fecha se s > -0,50; venda fecha se s < +0,75.
            Sem s-score válido hoje, a posição é mantida (valem só os itens 1 a 3).
    Devolve: o motivo (texto) ou None se a posição continua.
    """
    if not tem_preco_hoje:
        return "sem preço"
    if not esta_no_universo:
        return "saiu do universo"
    limite_de_perda = -parametros["stop_de_perda"] * posicao["valor_aplicado"]
    if resultado_da_operacao(posicao) <= limite_de_perda:
        return "stop"
    if s_hoje is None:
        return None
    if posicao["lado"] == "compra" and s_hoje > parametros["s_para_fechar_compra"]:
        return "sinal"
    if posicao["lado"] == "venda" and s_hoje < parametros["s_para_fechar_venda"]:
        return "sinal"
    return None


def registrar_operacao(posicao, data_saida, pregao_saida, s_saida, motivo):
    """
    Recebe: uma posição que terminou, a data e o número do pregão de saída, o s-score na
            saída (None se não havia s válido) e o motivo.
    Faz:    monta a linha da tabela de operações. Resultado = ganho - custos - aluguel;
            "resultado_pct" = resultado ÷ valor aplicado, guardado como fração (0,05 = 5%; na
            planilha aparece multiplicado por 100).
    Devolve: dicionário com a linha.
    """
    resultado = resultado_da_operacao(posicao)
    return {"ativo": posicao["ativo"], "lado": posicao["lado"],
            "data_entrada": posicao["data_entrada"], "data_saida": data_saida,
            "pregoes_na_operacao": pregao_saida - posicao["pregao_entrada"],
            "s_entrada": posicao["s_entrada"], "s_saida": s_saida,
            "valor_aplicado": posicao["valor_aplicado"], "valor_final": posicao["valor_atual"],
            "custos": posicao["custos"], "aluguel": posicao["aluguel"],
            "resultado_reais": resultado, "resultado_pct": resultado / posicao["valor_aplicado"],
            "motivo_saida": motivo}


def fechar_posicao(carteira, ativo, data, hoje, s_hoje, motivo, parametros, operacoes):
    """
    Recebe: a carteira, o ativo a fechar, a data e o número do pregão, o s-score de hoje (ou
            None), o motivo, os parâmetros e a lista de operações.
    Faz:    zera a posição no preço de fechamento (que, para ação sem negócio hoje, é o último
            preço negociado), paga o custo de 0,10% e registra a operação. Compra: recebemos o
            valor da venda das ações. Venda a descoberto: pagamos o valor para recomprar.
            Se o motivo for stop, bloqueia a ação hoje e nos 10 pregões seguintes.
    Devolve: o custo pago (R$).
    """
    posicao = carteira["posicoes"].pop(ativo)   # tira a posição da carteira
    custo = parametros["custo_por_ponta"] * posicao["valor_atual"]
    # Compra (direcao +1): o valor ENTRA no caixa. Venda (direcao -1): o valor SAI do caixa.
    carteira["caixa"] += direcao(posicao) * posicao["valor_atual"] - custo
    posicao["custos"] += custo
    operacoes.append(registrar_operacao(posicao, data, hoje, s_hoje, motivo))
    if motivo == "stop":
        carteira["bloqueada_ate"][ativo] = hoje + parametros["pregoes_de_quarentena"]
    return custo


def abrir_posicao(carteira, ativo, lado, valor, data, hoje, s_hoje, parametros):
    """
    Recebe: a carteira, o ativo, o lado ("compra" ou "venda"), o valor em R$, a data, o número
            do pregão e o s-score.
    Faz:    abre a posição no fechamento de hoje e paga 0,10% de custo. Compra: sai dinheiro do
            caixa. Venda a descoberto: pegamos as ações emprestadas e as vendemos; o dinheiro
            da venda ENTRA no caixa (e rende CDI), mas passamos a dever as ações (por isso
            pagamos aluguel, e no patrimônio elas entram com sinal negativo).
            Ex.: venda de R$ 10.000 -> caixa sobe 10.000 - 10 de custo = R$ 9.990.
    Devolve: o custo pago (R$).
    """
    custo = parametros["custo_por_ponta"] * valor
    posicao = {"ativo": ativo, "lado": lado, "data_entrada": data, "pregao_entrada": hoje,
               "s_entrada": s_hoje, "valor_aplicado": valor, "valor_atual": valor,
               "custos": custo, "aluguel": 0.0}
    # Compra (direcao +1): o valor SAI do caixa. Venda (direcao -1): o valor ENTRA no caixa.
    carteira["caixa"] += -direcao(posicao) * valor - custo
    carteira["posicoes"][ativo] = posicao
    return custo


def atualizar_posicoes_e_caixa(carteira, hoje, retornos, coluna_do_ticker, fator_cdi,
                               parametros):
    """
    Recebe: a carteira, o número do pregão, os retornos, o mapa de colunas e o fator do CDI.
    Faz:    passo (1) do dia, do fechamento de ontem ao de hoje:
            a) o caixa de ontem rende CDI (ex.: R$ 1.000.000 com fator 1,000507 -> R$ 507);
            b) as vendas a descoberto pagam aluguel de 2% ao ano / 252 sobre o valor de ontem
               (ex.: R$ 20.000 -> R$ 1,59 no dia);
            c) cada posição muda de valor com o retorno de hoje (sem preço hoje: fica parada).
               Ex.: venda de R$ 10.000 e a ação sobe 1% -> passa a valer 10.100: perdemos 100.
    Devolve: (juros do caixa, aluguel pago, ganho das posições), em R$.
    """
    juros = carteira["caixa"] * (fator_cdi - 1)
    carteira["caixa"] += juros
    aluguel_diario = parametros["aluguel_ao_ano"] / parametros["pregoes_por_ano"]
    aluguel_total, ganho_total = 0.0, 0.0
    for posicao in carteira["posicoes"].values():
        if posicao["lado"] == "venda":
            aluguel = posicao["valor_atual"] * aluguel_diario
            posicao["aluguel"] += aluguel
            aluguel_total += aluguel
        retorno = retornos[hoje, coluna_do_ticker[posicao["ativo"]]]
        if not np.isnan(retorno):
            valor_novo = posicao["valor_atual"] * (1 + retorno)
            ganho_total += direcao(posicao) * (valor_novo - posicao["valor_atual"])
            posicao["valor_atual"] = valor_novo
    carteira["caixa"] -= aluguel_total
    return juros, aluguel_total, ganho_total


def fazer_fechamentos(carteira, data, hoje, universo, s_scores, com_preco_hoje, parametros,
                      operacoes):
    """
    Recebe: a carteira, a data e o número do pregão, o universo e os s-scores de hoje, o
            conjunto de tickers com preço hoje, os parâmetros e a lista de operações.
    Faz:    passo (2) do dia: para cada posição aberta (em ordem alfabética, só para o registro
            ficar estável), vê se há motivo para fechar e, se houver, fecha.
    Devolve: (custos pagos nos fechamentos, quantidade de fechamentos).
    """
    custos, quantidade = 0.0, 0
    for ativo in sorted(carteira["posicoes"]):
        s_hoje = s_scores.get(ativo)  # None se a ação não tem s-score válido hoje
        motivo = motivo_para_fechar(carteira["posicoes"][ativo], ativo in com_preco_hoje,
                                    ativo in universo, s_hoje, parametros)
        if motivo is not None:
            custos += fechar_posicao(carteira, ativo, data, hoje, s_hoje, motivo, parametros,
                                     operacoes)
            quantidade += 1
    return custos, quantidade


def fazer_aberturas(carteira, data, hoje, universo, s_scores, parametros):
    """
    Recebe: a carteira, a data e o número do pregão, o universo e os s-scores de hoje e os
            parâmetros.
    Faz:    passo (3) do dia: abre posição nas ações do universo, sem posição, fora da
            quarentena, com s-score válido (o que já exige preço hoje):
              s < -1,25 -> compra (ação barata em relação à cópia);
              s > +1,25 -> venda a descoberto (ação cara).
            Valor de cada operação = patrimônio ÷ N (N = tamanho do universo de hoje), fixado
            agora e nunca rebalanceado. Ex.: patrimônio de R$ 2.000.000 e N = 100 -> R$ 20.000.
            Uma ação fechada por sinal hoje pode abrir do lado oposto no mesmo dia, se o
            s-score passar do limite (fechamentos vêm antes das aberturas).
    Devolve: (custos pagos nas aberturas, quantidade de aberturas).
    """
    if not universo:
        return 0.0, 0
    valor_por_operacao = calcular_patrimonio(carteira) / len(universo)
    custos, quantidade = 0.0, 0
    for ativo, s in s_scores.items():
        # .get(ativo, -1): ação que nunca teve stop devolve -1, e nenhum pregão é <= -1.
        na_quarentena = hoje <= carteira["bloqueada_ate"].get(ativo, -1)
        if ativo in carteira["posicoes"] or na_quarentena:
            continue
        if s < -parametros["s_para_abrir"]:
            lado = "compra"
        elif s > parametros["s_para_abrir"]:
            lado = "venda"
        else:
            continue
        custos += abrir_posicao(carteira, ativo, lado, valor_por_operacao, data, hoje, s,
                                parametros)
        quantidade += 1
    return custos, quantidade


def registrar_dia(data, carteira, universo, k, s_scores, juros, aluguel, ganho, custos,
                  patrimonio_ontem, fator_cdi, aberturas, fechamentos):
    """
    Recebe: tudo o que aconteceu no dia (passos 1 a 3).
    Faz:    passo (4): monta a linha do registro diário. Exposição bruta = (compras + vendas)
            ÷ patrimônio; exposição líquida = (compras - vendas) ÷ patrimônio.
            Ex.: R$ 600.000 comprados e R$ 500.000 vendidos, patrimônio de R$ 1.000.000 ->
            bruta = 1.100.000 / 1.000.000 = 110%; líquida = 100.000 / 1.000.000 = +10%.
    Devolve: dicionário com a linha do dia.
    """
    patrimonio = calcular_patrimonio(carteira)
    posicoes = carteira["posicoes"].values()
    compras = sum(p["valor_atual"] for p in posicoes if p["lado"] == "compra")  # R$ comprados
    vendas = sum(p["valor_atual"] for p in posicoes if p["lado"] == "venda")    # R$ vendidos
    # Abaixo, sum(p["lado"] == "compra" ...) conta as compras: cada True vale 1.
    return {"data": data, "patrimonio": patrimonio, "caixa": carteira["caixa"],
            "ganho_posicoes": ganho, "juros_caixa": juros, "custos": custos, "aluguel": aluguel,
            "retorno_estrategia": patrimonio / patrimonio_ontem - 1,
            "retorno_cdi": fator_cdi - 1,
            "posicoes_abertas": len(carteira["posicoes"]),
            "compras_abertas": sum(p["lado"] == "compra" for p in posicoes),
            "vendas_abertas": sum(p["lado"] == "venda" for p in posicoes),
            "exposicao_bruta": (compras + vendas) / patrimonio,
            "exposicao_liquida": (compras - vendas) / patrimonio,
            "tamanho_universo_N": len(universo), "fatores_K": k,
            "acoes_com_s_valido": len(s_scores), "aberturas": aberturas,
            "fechamentos": fechamentos}


def regras_em_matrizes(regras_tabelas):
    """
    Recebe: as regras do universo como tabelas do pandas (ver preparar_regras_do_universo).
    Faz:    converte cada tabela numa matriz do numpy (linhas = pregões, colunas = tickers, na
            mesma ordem), que é bem mais rápida de ler dentro do laço diário.
    Devolve: dicionário com as matrizes "regra_1", "preco_ate_ontem" e "volume_mediano".
    """
    return {"regra_1": regras_tabelas["regra_1"].to_numpy(),
            "preco_ate_ontem": regras_tabelas["preco_nao_ajustado_ate_ontem"].to_numpy(),
            "volume_mediano": regras_tabelas["volume_mediano"].to_numpy()}


def primeiro_pregao_possivel(pregoes, parametros):
    """
    Recebe: os pregões e os parâmetros.
    Faz:    acha o primeiro pregão em que a operação pode começar: ele precisa ter 252 pregões
            antes (para as janelas do universo e da PCA) e ser do ano inicial (2010) ou depois.
            np.searchsorted(anos, 2010) dá a posição do primeiro pregão de 2010.
    Devolve: o número desse pregão.
    """
    primeiro_do_ano_inicial = int(np.searchsorted(pregoes.year,
                                                  parametros["primeiro_ano_de_operacao"]))
    return max(parametros["janela_universo"], parametros["janela_pca"], primeiro_do_ano_inicial)


def registrar_posicoes_em_aberto(carteira, pregoes, s_scores_do_ultimo_dia, operacoes):
    """
    Recebe: a carteira no fim do último pregão, os pregões, os s-scores do último dia e a lista
            de operações.
    Faz:    acrescenta à lista as posições ainda abertas no último pregão, com o motivo
            "em aberto no fim", pelo valor de mercado e SEM custo de saída (não foram
            vendidas). Assim o patrimônio final e o resultado das operações fecham a conta.
    Devolve: nada (a lista de operações é alterada).
    """
    for ativo in sorted(carteira["posicoes"]):
        posicao = carteira["posicoes"][ativo]
        operacoes.append(registrar_operacao(posicao, pregoes[-1], len(pregoes) - 1,
                                            s_scores_do_ultimo_dia.get(ativo),
                                            "em aberto no fim"))


def aplicar_estrategia(dados, parametros):
    """
    Recebe: os dados limpos (Parte 2) e os parâmetros.
    Faz:    percorre os pregões em ordem. Em cada pregão t:
              - universo de t (dados até t-1) e s-scores de t (dados até o fechamento de t);
              - (1) atualiza posições com o retorno do dia, cobra aluguel, rende CDI no caixa;
              - (2) fechamentos;  (3) aberturas no fechamento de t;  (4) registro do dia.
            Simplificação usual do método: o sinal é calculado com o preço de fechamento e a
            ordem é executada nesse mesmo preço.
            A operação começa no 1º pregão de 2010 (ou depois) que tiver universo e sinal.
    Devolve: dicionário com "diario" e "operacoes" (tabelas), "universos" (data -> tickers),
             "s_scores" (data -> {ticker: s}), "regras" (tabelas do universo) e
             "patrimonio_inicial_data" (pregão em cujo fechamento o R$ 1 milhão está em caixa).
    """
    inicio_relogio = time.time()
    pregoes = dados["pregoes"]
    # Matrizes do numpy (linhas = pregões, colunas = tickers), mais rápidas no laço diário.
    tickers = np.array(dados["precos_ajustados"].columns)
    empresas = dados["empresas"].reindex(tickers).to_numpy()
    coluna_do_ticker = {ticker: coluna for coluna, ticker in enumerate(tickers)}
    retornos = dados["retornos"].to_numpy()
    tem_preco = dados["precos_ajustados"].notna().to_numpy()
    fator_cdi = dados["fator_cdi"].to_numpy()
    regras_tabelas = preparar_regras_do_universo(dados, parametros)
    regras = regras_em_matrizes(regras_tabelas)

    carteira = {"caixa": float(parametros["patrimonio_inicial"]), "posicoes": {},
                "bloqueada_ate": {}}
    diario, operacoes, universos, s_scores_por_dia = [], [], {}, {}
    comecou, data_inicial = False, None
    print("\nAplicando a estratégia (uma linha por ano):")
    for hoje in range(primeiro_pregao_possivel(pregoes, parametros), len(pregoes)):
        data = pregoes[hoje]
        universo = escolher_universo_do_dia(hoje, regras, tickers, empresas, parametros)
        s_scores, k = calcular_s_scores_do_dia(hoje, universo, retornos, tem_preco,
                                               coluna_do_ticker, parametros)
        # Enquanto não houver universo e sinal, nada acontece (aquecimento). No 1º dia com os
        # dois, a operação começa; o R$ 1 milhão está em caixa desde o fechamento da véspera.
        if not comecou:
            if not universo or not s_scores:
                continue
            comecou, data_inicial = True, pregoes[hoje - 1]
        universos[data], s_scores_por_dia[data] = universo, s_scores
        patrimonio_ontem = calcular_patrimonio(carteira)
        com_preco_hoje = set(tickers[tem_preco[hoje]])

        # (1) Posições, aluguel e CDI, do fechamento de ontem ao de hoje
        juros, aluguel, ganho = atualizar_posicoes_e_caixa(carteira, hoje, retornos,
                                                           coluna_do_ticker, fator_cdi[hoje],
                                                           parametros)
        # (2) Fechamentos   (3) Aberturas, ambos no preço de fechamento de hoje
        custos_fech, fechamentos = fazer_fechamentos(carteira, data, hoje, universo, s_scores,
                                                     com_preco_hoje, parametros, operacoes)
        custos_abert, aberturas = fazer_aberturas(carteira, data, hoje, universo, s_scores,
                                                  parametros)
        # (4) Registro do dia
        diario.append(registrar_dia(data, carteira, universo, k, s_scores, juros, aluguel,
                                    ganho, custos_fech + custos_abert, patrimonio_ontem,
                                    fator_cdi[hoje], aberturas, fechamentos))
        # Progresso na tela: uma linha no último pregão de cada ano.
        ultimo_do_ano = hoje == len(pregoes) - 1 or pregoes[hoje + 1].year != data.year
        if ultimo_do_ano:
            print(f"  {data.year}: patrimônio {reais_br(diario[-1]['patrimonio'])} | "
                  f"posições abertas {diario[-1]['posicoes_abertas']} | "
                  f"ações no universo {len(universo)} | "
                  f"tempo: {time.time() - inicio_relogio:.0f} s")

    if not comecou:
        raise ValueError("\n\nNenhum pregão a partir do ano inicial teve universo e sinal.")
    registrar_posicoes_em_aberto(carteira, pregoes, s_scores_por_dia[pregoes[-1]], operacoes)
    return {"diario": pd.DataFrame(diario).set_index("data"),
            "operacoes": pd.DataFrame(operacoes),
            "universos": universos, "s_scores": s_scores_por_dia, "regras": regras_tabelas,
            "patrimonio_inicial_data": data_inicial}


# ##############################################################################################
#
#                                    PARTE 4 — RESULTADOS
#
# ##############################################################################################
# Roteiro: gerar_resultados() (a última função desta parte, antes da execução) chama:
#   listar_retornos_grandes(), listar_ajustes_grandes() ........ relatórios só informativos
#   conferencias_de_vies() ..................................... conferências na tela
#   resultados_ano_a_ano(), resultados_acumulados() ............ métricas (tela e Excel)
#   conferir_contabilidade() ................................... a conta tem de fechar
#   montar_abas_do_excel(), salvar_excel(), salvar_grafico() ... pasta "resultados"
# Retorno diário da estratégia = variação do patrimônio; o do CDI = o mesmo fator do caixa.
def queda_maxima(patrimonios):
    """
    Recebe: série de patrimônios (começando pelo valor antes do 1º dia do período).
    Faz:    a maior queda desde um pico. Ex.: 100 -> 120 -> 90 -> 130: queda máxima = 90/120 - 1
            = -25%. É o pior tombo que alguém teria sofrido se tivesse entrado no pior momento.
    Devolve: a queda (número negativo ou zero).
    """
    pico_ate_cada_dia = patrimonios.cummax()       # no exemplo: 100, 120, 120, 130
    queda_desde_o_pico = patrimonios / pico_ate_cada_dia - 1   # 0%, 0%, -25%, 0%
    return float(queda_desde_o_pico.min())


def metricas_do_periodo(diario, operacoes, patrimonio_antes, parametros):
    """
    Recebe: o registro diário do período, as operações ENCERRADAS no período e o patrimônio no
            fechamento anterior ao 1º dia do período.
    Faz:    retorno composto, CDI composto, excesso (retorno - CDI), desvio anualizado (desvio
            dos retornos diários x raiz de 252), Sharpe = (retorno - CDI) / desvio anualizado,
            queda máxima, operações, acerto (% com resultado > 0), custos, aluguel.
            Por que raiz de 252: a variância cresce na proporção do tempo (um ano tem 252
            vezes a variância de um dia), então o desvio cresce com a raiz. Ex.: desvio diário
            de 0,13% -> 0,13% x raiz(252) = 0,13% x 15,87 = 2,1% ao ano.
    Devolve: dicionário com as métricas.
    """
    retorno = diario["patrimonio"].iloc[-1] / patrimonio_antes - 1
    # CDI composto: multiplica os fatores diários (1 + taxa do dia) e tira 1.
    cdi = float((1 + diario["retorno_cdi"]).prod() - 1)
    raiz_252 = math.sqrt(parametros["pregoes_por_ano"])
    desvio = float(diario["retorno_estrategia"].std(ddof=1)) * raiz_252
    sharpe = (retorno - cdi) / desvio if desvio > 0 else float("nan")
    # Para a queda máxima, a série começa no patrimônio da véspera do período, para que uma
    # queda logo no 1º dia também conte.
    patrimonio_de_partida = pd.Series([patrimonio_antes])
    patrimonios_do_periodo = diario["patrimonio"].reset_index(drop=True)
    serie = pd.concat([patrimonio_de_partida, patrimonios_do_periodo])
    if len(operacoes):
        taxa_de_acerto = float((operacoes["resultado_reais"] > 0).mean())  # fração com lucro
    else:
        taxa_de_acerto = float("nan")
    return {"retorno": retorno, "cdi": cdi, "excesso": retorno - cdi, "desvio_anualizado": desvio,
            "sharpe": sharpe, "queda_maxima": queda_maxima(serie),
            "operacoes_encerradas": len(operacoes), "taxa_de_acerto": taxa_de_acerto,
            "custos": float(diario["custos"].sum()), "aluguel": float(diario["aluguel"].sum()),
            "patrimonio_fim": float(diario["patrimonio"].iloc[-1])}


def resultados_ano_a_ano(diario, operacoes, parametros):
    """
    Recebe: registro diário e operações.
    Faz:    calcula as métricas de cada ano (o patrimônio de partida de um ano é o do último
            pregão do ano anterior; no 1º ano, o patrimônio inicial).
    Devolve: tabela com uma linha por ano.
    """
    encerradas = operacoes[operacoes["motivo_saida"] != "em aberto no fim"]
    linhas, patrimonio_antes = [], parametros["patrimonio_inicial"]
    for ano, diario_ano in diario.groupby(diario.index.year):   # um pedaço do diário por ano
        operacoes_do_ano = encerradas[encerradas["data_saida"].dt.year == ano]
        linha = metricas_do_periodo(diario_ano, operacoes_do_ano, patrimonio_antes, parametros)
        linha["ano"] = ano
        linhas.append(linha)
        patrimonio_antes = diario_ano["patrimonio"].iloc[-1]
    return pd.DataFrame(linhas).set_index("ano")


def resultados_acumulados(diario, operacoes, parametros):
    """
    Recebe: registro diário e operações.
    Faz:    métricas do período inteiro e, além delas, retorno e CDI anualizados
            ((1 + total)^(252 / nº de pregões) - 1), Sharpe com os anualizados e a contagem de
            saídas por motivo.
            Anualizar = achar a taxa por ano que, composta, daria o total. Ex.: 21% em 504
            pregões (2 anos) -> 1,21^(252/504) - 1 = 1,21^0,5 - 1 = 10% ao ano.
    Devolve: dicionário com as métricas.
    """
    encerradas = operacoes[operacoes["motivo_saida"] != "em aberto no fim"]
    metricas = metricas_do_periodo(diario, encerradas, parametros["patrimonio_inicial"],
                                   parametros)
    anos = len(diario) / parametros["pregoes_por_ano"]   # elevar a 1/anos = elevar a 252/n
    metricas["pregoes"] = len(diario)
    metricas["retorno_anualizado"] = (1 + metricas["retorno"]) ** (1 / anos) - 1
    metricas["cdi_anualizado"] = (1 + metricas["cdi"]) ** (1 / anos) - 1
    metricas["sharpe"] = ((metricas["retorno_anualizado"] - metricas["cdi_anualizado"])
                          / metricas["desvio_anualizado"])
    metricas["saidas_por_motivo"] = operacoes["motivo_saida"].value_counts().to_dict()
    return metricas


def conferir_contabilidade(diario, operacoes, parametros):
    """
    Recebe: registro diário e operações (inclusive as em aberto no fim).
    Faz:    confere a conta de duas formas independentes:
            A) inicial + soma das parcelas diárias (juros + ganho das posições - custos - aluguel)
            B) inicial + juros do caixa + resultado de todas as operações (cada resultado já
               desconta os custos e o aluguel daquela operação)
            Os dois têm de dar o patrimônio final calculado pela carteira (caixa + posições).
            Se não derem, algum real "sumiu" ou "apareceu" no meio do caminho: erro no código.
            math.fsum é uma soma mais precisa que a comum: evita que milhares de pequenos
            arredondamentos do computador se acumulem.
    Devolve: dicionário com os três valores e as duas diferenças.
    """
    inicial = parametros["patrimonio_inicial"]
    final = float(diario["patrimonio"].iloc[-1])
    juros_total = math.fsum(diario["juros_caixa"])
    ganho_total = math.fsum(diario["ganho_posicoes"])
    custos_total = math.fsum(diario["custos"])
    aluguel_total = math.fsum(diario["aluguel"])
    resultado_operacoes = math.fsum(operacoes["resultado_reais"])
    pelas_parcelas = inicial + (juros_total + ganho_total - custos_total - aluguel_total)  # A
    pelas_operacoes = inicial + juros_total + resultado_operacoes                         # B
    return {"final": final, "pelas_parcelas": pelas_parcelas, "pelas_operacoes": pelas_operacoes,
            "diferenca_parcelas": final - pelas_parcelas,
            "diferenca_operacoes": final - pelas_operacoes,
            "juros_total": juros_total, "resultado_operacoes": resultado_operacoes}


def havia_posicao_no_dia(operacoes_do_ativo, data):
    """
    Recebe: as operações de um ativo e uma data.
    Faz:    vê se havia posição vinda da véspera nesse dia: alguma operação abriu ANTES desse
            dia e fechou nesse dia ou depois (o retorno do dia entrou no resultado).
    Devolve: True ou False.
    """
    abriu_antes = operacoes_do_ativo["data_entrada"] < data
    fechou_no_dia_ou_depois = operacoes_do_ativo["data_saida"] >= data
    return bool((abriu_antes & fechou_no_dia_ou_depois).any())


def listar_retornos_grandes(dados, universos, operacoes, parametros):
    """
    Recebe: dados limpos, universos de cada dia, operações e parâmetros.
    Faz:    lista os retornos diários com |r| > 40% das ações que estiveram no universo em
            algum momento, para o grupo conferir se são eventos mal ajustados na base (como era
            a cisão do PCAR3). NÃO corrige nada por conta própria. Feito depois da estratégia:
            é só relatório, não entra em decisão nenhuma.
            Mostra também se havia posição aberta vinda da véspera: nesse caso o retorno do dia
            entrou no resultado (ele é aplicado antes dos fechamentos do dia).
    Devolve: tabela com data, ativo, retorno, se estava no universo e se havia posição.
    """
    ja_estiveram = set()
    for universo in universos.values():
        ja_estiveram.update(universo)
    limite = parametros["limite_retorno_grande"]
    linhas = []
    for ativo in sorted(ja_estiveram):
        serie = dados["retornos"][ativo]
        operacoes_do_ativo = operacoes[operacoes["ativo"] == ativo]
        for data, retorno in serie[serie.abs() > limite].items():
            linhas.append({"data": data, "ativo": ativo, "retorno": retorno,
                           "no_universo_nesse_dia": ativo in universos.get(data, ()),
                           "com_posicao_nesse_dia": havia_posicao_no_dia(operacoes_do_ativo,
                                                                         data)})
    colunas = ["data", "ativo", "retorno", "no_universo_nesse_dia", "com_posicao_nesse_dia"]
    return pd.DataFrame(linhas, columns=colunas).sort_values(["data", "ativo"], ignore_index=True)


def mostrar_retornos_grandes(tabela, quantos=5):
    """
    Recebe: a tabela de listar_retornos_grandes e quantos casos mostrar de cada lado
            (padrão 5).
    Faz:    imprime só os 5 maiores retornos diários (as maiores altas) e os 5 menores (as
            maiores quedas), com o dia e a ação. A lista completa fica na aba retornos_grandes
            do Excel. É só informativo: um retorno gigante costuma ser evento da empresa ou erro
            de ajuste da base, e o grupo pode conferir.
    Devolve: nada.
    """
    ordenada = tabela.sort_values("retorno")          # do mais negativo para o mais positivo
    maiores = ordenada.tail(quantos).iloc[::-1]       # as maiores altas, da maior para a menor
    menores = ordenada.head(quantos)                  # as maiores quedas, da pior para a menor
    for nome, parte in [("Maiores altas", maiores), ("Maiores quedas", menores)]:
        print(f"  {nome}:")
        for _, linha in parte.iterrows():
            print(f"    {data_br(linha['data'])}  {linha['ativo']:<8}"
                  f"{porcentagem_br(linha['retorno'], 1):>10}")
    print(f"  (lista completa, com {len(tabela)} casos, na aba retornos_grandes do Excel)")


def listar_ajustes_grandes(dados, universos, operacoes, parametros):
    """
    Recebe: dados limpos, universos de cada dia, operações e parâmetros.
    Faz:    SÓ INFORMATIVO (não decide nada; é feito depois da estratégia). Procura os dias em
            que o Economatica fez um ajuste grande no preço de uma ação que esteve no universo
            em algum momento, para o grupo achar eventos mal ajustados como as cisões dos
            PARÂMETROS (a lista de |r| > 40% não acha a maioria deles).
            Como: num dia normal, o preço ajustado e o não ajustado variam igual, e a razão
            ajustado ÷ não ajustado fica parada. Num dia de evento (dividendo, desdobramento,
            cisão...), o não ajustado "pula" e o ajustado não; a razão muda. Listamos os dias em
            que ela mudou mais de 5% de um pregão para o seguinte.
            Ex. de desdobramento de 2 por 1: na véspera, não ajustado R$ 20 e ajustado R$ 10
            (o ajustado antigo já foi dividido por 2); no dia, os dois valem R$ 10. A razão vai
            de 10 / 20 = 0,5 para 10 / 10 = 1: mudança de +100%, e o retorno ajustado do dia
            sai 0%, como deve ser.
            Ex. real (PCAR3 em 01/03/2021): ajustado -65,8%, não ajustado 23,33 / 83,00 - 1 =
            -71,9%; a razão muda (1 - 0,6584) / (1 - 0,7189) - 1 = 0,3416 / 0,2811 - 1 = +21,5%.
            Como ler a mudança: +100% costuma ser desdobramento de 2 por 1; +10% ou +20%,
            bonificação; -90%, grupamento de 10 em 1; alguns %, dividendo grande. Esses o
            Economatica costuma ajustar bem. Um valor "quebrado" num dia em que estreou um
            ticker novo é pista de cisão (como ASAI3 no dia do PCAR3).
            Como o grupo deve usar a lista:
              1) começar pelas linhas com ticker novo estreando no dia, sobretudo as marcadas
                 "no universo" ou "COM POSIÇÃO" (essas podem mudar o resultado);
              2) descobrir se, nesse dia, os acionistas receberam ações da empresa que estreou;
              3) se receberam, calcular o retorno do acionista (ver retorno_do_acionista_na_cisao)
                 com os preços não ajustados e comparar com a coluna do retorno ajustado da
                 base; se for bem diferente, acrescentar a cisão em PARAMETROS["cisoes"].
    Devolve: tabela com data, ativo, mudança da razão, retornos da base (ajustado e não
             ajustado), tickers que estrearam no dia, se a ação estava no universo, se havia
             posição e se a cisão já é corrigida pelo código.
    """
    ja_estiveram = set()
    for universo in universos.values():
        ja_estiveram.update(universo)
    ajustados, nao_ajustados = dados["precos_ajustados"], dados["precos_nao_ajustados"]
    razao = ajustados / nao_ajustados
    mudanca = razao / razao.shift(1) - 1          # de um pregão para o seguinte
    retorno_ajustado = ajustados / ajustados.shift(1) - 1          # o da base, SEM correção
    retorno_nao_ajustado = nao_ajustados / nao_ajustados.shift(1) - 1
    # Pares (data, ação) das cisões que o código já corrige, para marcar na lista.
    corrigidas = {(pd.Timestamp(cisao["data"]), cisao["acao"]) for cisao in parametros["cisoes"]}
    limite = parametros["limite_ajuste_grande"]
    linhas = []
    for ativo in sorted(ja_estiveram):
        serie = mudanca[ativo]
        operacoes_do_ativo = operacoes[operacoes["ativo"] == ativo]
        for data, valor in serie[serie.abs() > limite].items():
            # Tickers que tiveram o 1º negócio nesse dia (pista de cisão), menos o próprio ativo.
            estrearam = [outro for outro in dados["estreias"].get(data, []) if outro != ativo]
            linhas.append({"data": data, "ativo": ativo, "mudanca_da_razao": valor,
                           "retorno_ajustado_base": retorno_ajustado.at[data, ativo],
                           "retorno_nao_ajustado": retorno_nao_ajustado.at[data, ativo],
                           "estrearam_no_dia": ", ".join(estrearam),
                           "no_universo_nesse_dia": ativo in universos.get(data, ()),
                           "com_posicao_nesse_dia": havia_posicao_no_dia(operacoes_do_ativo,
                                                                         data),
                           "cisao_ja_corrigida": (data, ativo) in corrigidas})
    colunas = ["data", "ativo", "mudanca_da_razao", "retorno_ajustado_base",
               "retorno_nao_ajustado", "estrearam_no_dia", "no_universo_nesse_dia",
               "com_posicao_nesse_dia", "cisao_ja_corrigida"]
    return pd.DataFrame(linhas, columns=colunas).sort_values(["data", "ativo"], ignore_index=True)


def conferencias_de_vies(dados, resultado, parametros):
    """
    Recebe: dados limpos, resultado da Parte 3 e parâmetros.
    Faz:    confere, com os números do próprio teste, os casos de viés já conhecidos (itens (2)
            a (4) do texto do topo):
            - GOL e Azul (GOLL54, AZUL54) entram no universo; DUFB11, PPLA11 e TARP11 nunca
              entram;
            - os saltos do GOLL54 em 12 e 13/06/2025 (+1.847% e +250%, que vêm de uma troca de
              fator de cotação na base, não de ganho de verdade) acontecem fora do universo e
              sem posição aberta, ou seja, não entram no resultado;
            - a PETR4 não é barrada pelo filtro de R$ 1 em 2016 (o filtro usa o não ajustado);
            - o retorno usado no dia de cada cisão é o corrigido (ex.: +14,1% no PCAR3);
            - a mesma empresa não aparece duas vezes no universo (ABEV3 nunca junto com AMBV4;
              TIMS3 nunca junto com TCSL4; AESB3 nunca junto com TIET3/TIET4; BHIA3 nunca
              junto com VVAR11/VVAR4).
    Devolve: lista de linhas (etapa, quantidade, explicação) no formato do relatório.
    """
    universos, operacoes = resultado["universos"], resultado["operacoes"]
    linhas = []
    for ativo in list(parametros["excecoes_aceitas"]) + list(parametros["excecoes_excluidas"]):
        dias = [data_do_dia for data_do_dia, universo_do_dia in universos.items()
                if ativo in universo_do_dia]
        texto = (f"de {data_br(dias[0])} a {data_br(dias[-1])}" if dias else "nunca entrou")
        anotar(linhas, f"{ativo} no universo (pregões)", len(dias), texto)
    for ativo, empresa in parametros["mesma_empresa"].items():
        # Outros tickers da mesma empresa (ex.: para ABEV3, empresa AMBV: a AMBV4).
        mesma = [outro for outro, codigo in dados["empresas"].items()
                 if codigo == empresa and outro != ativo]
        # Conta os pregões em que o ativo E algum outro da mesma empresa estão no universo.
        juntos = 0
        for universo_do_dia in universos.values():
            if ativo in universo_do_dia and any(outro in universo_do_dia for outro in mesma):
                juntos += 1
        anotar(linhas, f"{ativo} junto com {', '.join(mesma) or '-'} no universo (pregões)",
               juntos, "mesma empresa: tem de ser 0")
    for data_texto in ["2025-06-12", "2025-06-13"]:
        data = pd.Timestamp(data_texto)
        if data in universos and "GOLL54" in dados["retornos"].columns:
            retorno = dados["retornos"].at[data, "GOLL54"]
            com_posicao = havia_posicao_no_dia(operacoes[operacoes["ativo"] == "GOLL54"], data)
            anotar(linhas, f"GOLL54 em {data_br(data)}", porcentagem_br(retorno, 0),
                   "troca de fator de cotação, não é retorno. No universo: "
                   f"{'SIM' if 'GOLL54' in universos[data] else 'não'}; posição aberta: "
                   f"{'SIM' if com_posicao else 'não'}")
    if "PETR4" in dados["precos_nao_ajustados"].columns:
        preco = resultado["regras"]["preco_nao_ajustado_ate_ontem"]["PETR4"]
        preco_2016 = preco[preco.index.year == 2016]
        barrada = int((preco_2016 < parametros["preco_minimo"]).sum())
        dias_no_universo = sum("PETR4" in universo_do_dia
                               for data_do_dia, universo_do_dia in universos.items()
                               if data_do_dia.year == 2016)
        anotar(linhas, "PETR4 em 2016: dias barrada pelo filtro de R$ 1", barrada,
               f"menor preço não ajustado usado no filtro: {reais_br(preco_2016.min())}; "
               f"no universo em {dias_no_universo} pregões de 2016")
    for cisao in parametros["cisoes"]:
        data = pd.Timestamp(cisao["data"])
        if data in dados["retornos"].index:
            anotar(linhas, f"Retorno usado do {cisao['acao']} em {data_br(data)}",
                   porcentagem_br(dados["retornos"].at[data, cisao["acao"]], 1),
                   "depois da correção da cisão")
    return linhas


def procurar_no_relatorio(relatorio, comeco):
    """Recebe o relatório e o começo do nome de uma etapa; devolve a quantidade dela (ou None)."""
    for linha in relatorio:
        if linha["etapa"].startswith(comeco):
            return linha["quantidade"]
    return None


def mostrar_resumo_da_limpeza(relatorio):
    """
    Recebe: o relatório de limpeza completo (lista de etapa / quantidade / explicação).
    Faz:    imprime só os 5 números mais importantes da limpeza. O relatório completo (cada
            regra, cada exceção, cada cisão) continua indo para a aba "limpeza" do Excel.
    Devolve: nada.
    """
    titulo("RESUMO DA LIMPEZA")
    cisoes = sum(1 for linha in relatorio if linha["etapa"].startswith("Cisão "))
    itens = [("Pregões (dias com negócio; feriados retirados)",
              procurar_no_relatorio(relatorio, "Pregões")),
             ("Tickers que nunca negociaram (descartados)",
              procurar_no_relatorio(relatorio, "Tickers que nunca negociaram")),
             ("Tickers que ficam para a estratégia (só ações; sem BDRs)",
              procurar_no_relatorio(relatorio, "Tickers que ficam para a estratégia")),
             ("... dos quais pararam de negociar antes do fim (FICAM: sem viés de sobrevivência)",
              procurar_no_relatorio(relatorio, "Tickers que param antes")),
             ("Cisões mal ajustadas na base, corrigidas", cisoes)]
    for nome, quantidade in itens:
        if isinstance(quantidade, (int, np.integer)):
            quantidade = numero_br(quantidade, 0)
        print(f"  {nome:<84}{str(quantidade):>10}")
    print("  (relatório completo na aba limpeza do Excel)")


def mostrar_ano_a_ano(tabela):
    """Recebe a tabela ano a ano; imprime uma linha por ano."""
    titulo("RESULTADOS ANO A ANO")
    cabecalho = (f"{'Ano':<5}{'Retorno':>9}{'CDI':>9}{'Excesso':>9}{'Desvio':>9}{'Sharpe':>8}"
                 f"{'Queda máx':>11}{'Operações':>10}{'Acerto':>8}{'Custos':>15}{'Aluguel':>14}"
                 f"{'Patrimônio':>19}")
    print(cabecalho)
    print("-" * len(cabecalho))
    for ano, linha in tabela.iterrows():
        print(f"{ano:<5}"
              f"{porcentagem_br(linha['retorno'], 1):>9}"
              f"{porcentagem_br(linha['cdi'], 1):>9}"
              f"{porcentagem_br(linha['excesso'], 1):>9}"
              f"{porcentagem_br(linha['desvio_anualizado'], 1):>9}"
              f"{numero_br(linha['sharpe'], 2):>8}"
              f"{porcentagem_br(linha['queda_maxima'], 1):>11}"
              f"{int(linha['operacoes_encerradas']):>10}"
              f"{porcentagem_br(linha['taxa_de_acerto'], 0):>8}"
              f"{reais_br(linha['custos']):>15}"
              f"{reais_br(linha['aluguel']):>14}"
              f"{reais_br(linha['patrimonio_fim']):>19}")
    print("Excesso = retorno - CDI. Desvio = desvio-padrão dos retornos diários do ano "
          "x raiz(252).")
    print("Sharpe = (retorno - CDI) / desvio: quanto se ganhou acima do CDI por unidade de "
          "oscilação.")
    print("Sharpe negativo = rendeu menos que o CDI. Queda máx = pior tombo desde um pico, "
          "dentro do ano.")
    print("Operações = encerradas no ano; acerto = % delas com resultado positivo.")


def itens_do_acumulado(acumulado, conta):
    """
    Recebe: as métricas acumuladas e a conferência da contabilidade.
    Faz:    organiza tudo numa lista única (nome, valor, unidade), usada tanto na tela quanto na
            aba "acumulado" do Excel, para as duas mostrarem exatamente o mesmo.
    Devolve: lista de tuplas (nome, valor, unidade); unidade é "%", "R$" ou "" (número puro).
    """
    itens = [("Pregões no período", acumulado["pregoes"], ""),
             ("Retorno total", acumulado["retorno"], "%"),
             ("CDI total", acumulado["cdi"], "%"),
             ("Retorno anualizado", acumulado["retorno_anualizado"], "%"),
             ("CDI anualizado", acumulado["cdi_anualizado"], "%"),
             ("Desvio anualizado", acumulado["desvio_anualizado"], "%"),
             ("Sharpe = (ret. anualizado - CDI anualizado) / desvio", acumulado["sharpe"], ""),
             ("Queda máxima", acumulado["queda_maxima"], "%"),
             ("Operações encerradas", acumulado["operacoes_encerradas"], ""),
             ("Taxa de acerto (operações encerradas)", acumulado["taxa_de_acerto"], "%"),
             ("Custos pagos", acumulado["custos"], "R$"),
             ("Aluguel pago", acumulado["aluguel"], "R$"),
             ("Patrimônio final", acumulado["patrimonio_fim"], "R$")]
    itens += [(f"Saídas por motivo: {motivo}", quantidade, "")
              for motivo, quantidade in acumulado["saidas_por_motivo"].items()]
    itens += [("Contabilidade: patrimônio final (caixa + posições)", conta["final"], "R$"),
              ("Contabilidade: inicial + soma das parcelas diárias", conta["pelas_parcelas"], "R$"),
              ("Contabilidade: inicial + juros + resultado das operações",
               conta["pelas_operacoes"], "R$"),
              ("Contabilidade: diferença (parcelas)", conta["diferenca_parcelas"], "R$"),
              ("Contabilidade: diferença (operações)", conta["diferenca_operacoes"], "R$")]
    return itens


def mostrar_acumulado(acumulado, conta, resultado):
    """Recebe as métricas acumuladas; imprime as do período inteiro (sem a contabilidade)."""
    titulo("RESULTADO ACUMULADO")
    diario = resultado["diario"]
    print(f"  Período: {data_br(diario.index[0])} a {data_br(diario.index[-1])}; o patrimônio "
          f"inicial está em caixa no fechamento de "
          f"{data_br(resultado['patrimonio_inicial_data'])}")
    for nome, valor, unidade in itens_do_acumulado(acumulado, conta):
        if nome.startswith("Contabilidade"):
            continue
        if unidade == "%":
            texto = porcentagem_br(valor)
        elif unidade == "R$":
            texto = reais_br(valor)
        else:
            texto = numero_br(valor, 0 if isinstance(valor, (int, np.integer)) else 2)
        print(f"  {nome:<56}{texto:>22}")


def mostrar_contabilidade(conta):
    """Recebe a conferência da contabilidade; imprime as três contas e as diferenças."""
    titulo("CONFERÊNCIA DA CONTABILIDADE")
    linhas = [("Patrimônio final (caixa + posições)", conta["final"]),
              ("Inicial + soma das parcelas diárias", conta["pelas_parcelas"]),
              ("Inicial + juros do caixa + resultado das operações", conta["pelas_operacoes"])]
    for nome, valor in linhas:
        print(f"  {nome:<76}{reais_br(valor):>20}")
    print(f"      (juros do caixa {reais_br(conta['juros_total'])}; resultado das operações "
          f"{reais_br(conta['resultado_operacoes'])})")
    for nome, chave in [("parcelas", "diferenca_parcelas"), ("operações", "diferenca_operacoes")]:
        # "+ 0.0" evita mostrar "-0,00" quando a sobra é um negativo minúsculo
        print(f"  Diferença ({nome}): {reais_br(round(conta[chave], 2) + 0.0)} "
              f"(sobra de arredondamento do computador: {numero_br(conta[chave], 10)} reais)")


def preparar_para_excel(tabela, colunas_em_pct):
    """
    Recebe: uma tabela e a lista de colunas que estão em fração (ex.: 0,05).
    Faz:    multiplica essas colunas por 100 e acrescenta "_pct" ao nome (0,05 -> 5 em
            "retorno_pct"); troca data-e-hora por data simples, para a planilha ficar legível.
    Devolve: a tabela pronta para o Excel.
    """
    tabela = tabela.copy()
    novos_nomes = {}
    for coluna in colunas_em_pct:
        tabela[coluna] = 100 * tabela[coluna]
        novos_nomes[coluna] = coluna if coluna.endswith("_pct") else coluna + "_pct"
    tabela = tabela.rename(columns=novos_nomes)
    for coluna in tabela.columns:
        if pd.api.types.is_datetime64_any_dtype(tabela[coluna]):
            tabela[coluna] = tabela[coluna].dt.date
    return tabela


def salvar_excel(caminho, abas):
    """
    Recebe: o caminho do arquivo e um dicionário nome_da_aba -> tabela.
    Faz:    grava cada tabela numa aba e alarga as colunas para o cabeçalho caber.
    Devolve: nada (o arquivo fica salvo).
    """
    with pd.ExcelWriter(caminho, engine="openpyxl") as escritor:
        for nome, tabela in abas.items():
            tabela.to_excel(escritor, sheet_name=nome, index=False)
            planilha = escritor.sheets[nome]
            for coluna in planilha.columns:   # coluna[0] é a célula do cabeçalho
                largura = max(len(str(coluna[0].value)), 12)
                planilha.column_dimensions[coluna[0].column_letter].width = min(largura + 2, 60)


def salvar_grafico(caminho, resultado, patrimonio_inicial):
    """
    Recebe: o caminho da imagem, o resultado da Parte 3 e o patrimônio inicial.
    Faz:    desenha três linhas, todas começando em 100 no fechamento anterior ao 1º dia:
            1) a estratégia de verdade (com custos de transação);
            2) a estratégia SEM os custos de transação (0,10% por ponta): a cada dia,
               devolvemos o custo pago naquele dia e acumulamos os retornos. É uma aproximação:
               sem pagar custos o patrimônio seria um pouco maior e as posições também, mas a
               diferença disso é pequena. O aluguel das vendas continua descontado (não é custo
               de transação, é o preço de manter a venda a descoberto);
            3) quem deixasse tudo no CDI.
            Ex. de um dia: patrimônio de ontem R$ 1.000.000, retorno de hoje +0,02% e custos de
            hoje R$ 300 -> sem custos, o retorno do dia seria 0,02% + 300 / 1.000.000 = 0,05%.
    Devolve: nada (a imagem fica salva).
    """
    diario = resultado["diario"]
    datas = [resultado["patrimonio_inicial_data"]] + list(diario.index)
    estrategia = [100.0] + list(100 * diario["patrimonio"] / patrimonio_inicial)
    # Patrimônio de ontem (no 1º dia, o inicial): é sobre ele que o custo de hoje vira %.
    patrimonio_ontem = diario["patrimonio"].shift(1).fillna(patrimonio_inicial)
    retorno_sem_custos = diario["retorno_estrategia"] + diario["custos"] / patrimonio_ontem
    # .cumprod() multiplica os fatores (1 + retorno do dia) acumulando: em cada dia, quanto
    # R$ 100 do início teriam virado.
    sem_custos = [100.0] + list(100 * (1 + retorno_sem_custos).cumprod())
    cdi = [100.0] + list(100 * (1 + diario["retorno_cdi"]).cumprod())
    figura, eixo = plt.subplots(figsize=(11, 5.5))
    eixo.plot(datas, estrategia, label=f"Estratégia com custos ({numero_br(estrategia[-1], 0)})",
              linewidth=1.4)
    eixo.plot(datas, sem_custos, label=f"Estratégia sem custos de transação "
              f"({numero_br(sem_custos[-1], 0)})", linewidth=1.2, linestyle="--")
    eixo.plot(datas, cdi, label=f"CDI ({numero_br(cdi[-1], 0)})", linewidth=1.4)
    eixo.set_title("Patrimônio da estratégia x CDI (base 100)")
    eixo.set_ylabel("Base 100")
    eixo.grid(alpha=0.3)
    eixo.legend(loc="upper left")
    figura.tight_layout()
    figura.savefig(caminho, dpi=150)
    plt.close(figura)


def desenhar_operacoes(eixo, precos, operacoes_do_ativo):
    """
    Recebe: um eixo do gráfico, a série de preços da ação e as operações dela.
    Faz:    desenha o preço e, por cima, cada operação:
              - faixa verde clara = período comprado; faixa vermelha clara = vendido;
              - triângulo verde para cima = abrimos uma COMPRA;
              - triângulo vermelho para baixo = abrimos uma VENDA a descoberto;
              - "x" preto = fechamos a posição (sinal, stop ou saída do universo).
    Devolve: nada.
    """
    eixo.plot(precos.index, precos.values, color="gray", linewidth=0.9, label="Preço")
    preco_no_dia = precos.ffill()   # para ação sem negócio no dia, usa o último preço
    for _, operacao in operacoes_do_ativo.iterrows():
        compra = operacao["lado"] == "compra"
        eixo.axvspan(operacao["data_entrada"], operacao["data_saida"], alpha=0.15,
                     color="green" if compra else "red", linewidth=0)
    for lado, marcador, cor, nome in [("compra", "^", "green", "Abrimos compra"),
                                      ("venda", "v", "red", "Abrimos venda")]:
        entradas = operacoes_do_ativo[operacoes_do_ativo["lado"] == lado]["data_entrada"]
        entradas = entradas[entradas.isin(preco_no_dia.index)]
        eixo.scatter(entradas, preco_no_dia.loc[entradas], marker=marcador, color=cor, s=28,
                     zorder=3, label=nome)
    fechadas = operacoes_do_ativo[operacoes_do_ativo["motivo_saida"] != "em aberto no fim"]
    saidas = fechadas["data_saida"][fechadas["data_saida"].isin(preco_no_dia.index)]
    eixo.scatter(saidas, preco_no_dia.loc[saidas], marker="x", color="black", s=22, zorder=3,
                 label="Fechamos")
    eixo.grid(alpha=0.3)


def resumir_acao_mais_operada(dados, resultado):
    """
    Recebe: os dados limpos e o resultado da Parte 3.
    Faz:    escolhe a ação com mais operações e resume:
              - a volatilidade da AÇÃO no período da estratégia: desvio-padrão dos retornos
                diários x raiz(252) (quanto ela oscila num ano típico);
              - o retorno SÓ das operações nela (as encerradas; as que ficaram em aberto no fim
                não entram):
                  * resultado total em R$ (soma dos resultados, já com custos e aluguel);
                  * resultado médio por operação, em % do valor aplicado;
                  * retorno acumulado, como se o mesmo dinheiro fosse passando de uma operação
                    para a seguinte (as operações numa mesma ação nunca se sobrepõem). Ex.: +2%
                    e depois -1% -> 1,02 x 0,99 - 1 = +0,98%;
                  * volatilidade das operações: desvio-padrão dos resultados % por operação;
                  * taxa de acerto (% de operações com resultado positivo).
    Devolve: dicionário com o nome da ação, as operações dela e os números acima.
    """
    operacoes = resultado["operacoes"]
    contagem = operacoes["ativo"].value_counts()   # nº de operações por ação, do maior ao menor
    ativo = contagem.index[0]
    operacoes_do_ativo = operacoes[operacoes["ativo"] == ativo]
    encerradas = operacoes_do_ativo[operacoes_do_ativo["motivo_saida"] != "em aberto no fim"]
    diario = resultado["diario"]
    retornos_da_acao = dados["retornos"][ativo].loc[diario.index[0]:diario.index[-1]]
    return {"ativo": ativo, "operacoes": operacoes_do_ativo,
            "quantidade": len(operacoes_do_ativo), "encerradas": len(encerradas),
            "volatilidade_acao": retornos_da_acao.std() * np.sqrt(252),
            "resultado_total": encerradas["resultado_reais"].sum(),
            "resultado_medio": encerradas["resultado_pct"].mean(),
            "retorno_acumulado": (1 + encerradas["resultado_pct"]).prod() - 1,
            "volatilidade_operacoes": encerradas["resultado_pct"].std(),
            "acerto": (encerradas["resultado_reais"] > 0).mean()}


def texto_do_resumo(resumo):
    """Recebe o resumo da ação mais operada; devolve as linhas de texto (tela e gráfico)."""
    return [f"Volatilidade da ação (anual): {porcentagem_br(resumo['volatilidade_acao'], 1)}",
            f"Operações encerradas: {resumo['encerradas']}  |  acerto: "
            f"{porcentagem_br(resumo['acerto'], 0)}",
            f"Resultado total das operações: {reais_br(resumo['resultado_total'])}",
            f"Resultado médio por operação: {porcentagem_br(resumo['resultado_medio'], 2)}",
            f"Retorno acumulado das operações: {porcentagem_br(resumo['retorno_acumulado'], 1)}",
            f"Volatilidade das operações (desvio por operação): "
            f"{porcentagem_br(resumo['volatilidade_operacoes'], 1)}"]


def mostrar_acao_mais_operada(resumo):
    """Recebe o resumo da ação mais operada; imprime os números na tela."""
    titulo(f"AÇÃO MAIS OPERADA: {resumo['ativo']} ({resumo['quantidade']} operações)")
    for linha in texto_do_resumo(resumo):
        print(f"  {linha}")


def salvar_grafico_acao_mais_operada(caminho, dados, resultado, resumo):
    """
    Recebe: o caminho da imagem, os dados limpos, o resultado da Parte 3 e o resumo da ação
            mais operada (de resumir_acao_mais_operada).
    Faz:    desenha o preço da ação mais operada com as entradas e saídas
            (ver desenhar_operacoes). São dois quadros: o período todo, para ver a frequência,
            e o último ano, ampliado, para ver cada operação com clareza.
            O preço é o AJUSTADO por proventos (o mesmo usado nos retornos da estratégia), para
            que dividendos e desdobramentos não apareçam como quedas falsas no gráfico.
            No canto do 1º quadro vai uma caixa com a volatilidade da ação e o retorno só das
            operações nela (ver resumir_acao_mais_operada).
    Devolve: nada (a imagem fica salva).
    """
    ativo, operacoes_do_ativo = resumo["ativo"], resumo["operacoes"]
    diario = resultado["diario"]
    precos = dados["precos_ajustados"][ativo].loc[diario.index[0]:diario.index[-1]]
    ultimo_ano = diario.index[-1].year
    figura, (eixo_todo, eixo_ano) = plt.subplots(2, 1, figsize=(12, 8))
    desenhar_operacoes(eixo_todo, precos, operacoes_do_ativo)
    eixo_todo.set_title(f"{ativo}: a ação que mais operamos ({resumo['quantidade']} operações; "
                        "preço ajustado por proventos)")
    eixo_todo.set_ylabel("Preço (R$)")
    eixo_todo.legend(loc="upper left", fontsize=8)
    # Caixa de texto no canto inferior direito com os números do resumo.
    eixo_todo.text(0.99, 0.03, "\n".join(texto_do_resumo(resumo)), transform=eixo_todo.transAxes,
                   ha="right", va="bottom", fontsize=8,
                   bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.9})
    # Ampliação do último ano: só as operações que tocam esse ano.
    no_ano = operacoes_do_ativo[operacoes_do_ativo["data_saida"].dt.year >= ultimo_ano]
    desenhar_operacoes(eixo_ano, precos[precos.index.year == ultimo_ano], no_ano)
    eixo_ano.set_xlim(precos[precos.index.year == ultimo_ano].index[[0, -1]])
    eixo_ano.set_title(f"{ativo} em {ultimo_ano} (ampliado)")
    eixo_ano.set_ylabel("Preço (R$)")
    figura.tight_layout()
    figura.savefig(caminho, dpi=150)
    plt.close(figura)


def montar_abas_do_excel(ano_a_ano, acumulado, conta, resultado, relatorio, retornos_grandes,
                         ajustes_grandes):
    """
    Recebe: as tabelas de resultado, o relatório (limpeza + conferências), os retornos grandes
            e os ajustes grandes.
    Faz:    deixa cada tabela no formato da planilha (frações viram %, datas viram data simples).
    Devolve: dicionário nome_da_aba -> tabela.
    """
    metricas_em_pct = ["retorno", "cdi", "excesso", "desvio_anualizado", "queda_maxima",
                       "taxa_de_acerto"]
    linhas_do_acumulado = []
    for nome, valor, unidade in itens_do_acumulado(acumulado, conta):
        valor_na_planilha = 100 * valor if unidade == "%" else valor   # fração vira %
        linhas_do_acumulado.append({"metrica": nome, "valor": valor_na_planilha,
                                    "unidade": unidade})
    acumulado_tabela = pd.DataFrame(linhas_do_acumulado)
    colunas_do_diario_em_pct = ["retorno_estrategia", "retorno_cdi", "exposicao_bruta",
                                "exposicao_liquida"]
    return {"ano_a_ano": preparar_para_excel(ano_a_ano.reset_index(), metricas_em_pct),
            "acumulado": acumulado_tabela,
            "operacoes": preparar_para_excel(resultado["operacoes"], ["resultado_pct"]),
            "diario": preparar_para_excel(resultado["diario"].reset_index(),
                                          colunas_do_diario_em_pct),
            "limpeza": pd.DataFrame(relatorio),
            "retornos_grandes": preparar_para_excel(retornos_grandes, ["retorno"]),
            "ajustes_grandes": preparar_para_excel(ajustes_grandes,
                                                   ["mudanca_da_razao", "retorno_ajustado_base",
                                                    "retorno_nao_ajustado"])}


def gerar_resultados(dados, relatorio_limpeza, resultado, parametros):
    """
    Recebe: dados limpos, relatório de limpeza, resultado da Parte 3 e parâmetros.
    Faz:    1) relatórios só informativos: retornos diários acima de 40% (na tela, só os 5
               maiores e os 5 menores), dias de ajuste grande do Economatica e conferências de
               viés (estes dois vão só para o Excel);
            2) resultados ano a ano, depois o acumulado, depois a conferência da contabilidade;
            3) salva resultados.xlsx, patrimonio.png e acao_mais_operada.png na pasta
               "resultados".
    Devolve: dicionário com as tabelas de resultado (útil para testes).
    """
    diario, operacoes = resultado["diario"], resultado["operacoes"]
    retornos_grandes = listar_retornos_grandes(dados, resultado["universos"], operacoes,
                                               parametros)
    titulo("MAIORES ALTAS E QUEDAS DIÁRIAS (|r| > "
           f"{porcentagem_br(parametros['limite_retorno_grande'], 0)}) DE AÇÕES QUE JÁ ESTIVERAM "
           "NO UNIVERSO")
    mostrar_retornos_grandes(retornos_grandes)
    anotar(relatorio_limpeza, f"Retornos diários com |r| > "
           f"{porcentagem_br(parametros['limite_retorno_grande'], 0)} (ações que já estiveram no "
           "universo)", len(retornos_grandes), "lista na aba retornos_grandes, para o grupo "
           "conferir; nenhum foi corrigido")
    ajustes_grandes = listar_ajustes_grandes(dados, resultado["universos"], operacoes, parametros)
    anotar(relatorio_limpeza, f"Dias de ajuste grande do Economatica (razão ajustado ÷ não "
           f"ajustado mudou mais de {porcentagem_br(parametros['limite_ajuste_grande'], 0)})",
           len(ajustes_grandes), "lista na aba ajustes_grandes, só informativa: pistas para o "
           "grupo achar cisões mal ajustadas; nada é corrigido por ela")
    conferencias = conferencias_de_vies(dados, resultado, parametros)   # vai só para o Excel

    ano_a_ano = resultados_ano_a_ano(diario, operacoes, parametros)
    acumulado = resultados_acumulados(diario, operacoes, parametros)
    conta = conferir_contabilidade(diario, operacoes, parametros)
    mostrar_ano_a_ano(ano_a_ano)
    mostrar_acumulado(acumulado, conta, resultado)
    mostrar_contabilidade(conta)

    pasta = Path(parametros["pasta_resultados"])
    pasta.mkdir(parents=True, exist_ok=True)
    abas = montar_abas_do_excel(ano_a_ano, acumulado, conta, resultado,
                                relatorio_limpeza + conferencias, retornos_grandes,
                                ajustes_grandes)
    salvar_excel(pasta / "resultados.xlsx", abas)
    salvar_grafico(pasta / "patrimonio.png", resultado, parametros["patrimonio_inicial"])
    resumo_da_acao = resumir_acao_mais_operada(dados, resultado)
    mostrar_acao_mais_operada(resumo_da_acao)
    salvar_grafico_acao_mais_operada(pasta / "acao_mais_operada.png", dados, resultado,
                                     resumo_da_acao)
    print(f"\nArquivos salvos em {pasta}: resultados.xlsx, patrimonio.png e "
          "acao_mais_operada.png")
    return {"ano_a_ano": ano_a_ano, "acumulado": acumulado, "contabilidade": conta,
            "retornos_grandes": retornos_grandes, "ajustes_grandes": ajustes_grandes,
            "conferencias": conferencias}


# ##############################################################################################
#                                      EXECUÇÃO
# ##############################################################################################
def main():
    """Roda as 4 partes em ordem e mostra o tempo total."""
    inicio = time.time()
    dados_lidos = ler_todos_os_dados(PARAMETROS)                             # PARTE 1
    dados_limpos, relatorio_limpeza = limpar_dados(dados_lidos, PARAMETROS)  # PARTE 2
    mostrar_resumo_da_limpeza(relatorio_limpeza)
    resultado = aplicar_estrategia(dados_limpos, PARAMETROS)                 # PARTE 3
    gerar_resultados(dados_limpos, relatorio_limpeza, resultado, PARAMETROS)  # PARTE 4
    print(f"\nTempo total: {time.time() - inicio:.0f} segundos.")


if __name__ == "__main__":
    main()