# Natour API 🏞️

Uma API REST robusta desenvolvida em Django para gerenciamento de pontos turísticos e naturais, permitindo aos usuários descobrir, avaliar e compartilhar locais incríveis.

## 📋 Sumário

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Arquitetura](#arquitetura)
- [Instalação e Configuração](#instalação-e-configuração)
- [Como Usar](#como-usar)
- [Endpoints da API](#endpoints-da-api)
- [Monitoramento](#monitoramento)
- [Contribuição](#contribuição)
- [Licença](#licença)

## 🎯 Sobre o Projeto

O **Natour** é uma plataforma que conecta amantes da natureza e viajantes, permitindo:

- **Descoberta**: Encontre trilhas, cachoeiras, parques e outros pontos naturais
- **Compartilhamento**: Cadastre novos locais e compartilhe experiências
- **Avaliação**: Sistema de reviews e classificações
- **Comunidade**: Interação entre usuários através de fotos e avaliações

## ✨ Funcionalidades

### 👤 Gestão de Usuários
- ✅ Cadastro e autenticação com JWT
- ✅ Verificação por email com códigos temporários
- ✅ Perfis de usuário com fotos
- ✅ Sistema de roles (usuário/administrador)
- ✅ Gestão de status de conta

### 📍 Gestão de Pontos
- ✅ Cadastro de pontos turísticos/naturais
- ✅ Categorização (trilhas, cachoeiras, parques, fazendas)
- ✅ Geolocalização (latitude/longitude)
- ✅ Horários de funcionamento
- ✅ Sistema de aprovação por administradores
- ✅ Contador de visualizações

### 📸 Gestão de Fotos
- ✅ Upload de imagens via Cloudinary
- ✅ Fotos para usuários e pontos
- ✅ Gerenciamento completo (CRUD)

### ⭐ Sistema de Avaliações
- ✅ Reviews com classificação (1-5 estrelas)
- ✅ Cálculo automático da média de avaliações

### 📧 Sistema de Notificações
- ✅ Templates de email personalizados
- ✅ Notificações para registro, alterações de status
- ✅ Envio de códigos de verificação

## 🛠️ Tecnologias Utilizadas

### Backend
- **Django 5.2.3** - Framework web principal
- **Django REST Framework** - APIs REST
- **PostgreSQL** - Banco de dados principal
- **JWT** - Autenticação e autorização
- **Cloudinary** - Armazenamento de imagens

### Monitoramento e Observabilidade
- **Prometheus** - Métricas de sistema
- **Grafana** - Dashboards e visualizações
- **Loki** - Agregação de logs
- **Promtail** - Coleta de logs
- **Tempo** - Tracing distribuído

### Infraestrutura
- **Docker** - Containerização
- **Docker Compose** - Orquestração de serviços

### Outras Tecnologias
- **Anymail** - Envio de emails
- **Django CORS Headers** - Configuração CORS
- **Python Decouple** - Configurações de ambiente
- **Rate Limiting** - Controle de taxa de requisições

## 🏗️ Arquitetura

```
natour/
├── api/                    # App principal da API
│   ├── models.py          # Modelos de dados
│   ├── serializers/       # Serializadores por funcionalidade
│   ├── views/             # Views organizadas por módulo
│   ├── methods/           # Métodos auxiliares
│   └── utils/             # Utilitários
├── settings.py            # Configurações do Django
├── urls.py               # Roteamento principal
├── docker/               # Configurações Docker
│   ├── prometheus/
│   ├── promtail/
│   └── tempo/
└── templates/            # Templates de email
```

### Modelos Principais

- **CustomUser**: Usuários do sistema com roles
- **Point**: Pontos turísticos/naturais
- **Photo**: Fotos de usuários e pontos
- **PointReview**: Avaliações dos pontos
- **Terms**: Termos e condições
- **Role**: Papéis de usuário

## 🏛️ Componentes da Arquitetura

### 📋 Views (Controladores)

As views estão organizadas por módulos funcionais para melhor manutenibilidade:

#### **auth.py** - Autenticação
- `MyTokenObtainPairView`: JWT personalizado com informações do usuário
- `create_user`: Registro de novos usuários com verificação de email
- `login`: Autenticação com rate limiting (5 tentativas/minuto)

#### **users.py** - Gestão de Usuários
- `get_my_info`: Perfil do usuário autenticado (cache 60s)
- `update_my_info`: Atualização de dados pessoais
- `delete_my_account`: Exclusão da própria conta
- `get_all_users`: Listagem paginada para admins
- `change_user_status`: Ativação/desativação de contas
- `get_user_points` / `get_my_points`: Pontos por usuário

#### **point.py** - Gestão de Pontos
- `create_point`: Criação de novos pontos turísticos
- `get_point_info`: Detalhes de um ponto específico
- `get_all_points`: Listagem administrativa com cache
- `point_approval`: Aprovação/rejeição por admins
- `edit_point`: Edição por proprietários
- `show_points_on_map`: Dados otimizados para mapas
- `add_view`: Contador de visualizações

#### **photo.py** - Gestão de Imagens
- `create_photo`: Upload via Cloudinary
- `update_photo`: Atualização de imagens existentes
- `get_photo`: Busca com filtros (user_id/point_id)
- `delete_photo`: Remoção com cleanup no Cloudinary

#### **review.py** - Sistema de Avaliações
- `add_review`: Criação de reviews com cálculo automático de média

#### **code.py** - Verificação por Email
- `send_verification_code`: Envio com rate limiting
- `verify_code`: Validação de códigos temporários

#### **terms.py** - Termos e Condições
- `create_terms`: Criação por admins
- `get_terms`: Visualização pública com cache
- `update_terms`: Atualização com notificação automática

### 📧 Email Templates

Sistema de templates HTML personalizados para comunicação:

#### **user_registration.html**
- Boas-vindas para novos usuários
- Design responsivo e profissional
- Variáveis: `username`

#### **validation_code.html**
- Códigos de verificação de 6 dígitos
- Tempo de expiração destacado
- Variáveis: `code`, `expiration_time`

#### **password_code_request.html**
- Recuperação de senha
- Instruções claras de uso
- Variáveis: `code`, `username`

#### **user_status_change.html**
- Notificações de ativação/desativação
- Motivos de mudança de status
- Variáveis: `username`, `status`, `reason`

#### **point_status_change.html**
- Aprovação/rejeição de pontos
- Feedback para criadores
- Variáveis: `point_name`, `status`, `reason`

#### **updated_terms.html**
- Notificação de novos termos
- Link para visualização
- Variáveis: `username`, `terms_url`

#### **delete_user_account.html**
- Confirmação de exclusão de conta
- Informações de backup/recuperação
- Variáveis: `username`, `deletion_date`

#### **delete_point.html**
- Notificação de exclusão de ponto
- Motivos administrativos
- Variáveis: `point_name`, `reason`

### 🔧 Utils (Utilitários)

#### **filter_logs.py**
```python
class ExcludeMetricsFilter:
    """Filtro para excluir logs de métricas do Prometheus"""
    - Remove ruído dos logs de monitoramento
    - Melhora legibilidade dos logs de aplicação
    - Configurável por path patterns
```

### 📊 Serializers (Serializadores)

Organizados por entidade para validação e serialização de dados:

#### **user.py**
- `CreateUserSerializer`: Validação de registro
  - Verificação de email único
  - Hash seguro de senhas
  - Validação de roles
- `CustomUserInfoSerializer`: Dados do perfil
- `UpdateUserSerializer`: Atualização de dados
- `AllUsersSerializer`: Listagem administrativa
- `UserStatusSerializer`: Mudança de status
- `GenericUserSerializer`: Dados básicos para tokens

#### **point.py**
- `CreatePointSerializer`: Criação de pontos
  - Validação de coordenadas
  - Verificação de horários
  - Validação de endereços
- `PointInfoSerializer`: Detalhes completos
- `PointOnMapSerializer`: Dados otimizados para mapas
- `PointApprovalSerializer`: Aprovação administrativa
- `PointStatusUser`: Status para usuários

#### **photo.py**
- `PhotoSerializer`: Upload e gestão de imagens
  - Validação de formatos
  - Compressão automática
  - Metadata de upload
- `PhotoIDSerializer`: Referências simples

#### **review.py**
- `CreateReviewSerializer`: Criação de avaliações
  - Validação de rating (1-5)
  - Verificação de usuário único por ponto
  - Cálculo automático de média

#### **terms.py**
- `CreateTermsSerializer`: Criação de termos
- `GetTermsSerializer`: Visualização pública
- `UpdateTermsSerializer`: Atualização com versionamento

### ⚙️ Methods (Métodos Auxiliares)

Funções especializadas para lógica de negócio:

#### **create_code.py**
```python
def create_code(length=6):
    """Geração de códigos de verificação seguros"""
    - Códigos alfanuméricos de 6 dígitos
    - Exclusão de caracteres ambíguos (0, O, I, 1)
    - Criptograficamente seguro com secrets
    - Cache Redis com TTL de 10 minutos
```

#### **send_terms_email.py**
```python
def send_updated_terms_email():
    """Notificação em massa para novos termos"""
    - Threading para performance
    - Processamento em lotes
    - Tratamento de falhas de envio
    - Log detalhado de operações
    - Rate limiting inteligente
```

### 🔐 Segurança e Performance

#### **Rate Limiting**
- Django RateLimit com chaves por IP
- Configurações específicas por endpoint
- Bloqueio automático em caso de abuso

#### **Cache Strategy**
- Cache de 60 segundos em listagens
- Invalidação automática em updates
- Varia por headers de autorização
- Redis como backend (produção)

#### **Validações**
- Sanitização de inputs
- Validação de tipos de arquivo
- Verificação de permissões por objeto
- Escape automático em templates

#### **Monitoring Integration**
- Métricas automáticas do Prometheus
- Logs estruturados para Loki
- Tracing distribuído com Tempo
- Health checks automáticos

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.12+
- PostgreSQL 13+
- Docker e Docker Compose (para monitoramento)

### 1. Clone o Repositório
```bash
git clone <url-do-repositorio>
cd natour-api
```

### 2. Configuração do Ambiente Virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instale as Dependências
```bash
pip install -r requirements.txt
```

### 4. Configuração das Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=sua_secret_key_aqui
DEBUG=True
DATABASE_URL=postgresql://usuario:senha@localhost:5432/natour_db

# Cloudinary
CLOUDINARY_CLOUD_NAME=seu_cloud_name
CLOUDINARY_API_KEY=sua_api_key
CLOUDINARY_API_SECRET=seu_api_secret

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu_email@gmail.com
EMAIL_HOST_PASSWORD=sua_senha_de_app
```

### 5. Configuração do Banco de Dados
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Execute o Servidor
```bash
python manage.py runserver
```

A API estará disponível em `http://localhost:8000`

### 7. Monitoramento (Opcional)
Para ativar o stack de monitoramento:

```bash
docker-compose up -d
```

Isso iniciará:
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3000`
- **Loki**: `http://localhost:3100`

## 🔄 Fluxo de Dados e Integração

### Exemplo: Criação de Ponto Turístico

```mermaid
graph TD
    A[Cliente POST /points/create/] --> B[View: create_point]
    B --> C[Serializer: CreatePointSerializer]
    C --> D[Validações de Negócio]
    D --> E[Model: Point.save()]
    E --> F[Cache Invalidation]
    F --> G[Response Serializada]
    G --> H[Cliente recebe dados]
```

#### **1. Recebimento da Requisição**
```python
# point.py - View
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_point(request):
    serializer = CreatePointSerializer(data=request.data)
```

#### **2. Validação dos Dados**
```python
# serializers/point.py
class CreatePointSerializer(serializers.ModelSerializer):
    def validate_coordinates(self, attrs):
        # Validação de latitude/longitude
        # Verificação de limites geográficos
```

#### **3. Lógica de Negócio**
```python
# models.py
class Point(models.Model):
    def save(self, *args, **kwargs):
        # Auto-cálculo de média de ratings
        # Geocoding reverso de endereço
        super().save(*args, **kwargs)
```

### Exemplo: Sistema de Notificações

```mermaid
graph TD
    A[Admin aprova ponto] --> B[View: point_approval]
    B --> C[Update Point Status]
    C --> D[Trigger Email Task]
    D --> E[Load Template HTML]
    E --> F[Render com Context]
    F --> G[Send via SMTP]
    G --> H[Log Success/Error]
```

#### **1. Trigger de Notificação**
```python
# views/point.py
def point_approval(request, point_id):
    # Lógica de aprovação
    if point.status == 'approved':
        send_approval_email.delay(point.id)  # Async task
```

#### **2. Template Rendering**
```python
# methods/send_terms_email.py
html_content = render_to_string(
    'email_templates/point_status_change.html',
    {
        'point_name': point.name,
        'status': 'Aprovado',
        'username': point.user.username
    }
)
```

#### **3. Envio Assíncrono**
```python
def send_email_notification(template, context, recipients):
    try:
        msg = EmailMultiAlternatives(
            subject=f"Natour - {context['subject']}",
            body="Versão texto do email",
            from_email="natourproject@gmail.com",
            to=recipients
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except SMTPException as e:
        logger.error(f"Erro no envio: {str(e)}")
```

### Exemplo: Gestão de Cache e Performance

```python
# Decorators de cache nas views
@cache_page(60)  # Cache por 60 segundos
@vary_on_headers("Authorization")  # Varia por usuário
@api_view(['GET'])
def get_all_points(request):
    # Consulta pesada otimizada
    queryset = Point.objects.select_related('user', 'photos')
    return paginated_response(queryset)
```

### Exemplo: Upload de Fotos com Cloudinary

```python
# serializers/photo.py
class PhotoSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        # Upload automático para Cloudinary
        image = validated_data.pop('image')
        
        # Configurações de transformação
        upload_result = cloudinary.uploader.upload(
            image,
            transformation=[
                {'width': 800, 'height': 600, 'crop': 'limit'},
                {'quality': 'auto:best'},
                {'format': 'auto'}
            ]
        )
        
        # Salvar metadata
        validated_data['public_id'] = upload_result['public_id']
        return super().create(validated_data)
```

## � Exemplos de Código Detalhados

### 🔐 Sistema de Autenticação

#### **JWT Personalizado com Informações do Usuário**
```python
# natour/api/views/auth.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado que adiciona informações extras ao token JWT
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Adicionar claims personalizados ao token
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role.name if user.role else 'user'
        
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    """
    View que usa o serializer personalizado
    """
    serializer_class = MyTokenObtainPairSerializer
```

**Explicação:**
- Estende o serializer padrão do SimpleJWT
- Adiciona informações do usuário diretamente no token
- Evita consultas extras ao banco para obter dados básicos
- O frontend pode usar essas informações sem fazer requests adicionais

#### **Login com Validação e Rate Limiting**
```python
# natour/api/views/auth.py
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', block=True)  # 5 tentativas por minuto por IP
def login(request):
    """
    Endpoint de login com proteção contra força bruta
    """
    try:
        # Buscar usuário por email (não por username)
        user = CustomUser.objects.get(email=request.data['email'])
    except CustomUser.DoesNotExist:
        return Response(
            {"error": "E-mail ou senha incorretos."}, 
            status=status.HTTP_404_NOT_FOUND
        )

    # Verificar senha
    if user.check_password(request.data['password']):
        # Verificar se a conta está ativa
        if user.is_active is False:
            return Response(
                {"error": "Conta desativada."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Atualizar último login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Gerar tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": GenericUserSerializer(user).data
        }, status=status.HTTP_200_OK)

    return Response(
        {"error": "E-mail ou senha incorretos."}, 
        status=status.HTTP_401_UNAUTHORIZED
    )
```

**Explicação:**
- `@ratelimit`: Protege contra ataques de força bruta
- Busca por email ao invés de username (mais seguro)
- Verifica status da conta antes de autenticar
- Atualiza timestamp de último login
- Retorna tokens e dados básicos do usuário

### 📊 Serializers com Validações Complexas

#### **Criação de Pontos Turísticos**
```python
# natour/api/serializers/point.py
from rest_framework import serializers
from django.core.validators import MinValueValidator, MaxValueValidator

class CreatePointSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de pontos com validações customizadas
    """
    class Meta:
        model = Point
        fields = [
            'name', 'description', 'point_type', 'latitude', 'longitude',
            'zip_code', 'city', 'neighborhood', 'state', 'street', 'number',
            'week_start', 'week_end', 'open_time', 'close_time', 'link'
        ]

    def validate_coordinates(self, attrs):
        """
        Validação personalizada para coordenadas geográficas
        """
        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')
        
        if latitude and longitude:
            # Verificar limites do Brasil
            if not (-35 <= latitude <= 5):
                raise serializers.ValidationError(
                    "Latitude deve estar entre -35 e 5 graus (território brasileiro)"
                )
            if not (-75 <= longitude <= -30):
                raise serializers.ValidationError(
                    "Longitude deve estar entre -75 e -30 graus (território brasileiro)"
                )
        
        return attrs

    def validate(self, attrs):
        """
        Validação cruzada entre campos
        """
        week_start = attrs.get('week_start')
        week_end = attrs.get('week_end')
        open_time = attrs.get('open_time')
        close_time = attrs.get('close_time')

        # Validar período da semana
        if week_start and week_end and week_start > week_end:
            raise serializers.ValidationError(
                "Data de início deve ser anterior à data de fim"
            )

        # Validar horários
        if open_time and close_time and open_time >= close_time:
            raise serializers.ValidationError(
                "Horário de abertura deve ser anterior ao de fechamento"
            )

        return attrs

    def create(self, validated_data):
        """
        Lógica customizada de criação
        """
        # Associar automaticamente ao usuário logado
        validated_data['user'] = self.context['request'].user
        
        # Status inicial como pendente para aprovação
        validated_data['is_active'] = False
        validated_data['status'] = None  # Aguardando aprovação
        
        return super().create(validated_data)
```

**Explicação:**
- `validate_coordinates`: Validação geográfica específica para o Brasil
- `validate`: Validação cruzada entre múltiplos campos
- `create`: Lógica personalizada que adiciona dados automáticos
- Garante que apenas pontos aprovados ficam ativos

#### **Upload de Fotos com Cloudinary**
```python
# natour/api/serializers/photo.py
from cloudinary.uploader import upload, destroy
from cloudinary.exceptions import Error as CloudinaryError

class PhotoSerializer(serializers.ModelSerializer):
    """
    Serializer para upload de fotos com otimizações automáticas
    """
    image = serializers.ImageField(write_only=True)
    
    class Meta:
        model = Photo
        fields = ['image', 'user', 'point']

    def validate_image(self, value):
        """
        Validação de arquivo de imagem
        """
        # Verificar tamanho (máximo 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(
                "Imagem muito grande. Máximo 10MB."
            )
        
        # Verificar tipo de arquivo
        allowed_types = ['image/jpeg', 'image/png', 'image/webp']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Formato não suportado. Use JPEG, PNG ou WebP."
            )
        
        return value

    def validate(self, attrs):
        """
        Validação de regra de negócio: foto deve ter usuário OU ponto
        """
        user = attrs.get('user')
        point = attrs.get('point')
        
        if not user and not point:
            raise serializers.ValidationError(
                "Foto deve ser associada a um usuário ou ponto."
            )
        
        if user and point:
            raise serializers.ValidationError(
                "Foto não pode ser associada a usuário e ponto simultaneamente."
            )
        
        return attrs

    def create(self, validated_data):
        """
        Upload para Cloudinary com otimizações automáticas
        """
        image_file = validated_data.pop('image')
        
        try:
            # Configurações de upload otimizadas
            upload_result = upload(
                image_file,
                transformation=[
                    {'width': 1200, 'height': 800, 'crop': 'limit'},  # Redimensionar
                    {'quality': 'auto:best'},  # Qualidade automática
                    {'format': 'auto'},  # Formato automático (WebP se suportado)
                    {'flags': 'progressive'}  # JPEG progressivo
                ],
                folder="natour/photos",  # Organizar em pastas
                use_filename=True,
                unique_filename=True
            )
            
            # Salvar informações do upload
            validated_data['public_id'] = upload_result['public_id']
            validated_data['image'] = upload_result['secure_url']
            
            return super().create(validated_data)
            
        except CloudinaryError as e:
            raise serializers.ValidationError(f"Erro no upload: {str(e)}")

    def update(self, instance, validated_data):
        """
        Atualização com cleanup da imagem anterior
        """
        if 'image' in validated_data:
            # Deletar imagem anterior do Cloudinary
            if instance.public_id:
                try:
                    destroy(instance.public_id)
                except CloudinaryError:
                    pass  # Log mas não falha se não conseguir deletar
            
            # Upload da nova imagem
            # ... (mesmo código do create)
        
        return super().update(instance, validated_data)
```

**Explicação:**
- Validação de tamanho e tipo de arquivo
- Upload otimizado com transformações automáticas
- Organização em pastas no Cloudinary
- Cleanup automático de imagens antigas
- Tratamento de erros específicos do Cloudinary

### 🎯 Views com Cache e Paginação

#### **Listagem de Pontos com Cache Inteligente**
```python
# natour/api/views/point.py
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from natour.api.pagination import CustomPagination

@cache_page(60)  # Cache por 60 segundos
@vary_on_headers("Authorization")  # Cache diferente por usuário
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_all_points(request):
    """
    Listagem administrativa de pontos com cache e filtros
    """
    # Query otimizada com select_related
    queryset = Point.objects.select_related('user').prefetch_related('photos')
    
    # Filtros dinâmicos
    point_name = request.query_params.get('name')
    if point_name:
        queryset = queryset.filter(name__icontains=point_name)
    
    point_type = request.query_params.get('type')
    if point_type:
        queryset = queryset.filter(point_type=point_type)
    
    status_filter = request.query_params.get('status')
    if status_filter == 'active':
        queryset = queryset.filter(is_active=True)
    elif status_filter == 'pending':
        queryset = queryset.filter(is_active=False, status__isnull=True)
    
    # Ordenação
    queryset = queryset.order_by('-created_at')
    
    # Paginação customizada
    paginator = CustomPagination()
    page = paginator.paginate_queryset(queryset, request)
    
    if page is not None:
        serializer = PointInfoSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    # Fallback sem paginação
    serializer = PointInfoSerializer(queryset, many=True)
    return Response(serializer.data)
```

**Explicação:**
- `@cache_page(60)`: Cache de 1 minuto para reduzir carga no banco
- `@vary_on_headers("Authorization")`: Cache separado por usuário
- `select_related` e `prefetch_related`: Otimização de queries
- Filtros dinâmicos baseados em query parameters
- Paginação customizada para grandes datasets

#### **Sistema de Reviews com Cálculo Automático**
```python
# natour/api/views/review.py
from django.db import transaction
from django.db.models import Avg

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request, point_id):
    """
    Adicionar review com atualização automática da média
    """
    point = get_object_or_404(Point, id=point_id)
    
    # Verificar se usuário já avaliou este ponto
    existing_review = PointReview.objects.filter(
        user=request.user, 
        point=point
    ).first()
    
    if existing_review:
        return Response(
            {"detail": "Você já avaliou este ponto."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    serializer = CreateReviewSerializer(data=request.data)
    
    if serializer.is_valid():
        # Usar transação para garantir consistência
        with transaction.atomic():
            # Criar a review
            review = serializer.save(user=request.user, point=point)
            
            # Recalcular média de ratings do ponto
            avg_rating = PointReview.objects.filter(
                point=point
            ).aggregate(avg=Avg('rating'))['avg']
            
            # Atualizar o ponto com a nova média
            point.avg_rating = round(avg_rating, 1) if avg_rating else 0
            point.save(update_fields=['avg_rating'])
        
        return Response(
            CreateReviewSerializer(review).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

**Explicação:**
- Verificação de review duplicada
- Uso de `transaction.atomic()` para garantir consistência
- Cálculo automático da média usando `Avg`
- Atualização eficiente com `update_fields`
- Validação de regras de negócio

### 📧 Sistema de Emails e Códigos

#### **Geração de Códigos Seguros**
```python
# natour/api/methods/create_code.py
import secrets
import string
from django.core.cache import cache

def create_code(length=6):
    """
    Gera códigos de verificação criptograficamente seguros
    """
    # Caracteres permitidos (sem ambíguos: 0, O, I, 1)
    alphabet = string.ascii_uppercase + string.digits
    alphabet = alphabet.replace('0', '').replace('O', '').replace('I', '').replace('1', '')
    
    # Gerar código usando secrets (criptograficamente seguro)
    code = ''.join(secrets.choice(alphabet) for _ in range(length))
    
    return code

def store_verification_code(email, code, ttl_minutes=10):
    """
    Armazena código no cache com TTL
    """
    cache_key = f'verification_code:{email}'
    cache.set(cache_key, code, timeout=ttl_minutes * 60)
    
    return cache_key

def verify_code(email, provided_code):
    """
    Verifica se o código fornecido está correto
    """
    cache_key = f'verification_code:{email}'
    stored_code = cache.get(cache_key)
    
    if stored_code and stored_code == provided_code:
        # Invalidar código após uso
        cache.delete(cache_key)
        return True
    
    return False
```

**Explicação:**
- `secrets.choice()`: Geração criptograficamente segura
- Exclusão de caracteres ambíguos para melhor UX
- Cache Redis com TTL automático
- Invalidação após uso único (segurança)

#### **Envio de Emails com Templates**
```python
# natour/api/views/code.py
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django_ratelimit.decorators import ratelimit

@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', block=True)
def send_verification_code(request):
    """
    Envio de código de verificação com rate limiting
    """
    email = request.data.get('email')
    
    if not email:
        return Response(
            {"detail": "Email é obrigatório."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Gerar código
    code = create_code()
    
    # Armazenar no cache
    store_verification_code(email, code, ttl_minutes=10)
    
    # Renderizar template HTML
    html_content = render_to_string(
        'email_templates/validation_code.html',
        {
            'code': code,
            'expiration_time': '10 minutos',
            'email': email
        }
    )
    
    try:
        # Criar email multipart (texto + HTML)
        msg = EmailMultiAlternatives(
            subject="Natour - Código de Verificação",
            body=f"Seu código de verificação é: {code}",
            from_email="natourproject@gmail.com",
            to=[email]
        )
        
        # Anexar versão HTML
        msg.attach_alternative(html_content, "text/html")
        
        # Enviar
        msg.send()
        
        return Response(
            {"detail": "Código enviado com sucesso."},
            status=status.HTTP_200_OK
        )
        
    except SMTPException as e:
        return Response(
            {"detail": f"Erro ao enviar email: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
```

**Explicação:**
- Rate limiting para prevenir spam
- Template HTML responsivo
- Email multipart (texto + HTML)
- Tratamento específico de erros SMTP
- TTL configurável para códigos

### 🔧 Utilitários e Middleware

#### **Filtro de Logs Customizado**
```python
# natour/api/utils/filter_logs.py
import logging

class ExcludeMetricsFilter(logging.Filter):
    """
    Filtro para excluir logs de métricas do Prometheus
    Reduz ruído nos logs de aplicação
    """
    
    def filter(self, record):
        """
        Retorna False para logs que devem ser excluídos
        """
        # Excluir requisições para /metrics
        if hasattr(record, 'request') and record.request:
            path = record.request.get('PATH_INFO', '')
            if path.startswith('/metrics'):
                return False
        
        # Excluir logs de health checks
        if hasattr(record, 'msg'):
            message = str(record.msg).lower()
            if any(keyword in message for keyword in ['health', 'ping', 'metrics']):
                return False
        
        return True

# Configuração no settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'exclude_metrics': {
            '()': 'natour.api.utils.filter_logs.ExcludeMetricsFilter',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'app.log',
            'filters': ['exclude_metrics'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

**Explicação:**
- Herda de `logging.Filter` do Django
- Filtra requisições baseado no path
- Remove ruído de monitoramento dos logs
- Configuração declarativa no settings

#### **Paginação Customizada**
```python
# natour/api/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    """
    Paginação customizada com metadados extras
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """
        Resposta customizada com metadados úteis
        """
        return Response({
            'pagination': {
                'count': self.page.paginator.count,
                'page_size': self.page_size,
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            },
            'results': data
        })
```

**Explicação:**
- Estende `PageNumberPagination` padrão
- Adiciona metadados úteis para o frontend
- Page size configurável com limite máximo
- Links de navegação automáticos

## �📖 Como Usar

### Fluxo Básico de Uso

1. **Registro do Usuário**
   - Solicitar código de verificação → `POST /code/send/`
   - Verificar código → `POST /code/verify/`
   - Criar conta → `POST /users/create/`

2. **Autenticação**
   - Login → `POST /users/login/`
   - Obter token → `POST /token/`

3. **Gestão de Pontos**
   - Criar ponto → `POST /points/create/`
   - Listar pontos → `GET /points/`
   - Ver detalhes → `GET /points/{id}/`

4. **Interações**
   - Adicionar foto → `POST /points/{id}/photo/upload/`
   - Avaliar ponto → `POST /points/{id}/review/`
   - Incrementar views → `PUT /points/{id}/add_view/`

## 🧪 Exemplos de Uso da API

### 📝 **Registro de Usuário Completo**

#### 1. Solicitar Código de Verificação
```bash
curl -X POST http://localhost:8000/code/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@exemplo.com"
  }'
```

**Resposta:**
```json
{
  "detail": "Código enviado com sucesso."
}
```

#### 2. Verificar Código
```bash
curl -X POST http://localhost:8000/code/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@exemplo.com",
    "code": "ABC123"
  }'
```

**Resposta:**
```json
{
  "detail": "Código verificado com sucesso."
}
```

#### 3. Criar Conta
```bash
curl -X POST http://localhost:8000/users/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "joao_natureza",
    "email": "usuario@exemplo.com",
    "password": "senha_segura_123",
    "first_name": "João",
    "last_name": "Silva"
  }'
```

**Resposta:**
```json
{
  "id": 1,
  "username": "joao_natureza",
  "email": "usuario@exemplo.com",
  "first_name": "João",
  "last_name": "Silva",
  "role": {
    "id": 1,
    "name": "user"
  },
  "created_at": "2025-07-03T10:30:00Z"
}
```

### 🔐 **Autenticação**

#### Login
```bash
curl -X POST http://localhost:8000/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@exemplo.com",
    "password": "senha_segura_123"
  }'
```

**Resposta:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "joao_natureza",
    "email": "usuario@exemplo.com",
    "role": "user"
  }
}
```

### 📍 **Criação de Ponto Turístico**

```bash
curl -X POST http://localhost:8000/points/create/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cachoeira do Eldorado",
    "description": "Uma cachoeira deslumbrante com 50 metros de altura, localizada em meio à Mata Atlântica. Ideal para trilhas e banhos refrescantes.",
    "point_type": "water_fall",
    "latitude": -22.9068,
    "longitude": -43.1729,
    "zip_code": "25960-000",
    "city": "Teresópolis",
    "neighborhood": "Alto",
    "state": "Rio de Janeiro",
    "street": "Estrada do Eldorado",
    "number": "Km 15",
    "week_start": "2025-01-01",
    "week_end": "2025-12-31",
    "open_time": "08:00:00",
    "close_time": "17:00:00",
    "link": "https://www.teresopolis.rj.gov.br/turismo"
  }'
```

**Resposta:**
```json
{
  "id": 1,
  "name": "Cachoeira do Eldorado",
  "description": "Uma cachoeira deslumbrante...",
  "point_type": "water_fall",
  "status": null,
  "is_active": false,
  "views": 0,
  "avg_rating": 0,
  "user": {
    "id": 1,
    "username": "joao_natureza"
  },
  "latitude": -22.9068,
  "longitude": -43.1729,
  "created_at": "2025-07-03T11:00:00Z",
  "updated_at": "2025-07-03T11:00:00Z"
}
```

### 📸 **Upload de Foto**

```bash
curl -X POST http://localhost:8000/points/1/photo/upload/ \
  -H "Authorization: Bearer {access_token}" \
  -F "image=@cachoeira.jpg"
```

**Resposta:**
```json
{
  "id": 1,
  "image": "https://res.cloudinary.com/natour/image/upload/v1625304600/natour/photos/cachoeira_abc123.jpg",
  "public_id": "natour/photos/cachoeira_abc123",
  "point": 1,
  "created_at": "2025-07-03T11:15:00Z"
}
```

### ⭐ **Adicionar Avaliação**

```bash
curl -X POST http://localhost:8000/points/1/review/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "comment": "Lugar incrível! A cachoeira é maravilhosa e a trilha é bem sinalizada. Recomendo muito!"
  }'
```

**Resposta:**
```json
{
  "id": 1,
  "rating": 5,
  "comment": "Lugar incrível! A cachoeira é maravilhosa...",
  "user": {
    "id": 1,
    "username": "joao_natureza"
  },
  "point": {
    "id": 1,
    "name": "Cachoeira do Eldorado",
    "avg_rating": 5.0
  },
  "created_at": "2025-07-03T12:00:00Z"
}
```

### 🗺️ **Buscar Pontos para Mapa**

```bash
curl -X GET "http://localhost:8000/points/map/" \
  -H "Authorization: Bearer {access_token}"
```

**Resposta:**
```json
{
  "points": [
    {
      "id": 1,
      "name": "Cachoeira do Eldorado",
      "point_type": "water_fall",
      "latitude": -22.9068,
      "longitude": -43.1729,
      "avg_rating": 5.0,
      "views": 15,
      "city": "Teresópolis",
      "state": "Rio de Janeiro"
    }
  ]
}
```

## 🌐 Endpoints da API

### 🔐 Autenticação
```http
POST /token/                    # Obter token JWT
POST /token/refresh/            # Renovar token
POST /users/login/              # Login de usuário
POST /users/create/             # Criar conta
```

### 👤 Usuários
```http
GET    /users/me/               # Meus dados
PUT    /users/me/update/        # Atualizar perfil
DELETE /users/me/delete/        # Deletar minha conta
GET    /users/list/             # Listar usuários (admin)
PUT    /users/{id}/status/      # Alterar status (admin)
GET    /users/me/points/        # Meus pontos
```

### 📍 Pontos
```http
POST   /points/create/          # Criar ponto
GET    /points/{id}/            # Detalhes do ponto
GET    /points/                 # Listar todos (admin)
PUT    /points/{id}/status/     # Alterar status
DELETE /points/{id}/delete/     # Deletar ponto (admin)
PUT    /points/{id}/edit/       # Editar ponto
GET    /points/map/             # Pontos para mapa
PUT    /points/{id}/approve/    # Aprovar ponto (admin)
PUT    /points/{id}/add_view/   # Incrementar visualização
```

### 📸 Fotos
```http
POST   /users/{id}/photo/upload/     # Upload foto usuário
POST   /points/{id}/photo/upload/    # Upload foto ponto
PUT    /users/{id}/photo/update/{photo_id}/  # Atualizar foto
GET    /photos/                      # Listar fotos
DELETE /photos/delete/               # Deletar foto
```

### ⭐ Avaliações
```http
POST   /points/{id}/review/     # Adicionar avaliação
```

### 📧 Verificação
```http
POST   /code/send/              # Enviar código
POST   /code/verify/            # Verificar código
```

### 📋 Termos
```http
POST   /terms/create/           # Criar termos (admin)
GET    /terms/{id}/             # Ver termos
PUT    /terms/{id}/update/      # Atualizar termos (admin)
```

### 📊 Monitoramento
```http
GET    /metrics                # Métricas Prometheus
```

## 🔧 Configurações Avançadas

### Autenticação JWT
- **Access Token**: 75 minutos
- **Refresh Token**: 90 dias
- **Rotação automática**: Habilitada

### Rate Limiting
- **Login**: 5 tentativas por minuto por IP
- **Código verificação**: 5 envios por minuto por IP

### Cache
- Cache de 60 segundos em endpoints de listagem
- Varia por cabeçalho de autorização

### Permissões
- **IsAuthenticated**: Usuários autenticados
- **IsAdminUser**: Apenas administradores
- **AllowAny**: Acesso público

## 📊 Monitoramento

### Métricas Disponíveis
- **Requisições HTTP**: Contadores e latência
- **Usuários**: Registros, logins, status
- **Pontos**: Criações, aprovações, visualizações
- **Sistema**: CPU, memória, disco

### Logs Estruturados
- **Aplicação**: `/app.log`
- **Acesso**: Logs de requisições HTTP
- **Erros**: Stack traces e exceções

### Alertas Configuráveis
- Alta latência de resposta
- Taxa de erro elevada
- Falhas de autenticação
- Recursos do sistema

## 🚦 Status do Projeto

- ✅ **Core APIs**: Implementadas e testadas
- ✅ **Autenticação**: JWT com refresh tokens
- ✅ **Upload de Arquivos**: Integração Cloudinary
- ✅ **Email**: Templates e envio automático
- ✅ **Monitoramento**: Stack completo
- 🔄 **Testes**: Em desenvolvimento
- 🔄 **Documentação API**: Swagger/OpenAPI