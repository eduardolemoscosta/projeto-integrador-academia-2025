# Fitcrol

**Sistema Integrado de Gestão de Academias**

O **Fitcrol** é uma solução completa para modernizar o gerenciamento de academias. O sistema centraliza a gestão de treinos, matrículas e avaliações físicas, oferecendo uma experiência fluida tanto para administradores quanto para alunos.

---

## Principais Funcionalidades

### Segurança e Performance
* **Proteção Avançada:** Validações robustas de senha e suporte seguro a variáveis de ambiente (`SECRET_KEY`, `DEBUG`).
* **Alta Performance:** Consultas otimizadas (`select_related`) reduzindo drasticamente o acesso ao banco de dados.
* **Consistência de Dados:** Validações rigorosas para IMC, datas de tarefas e cargas de exercícios.

### Interface e UX (Design Moderno)
O sistema foi projetado com foco na experiência do usuário, utilizando **Glassmorphism** e **Transições Suaves**.
* **Visual:** Paleta de cores moderna (Indigo/Roxo), sombras em camadas e tipografia *Inter*.
* **Interatividade:** Feedback visual imediato, animações CSS puras e estados de carregamento.
* **Responsividade:** Layout totalmente adaptável para mobile, tablet e desktop.

---

## Tecnologias Utilizadas

* **Backend:** Python 3.8+, Django 5.2.7
* **Frontend:** Bootstrap 5, CSS3 Avançado (Animations, Backdrop-filter)
* **Forms:** Django Crispy Forms
* **Banco de Dados:** SQLite (Dev) / Configurável para produção
