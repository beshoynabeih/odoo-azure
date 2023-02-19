odoo.define('itq_azure_devops.config_registration', function (require) {
'use strict';
var publicWidget = require('web.public.widget');

publicWidget.registry.config_registration = publicWidget.Widget.extend({

     selector: '#form_config',
     events: {
        'change  #organization': '_onChangeOrganization',
        'change  #token': '_onChangeToken',
        'click  #btnSave' :'_onSubmit',
    },
    init: function (parent, options) {
        this._super.apply(this, arguments);
    },
    _onChangeOrganization: function (ev) {
        var $input = $(ev.currentTarget);
        var $token = $('#token');
        var $btn = $('#btnSave');
        if ($input.val()=="" || $token.val()=="")
        {
            this.do_warn("Error","Input Must be non Empty",false);
            $(ev.currentTarget).attr('required', true);
            $btn.attr('disabled', true);
        }
        else
        {
           $btn.attr('disabled', false);
        }
    },
    _onChangeToken: function (ev) {
        var $input = $(ev.currentTarget);
        var $btn = $('#btnSave');
        var $org = $('#organization');
        if ($input.val()=="" || $org.val()=="")
        {
            this.do_warn("Error","Input Must be non Empty",false);
            $(ev.currentTarget).attr('required', true);
            $btn.attr('disabled', true);
        }
        else
        {
           $btn.attr('disabled', false);
        }
    },
     _onSubmit: function (ev) {
        console.log("yes can");

    },

    });
});
