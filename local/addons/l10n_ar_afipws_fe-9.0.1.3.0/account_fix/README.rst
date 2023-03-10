.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============
Account Fixes
=============

#. Fix related to partner credit / debit fields and computation on multi company
#. Fix the tax computation when creating a refund invoice from an invoice.
#. Backport of ir.model.access rules of v10, moslty to allow account users (without sale or others) to manage products
#. Backport of code being editable on journals: https://github.com/odoo/odoo/commit/d0029f11ce5d4b9e9de6ceb8a1904c76915cee84 (REMOVE on v10)
#. Make readonly the journal_type related field of bank statements so that users are allow to create statement without perm to write on journals.
#. Overwrite create_bank_statement method so that users are allow to create statement without perm to write on journals.
#. Fix importantisimo haciendo readonly el campo releated company_id de account.move.line ya que si se agrega en una vista fuerza un terrible recomputo
#. Do not allow to recompute taxes on invoices that are not on draft state because tax and invoice amounts could change


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.adhoc.com.ar/

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "9.0" for example

Known issues / Roadmap
======================

* ...

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/ingadhoc/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* ADHOC SA: `Icon <http://fotos.subefotos.com/83fed853c1e15a8023b86b2b22d6145bo.png>`_.

Contributors
------------


Maintainer
----------

.. image:: http://fotos.subefotos.com/83fed853c1e15a8023b86b2b22d6145bo.png
   :alt: Odoo Community Association
   :target: https://www.adhoc.com.ar

This module is maintained by the ADHOC SA.

To contribute to this module, please visit https://www.adhoc.com.ar.
