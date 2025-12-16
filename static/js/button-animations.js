/**
 * Script para adicionar animações interativas aos botões
 * Adiciona efeitos de ripple, loading e outras animações
 */

document.addEventListener('DOMContentLoaded', function() {
    // Adiciona animação de ripple a todos os botões
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        // Adiciona classe para animação de entrada
        button.classList.add('animate-in');
        
        // Adiciona efeito de ripple ao clicar
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
        
        // Adiciona estado de loading para formulários
        const form = button.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                if (button.type === 'submit') {
                    button.classList.add('loading');
                    const originalText = button.innerHTML;
                    button.innerHTML = '<span>' + originalText + '</span>';
                    
                    // Remove loading após 5 segundos (fallback)
                    setTimeout(() => {
                        button.classList.remove('loading');
                        button.innerHTML = originalText;
                    }, 5000);
                }
            });
        }
    });
    
    // Adiciona efeito de pulso para botões importantes
    const importantButtons = document.querySelectorAll('.btn-primary, .btn-danger');
    importantButtons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.animation = 'pulse 2s infinite';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.animation = '';
        });
    });
    
    // Adiciona animação de shake para botões de exclusão
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Adiciona shake apenas se não for submit de formulário
            if (this.type !== 'submit') {
                this.style.animation = 'shake 0.3s';
                setTimeout(() => {
                    this.style.animation = '';
                }, 300);
            }
        });
    });
    
    // Adiciona efeito de glow para botões de ação principal
    const primaryButtons = document.querySelectorAll('.btn-primary');
    primaryButtons.forEach(button => {
        if (button.classList.contains('btn-lg') || button.classList.contains('w-100')) {
            button.classList.add('glow');
        }
    });
});

// Estilo adicional para o ripple (adicionado via JavaScript)
const style = document.createElement('style');
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

