Feito:
Biblioteca de log para fazer o tratamento estruturado

Time stamp de quando terminou o round

Qual o erro que deu se deu algum erro

No server, toda vez que receber um model

Quanod o serve receber todos os models, exibir as métricas de acurácia
-> Baseado nas métricas do flower

se não houver biblioteca de log, fazer classe log

Script para explorar o log
Como mostrar os resultadoS? (extrair informações e plotar o necessário)

Expressão regular em python
REGEX

Mudar a tag INFO para METRIC quando se tratar de métrica ou fazer de outra forma similar

---

logs:
O quão verboso ele vai ser? (modos)
-> Pode ter 2 logs: Um log all e um log de métricas

---

para quinta:
Estruturar para extrair informações
Montar CSV com coluna tempo, round, accuracy
-> A linha vai ter tempo (fim 5 - começo 18), round 1, e accuracy do round 1

---

# Métricas

Dados coletados
-> Tempo de cada um
-> Tempo total

### Métricas de tempo

- Delta T de cada round (Milisegundos (ms))
- Tempo para convergir

### Métricas de aprendizado (por cliente e médio)

- Loss
- Accuracy
- Precision
- Recall
- F1-score

### Métricas de rede (por cliente, médio, e total)

- Uso de rede
-

### Métricas de aprendizado Federado

- Equidade entre os clientes (gráfico de pizza da quantidade que cada cliente foi escolhido???)
- Convergência do modelo global

---

[X] Implementar métodos de seleção de clientes do artigo
[] Implementar gráficos comparativos (seleção relativa de clientes)
[] Implementar gráfico de pizza para seleção de clientes

---