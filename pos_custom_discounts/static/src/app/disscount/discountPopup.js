/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */

import { usePos } from "@point_of_sale/app/hooks/pos_hook";
import { useState, onMounted, Component } from "@odoo/owl";
import { NumberPopup } from "@point_of_sale/app/components/popups/number_popup/number_popup";
import { _t } from "@web/core/l10n/translation";
import { WkCustomDiscountPopup } from "@pos_custom_discounts/app/disscount/CoustomDiscountPoupop";
import { Dialog } from "@web/core/dialog/dialog";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";


function getLineBaseAmount(orderline) {
    const unitPrice = parseFloat(orderline.price_unit || 0);
    const quantity = parseFloat(orderline.qty || 0);

    return unitPrice * quantity;
}

function getCappedDiscountPercentage(
    amount,
    discountPercentage,
    discountCap
) {
    if (!amount || amount <= 0) {
        return 0;
    }

    const normalDiscount =
        amount * discountPercentage / 100;

    // No cap
    if (!discountCap || discountCap <= 0) {
        return discountPercentage;
    }

    // Normal discount is within cap
    if (normalDiscount <= discountCap) {
        return discountPercentage;
    }

    // Cap exceeded -> calculate equivalent %
    return (discountCap / amount) * 100;
}

export class WkDiscountPopup extends Component {
    static template = "WkDiscountPopup";
    static components = { Dialog };

    setup() {
        super.setup();
        this.pos = usePos();
        this.state = useState({ value: this.props.value });
        onMounted(this.onMounted);
    }
    // onMounted() {
    //     var wk_discount_list = this.pos.all_discounts;
    //     this.wk_discount_percentage = 0;
    //     this.selected_discount = false;
    //     $(".button.apply").show();
    //     $(".button.apply_complete_order").show();
    //     $("#discount_error").hide();
    //     if (wk_discount_list && !wk_discount_list.length) {
    //         $(".button.apply_complete_order").hide();
    //         $(".button.apply").hide();
    //     }
    //     if (this.props.selected_list_discount) {
    //         $(".wk_popup_body span.discount_percent[id=" + this.props.selected_list_discount.id + "]").click()
    //     }
    // }
    onMounted() {
        var wk_discount_list = this.pos.all_discounts;

        this.wk_discount_percentage = 0;
        this.selected_discount = false;

        $(".button.apply").show();
        $(".button.apply_complete_order").show();
        $("#discount_error").hide();

        if (wk_discount_list && !wk_discount_list.length) {
            $(".button.apply_complete_order").hide();
            $(".button.apply").hide();
        }

        // Existing selected discount ko sirf select/highlight karo.
        // CLICK mat karo, warna fixed discount confirmation dobara aa jayegi.
        if (this.props.selected_list_discount) {

            const selectedId =
                this.props.selected_list_discount.id;

            for (let i = 0; i < wk_discount_list.length; i++) {

                if (wk_discount_list[i].id == selectedId) {

                    this.selected_discount =
                        wk_discount_list[i];

                    this.wk_discount_percentage =
                        wk_discount_list[i].discount_percent;

                    const discountButton =
                        $(".wk_product_discount[id=" + selectedId + "]");

                    discountButton.css(
                        "background",
                        "#6EC89B"
                    );

                    break;
                }
            }
        }
    }


    async wk_ask_password(password) {
        var self = this;
        var ret = new $.Deferred();
        if (password) {
            await this.pos.dialog.add(NumberPopup, {
                title: _t("Password?"),
                startingValue: undefined,
                getPayload: async  (num) => {
                    if (password !== Sha1.hash(num)) {
                        this.pos.dialog.add(AlertDialog, {
                            title: _t("Incorrect Password"),
                            body: _t(
                                "Please try again."
                            ),
                        });
                        return false;
                    }
                    await self.pos.dialog.add(WkCustomDiscountPopup);
                },
            });
        } else {
            ret.resolve();
        }
        return ret;
    }
    async click_customize() {
        var self = this;
        let employee = self.pos.getCashier();
        if (self.pos.config.allow_security_pin && employee && employee._pin) {
                self.props.close();
                await self.wk_ask_password(employee._pin);
        }
        else {
            self.props.close();
            this.pos.dialog.add(WkCustomDiscountPopup);
        }

    }
    // click_wk_product_discount(event) {
    //     $("#discount_error").hide();
    //     $(".wk_product_discount").css('background', 'white');
    //     var discount_id = parseInt($(event.currentTarget).attr('id'));
    //     $(event.currentTarget).css('background', '#6EC89B');
    //     var wk_discount_list = this.pos.all_discounts;
    //     for (var i = 0; i < wk_discount_list.length; i++) {
    //         if (wk_discount_list[i].id == discount_id) {
    //             var wk_discount = wk_discount_list[i];
    //             this.wk_discount_percentage = wk_discount.discount_percent;
    //             this.selected_discount = wk_discount;
    //         }
    //     }
    // }
    click_wk_product_discount(event) {

        $("#discount_error").hide();

        // Remove previous selection color
        $(".wk_product_discount").css(
            "background",
            "white"
        );

        // Green selected discount
        $(event.currentTarget).css(
            "background",
            "#6EC89B"
        );

        const discount_id = parseInt(
            $(event.currentTarget).attr("id")
        );

        const wk_discount_list =
            this.pos.all_discounts;

        for (let i = 0; i < wk_discount_list.length; i++) {

            if (wk_discount_list[i].id == discount_id) {

                const wk_discount =
                    wk_discount_list[i];

                this.wk_discount_percentage =
                    wk_discount.discount_percent;

                this.selected_discount =
                    wk_discount;

                break;
            }
        }
    }



    // async click_remove_discount() {
    //     let order = this.pos.getOrder();
    //     let selected_orderline = order.getSelectedOrderline();
    //     selected_orderline.setDiscount(0);
    //     selected_orderline.update({'list_discount': false})
    //     selected_orderline.selected_list_discount = false;
    //     selected_orderline.update({'custom_discount_reason': ""});
    //     if (order._updateRewards) {
    //         order._updateRewards();
    //     }
    //     this.props.close();
    // }
    async click_remove_discount() {
        let order = this.pos.getOrder();
        let selected_orderline = order.getSelectedOrderline();

        selected_orderline.setDiscount(0);

        selected_orderline.update({
            'custom_discount': false,
            'custom_discount_reason': "",
            'fixed_discount_amount': 0,
            'list_discount': false,
            'selected_list_discount': false,
        });

        if (order._updateRewards) {
            order._updateRewards();
        }

        this.props.close();
    }



    // click_apply(event) {
    //     var order = this.pos.getOrder();
    //     let selected_orderline = order.getSelectedOrderline();
    //     if (this.wk_discount_percentage != 0) {
    //         selected_orderline.setDiscount(this.wk_discount_percentage);
    //         selected_orderline.update({'custom_discount_reason': this.selected_discount.name || ""});
    //         selected_orderline.update({'custom_discount': false});
    //         selected_orderline.update({'list_discount': true});
    //         selected_orderline.update({'selected_list_discount': this.selected_discount});
    //         $('ul.orderlines li.selected div#custom_discount_reason').text('');
    //
    //         if (order._updateRewards) {
    //             order._updateRewards();
    //         }
    //         this.props.close();
    //     } else {
    //         $(".wk_product_discount").css("background-color", "burlywood");
    //         setTimeout(function () {
    //             $(".wk_product_discount").css("background-color", "");
    //         }, 100);
    //         setTimeout(function () {
    //             $(".wk_product_discount").css("background-color", "burlywood");
    //         }, 200);
    //         setTimeout(function () {
    //             $(".wk_product_discount").css("background-color", "");
    //         }, 300);
    //         setTimeout(function () {
    //             $(".wk_product_discount").css("background-color", "burlywood");
    //         }, 400);
    //         setTimeout(function () {
    //             $(".wk_product_discount").css("background-color", "");
    //         }, 500);
    //         return;
    //     }
    // }

    async click_apply(event) {

        const order = this.pos.getOrder();

        const selected_orderline =
            order.getSelectedOrderline();

        if (!this.selected_discount) {
            $("#discount_error").show();
            return;
        }

        const discountPercentage =
            parseFloat(
                this.selected_discount.discount_percent || 0
            );

        const discountCap =
            parseFloat(
                this.selected_discount.discount_cap || 0
            );

        const lineAmount =
            getLineBaseAmount(selected_orderline);

        if (lineAmount <= 0) {
            return;
        }

        // Normal discount amount
        const normalDiscount =
            lineAmount * discountPercentage / 100;

        // ==========================================
        // NO CAP
        // ==========================================

        if (!discountCap || discountCap <= 0) {

            selected_orderline.setDiscount(
                discountPercentage
            );

            selected_orderline.update({
                custom_discount: false,
                custom_discount_reason:
                    this.selected_discount.name || "",
                list_discount: true,
                selected_list_discount:
                    this.selected_discount,

                // No cap
                fixed_discount_amount: 0,
            });

            if (order._updateRewards) {
                order._updateRewards();
            }

            this.props.close();
            return;
        }

        // ==========================================
        // CAP NOT REACHED
        // Example:
        // 4000 × 20% = 800
        // Cap = 1000
        // Actual = 800
        // ==========================================

        if (normalDiscount <= discountCap) {

            selected_orderline.setDiscount(
                discountPercentage
            );

            selected_orderline.update({
                custom_discount: false,
                custom_discount_reason:
                    this.selected_discount.name || "",
                list_discount: true,
                selected_list_discount:
                    this.selected_discount,

                // IMPORTANT:
                // Cap hit nahi hua
                fixed_discount_amount: 0,
            });

            if (order._updateRewards) {
                order._updateRewards();
            }

            this.props.close();
            return;
        }

        const confirmed = await new Promise((resolve) => {

            this.pos.dialog.add(
                ConfirmationDialog,
                {
                    title: _t("Fixed Discount"),

                    body: _t(
                        "This discount has a fixed amount of Rs. %s. Do you want to apply it?",
                        discountCap.toFixed(2)
                    ),

                    confirmLabel: _t("OK"),
                    cancelLabel: _t("Cancel"),

                    confirm: () => {
                        resolve(true);
                    },

                    cancel: () => {
                        resolve(false);
                    },
                }
            );
        });

        if (!confirmed) {
            return;
        }

        // ==========================================
        // CAP EXCEEDED
        // Example:
        // 20000 × 20% = 4000
        // Cap = 1000
        //
        // Effective % = 1000 / 20000 × 100
        //              = 5%
        // ==========================================

        const actualDiscount =
            Math.min(
                normalDiscount,
                discountCap
            );

        const effectivePercentage =
            actualDiscount /
            lineAmount *
            100;

        selected_orderline.setDiscount(
            effectivePercentage
        );

        selected_orderline.update({
            custom_discount: false,
            custom_discount_reason:
                this.selected_discount.name || "",
            list_discount: true,
            selected_list_discount:
                this.selected_discount,

            // IMPORTANT:
            // Sirf cap hit hone par value save hogi
            fixed_discount_amount: actualDiscount,
        });

        if (order._updateRewards) {
            order._updateRewards();
        }

        this.props.close();
    }





    // click_apply_complete_order(event) {
    //     var order = this.pos.getOrder();
    //     if (this.wk_discount_percentage != 0) {
    //         var orderline_ids = order.getOrderlines();
    //         for (var i = 0; i < orderline_ids.length; i++) {
    //             orderline_ids[i].update({'custom_discount': false});
    //             orderline_ids[i].update({'custom_discount_reason': this.selected_discount.name || ""});
    //             orderline_ids[i].setDiscount(this.wk_discount_percentage);
    //             orderline_ids[i].update({'list_discount': true})
    //             orderline_ids[i].update({'selected_list_discount': this.selected_discount});
    //         }
    //         if (order._updateRewards) {
    //             order._updateRewards();
    //         }
    //         this.props.close();
    //     } else {
    //         $(".wk_product_discount").css("background-color", "burlywood");
    //         setTimeout(function () {
    //             $(".wk_product_discount").css("background-color", "");
    //         }, 100);
    //         setTimeout(function () {
    //             $(".wk_product_discount").css("background-color", "burlywood");
    //         }, 200);
    //         setTimeout(function () {
    //             $(".wk_product_discount").css("background-color", "");
    //         }, 300);
    //         setTimeout(function () {
    //             $(".wk_product_discount").css("background-color", "burlywood");
    //         }, 400);
    //         setTimeout(function () {
    //             $(".wk_product_discount").css("background-color", "");
    //         }, 500);
    //         return;
    //     }
    // }

    async click_apply_complete_order(event) {

        const order = this.pos.getOrder();

        if (!this.selected_discount) {
            $("#discount_error").show();
            return;
        }

        const orderline_ids =
            order.getOrderlines();

        const discountPercentage =
            parseFloat(
                this.selected_discount.discount_percent || 0
            );

        const discountCap =
            parseFloat(
                this.selected_discount.discount_cap || 0
            );

        // ==========================================
        // NO CAP
        // NORMAL PERCENTAGE DISCOUNT
        // ==========================================

        if (!discountCap || discountCap <= 0) {

            for (let i = 0; i < orderline_ids.length; i++) {

                const line =
                    orderline_ids[i];

                line.setDiscount(
                    discountPercentage
                );

                line.update({
                    custom_discount: false,

                    custom_discount_reason:
                        this.selected_discount.name || "",

                    list_discount: true,

                    selected_list_discount:
                        this.selected_discount,

                    fixed_discount_amount: 0,
                });
            }

            if (order._updateRewards) {
                order._updateRewards();
            }

            this.props.close();

            return;
        }

        // ==========================================
        // TOTAL ORDER AMOUNT
        // ==========================================

        let totalOrderAmount = 0;

        for (let i = 0; i < orderline_ids.length; i++) {

            totalOrderAmount +=
                getLineBaseAmount(
                    orderline_ids[i]
                );
        }

        if (totalOrderAmount <= 0) {
            return;
        }

        // ==========================================
        // NORMAL TOTAL DISCOUNT
        // ==========================================

        const normalTotalDiscount =
            totalOrderAmount *
            discountPercentage /
            100;

        // ==========================================
        // CAP NOT REACHED
        //
        // Example:
        // Order = 4000
        // 20% = 800
        // Cap = 1000
        //
        // Keep 20%
        // Do NOT show Capped Amount
        // ==========================================

        if (normalTotalDiscount <= discountCap) {

            for (let i = 0; i < orderline_ids.length; i++) {

                const line =
                    orderline_ids[i];

                line.setDiscount(
                    discountPercentage
                );

                line.update({
                    custom_discount: false,

                    custom_discount_reason:
                        this.selected_discount.name || "",

                    list_discount: true,

                    selected_list_discount:
                        this.selected_discount,

                    // IMPORTANT:
                    // Cap hit nahi hua
                    fixed_discount_amount: 0,
                });
            }

            if (order._updateRewards) {
                order._updateRewards();
            }

            this.props.close();

            return;
        }



        // ==========================================
        // CAP EXCEEDED
        // CONFIRMATION
        // ==========================================

        const confirmed = await new Promise((resolve) => {

            this.pos.dialog.add(
                ConfirmationDialog,
                {
                    title: _t("Fixed Discount"),

                    body: _t(
                        "This discount has a fixed amount of Rs. %s. Do you want to apply it?",
                        discountCap.toFixed(2)
                    ),

                    confirmLabel: _t("OK"),
                    cancelLabel: _t("Cancel"),

                    confirm: () => {
                        resolve(true);
                    },

                    cancel: () => {
                        resolve(false);
                    },
                }
            );
        });

        if (!confirmed) {
            return;
        }


        // ==========================================
        // CAP EXCEEDED
        //
        // Example:
        // Order = 25000
        // 20% = 5000
        // Cap = 1000
        //
        // Effective % = 4%
        //
        // Line 1 = 800
        // Line 2 = 200
        // Total = 1000
        // ==========================================

        const actualTotalDiscount =
            Math.min(
                normalTotalDiscount,
                discountCap
            );

        const effectivePercentage =
            actualTotalDiscount /
            totalOrderAmount *
            100;

        for (let i = 0; i < orderline_ids.length; i++) {

            const line =
                orderline_ids[i];

            const lineAmount =
                getLineBaseAmount(line);

            const lineDiscount =
                lineAmount *
                effectivePercentage /
                100;

            line.setDiscount(
                effectivePercentage
            );

            line.update({
                custom_discount: false,

                custom_discount_reason:
                    this.selected_discount.name || "",

                list_discount: true,

                selected_list_discount:
                    this.selected_discount,

                // IMPORTANT:
                // Sirf yahan cap actually hit hua hai
                fixed_discount_amount:
                    lineDiscount,
            });
        }

        if (order._updateRewards) {
            order._updateRewards();
        }

        this.props.close();
    }




    cancel() {
        this.props.close();
    }

}

