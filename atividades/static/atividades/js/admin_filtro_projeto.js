document.addEventListener('DOMContentLoaded', function() {
    // Função para aguardar o jQuery do Django
    function initFiltro() {
        const $ = django.jQuery;
        const fieldProjeto = $('#id_projeto');
        const fieldAtividade = $('#id_tipo_atividade');

        if (!fieldProjeto.length || !fieldAtividade.length) {
            return; 
        }

        // 1. CLONAR: Guarda todas as opções originais na memória
        const todasOpcoes = fieldAtividade.find('option').clone();

        // 2. LEMBRAR: Captura qual ID veio salvo do banco de dados (Fundamental para a edição!)
        const valorInicialBanco = fieldAtividade.val();

        function filtrarAtividades(manterValorSalvo = false) {
            const projetoNome = fieldProjeto.find('option:selected').text().trim();
            const projetoId = fieldProjeto.val();
            
            // Se não for para manter o valor do banco (ex: usuário trocou de projeto manualmente),
            // tentamos manter o que o usuário clicou por último, ou limpa.
            let valorParaSelecionar = manterValorSalvo ? valorInicialBanco : fieldAtividade.val();

            // Limpa o select visualmente
            fieldAtividade.empty();

            if (!projetoId) {
                // Se não tem projeto, mostra só o traço "---------"
                fieldAtividade.append(todasOpcoes.filter(function() {
                    return !$(this).val(); 
                }));
            } else {
                // Reconstrói a lista filtrada
                todasOpcoes.each(function() {
                    const textoOpcao = $(this).text();
                    const valorOpcao = $(this).val();

                    // Sempre adiciona a opção vazia "---------"
                    if (!valorOpcao) {
                        fieldAtividade.append($(this));
                        return;
                    }

                    // Verifica se a opção pertence ao projeto selecionado
                    // Procura pelo padrão "Nome do Projeto | "
                    const prefixo = projetoNome + " | ";
                    
                    if (textoOpcao.indexOf(prefixo) === 0) {
                        fieldAtividade.append($(this));
                    }
                });
            }

            // 3. RESTAURAR: Se o valor antigo ainda existir na nova lista filtrada, seleciona ele de volta.
            if (valorParaSelecionar && fieldAtividade.find('option[value="' + valorParaSelecionar + '"]').length > 0) {
                fieldAtividade.val(valorParaSelecionar);
            } else {
                // Se o valor antigo não faz sentido para o novo projeto, reseta para vazio
                fieldAtividade.val('');
            }
        }

        // EVENTO: Quando o usuário muda o projeto manualmente
        fieldProjeto.change(function() {
            // Passamos false, pois se mudou o projeto, o valor antigo da atividade não serve mais
            filtrarAtividades(false); 
        });

        // INICIALIZAÇÃO: Ao carregar a página
        // Passamos true para forçar ele a selecionar o valor que veio do banco de dados
        filtrarAtividades(true);
    }

    // Pequeno delay para garantir que o Django Admin carregou tudo
    setTimeout(initFiltro, 100);
});