# PMVisualization

Projeto de Iniciação Cientifica apresentando prova de conceito da visualização de grupos provenientes de Trace Clustering junto com as semelhanças e diferenças entre cada uma dessas representações de sublogs.

Geração da analise feita em python com manipulação de dados em Pandas Dataframe e visualização desenvolvida em Plotly e iGraph. Interface desenvolvida em Flask e WTForms.

## Requisitos de Máquina
* Python 3.9 ou superior

## Rodando o Projeto
* Para executar o projeto em sua máquina é necessário criar um ambiente virtual após clonar ou baixar o repositório. Para isso, entre na pasta onde o projeto está localizado em seu computador através do cmd,PowerShell ou terminal de sua IDE e use ```python3 -m venv venv-name```, com ```venv venv-name``` sendo o nome do seu ambiente virutal, para criar o ambiente para um interpretador exclusivo para este projeto.
* Após isso, você deve ingressar no ambiente virtual para poder instalar os requisitos necessários do projeto. Ainda no diretorio do projeto, execute o comando ```venv-name\Scripts\activate.bat``` para entrar no venv do projeto. Assim, todos os requisitos e comandos que você rodar, valerão apenas para o interpretador do programa.

* Estando no ambiente virtual do projeto, execute o comando ```pip install -r requirements.txt``` para instalar os pacotes necessários para executar o programa.

* Com isso, basta executar o arquivo ```run.py``` que se encontra dentro da pasta ```proj```. Você pode executá-lo na sua IDE ou no prompt de comando usando ```python3 run.py```.

## Usando a Ferramenta
Ao abrir o programa, será necessário o upload de um registro de logs personalizado para a visualização. Esse registro deve ser carregado APENAS EM .CSV.
Considerando que você possua um log de eventos com sequencias de atividades que possam ser definidas e que tenha seus traces agrupados em diferentes clusters, para poder visualizar suas topologias e outras estatísticas por grupos na ferramenta, é necessário que o documento em upload no programa contenha: 
* ID de case: único para cada trace
* Sequencia das Atividades do trace de cada case: um campo para cada case que contenha a ordem temporal de cada atividade no trace
* Cluster a qual o case pertence: um campo por case com a especificação do agrupamento a qual aquele case pertence

Abaixo um exemplo de como o log deve estar exposto em um dataset do tipo .csv:

| CaseID | Sequence                                        | cluster |
|--------|-------------------------------------------------|---------|
| 0      | A B C F G L I O H J P K Q T V U X Y Z           | 2       |
| 1      | A B C D E B C F G I L H O P J K Q T V U X Y Z Z | 1       |
| 2      | A B C F L G I H O P J K Q T U V X Q T U V X Q R | 3       |

Importante ressaltar que se o log carregado estiver com colunas que não estejam com os nomes iguais ao do exemplo, o carregamento da visualização falhará, e o upload não trará resultado.

## Testes e Dados
Os datasets usados para testar e desenvolver a ferramenta são provenientes de bancos de pesquisa pertencentes aos seguintes repositórios:
* Enriched event log of an incident management process: http://processmining.each.webhostusp.sti.usp.br/index.php/event-logs/
* 11th International Workshop on Business Process Intelligence 2015: https://www.win.tue.nl/bpi/doku.php?id=2015:challenge
* Sepsis Cases Event Log: https://data.4tu.nl/articles/dataset/Sepsis_Cases_-_Event_Log/12707639
