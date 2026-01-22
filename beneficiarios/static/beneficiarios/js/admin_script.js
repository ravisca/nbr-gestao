document.addEventListener('DOMContentLoaded', function() {
    const $ = django.jQuery; // Garante uso do jQuery do Django

    const phoneInput = document.getElementById('id_telefone');
    const dateInput = document.getElementById('id_data_nascimento');

    // 1. MÁSCARA DE TELEFONE (Mantida)
    if(phoneInput){
        phoneInput.addEventListener('input', function (e) {
            let x = e.target.value.replace(/\D/g, '').match(/(\d{0,2})(\d{0,5})(\d{0,4})/);
            e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
        });
    }

    // 2. MÁSCARA DE DATA (NOVO: Adiciona as barras / enquanto digita)
    if(dateInput){
        dateInput.addEventListener('input', function(e) {
            let v = e.target.value.replace(/\D/g, ''); // Remove tudo que não é número
            
            // Limita a 8 dígitos (DDMMAAAA)
            if (v.length > 8) v = v.substring(0, 8);

            // Adiciona a primeira barra após o dia
            if (v.length > 2) {
                v = v.replace(/^(\d{2})(\d)/, '$1/$2');
            }
            // Adiciona a segunda barra após o mês
            if (v.length > 5) {
                v = v.replace(/^(\d{2})\/(\d{2})(\d)/, '$1/$2/$3');
            }
            
            e.target.value = v;
        });
    }

    // 3. Lógica de Saúde e Acessibilidade (Mostrar/Esconder)
    function toggleField(checkboxId, fieldRowClass) {
        const checkbox = document.getElementById(checkboxId);
        // Tenta achar a linha pelo nome do campo de texto
        let fieldRow = $('.field-' + fieldRowClass).closest('.form-row');
        
        // Fallback: Se não achar, tenta achar pelo ID do input
        if (fieldRow.length === 0) {
             fieldRow = $('#id_' + fieldRowClass).closest('.form-row');
        }

        function updateVisibility() {
            if (checkbox.checked) {
                fieldRow.show();
            } else {
                fieldRow.hide();
                // Limpa o campo de texto se desmarcar
                $('#id_' + fieldRowClass).val('');
            }
        }
        
        if (checkbox) {
            checkbox.addEventListener('change', updateVisibility);
            updateVisibility(); // Executa ao carregar a página
        }
    }

    toggleField('id_tem_problema_saude', 'descricao_saude');
    toggleField('id_necessita_acessibilidade', 'descricao_acessibilidade');

    // 4. Lógica do Responsável (Menor de 18 anos)
    function checkAge() {
        // Pega o valor atual do campo
        const dobValue = dateInput.value;
        // Pega o grupo (fieldset) do Responsável (procura pela classe que definimos no admin.py)
        const responsavelGroup = $('.responsavel-group'); 

        if (dobValue && dobValue.length === 10) { // Só calcula se tiver a data completa (10 chars)
            const parts = dobValue.split('/');
            if (parts.length === 3) {
                // Cria data no formato JS (Ano, Mês-1, Dia)
                const dob = new Date(parts[2], parts[1] - 1, parts[0]);
                const diff_ms = Date.now() - dob.getTime();
                const age_dt = new Date(diff_ms); 
                const age = Math.abs(age_dt.getUTCFullYear() - 1970);

                if (age < 18) {
                    responsavelGroup.show();
                } else {
                    responsavelGroup.hide();
                    // Opcional: Limpar campos do responsável se virar maior de idade
                    $('#id_responsavel').val('');
                    $('#id_grau_parentesco').val('');
                }
            }
        } else {
            // Se a data for apagada ou inválida, esconde por segurança (ou mostra, dependendo da regra)
            // Aqui vou deixar escondido até ter uma data válida de menor
            responsavelGroup.hide();
        }
    }

    if (dateInput) {
        dateInput.addEventListener('keyup', checkAge); // Verifica a cada digito (para ser ágil)
        dateInput.addEventListener('change', checkAge); // Verifica ao sair do campo
        
        // Executa ao carregar a página (para edições de cadastro)
        setTimeout(checkAge, 500); 
    }
});