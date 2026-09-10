/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";

patch(PosOrderline, {
    extraFields: {
        ...(PosOrderline.extraFields || {}),

        selected_list_discount: {
            model: "pos.order.line",
            name: "selected_list_discount",
            relation: "pos.custom.discount",
            type: "many2one",
            local: true,
        },

        custom_discount: {
            model: "pos.order.line",
            name: "custom_discount",
            type: "boolean",
            local: true,
        },

        list_discount: {
            model: "pos.order.line",
            name: "list_discount",
            type: "boolean",
            local: true,
        },

        fixed_discount_amount: {
            model: "pos.order.line",
            name: "fixed_discount_amount",
            type: "float",
            local: true,
        },
    }
});

patch(PosOrderline.prototype, {
    setup(vals) {
        super.setup(...arguments);

        this.custom_discount = this.custom_discount || false;
        this.custom_discount_reason = this.custom_discount_reason || "";
        this.list_discount = this.list_discount || false;
        this.selected_list_discount = this.selected_list_discount || false;
        this.discount = this.discount || 0;
        this.fixed_discount_amount = this.fixed_discount_amount || 0;
    },

    get_custom_discount_reason() {
        return this.custom_discount_reason || "";
    },

    get_fixed_discount_amount() {
        return this.fixed_discount_amount || 0;
    },

    get_discount_display() {
        return parseFloat(this.discount || 0).toFixed(2);
    },

    is_fixed_discount() {
        return (this.fixed_discount_amount || 0) > 0;
    },
});
