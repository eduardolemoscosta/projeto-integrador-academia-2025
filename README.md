# 🏋️‍♂️ Projeto Integrador - Sistema de Academia

## 💡 Sobre o projeto
O **Fitcrol** é um sistema desenvolvido para facilitar o **gerenciamento de academias**, oferecendo recursos tanto para **alunos** quanto para **administradores**.  
O objetivo é centralizar informações como treinos e matrículas, promovendo uma melhor experiência para os usuários.

## ✨ Melhorias Implementadas

### 🔒 Segurança
- Suporte a variáveis de ambiente para `SECRET_KEY`, `DEBUG` e `ALLOWED_HOSTS`
- Validações de senha mais robustas (similaridade, comprimento mínimo, senhas comuns, senhas numéricas)
- Configuração preparada para produção

### ✅ Validações
- Validações aprimoradas em todos os formulários:
  - **TrainingExercicioForm**: Validação de séries, repetições, carga e tempo
  - **IMCForm**: Validação de valores realistas para peso e altura, validação cruzada
  - **TaskForm**: Validação de datas e horários, verificação de consistência temporal
  - **ExercicioForm**: Validação de nome do exercício

### ⚡ Performance
- Otimização de queries com `select_related` em todas as views principais
- Redução significativa de queries ao banco de dados
- Melhor ordenação de resultados

### 📚 Documentação
- Docstrings adicionadas em todos os modelos, views e formulários
- Documentação clara de métodos e classes
- Comentários explicativos no código

### 🎯 Tratamento de Erros
- Mensagens de sucesso e erro mais informativas
- Feedback claro para o usuário em todas as operações
- Tratamento adequado de permissões e validações

### 🧹 Qualidade de Código
- Remoção de código duplicado
- Padronização de nomenclatura
- Melhor organização e estrutura do código

## 🎨 Design Moderno

O sistema foi completamente redesenhado com uma interface moderna e elegante:

### ✨ Características do Design

- **Paleta de Cores Moderna**: Gradientes vibrantes com cores indigo, roxo e rosa
- **Glassmorphism**: Efeitos de vidro fosco em cards e elementos
- **Sombras Suaves**: Sistema de sombras em camadas para profundidade
- **Tipografia Moderna**: Fonte Inter para melhor legibilidade
- **Animações Suaves**: Transições fluidas em todos os elementos
- **Bordas Arredondadas**: Sistema consistente de raios de borda
- **Gradientes Vibrantes**: Gradientes modernos em botões e elementos hero
- **Hover Effects**: Efeitos interativos ao passar o mouse
- **Scrollbar Personalizada**: Scrollbar estilizada com gradiente
- **Responsivo**: Design adaptável para todos os dispositivos

### 🎯 Elementos Redesenhados

- Cards com efeito de elevação e borda superior colorida
- Botões com gradientes e efeitos de brilho
- Formulários com bordas destacadas no foco
- Tabelas com hover suave e cabeçalhos com gradiente
- Alertas com gradientes suaves e bordas laterais
- Paginação moderna com efeitos hover
- Sidebar e topbar com animações de entrada

## 🚀 Tecnologias Utilizadas
- Django 5.2.7
- Django Crispy Forms
- Bootstrap 5
- CSS3 (Gradientes, Animations, Backdrop-filter)
- SQLite (desenvolvimento)

## 📋 Requisitos
- Python 3.8+
- Django 5.2.7
- Ver `requirements.txt` para dependências completas

## 🎨 Animações e Transições

O sistema inclui animações interativas para melhorar a experiência do usuário:

### ✨ Animações de Botões

1. **Efeito Ripple**: Ondas que se expandem a partir do ponto de clique
2. **Hover Elevado**: Botões se elevam e aumentam de tamanho ao passar o mouse
3. **Animação de Clique**: Efeito de escala ao clicar
4. **Loading State**: Indicador de carregamento durante submissão de formulários
5. **Pulso**: Animação de pulso para botões importantes
6. **Shake**: Animação de tremor para botões de exclusão
7. **Glow**: Efeito de brilho para botões principais
8. **Fade In**: Animação de entrada suave

### 🌊 Transições entre Páginas (CSS Puro)

O sistema inclui animações suaves ao carregar páginas usando apenas CSS:

1. **Fade In**: Transição suave de opacidade ao carregar
2. **Fade In Up**: Conteúdo desliza de baixo para cima
3. **Slide In**: Sidebar e topbar deslizam suavemente
4. **Animação Escalonada**: Cards e elementos aparecem em sequência com delays
5. **Transições Suaves**: Todos os elementos têm transições CSS suaves

**Todas as animações são feitas apenas com CSS, sem JavaScript!**

### 🎯 Tipos de Botões com Animações

- **btn-primary**: Efeitos de ripple, hover elevado, glow e loading
- **btn-danger**: Animação shake ao clicar, hover destacado
- **btn-success**: Hover suave e animação de clique
- **btn-secondary**: Transições suaves
- **btn-outline-primary**: Efeito de preenchimento ao hover

### 📝 Como Usar

As animações são aplicadas automaticamente. Para desabilitar transições em um link específico:

```html
<!-- Link sem transição -->
<a href="/pagina" data-no-transition>Link sem animação</a>
```

## 🔧 Configuração

### Variáveis de Ambiente (Recomendado)
Para produção, configure as seguintes variáveis de ambiente:
- `SECRET_KEY`: Chave secreta do Django
- `DEBUG`: `False` para produção
- `ALLOWED_HOSTS`: Domínios permitidos (separados por vírgula)

### Instalação
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```