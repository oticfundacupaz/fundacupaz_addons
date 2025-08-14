def migrate(cr, version):
    """
    Limpia los valores incorrectos en la columna 'plan_id' antes de que Odoo
    intente convertirla a Many2one.
    """
    # Encuentra y actualiza los registros donde el valor no es un número.
    # Esto permite que la columna se convierta correctamente.
    cr.execute("UPDATE fundacupaz_phone SET plan_id = NULL WHERE plan_id LIKE '%%'")