/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { useService } from "@web/core/utils/hooks";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";

console.log("✅ El archivo fundacupaz_phone_form_view.js se ha cargado (v_diagnostico).");

patch(FormController.prototype, {
    /**
     * Usamos patch.instead para reemplazar la función original por completo.
     * Es una prueba de diagnóstico para ver si nuestro parche se está aplicando.
     */
    _onFieldChange: patch.instead(function (ev) {
        // La función original se pasa como primer argumento. La guardamos.
        const originalFn = arguments[0];

        // NUESTRO CÓDIGO DE PRUEBA
        console.log("💥 USANDO PATCH.INSTEAD - ¡El método _onFieldChange fue interceptado!");

        const fieldName = ev.detail.name;
        const record = this.model.root;

        if (fieldName === 'es_cuadrante') {
            console.log("🔍 Se ha detectado un cambio en 'es_cuadrante'.");

            if (!record.data.es_cuadrante && !record.isNew) {
                // Si la condición se cumple, mostramos nuestro diálogo en lugar de llamar a la función original
                const dialogService = useService("dialog");
                dialogService.add(ConfirmationDialog, {
                    title: "Confirmación",
                    body: "¿Estás seguro de que deseas desmarcar la casilla 'Es un cuadrante?'.",
                    confirm: () => {
                        record.update({ 'estado': false, 'municipio': false, 'cuadrantes': false });
                        // Después de confirmar, llamamos a la función original para que Odoo procese el cambio
                        return originalFn.call(this, ev);
                    },
                    cancel: () => {
                        record.update({ 'es_cuadrante': true });
                        // No llamamos a la función original si cancelamos
                    },
                });
            } else {
                // Si no es nuestro campo o la condición no se cumple, dejamos que Odoo siga su curso normal
                return originalFn.call(this, ev);
            }
        } else {
            // Si no es nuestro campo, dejamos que Odoo siga su curso normal
            return originalFn.call(this, ev);
        }
    }),
});