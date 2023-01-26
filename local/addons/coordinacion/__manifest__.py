# -*- coding: utf-8 -*-
{
    'name': "coordinacion",

    'summary': "Coordinación.",

    'description': """
        Long description of module's purpose
    """,

    'author': "Luciano Diamand",
    'website': "http://www.hcencasa.com.ar",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Services/Coordinacion',
    'version': '1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base','product','crm','l10n_ar','mail','sale'],

    # always loaded
    'data': [
        'security/coordinacion_security.xml',
        'security/ir.model.access.csv',
        #'data/lista_precio.xml',
        'data/nomenclador.xml',
        'data/nomenclador_costo_seq.xml',
        'data/categories.xml',
        'data/nomenclador_categories.xml',
        'data/poblacion_asistida.xml',
        'data/scheduled_jobs.xml',
        #'data/dia.xml',
        #'data/complejidad.xml',
        #'data/discapacidad.xml',
        'data/dias_semana.xml',
        'data/convenio.xml',
        'wizard/creo_servicios_views.xml',
        'wizard/actualizo_precios_views.xml',
        'wizard/actualizo_precios_valor_views.xml',
        'wizard/actualizo_costos_valor_views.xml',
        'wizard/actualizo_costos_views.xml',
        'wizard/actualizo_costos_nomenclador_valor_views.xml',
        'wizard/actualizo_costos_nomenclador_views.xml',
        'wizard/actualiza_prorroga_viatico_view.xml',
        'wizard/liquido_prestador_views.xml',
        'wizard/desasignar_agenda_views.xml',
        'wizard/asignar_agenda_views.xml',
        'wizard/recalcular_costo_agenda_views.xml',
        'views/servicio.xml',
        'views/nomenclador_costo.xml',
        'views/equipamiento.xml',
        'views/laboratorio.xml',
        #'views/material.xml',
        'views/categoria_nomenclador.xml',
        'views/modelo_pami.xml',
        'views/visitas_pami.xml',
        'views/diagnostico.xml',
        'views/coordinacion_menu.xml',
        'views/paciente.xml',
        'views/prestador.xml',
        'views/proveedor.xml',
        'views/efector.xml',
        'views/tecnico.xml',
        'views/nomenclador.xml',
        'views/plan_trabajo.xml',
        'views/plan_trabajo_line.xml',
        'views/modulado.xml',
        'views/modulado_line.xml',
        'views/agenda.xml',
        'views/sale_order_views.xml',
        'views/chatter_lateral.xml', # agregar aca para que aparezca el sheet lateral de chatter
        'views/hcd_hr_recruitment_form_extend.xml',
        'views/cliente.xml',
        'views/view_product_form_extend.xml',
        'views/view_partner_form_extend.xml',
        'views/view_partner_tree_extend.xml',
        'views/hr_expense_form_extend.xml',
        'views/hr_expense_tree_extend.xml',
        'views/excepciones_costos_prestador.xml',
        'reports/report_paciente_card.xml',
        'reports/paciente_op_pami.xml',
        'reports/report.xml',
        'reports/hr_expense_report.xml'
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'installable' : True,
}

