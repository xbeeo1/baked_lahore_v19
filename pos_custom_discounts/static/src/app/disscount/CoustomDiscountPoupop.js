/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { usePos } from "@point_of_sale/app/hooks/pos_hook";
import { onMounted, Component } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

export class WkCustomDiscountPopup extends Component {
    static template = "WkCustomDiscountPopup";
    static components = { Dialog };
    setup() {
        super.setup();
        this.pos = usePos();
        onMounted(this.onMounted);
    }
    onMounted() {
        if (this.props.custom_discount) {
            $("#discount").val(this.props.discount)
            $("#reason").val(this.props.custom_discount_reason)
        }
    }
    click_current_product(event) {
        if (($('#discount').val()) > 100 || $('#discount').val() <= 0) {
            $('#error_div').show();
            $('#customize_error').html('<i class="fa fa-exclamation-triangle" aria-hidden="true"></i > Discount percent must be between 0 and 100.')
        } else {
            var wk_customize_discount = parseFloat($('#discount').val())
            var reason = ($("#reason").val());
            var order = this.pos.getOrder();
            let selected_orderline = this.pos.getOrder().getSelectedOrderline();
            selected_orderline.update({'list_discount': false});
            selected_orderline.update({'selected_list_discount': false});
            selected_orderline.setDiscount(wk_customize_discount);
            selected_orderline.update({'custom_discount_reason': reason});
            selected_orderline.update({'custom_discount' :true});
            if (order._updateRewards) {
                order._updateRewards();
            }
            this.props.close();
        }
    }
    click_whole_order(event) {
        var self = this;
        var order = this.pos.getOrder();
        var orderline_ids = order.getOrderlines();
        if (($('#discount').val()) > 100 || $('#discount').val() <= 0) {
            $('#error_div').show();
            $('#customize_error').html('<i class="fa fa-exclamation-triangle" aria-hidden="true"></i > Discount percent must be between 0 and 100.')
        } else {
            var wk_customize_discount = parseFloat($('#discount').val());
            var reason = ($("#reason").val());
            for (var i = 0; i < orderline_ids.length; i++) {
                orderline_ids[i].update({'list_discount': false})
                orderline_ids[i].update({'selected_list_discount': false});
                orderline_ids[i].setDiscount(wk_customize_discount);
                orderline_ids[i].update({'custom_discount_reason': reason})
                orderline_ids[i].update({'custom_discount' :true});
            }
            if (order._updateRewards) {
                order._updateRewards();
            }
            self.props.close();
        }
    }
    async click_remove_discount() {
        let selected_orderline = this.pos.getOrder().getSelectedOrderline();
        selected_orderline.setDiscount(0);
        selected_orderline.update({'custom_discount' :false});
        selected_orderline.custom_discount_reason = '';
        if (this.pos.getOrder()._updateRewards) {
            this.pos.getOrder()._updateRewards();
        }
        this.props.close();
    }
    cancel(){
        this.props.close();
    }

}
