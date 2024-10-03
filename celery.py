from celery import Celery

app = Celery('product_sync', broker='redis://redis:6379/0')

@app.task
def sync_products_task():
    from odoo import api, SUPERUSER_ID
    env = api.Environment(api.Environment.cr, SUPERUSER_ID, {})
    product_sync = env['product.sync']
    product_sync.sync_products()
