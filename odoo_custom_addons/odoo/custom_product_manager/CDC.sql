EXEC sys.sp_cdc_enable_db;

EXEC sys.sp_cdc_enable_table
    @source_schema = 'dbo',
    @source_name = 'Products',
    @role_name = NULL;

EXEC sys.sp_cdc_enable_table
    @source_schema = 'logistics',
    @source_name = 'ProductBarcodes',
    @role_name = NULL;
