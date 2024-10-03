import pyodbc
import configparser
import os
from odoo import models, fields, api
from celery import sync_products_task
import logging

_logger = logging.getLogger(__name__)

class ProductSync(models.Model):
    _name = 'product.sync'
    _description = 'Sync products from MSSQL'

    def _get_mssql_connection(self):
        """Подключение к MS SQL Server на основе параметров из конфигурационного файла."""
        config = configparser.ConfigParser()

        config_path = os.path.join(os.path.dirname(__file__), '..', 'mssql_config.conf')

        try:
            config.read(config_path)

            server = config.get('database', 'server')
            database = config.get('database', 'database')
            username = config.get('database', 'username')
            password = config.get('database', 'password')
            driver = config.get('database', 'driver')

            conn = pyodbc.connect(
                f'DRIVER={{{driver}}};'
                f'SERVER={server};'
                f'DATABASE={database};'
                f'UID={username};'
                f'PWD={password}'
            )
            return conn
        except Exception as e:
            _logger.error(f"Error reading MSSQL config or connecting to MSSQL: {e}")
            return None

    def sync_products(self):
        """
        Метод синхронизации товаров из MSSQL в Odoo (работает при настройке CDC в MSSQL)
        Команды для настройки CDC: ./CDC.sql
        """
        conn = self._get_mssql_connection()
        if not conn:
            return

        cursor = conn.cursor()

        # Запрос данных из MS SQL Server (с использованием CDC, если настроен)
        query = '''
            SELECT p.ProductID, p.ProductName, pb.Barcode
            FROM dbo.Products p
            LEFT JOIN logistics.ProductBarcodes pb ON p.ProductID = pb.ProductID
        '''
        cursor.execute(query)
        products = cursor.fetchall()

        # Обработка каждой строки данных и синхронизация с Odoo
        for product in products:
            product_id, product_name, barcode = product
            # Проверяем наличие продукта в Odoo по штрихкоду
            odoo_product = self.env['product.product'].search([('barcode', '=', barcode)], limit=1)
            if odoo_product:
                # Обновляем существующий продукт
                odoo_product.write({
                    'name': product_name,
                })
            else:
                # Создаем новый продукт
                self.env['product.product'].create({
                    'name': product_name,
                    'barcode': barcode,
                })

        cursor.close()
        conn.close()

    @api.model
    def schedule_sync(self):
        """Запуск задачи синхронизации продуктов в фоне."""
        sync_products_task.delay()
