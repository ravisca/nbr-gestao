/**
 * Quick Add Functionality
 * Usage:
 * <a href="#" class="quick-add-btn" data-url="/path/to/create/" data-target="#id_field_name">
 *    <i class="bi bi-plus-lg"></i>
 * </a>
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Create Modal HTML dynamically if it doesn't exist
    if (!document.getElementById('quickAddModal')) {
        const modalHtml = `
            <div class="modal fade" id="quickAddModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Adicionar Novo</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <!-- Form content loads here -->
                            <div class="text-center"><div class="spinner-border text-primary" role="status"></div></div>
                        </div>
                    </div>
                </div>
            </div>`;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    const modalElement = document.getElementById('quickAddModal');
    const modal = new bootstrap.Modal(modalElement);
    let currentTargetSelectId = null;

    // 2. Delegate click event for .quick-add-btn
    document.body.addEventListener('click', function (e) {
        const btn = e.target.closest('.quick-add-btn');
        if (!btn) return;

        e.preventDefault();
        const url = btn.dataset.url;
        currentTargetSelectId = btn.dataset.target;

        // Load content
        fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(response => response.text())
            .then(html => {
                modalElement.querySelector('.modal-body').innerHTML = html;
                modal.show();

                // Bind form submission within modal
                const form = modalElement.querySelector('form');
                if (form) {
                    form.addEventListener('submit', function (ev) {
                        ev.preventDefault();
                        const formData = new FormData(form);

                        fetch(url, {
                            method: 'POST',
                            body: formData,
                            headers: { 'X-Requested-With': 'XMLHttpRequest' }
                        })
                            .then(resp => resp.json())
                            .then(data => {
                                if (data.success) {
                                    // Close modal
                                    modal.hide();

                                    // Update Select
                                    const select = document.querySelector(currentTargetSelectId);
                                    if (select) {
                                        const option = new Option(data.name, data.id, true, true);
                                        select.add(option);

                                        // Trigger change for Select2 (jQuery) and native listeners
                                        if (window.jQuery) {
                                            window.jQuery(select).trigger('change');
                                        } else {
                                            select.dispatchEvent(new Event('change'));
                                        }
                                    }
                                } else {
                                    // Show errors (simple replace of body for now)
                                    // Ideally rework to just show form errors
                                    modalElement.querySelector('.modal-body').innerHTML = data.form_html || 'Erro ao salvar.';
                                }
                            })
                            .catch(err => console.error('Error submitting form:', err));
                    });
                }
            })
            .catch(err => console.error('Error loading modal:', err));
    });
});
