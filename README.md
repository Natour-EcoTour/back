# Guia de Inicialização do Projeto Natour (Desenvolvimento)

Este documento explica como iniciar o aplicativo para desenvolvimento, descreve as principais pastas do projeto e suas funções.

## Como iniciar o aplicativo para desenvolvimento

1. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Execute as migrações**:
   ```bash
   python manage.py migrate
   ```
3. **Inicie o servidor de desenvolvimento**:
   ```bash
   python manage.py runserver
   ```
4. **(Opcional) Inicie os serviços do Docker**:
   Caso utilize monitoramento/logs:
   ```bash
   docker-compose up
   ```

## Estrutura de Pastas

- `natour/` — Código principal do backend Django.
  - `api/` — Lógica da aplicação, modelos, views, serializers, métodos, migrações, etc.
    - `methods/` — Funções auxiliares e métodos específicos (ex: criação de código, envio de email).
    - `migrations/` — Arquivos de migração do banco de dados.
    - `schemas/` — Schemas para validação de dados.
    - `serializers/` — Serializadores para transformar dados entre modelos e APIs.
    - `utils/` — Funções utilitárias.
    - `views/` — Views da API (endpoints).
  - `settings.py` — Configurações do projeto Django.
  - `urls.py` — Rotas principais do projeto.
  - `wsgi.py`/`asgi.py` — Arquivos para deploy do projeto.
- `manage.py` — Script principal para comandos Django.
- `requirements.txt` — Lista de dependências Python.
- `docker/` — Configurações de serviços Docker (monitoramento, logs, etc).
  - `loki/`, `prometheus/`, `promtail/`, `tempo/` — Configurações de monitoramento/logs.
- `staticfiles/` — Arquivos estáticos (CSS, JS, imagens).
- `templates/` — Templates HTML para emails e páginas.
  - `email_templates/` — Templates de email.
- `logs/` — Logs gerados pela aplicação.
- `tests/` — Testes automatizados do projeto.
- `documents/` — Documentação e diagramas.
- `postman/` — Coleções de testes para API (Postman).
