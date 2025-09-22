
### **Relatório de Análise Estatística de Acidentes Rodoviários**

Este relatório detalha os resultados da análise estatística exploratória realizada sobre os dados de acidentes da Polícia Rodoviária Federal. O objetivo é compreender as características centrais, a variabilidade e as relações entre as diferentes variáveis do conjunto de dados.

#### **1. O "Retrato" dos Acidentes: Medidas de Tendência Central e Dispersão**

Primeiro, buscamos entender o "acidente típico". Para isso, usamos medidas de tendência central (média, mediana, moda) e de dispersão (desvio padrão, variância).

##### **a. Tendência Central: O Acidente Mais Comum**

  * [cite\_start]**Pessoas e Veículos:** O acidente mais comum envolve **2 pessoas** e **2 veículos**[cite: 8]. [cite\_start]A média é um pouco maior (2.5 pessoas), indicando que, embora acidentes com 2 envolvidos sejam os mais frequentes, existem acidentes com um número bem maior de pessoas (como os de ônibus) que "puxam" a média para cima[cite: 8].
  * [cite\_start]**Gravidade:** Na grande maioria dos acidentes, o número de **mortos e feridos graves é zero**[cite: 8]. [cite\_start]Isso é confirmado pela mediana e moda, que são 0 para ambas as variáveis[cite: 8]. [cite\_start]A média, apesar de baixa (0.08 mortos por acidente), é maior que zero, o que nos alerta que uma minoria de acidentes concentra uma alta gravidade[cite: 8].

##### **b. Dispersão: A Imprevisibilidade da Gravidade**

  * **Desvio Padrão:** O desvio padrão nos mostra o quão "espalhados" são os dados. [cite\_start]Para a variável `mortos`, o desvio padrão (0.34) é mais de **4 vezes maior que a média** (0.08)[cite: 9].
      * **O que isso significa?** Significa que a gravidade de um acidente é altamente imprevisível. Embora a maioria não tenha fatalidades, quando um acidente grave ocorre, o número de mortes pode ser muito superior à média.
  * [cite\_start]**Amplitude:** A amplitude (diferença entre o maior e o menor valor) confirma isso, com acidentes envolvendo de 1 a 95 pessoas e registrando até 37 mortes em um único evento[cite: 9].

#### **2. Relações Entre as Variáveis: O Que Anda Junto?**

Investigamos como as variáveis se relacionam entre si, usando matrizes de covariância e correlação.

##### **a. Correlação de Pearson (Relações Lineares)**

O Mapa de Calor de Pearson mostra a força de uma relação *linear* (do tipo "quanto mais de A, mais de B") entre as variáveis.

  * **Correlações Fortes e Esperadas:**
      * [cite\_start]A correlação entre `pessoas` e `ilesos` é a mais forte (**0.74**)[cite: 3]. [cite\_start]Isso é intuitivo: quanto mais gente no acidente, maior a chance de ter mais pessoas que saem ilesas[cite: 3].
      * [cite\_start]`pessoas` e `veiculos` também têm uma correlação positiva moderada (**0.44**), o que faz sentido[cite: 3].
  * **Correlações Fracas ou Inexistentes:**
      * [cite\_start]A relação entre `feridos_leves` e `feridos_graves` é quase nula (**-0.05**), indicando que a ocorrência de um tipo de ferimento não implica na ocorrência do outro[cite: 4].
      * [cite\_start]Curiosamente, o número de `mortos` tem uma correlação muito baixa com quase todas as outras variáveis, exceto `pessoas` (**0.20**), reforçando a ideia de que a fatalidade depende de fatores muito específicos em cada acidente[cite: 3].

##### **b. Correlação de Spearman (Relações Monotônicas)**

O Coeficiente de Spearman é útil para relações que não são perfeitamente lineares.

  * [cite\_start]**Destaque:** A correlação entre `pessoas` e `veiculos` sobe de 0.44 (Pearson) para **0.70** (Spearman)[cite: 3, 12].
      * **O que isso significa?** A relação entre o número de pessoas e de veículos não é uma linha reta perfeita, mas segue uma tendência clara: quando um aumenta, o outro também aumenta. Spearman captura essa tendência de forma mais eficaz.

#### **3. Análise Visual: Gráficos que Contam a História**

Os gráficos nos ajudam a visualizar e confirmar nossas descobertas estatísticas.

  * **Boxplots:** Os gráficos de caixa para `mortos` e `feridos_graves` mostram claramente que a maioria dos dados está concentrada no zero (a linha da mediana está no zero), com uma grande quantidade de "pontos" acima dela. Esses pontos são os **outliers**, ou seja, os acidentes graves que fogem ao padrão.
  * **Gráficos de Linha e Dispersão:**
      * O gráfico "Hora do Dia vs. Total de Mortos" revela uma **relação não linear**, com picos de fatalidade no início da manhã e, principalmente, no final da tarde (entre 18h e 20h).
      * O gráfico de dispersão "Pessoas vs. Total de Feridos" mostra uma **tendência positiva**, confirmando a correlação que calculamos.

#### **4. Amostragem e o Teorema do Limite Central**

##### **a. Uma Fatia do Todo**

Testamos diferentes formas de "fatiar" os dados para ver se as amostras representavam bem o todo.

  * [cite\_start]**Técnicas de Amostragem:** As médias de pessoas por acidente nas amostragens **Simples (2.57)**, **Sistemática (2.47)** e **Estratificada (2.53)** ficaram muito próximas da média real de toda a base de dados (**2.53**)[cite: 11].
  * [cite\_start]A amostragem por **Conglomerados (2.75)** teve um resultado um pouco mais distante, o que é esperado, pois ao sortear alguns municípios, corre-se o risco de pegar cidades com um perfil de acidentes diferente da média nacional[cite: 11].
  * [cite\_start]**Tamanho da Amostra:** Com uma confiança de 95%, calculamos que uma amostra de apenas **384 acidentes** seria suficiente para ter uma boa estimativa da realidade[cite: 11]. [cite\_start]Na prática, confirmamos que amostras maiores produzem médias mais próximas da realidade[cite: 10]. [cite\_start]A média com 10.000 amostras (**2.5086**) foi mais precisa que a média com apenas 10 amostras (**2.9000**)[cite: 10].

##### **b. Teorema do Limite Central na Prática**

O Teorema do Limite Central (TLC) diz que, se pegarmos muitas amostras de uma população e calcularmos a média de cada uma, a distribuição dessas médias se parecerá com uma curva normal (curva de sino).

O histograma acima comprova o TLC. Embora a distribuição original de pessoas por acidente seja assimétrica, a distribuição das médias de 1000 amostras de tamanho 30 se aproxima muito de uma curva normal. A "Média das Médias" (2.51) ficou quase idêntica à "Média Populacional" (2.53), mostrando o poder do teorema para estimar parâmetros populacionais.

Para reforçar, geramos dados com uma **distribuição Exponencial** (totalmente diferente da normal) e repetimos o processo.

Como visto acima, mesmo partindo de uma distribuição exponencial (canto superior esquerdo), a distribuição das médias das amostras rapidamente tende para a forma de uma curva normal à medida que o tamanho da amostra aumenta de 10 para 30 e 50.

#### **5. Aderência de Distribuições: Qual a "Forma" dos Nossos Dados?**

Utilizamos a função Fitter para descobrir qual modelo matemático melhor descreve a distribuição do número de feridos graves (em acidentes que tiveram ao menos um).

  * [cite\_start]**Resultado:** A **distribuição Exponencial** foi a que melhor se ajustou aos dados, com o menor erro (`sumsquare_error` de 0.47)[cite: 5].
      * **O que isso significa?** A distribuição exponencial é comum em eventos onde ocorrências "pequenas" são muito frequentes e ocorrências "grandes" são muito raras. No nosso caso, acidentes com 1 ferido grave são os mais comuns, acidentes com 2 são mais raros, com 3 ainda mais raros, e assim por diante. Isso descreve perfeitamente o padrão de gravidade dos acidentes.

O gráfico abaixo sobrepõe a curva exponencial teórica aos dados reais, mostrando um excelente ajuste.

-----

### **Conclusão Geral**

[cite\_start]A análise estatística revela que o "acidente padrão" nas rodovias federais envolve dois veículos e duas pessoas, resultando, na maioria das vezes, apenas em danos materiais ou ferimentos leves[cite: 8]. [cite\_start]No entanto, a alta variabilidade, especialmente no número de mortos, destaca a existência de uma minoria de eventos extremamente graves que elevam o risco e a imprevisibilidade[cite: 9]. [cite\_start]As correlações mostram relações esperadas entre o número de envolvidos [cite: 3][cite\_start], enquanto a análise de amostragem e o Teorema do Limite Central confirmam a robustez dos dados e a validade das estimativas[cite: 11]. [cite\_start]Finalmente, a aderência à distribuição exponencial fornece um modelo matemático para a ocorrência de feridos graves, confirmando o padrão de "muitos acidentes com pouca gravidade e poucos acidentes com muita gravidade"[cite: 5].