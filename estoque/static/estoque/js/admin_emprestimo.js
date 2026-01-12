document.addEventListener('DOMContentLoaded', function() {
    const $ = django.jQuery;
    
    const campoEmprestada = $('#id_quantidade_emprestada');
    const campoDevolvida = $('#id_quantidade_devolvida');
    // Pegamos a linha inteira (row) do campo motivo para esconder ela toda
    const rowMotivo = $('.field-motivo_falta').closest('.form-row');

    function verificarDiferenca() {
        const qtdSaiu = parseInt(campoEmprestada.val()) || 0;
        const qtdVoltou = parseInt(campoDevolvida.val()); // Pode ser NaN se vazio

        // Só mostra o motivo se QtdVoltou for um número válido E for menor que QtdSaiu
        if (!isNaN(qtdVoltou) && qtdVoltou < qtdSaiu) {
            rowMotivo.slideDown(); // Mostra com animação
        } else {
            rowMotivo.hide(); // Esconde
        }
    }

    if (campoEmprestada.length && campoDevolvida.length) {
        // Monitora digitação nos dois campos
        campoEmprestada.on('input change', verificarDiferenca);
        campoDevolvida.on('input change', verificarDiferenca);
        
        // Roda ao abrir a página
        verificarDiferenca();
    }
});