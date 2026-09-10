/** @odoo-module */

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    setup() {
        super.setup(...arguments);
        const defaultPartner = this.config?.default_customer;
        if (defaultPartner?.id && !this.finalized && !this.getPartner()) {
            try {
                this.setPartner(defaultPartner);
            } catch (error) {
                console.warn("Default partner could not be set:", error);
            }
        }
    },
});