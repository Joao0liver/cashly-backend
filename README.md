# Cashly

Sistema web simplificado para **controle e fechamento de caixa**, desenvolvido com Django. O projeto permite registrar fechamentos de vendas, consultar seus detalhes, editar ou excluir registros e gerar relatórios financeiros em PDF por período.

> Projeto desenvolvido para fins acadêmicos e de aprendizado com o framework Django.
> João Augusto de Oliveira Pereira e Kleber Ramon de Aquino

## Tecnologias utilizadas

- **Python**
- **Django 6.1**
- **SQLite**
- **ReportLab** — geração de relatórios em PDF
- **Bootstrap 5.3.3** — interface
- **HTML5 / CSS3**
- **Git / GitHub**

As dependências utilizadas pelo projeto estão disponíveis no arquivo `requirements.txt`.

---

## Estrutura do projeto

```text
cashly-backend/
│
├── core/                 # Configurações principais do projeto Django
│
├── vendas/               # Gerenciamento dos fechamentos
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── relatorios/           # Geração e visualização de relatórios
│   ├── migrations/
│   ├── static/
│   ├── templates/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── db.sqlite3            # Banco de dados SQLite
├── manage.py
├── requirements.txt
└── README.md
```

As apps `vendas` e `relatorios` possuem seus próprios templates, arquivos estáticos, URLs e views.

---

# 🚀 Como executar o projeto

## Pré-requisitos

Antes de iniciar, certifique-se de possuir instalado:

- Python 3.x
- Git
- pip

Recomenda-se utilizar um **ambiente virtual (`venv`)** para instalar as dependências do projeto de forma isolada.

---

## 1. Clonar o repositório

Clone a branch `dev`:

```bash
git clone -b dev https://github.com/Joao0liver/cashly-backend.git
```

Entre na pasta do projeto:

```bash
cd cashly-backend
```

---

## 2. Criar o ambiente virtual

No Windows:

```bash
python -m venv venv
```

No Linux/macOS:

```bash
python3 -m venv venv
```

---

## 3. Ativar o ambiente virtual

### Windows — PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

### Windows — CMD

```cmd
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

Após a ativação, o terminal deverá apresentar algo semelhante a:

```text
(venv) C:\...\cashly-backend>
```

---

## 4. Instalar as dependências

Com o ambiente virtual ativado:

```bash
pip install -r requirements.txt
```

Entre as dependências atuais estão Django 6.1, Pillow e ReportLab.

---

## 5. Aplicar as migrações

Execute:

```bash
python manage.py migrate
```

Esse comando cria/aplica as estruturas necessárias no banco de dados.

Caso tenha ocorrido alguma alteração nos models e seja necessário criar novas migrações:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 6. Executar o servidor

Inicie o servidor de desenvolvimento:

```bash
python manage.py runserver
```

Por padrão, o projeto ficará disponível em:

```text
http://127.0.0.1:8000/
```

Para encerrar o servidor:

```text
CTRL + C
```

---

# 💰 App `vendas`

A app `vendas` é responsável pelo **cadastro e gerenciamento dos fechamentos de caixa**.

O model `Vendas` atualmente possui informações como data, tipo de pagamento, valor total, bandeira do cartão, responsável, número do caixa, observações e situação de conferência.

## Funcionalidades

### 📋 Listagem de fechamentos

Permite visualizar os fechamentos registrados no sistema.

A listagem recupera os registros armazenados no banco de dados utilizando o ORM do Django.

---

### ➕ Novo fechamento

Permite cadastrar um novo fechamento de caixa.

São registradas informações como:

- Data;
- Tipo de pagamento;
- Valor total;
- Bandeira do cartão;
- Responsável;
- Número do caixa;
- Observações;
- Status de conferência.

Os tipos de pagamento disponíveis atualmente são:

- Dinheiro;
- Pix;
- Débito;
- Crédito.

Para pagamentos realizados com cartão, também podem ser informadas as bandeiras:

- Visa;
- Mastercard;
- Elo.

---

### 🔎 Detalhes do fechamento

Cada registro pode ser consultado individualmente para visualizar suas informações completas.

A aplicação utiliza o identificador do registro para recuperar o fechamento correspondente. Caso ele não exista, o Django retorna uma página `404`.

---

### ✏️ Editar fechamento

Permite alterar os dados de um fechamento já registrado.

Após a edição, o registro é atualizado no banco de dados e o usuário retorna para a listagem de fechamentos.

---

### 🗑️ Excluir fechamento

Permite excluir um fechamento existente.

Antes da exclusão, o sistema apresenta uma tela de confirmação. A remoção é realizada após uma requisição `POST`.

---

# 📊 App `relatorios`

A app `relatorios` é responsável pela **consulta e geração de relatórios dos fechamentos registrados**.

Ela utiliza os dados cadastrados pela app `vendas` e o **ReportLab** para gerar documentos PDF.

## Funcionalidades

### 📅 Relatório diário

Permite gerar um relatório referente a uma data específica.

O sistema recebe a data selecionada, consulta os fechamentos daquele dia e utiliza os registros encontrados para montar o relatório.

---

### 🗓️ Relatório mensal

Também é possível gerar um relatório referente a um mês específico.

O sistema identifica automaticamente:

- Primeiro dia do mês;
- Último dia do mês;
- Registros pertencentes ao período selecionado.

Dessa forma, o relatório contempla todo o mês escolhido.

---

### 💵 Valor movimentado

O relatório apresenta o **valor total movimentado no período selecionado**, calculado a partir da soma dos valores dos fechamentos encontrados.

---

### 💳 Valores por tipo de pagamento

O relatório também apresenta a soma dos valores separados por tipo de pagamento:

- Dinheiro;
- Pix;
- Débito;
- Crédito.

Esses valores são calculados utilizando agregações do Django ORM.

---

### 📑 Relação dos fechamentos

Além do resumo financeiro, o PDF apresenta os fechamentos que fazem parte do período selecionado.

A tabela contém:

| Informação | Descrição |
|---|---|
| Data | Data do fechamento |
| Pagamento | Tipo de pagamento |
| Caixa | Número do caixa |
| Responsável | Responsável pelo fechamento |
| Valor | Valor movimentado |



---

### ⚠️ Validação de períodos sem registros

Caso não existam fechamentos para o período selecionado, o sistema não gera um relatório vazio.

Em vez disso, apresenta uma mensagem informando que não existem fechamentos registrados para o período escolhido.

---

### 📄 Geração do PDF

Os relatórios são gerados utilizando a biblioteca **ReportLab**.

O documento utiliza o formato A4 e possui seções para:

- Identificação do Cashly;
- Período do relatório;
- Resumo;
- Valor movimentado;
- Valores por tipo de pagamento;
- Relação dos fechamentos;
- Data e hora de geração.



---

# 🗃️ Banco de dados

O projeto utiliza **SQLite** durante o desenvolvimento.

O arquivo do banco de dados está localizado na raiz do projeto:

```text
db.sqlite3
```

Para criar ou atualizar a estrutura do banco:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

# 🛠️ Comandos úteis

### Criar migrações

```bash
python manage.py makemigrations
```

### Aplicar migrações

```bash
python manage.py migrate
```

### Criar usuário administrador

```bash
python manage.py createsuperuser
```

### Executar o servidor

```bash
python manage.py runserver
```

### Executar os testes

```bash
python manage.py test
```

---

# 👨‍💻 Autor

**João Augusto de Oliveira Pereira e Kleber Ramon de Aquino**

Projeto desenvolvido como atividade acadêmica para prática de desenvolvimento backend com Django.

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos e de aprendizado.