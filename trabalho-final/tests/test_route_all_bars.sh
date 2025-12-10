\documentclass[conference]{IEEEtran}
\IEEEoverridecommandlockouts

\usepackage{cite}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{graphicx}
\usepackage{textcomp}
\usepackage{xcolor}
\def\BibTeX{{\rm B\kern-.05em{\sc i\kern-.025em b}\kern-.08em
    T\kern-.1667em\lower.7ex\hbox{E}\kern-.125emX}}
\usepackage{graphicx} 
\usepackage{amsmath,amssymb,amsthm}
\usepackage{graphicx,float}
\graphicspath{{images/}}
\usepackage{textgreek}
\usepackage{relsize}
\usepackage{siunitx}
\usepackage{tabto}
\usepackage[brazil]{babel}
\usepackage[T1]{fontenc} 
\usepackage{amsmath}
\usepackage[cmintegrals]{newtxmath}
\usepackage{bm} 

\renewcommand{\IEEEkeywordsname}{Palavras-chave}

\begin{document}

\title{Aplicação de Algoritmos de Computação Evolucionária para o Problema do Caixeiro Viajante (TSP) para Rotas de Bares Participantes do Projeto "Comida Di Buteco" \\
{\footnotesize \textsuperscript{}}

}

\author{\IEEEauthorblockN{1\textsuperscript{st}Gabriel Silva de Araujo }
\IEEEauthorblockA{\textit{Escola de Engenharia UFMG} \\
\textit{Universidade Federal de Minas Gerais
}\\
Belo horizonte, Brasil \\
gabrvalete@gmail.com}
\and
\IEEEauthorblockN{2\textsuperscript{nd} Gabrielli Valelia Sousa da Silva}
\IEEEauthorblockA{\textit{Escola de Engenharia UFMG} \\
\textit{Universidade Federal de Minas Gerais
}\\
Belo Horizonte, Brasil \\
gabriellivalelia@gmail.com
}
\and
\IEEEauthorblockN{3\textsuperscript{rd}  Júlia Diniz Rodrigues}
\IEEEauthorblockA{\textit{Escola de Engenharia UFMG} \\
\textit{Universidade Federal de Minas Gerais
}\\
Belo Horizonte, Brasil \\
juliadinizrodrigues@gmail.com}


}

\maketitle

\begin{abstract}
Este trabalho apresenta uma abordagem baseada em meta-heurísticas para otimização de rotas no contexto do evento gastronômico "Comida di Buteco". O problema é modelado como uma variante do Problema do Caixeiro Viajante com Janelas de Tempo (TSPTW), considerando restrições reais de horários de funcionamento, avaliações dos estabelecimentos e tempos de deslocamento obtidos via Google Maps. Foram implementados e comparados algoritmos clássicos (Kruskal, Bellmore-Nemhauser), Ant Colony Optimization (ACO) e Busca Tabu (Tabu Search), integrados a uma aplicação web interativa. Os resultados demonstram que a Busca Tabu, adaptada para múltiplos dias e restrições práticas, supera as heurísticas construtivas e apresenta desempenho competitivo frente ao ACO, proporcionando soluções de alta qualidade em tempo viável para instâncias reais.
\end{abstract}

\begin{IEEEkeywords}
Otimização, TSP, Busca Tabu, Ant Colony Optimization, Meta-heurísticas, Google Maps, Rotas, Janelas de Tempo, Comida di Buteco
\end{IEEEkeywords}

\section{Introdução}
\label{sec:introducao}

Problemas de otimização combinatória, como o clássico Problema do Caixeiro Viajante (TSP), representam desafios computacionais significativos devido à sua natureza NP-difícil. Em cenários reais, a complexidade cresce com a presença de restrições dinâmicas, como janelas de tempo e tráfego urbano, configurando variantes como o TSP com janelas de tempo ((TSPTW -- \textit{Traveling Salesperson Problem with Time Windows})) e problemas de roteamento com restrições temporais e de serviço. Nessas circunstâncias, métodos exatos tornam-se inviáveis à medida que o número de vértices cresce, o que demanda o uso de meta-heurísticas que consigam explorar eficientemente espaços de busca vastos~\cite{toaza2023meta}.

Neste contexto, o presente trabalho propõe a aplicação da meta-heurística \textit{Tabu Search} para otimizar o roteiro de visitação do evento gastronômico “Comida di Buteco”, cuja descrição oficial está disponível no site institucional do festival~\cite{comidadibuteco2025}. A escolha se justifica pela capacidade da Tabu Search de escapar de mínimos locais e explorar regiões promissoras, mesmo em espaços de busca altamente não lineares e com restrições complexas~\cite{junior2024hybrid}. A motivação prática advém da dificuldade que os participantes enfrentam para planejar rotas que maximizem a visitação de bares bem avaliados e a qualidade da experiência, respeitando horários restritos e variabilidade no tempo de deslocamento.

Além disso, este estudo adota uma etapa sistemática de \textbf{validação das heurísticas}. Para tanto, foram implementados e comparados algoritmos clássicos e contemporâneos, como: uma heurística construtiva baseada em AGM (via Kruskal), a heurística de inserção de Bellmore–Nemhauser, e uma versão moderna de \textit{Ant Colony Optimization (ACO)}, além da Tabu Search. Essa validação permite estabelecer referências de custo, padrões de convergência e estabilidade, contribuindo para avaliar a eficácia da abordagem proposta em diferentes cenários.  

O desenvolvimento foi realizado em Python, aproveitando seu amplo ecossistema de bibliotecas, e integrou a API do Google Maps para geração de uma matriz realista de tempos de deslocamento, substituindo a simplificação por distâncias euclidianas, mais comum em estudos teóricos.

Este artigo está organizado da seguinte forma: a Seção~\ref{sec:metodologia} apresenta a modelagem, a construção da matriz de custos e a descrição dos algoritmos; a Seção~\ref{sec:resultados} traz os resultados dos experimentos e comparações entre métodos; e a Seção~\ref{sec:conclusoes} discute as conclusões obtidas e propõe direções para trabalhos futuros.

\section{Metodologia}
\label{sec:metodologia}

A abordagem proposta para a otimização das rotas do evento "Comida di Buteco" baseia-se na modelagem do problema como uma variação do Problema do Caixeiro Viajante com Janelas de Tempo (TSPTW), solucionado através da meta-heurística Busca Tabu (\textit{Tabu Search}).

\subsection{Coleta de Dados e Modelagem do Grafo}

 Diferente das abordagens clássicas que utilizam distâncias euclidianas, este trabalho prioriza o tempo de deslocamento real como métrica de custo. Para isso, foi utilizada a API do \textit{Google Maps} para gerar a matriz de distâncias entre os estabelecimentos e, a partir dela, estimar o tempo de deslocamento considerando uma velocidade média urbana de 18 km/h, conforme apresentado em \cite{reddit_velocidade_media}. Dessa forma, a matriz de custos reflete de maneira mais realista as condições de mobilidade encontradas no cenário do problema.

O problema é representado por um grafo orientado $G = (V, A)$, onde $V$ é o conjunto de vértices (bares) e $A$ o conjunto de arestas representando o trajeto. Cada vértice $v_i$ possui os seguintes atributos associados:

\begin{itemize}
    \item \textbf{Janela de Tempo:} Horário de abertura ($O_i$) e fechamento ($C_i$);
    \item \textbf{Avaliação ($R_i$):} Nota do estabelecimento no Google (utilizada na função de aptidão);
    \item \textbf{Tempo de Serviço ($S_i$):} Tempo médio de permanência no local, definido por padrão como 60 minutos.
\end{itemize}

\subsection{Validação e Métodos de Referência}

Antes da aplicação da meta-heurística principal, diferentes heurísticas clássicas foram utilizadas como parâmetros para validar a qualidade das soluções obtidas. Embora elas não considerem janelas de tempo, fornecem limites inferiores, superiores e padrões de referência fundamentais para avaliar o desempenho dos métodos implementados.

\subsubsection{Árvore Geradora Mínima (Kruskal)}

A Árvore Geradora Mínima (AGM) foi obtida pelo algoritmo de Kruskal, implementado com Union--Find com compressão de caminho e união por rank. Apesar de não constituir uma solução para o TSP, a AGM estabelece um limite inferior teórico para o custo mínimo.

\begin{algorithm}[H]
\caption{Algoritmo de Kruskal}
\begin{algorithmic}[1]
\State Ordenar as arestas por peso crescente.
\ForAll{arestas $(u,v)$ ordenadas}
    \If{$Find(u) \neq Find(v)$}
        \State $Union(u,v)$
        \State Adicionar $(u,v)$ à AGM
    \EndIf
\EndFor
\end{algorithmic}
\end{algorithm}

\subsubsection{Heurística de Bellmore--Nemhauser}

A heurística construtiva de Bellmore--Nemhauser produz rapidamente uma rota para o TSP clássico, sem janelas de tempo. A cada passo, o algoritmo expande parcialmente a rota inserindo o vértice que causa o menor aumento no custo total. Essa abordagem gera uma solução inicial determinística de baixo custo computacional, útil como limite superior simples.

\begin{algorithm}[H]
\caption{Bellmore--Nemhauser}
\begin{algorithmic}[1]
\State Escolher um vértice inicial $v_0$
\State Rota $R \gets [v_0]$
\While{existem vértices não visitados}
    \State Para cada vértice não visitado $u$, calcular o custo de inserção em todas as posições de $R$
    \State Inserir o vértice $u^\*$ e posição que minimizam o custo
    \State Atualizar $R$
\EndWhile
\State Fechar o ciclo adicionando o retorno ao vértice inicial
\end{algorithmic}
\end{algorithm}

\subsubsection{Otimização por Colônia de Formigas (ACO)}

A heurística ACO foi implementada em três variações que diferem quanto à influência relativa do feromônio, da heurística baseada em distância ($1/d$) e da taxa de evaporação. A cada iteração, cada formiga constrói uma rota probabilisticamente, guiada pelo histórico de boas soluções (feromônios) e pela proximidade entre vértices.

Após a construção das rotas, o feromônio é atualizado reforçando caminhos de menor custo, enquanto parte do feromônio global evapora.

\begin{algorithm}[H]
\caption{ACO}
\begin{algorithmic}[1]
\State Inicializar matriz de feromônios $\tau$
\For{cada iteração}
    \For{cada formiga $k$}
        \State Construir solução probabilística baseada em $\tau$ e na heurística $1/d$
        \State Calcular custo da solução
    \EndFor
    \State Evaporar feromônio: $\tau \gets (1-\rho)\tau$
    \State Depositar feromônio proporcional ao inverso do custo das melhores soluções
\EndFor
\end{algorithmic}
\end{algorithm}

As configurações foram:
\begin{itemize}
    \item \textbf{ACO Config 1 (Rápida):} 10 formigas, 150 iterações, $\alpha=1.0$, $\beta=2.0$, $\rho=0.5$, peso da elite 2.0.
    \item \textbf{ACO Config 2 (Balanceada):} 20 formigas, 150 iterações, $\alpha=1.0$, $\beta=2.5$, $\rho=0.5$, peso da elite 2.0.
    \item \textbf{ACO Config 3 (Exploratória):} 30 formigas, 150 iterações, $\alpha=1.0$, $\beta=3.0$, $\rho=0.4$, peso da elite 3.0.
\end{itemize}



\subsubsection{Busca Tabu (Tabu Search)}

A Busca Tabu foi empregada como método de intensificação local baseado em vizinhança. A técnica realiza buscas sucessivas na vizinhança da solução corrente aplicando movimentos como \textit{swap}, \textit{2-opt} ou inserção. Para evitar ciclos e escapar de mínimos locais, movimentos recentemente aplicados são armazenados em uma lista tabu de duração limitada.

Além disso, uma função de aspiração permite que um movimento tabu seja aceito caso produza uma solução melhor que qualquer outra encontrada até o momento.

\begin{algorithm}[H]
\caption{Busca Tabu}
\begin{algorithmic}[1]
\State Gerar solução inicial $S$
\State Melhor solução $S^\* \gets S$
\State Inicializar lista tabu $T$
\While{critério de parada não atingido}
    \State Gerar vizinhança $N(S)$
    \State Selecionar o melhor movimento $m \in N(S)$ não proibido por $T$
    \State Aplicar $m$ obtendo nova solução $S'$
    \State Atualizar $S \gets S'$
    \If{$f(S) < f(S^\*)$}
        \State $S^\* \gets S$
    \EndIf
    \State Inserir movimento $m$ em $T$ e remover itens expirados
\EndWhile
\State Retornar $S^\*$
\end{algorithmic}
\end{algorithm}

O Tabu Search também foi avaliado em três configurações distintas, variando o tamanho da lista tabu e os critérios de parada:
\begin{itemize}
    \item \textbf{Tabu Config 1 (Rápida):} lista tabu de tamanho 10, 150 iterações, 45 iterações sem melhoria.
    \item \textbf{Tabu Config 2 (Balanceada):} lista tabu de tamanho 20, 150 iterações, 45 iterações sem melhoria.
    \item \textbf{Tabu Config 3 (Exploratória):} lista tabu de tamanho 30, 150 iterações, 45 iterações sem melhoria.
\end{itemize}

Em todas as configurações, foi utilizada uma solução inicial inteligente baseada em nearest neighbor, e a avaliação incremental foi empregada para acelerar a busca. Essas configurações permitiram comparar o efeito da diversificação e do controle de memória na performance do algoritmo.

\subsection{Estratégia de Otimização (Tabu Search)}

A Busca Tabu foi escolhida como técnica principal de otimização devido à sua capacidade de escapar de mínimos locais e explorar regiões promissoras do espaço de busca. O algoritmo foi adaptado para lidar com restrições de janelas de tempo e rotas de múltiplos dias.

O algoritmo de Busca Tabu foi implementado para construir rotas que respeitem as restrições temporais e maximizem a experiência do usuário. O processo de busca opera com os seguintes parâmetros de entrada fornecidos pelo usuário: data de início e fim, horário inicial e final diário e ponto de partida (deve ser necessariamente um dos bares).

A construção da solução difere do TSP tradicional pela verificação dinâmica de viabilidade (\textit{Hard Constraints}):

\begin{enumerate}
    \item \textbf{Cálculo de Chegada:} Ao avaliar a ida do bar $i$ para o bar $j$, calcula-se o tempo estimado de chegada ($T_{chegada}$) somando-se o horário atual, o tempo de permanência em $i$ e o tempo de deslocamento $t_{ij}$.
    
    \item \textbf{Validação de Janela:} A transição só é considerada válida se $O_j \leq T_{chegada} \leq C_j$. Caso o bar esteja fechado no momento da chegada, a aresta é descartada ou penalizada severamente na iteração atual.
    
    \item \textbf{Transição entre Dias:} O algoritmo suporta rotas de múltiplos dias. Caso $T_{chegada}$ ultrapasse o horário final definido pelo usuário para o dia atual, a rota é retomada no dia seguinte, a partir do horário inicial configurado.
\end{enumerate}

\subsection{Função Objetivo}

A avaliação da qualidade da solução é multiobjetivo, buscando minimizar o tempo total de deslocamento enquanto maximiza a soma das avaliações dos bares visitados. Para transformar isso em um problema de otimização único, utiliza-se uma soma ponderada controlada pelo parâmetro $\alpha$ (Alfa), que permite ajustar a preferência entre ``rapidez'' e ``qualidade''.

A função de custo $Z$ a ser minimizada é dada pela Equação \ref{eq:funcao_objetivo}:

\begin{equation} \label{eq:funcao_objetivo}
    Z = \alpha \cdot \left( \sum_{(i,j) \in Rota} t_{ij} \right) - (1 - \alpha) \cdot \left( \sum_{j \in Rota} R_j \right)
\end{equation}

\noindent Onde:
\begin{itemize}
    \item $t_{ij}$ representa o tempo de deslocamento entre o bar $i$ e o bar $j$;
    \item $R_j$ representa a nota (avaliação) do bar $j$;
    \item $\alpha$ é o coeficiente de ponderação, tal que $0 \leq \alpha \leq 1$.
\end{itemize}

Dessa forma, o algoritmo busca o equilíbrio ideal, penalizando rotas com tempos de viagem excessivos e premiando a inclusão de bares bem avaliados. Dentre os possíveis valores para o parâmetro $\alpha$, foi escolhido $\alpha = 0.85$ como padrão nos experimentos principais. Esse valor prioriza fortemente a minimização do tempo total de deslocamento, mas ainda confere peso relevante à soma das avaliações dos bares visitados. A escolha foi baseada em testes preliminares, que indicaram que valores muito próximos de 1 resultavam em rotas mais rápidas porém com menor qualidade média dos bares, enquanto valores muito baixos priorizavam excessivamente a nota, levando a rotas pouco realistas em termos de deslocamento. O valor intermediário adotado proporcionou um bom equilíbrio entre eficiência logística e experiência do usuário.

\subsection{Integração com o Frontend e Contrato da API}
\label{sec:frontend_api_actual}

A interface do sistema foi desenvolvida como uma aplicação web em React, empacotada com Vite, com o objetivo de facilitar a interação do usuário e apoiar a execução dos experimentos de otimização. O frontend disponibiliza telas para configuração dos filtros de busca (datas, horários, ponto de partida e nota mínima), além de apresentar a rota resultante por meio de um mapa interativo integrado à Google Maps JavaScript API. 

Além das funcionalidades de configuração e visualização das rotas, a interface também incorpora uma seção introdutória destinada a contextualizar o usuário sobre o evento e sobre o propósito acadêmico do projeto. Nessa área, apresenta-se uma descrição concisa da competição gastronômica “Comida di Buteco”, acompanhada de uma galeria de imagens dos pratos participantes, obtidas diretamente do site oficial do evento e redirecionamento para a página correspondente. A interface inclui ainda uma breve apresentação da disciplina universitária à qual este trabalho está vinculado, bem como a identificação dos integrantes do grupo responsáveis pelo desenvolvimento do sistema. Essa camada informativa complementa o módulo de otimização ao situar o problema no cenário real da competição e ao reforçar o caráter educacional do estudo, enriquecendo a experiência de navegação e aproximando o usuário do contexto prático que motivou o desenvolvimento da ferramenta.

\textbf{Fluxo de dados e responsabilidades.}  
\begin{enumerate}
    \item O usuário configura os filtros desejados na interface (datas, horários, ponto inicial, nota mínima, categorias de cardápio, etc.).
    \item O frontend envia um pedido \texttt{POST} para \texttt{/api/optimize-route}, contendo o payload de parâmetros fornecidos pelo usuário.
    \item O backend executa o algoritmo de otimização retornando a melhor rota a partir das preferências fornecidas pelo usuário.
    \item O frontend processa a resposta e exibe:
    \begin{itemize}
        \item rota por dia sobreposta ao mapa (usando \texttt{Markers} e \texttt{DirectionsRenderer});
        \item painel lateral com estatísticas agregadas (distância, duração total, número de paradas, custo estimado);
        \item lista ordenada de bares com horários previstos de chegada/saída.
    \end{itemize}
\end{enumerate}

\textbf{Contrato da API (endpoints utilizados).}
\begin{itemize}
    \item \texttt{GET /api/health} — verificação simples de disponibilidade do backend.
    \item \texttt{POST /api/optimize-route} — executa a otimização com base nos filtros enviados pelo frontend.
\end{itemize}

\section{Resultados e Discussão}
\label{sec:resultados}

\subsection{Desempenho das Heurísticas ACO e Tabu Search em Relação aos Limites Teóricos (AGM e Bellmore--Nemhauser)}
\label{sec:resultados_limites}

Os experimentos realizados com a matriz de distâncias realista (Google Maps) para 124 bares de Belo Horizonte permitiram comparar o desempenho das heurísticas implementadas. A Tabela~\ref{tab:comparativo_algoritmos} apresenta os custos finais e tempos de execução para cada algoritmo e configuração testada.

\begin{table*}[ht]
\centering
\caption{Comparativo de desempenho entre algoritmos}
\label{tab:comparativo_algoritmos}
\begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}cccc}
\hline
Algoritmo & Custo Final (km) & Tempo (s) & Iterações & Tamanho Rota \\
\hline
Kruskal (AGM) &  \textasciitilde 180.5 & 0.01 & -- & 124 \\
Bellmore-Nemhauser &  370.2 & 0.05 & -- & 124 \\
Tabu Config 1 &  220.7 & 2.1 & 150 & 124 \\
Tabu Config 2 &  218.9 & 2.3 & 150 & 124 \\
Tabu Config 3 &  217.5 & 2.5 & 150 & 124 \\
ACO Config 1 &  229.8 & 22.1 & 150 & 124 \\
ACO Config 2 &  225.4 & 25.3 & 150 & 124 \\
ACO Config 3 &  223.9 & 28.7 & 150 & 124 \\
\hline
\end{tabular*}
\end{table*}

Os resultados indicam que a Busca Tabu produziu rotas de menor custo em relação ao ACO, com tempo de execução significativamente inferior. O ACO, por sua vez, apresentou desempenho competitivo, mas com maior variabilidade e custo computacional. As heurísticas construtivas (Kruskal e Bellmore-Nemhauser) serviram como limites inferior e superior, respectivamente, validando a qualidade das soluções obtidas pelas meta-heurísticas.

O Gráfico~\ref{fig:grafico_evolucao} ilustra a evolução do custo das soluções ao longo das iterações para as diferentes configurações de Tabu Search e ACO, evidenciando a convergência dos métodos e a posição relativa em relação aos limites teóricos. Nota-se que o Tabu Search atinge rapidamente soluções próximas do ótimo, enquanto o ACO apresenta uma convergência mais lenta e maior dispersão entre execuções.

\begin{figure}[H]
    \centering
    \fbox{\includegraphics[width=0.48\textwidth]{grafico_evolucao.png}}
    \caption{Evolução do custo das soluções ao longo das iterações para as diferentes configurações de Tabu Search e ACO, comparadas aos limites teóricos de Kruskal (AGM) e Bellmore-Nemhauser.}
    \label{fig:grafico_evolucao}
\end{figure}

\subsection{Otimização Completa com Tabu Search Utilizando Todos os Filtros Propostos}
\label{sec:resultados_tabu_completo}

A execução da Busca Tabu com todos os filtros disponíveis --- intervalo de datas, janelas de horário, nota mínima e ponto de partida --- demonstrou a capacidade do algoritmo de gerar rotas personalizadas que atendem simultaneamente às preferências do usuário e às restrições impostas pelo problema. A heurística distribui as visitas ao longo de múltiplos dias, priorizando estabelecimentos bem avaliados e evitando violações de janelas de funcionamento, enquanto busca minimizar o custo total da rota.

\subsubsection*{Exemplo prático: configuração e saída do sistema}

Para ilustrar o comportamento completo da heurística, apresenta-se abaixo um exemplo real de requisição enviada ao backend e a resposta retornada ao usuário.

\paragraph{Parâmetros de entrada:}
\begin{verbatim}
{
    "startDate": "2025-11-24",
    "endDate": "2025-11-25",
    "startTime": "20:00",
    "endTime": "23:00",
    "startPoint": "Baiuca"
}
\end{verbatim}

\paragraph{Resumo da Otimização:}
\begin{verbatim}
Sucesso: True

ESTATÍSTICAS DA OTIMIZAÇÃO:
 • Número de paradas:          6
 • Distância total percorrida: 7.47 km
 • Duração total:              382.47 min
 • Custo (função objetivo):    98856.4
 • Dias necessários:           2
\end{verbatim}

\paragraph{Rota otimizada gerada pelo sistema:}
A Tabela~\ref{tab:rota_otimizada} apresenta a rota final produzida pela Busca Tabu após a aplicação dos filtros mencionados. Ela exibe, para cada estabelecimento visitado, o intervalo de atendimento utilizado no planejamento e o tempo estimado de deslocamento até o próximo ponto da rota.

\begin{table}[h!]
\centering
\caption{Rota otimizada gerada pela Busca Tabu}
\label{tab:rota_otimizada}
\begin{tabular}{c l c c }
\hline
\textbf{\#} & \textbf{Estabelecimento} & \textbf{Janela de Visita} & \textbf{Próx. Deslocamento} \\
\hline
1 & Rei do Peixe           & 20:00 -- 21:00 & 0 min  \\
2 & Dona Suica             & 21:00 -- 22:00 & 6 min  \\
3 & Bar da Lu              & 22:06 -- 23:06 & 1 min \\
4 & Bar da Cíntia          & 20:00 -- 21:00 & 0 min \\
5 & Tropeiro do Lisboa     & 21:00 -- 22:00 & 3 min  \\
6 & Recanto Vovó Tela      & 22:03 -- 23:03 & 12 min\\
\hline
\end{tabular}
\end{table}

\subsubsection*{Discussão dos resultados}

A solução demonstra três características centrais do modelo:

\begin{itemize}
    \item \textbf{Respeito às janelas de tempo}: todas as entradas e saídas se mantêm dentro dos horários de funcionamento informados.
    \item \textbf{Sequenciamento consistente}: as transições entre estabelecimentos apresentam tempos de deslocamento coerentes com a matriz de custos real obtida via Google Maps.
    \item \textbf{Distribuição multi-dia eficiente}: a heurística evita sobrecarga de um único período e cria um roteiro factível para o usuário.
\end{itemize}

Esse exemplo evidencia que a Tabu Search se adapta bem às restrições práticas do evento, oferecendo soluções de boa qualidade mesmo quando o espaço de busca é altamente restrito e não linear.

\paragraph{Teste automatizado para todos os bares.}
Para validar a robustez e a capacidade do algoritmo de englobar todos os bares do evento, foi desenvolvido o teste automatizado \texttt{test\_route\_all\_bars}. Esse teste executa a Busca Tabu com parâmetros configurados para permitir a visita a todos os estabelecimentos, removendo restrições de nota mínima e ampliando o intervalo de datas e horários. O objetivo é garantir que, sob condições permissivas, o algoritmo seja capaz de construir uma rota viável que percorra todos os bares participantes, respeitando as janelas de tempo e restrições operacionais. O sucesso desse teste demonstra a flexibilidade do backend e a adequação dos parâmetros finais do Tabu Search para instâncias de grande porte, servindo como validação prática da implementação e da modelagem do problema.

\paragraph{Configuração do experimento:}
O teste completo foi conduzido considerando todos os 124 bares participantes do evento. Os parâmetros utilizados foram:

\begin{itemize}
    \item \textbf{Período:} 24 de novembro a 7 de dezembro (14 dias)
    \item \textbf{Horário diário:} 00:00 às 23:59 (24 horas)
    \item \textbf{Nota mínima:} 0 (todos os bares incluídos)
    \item \textbf{Ponto inicial:} Baiuca
\end{itemize}

\paragraph{Estatísticas da otimização:}
\begin{table}[H]
\centering
\caption{Resumo da otimização completa para os 124 bares}
\label{tab:resultado_geral_124}
\begin{tabular}{lc}
\hline
\textbf{Métrica} & \textbf{Valor} \\
\hline
Número de paradas & 124 \\
Distância total percorrida & 188.14 km \\
Duração total & 7836.12 min \\
Custo (função objetivo) & 94914.12 \\
Dias necessários & 6 \\
\hline
\end{tabular}
\end{table}

\paragraph{Desafios de performance e soluções.}
Durante o desenvolvimento, foram identificados gargalos de performance ao executar o Tabu Search em instâncias grandes, especialmente ao tentar englobar todos os bares do evento. Inicialmente, o tempo de execução era elevado devido à avaliação repetida de soluções e à falta de estratégias eficientes de vizinhança e inicialização. Para mitigar esses problemas, foram implementadas as seguintes melhorias:
\begin{itemize}
    \item \textbf{Inicialização inteligente:} Utilização de heurísticas construtivas (como nearest neighbor) para gerar uma solução inicial de boa qualidade, reduzindo o número de iterações necessárias para convergência.
    \item \textbf{Avaliação incremental:} Reestruturação da função de avaliação para calcular apenas as diferenças de custo entre soluções vizinhas, evitando o recálculo completo da rota a cada iteração.
    \item \textbf{Tabu list baseada em movimentos:} Implementação de uma lista tabu eficiente, que armazena apenas os movimentos realizados (e não as soluções completas), reduzindo o overhead de verificação e acelerando a busca.
    \item \textbf{Ajuste de parâmetros:} Otimização dos parâmetros do algoritmo (tamanho da lista tabu, número máximo de iterações, critério de parada) para equilibrar qualidade da solução e tempo de execução.
\end{itemize}
Essas estratégias permitiram que o Tabu Search resolvesse instâncias com todos os bares em tempo viável, tornando o sistema responsivo mesmo para cenários de grande porte.

\subsection{Interface Gráfica e Visualização dos Resultados}
\label{sec:resultados_interface}

Ao entrar na aplicação, o usuário é direcionado para uma página inicial, apresentada na Figura~\ref{fig:home}. Essa tela serve como ponto de partida para a navegação e introduz o contexto geral do sistema.

Como discutido na Seção~\ref{sec:metodologia}, a interface gráfica não se limita aos filtros de otimização e à exibição das rotas, mas inclui também um conjunto de telas informativas. A primeira delas oferece uma introdução ao projeto “Comida di Buteco”, com descrição do evento e uma galeria de imagens dos pratos participantes, conforme ilustrado na Figura~\ref{fig:intro_evento}. A segunda apresenta a disciplina universitária à qual este trabalho está vinculado, destacada na Figura~\ref{fig:intro_disciplina}. Essas telas têm o objetivo de contextualizar o usuário, reforçando o caráter pedagógico do estudo e sua relação com o cenário real da competição.

\begin{figure}[h]
    \centering
    \fbox{\includegraphics[width=0.45\textwidth]{imagens/home.png}}
    \caption{Página Home.}
    \label{fig:home}
\end{figure}

\begin{figure}[h]
    \centering
    \fbox{\includegraphics[width=0.45\textwidth]{imagens/competicao.png}}
    \caption{Página de introdução ao projeto “Comida di Buteco”.}
    \label{fig:intro_evento}
\end{figure}

\begin{figure}[h]
    \centering
    \fbox{\includegraphics[width=0.45\textwidth]{imagens/projeto.png}}
    \caption{Página de introdução à disciplina.}
    \label{fig:intro_disciplina}
\end{figure}


\subsubsection{Fluxo de Seleção dos Filtros e Chamada ao Backend}
\label{sec:resultados_interface_fluxo}

O fluxo de interação do usuário com a aplicação inicia-se na seleção dos filtros desejados (datas, horários, nota mínima, ponto de partida, categorias de cardápio). Após a configuração, o frontend envia uma requisição para o backend, que executa o algoritmo de otimização e retorna a rota sugerida. O frontend então exibe a rota no mapa, juntamente com estatísticas e horários previstos, conforme ilustrado na Figura~\ref{fig:fluxo_interface}.

\begin{figure}[H]
    \centering
    \fbox{\includegraphics[width=0.45\textwidth]{imagens/fluxo_interface.png}}
    \caption{Fluxo de seleção de filtros e visualização da rota otimizada.}
    \label{fig:fluxo_interface}
\end{figure}

\section{Conclusões e Trabalhos Futuros}
\label{sec:conclusoes}

Este trabalho demonstrou a viabilidade e a eficácia da aplicação de meta-heurísticas, em especial a Busca Tabu, para a otimização de rotas em cenários reais com múltiplas restrições, como o evento “Comida di Buteco”. A integração de dados reais de deslocamento, avaliações e horários de funcionamento permitiu a geração de soluções personalizadas e de alta qualidade, superando abordagens construtivas clássicas e apresentando desempenho competitivo frente ao ACO.

Como trabalhos futuros, sugere-se:
\begin{itemize}
    \item Explorar variantes multiobjetivo, considerando explicitamente o trade-off entre tempo de deslocamento e qualidade dos bares visitados;
    \item Integrar preferências individuais dos usuários (ex: tipos de pratos, restrições alimentares);
    \item Avaliar o impacto de diferentes estratégias de inicialização e parâmetros da Busca Tabu;
    \item Ampliar a base de dados para outras cidades e eventos similares.
\end{itemize}

\appendices
\section{Repositório e Execução do Projeto}
O código-fonte do projeto \textit{MindHub} está disponível em: 

\begin{itemize}
    \item \textit{Frontend}: \url{https://github.com/gabriellivalelia/mindhub-frontend};
    \item \textit{Backend}: \url{https://github.com/gabriellivalelia/mindhub-backend}.
\end{itemize}

As instruções de execução estão descritas no arquivo \texttt{README.md} do respectivo repositório.


\bibliographystyle{ieeetr}
\bibliography{referencias}

\end{document}
