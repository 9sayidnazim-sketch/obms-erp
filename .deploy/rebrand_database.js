const { Client } = require('pg');

const useSsl = process.env.DB_SSL_MODE === 'true' || (process.env.DB_HOST && process.env.DB_HOST.includes('amazonaws.com'));
const client = new Client({
  host: process.env.DB_HOST || 'gauzy-db.chmeo2uym5py.ap-south-1.rds.amazonaws.com',
  port: parseInt(process.env.DB_PORT || '5432', 10),
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASS || 'GauzySecurePass2026',
  database: process.env.DB_NAME || 'gauzy',
  ssl: useSsl ? { rejectUnauthorized: false } : false
});

async function run() {
  console.log('[REBRAND DB] Connecting to PostgreSQL database...');
  await client.connect();
  console.log('[REBRAND DB] Connected successfully.');

  // 1. Update Tenant Name
  const tenantRes = await client.query(`
    UPDATE tenant 
    SET name = 'Octapus System'
    RETURNING id, name
  `);
  console.log(`[REBRAND DB] Updated ${tenantRes.rowCount} tenant rows:`, tenantRes.rows);

  // 2. Update Organization Names and Currency
  const orgRes = await client.query(`
    UPDATE organization 
    SET name = CASE 
          WHEN name ILIKE '%Ever Co%' THEN 'OBMS ERP - Octapus System'
          WHEN name ILIKE '%Ever Tech%' THEN 'OBMS ERP Technologies - Octapus System'
          ELSE name 
        END,
        currency = 'AED',
        "currencyPosition" = 'LEFT'
    RETURNING id, name, currency
  `);
  console.log(`[REBRAND DB] Updated ${orgRes.rowCount} organization rows.`);

  // 3. Update Currencies across all financial tables
  const updates = [
    { table: 'income', col: 'currency' },
    { table: 'expense', col: 'currency' },
    { table: 'invoice', col: 'currency' },
    { table: 'payment', col: 'currency' },
    { table: 'employee', col: 'billRateCurrency' },
    { table: 'candidate', col: 'billRateCurrency' },
    { table: 'organization_project', col: 'currency' },
    { table: 'equipment', col: 'currency' },
    { table: 'merchant', col: 'currency' },
    { table: 'payroll_run', col: 'currency' },
    { table: 'employee_recurring_expense', col: 'currency' },
    { table: 'organization_recurring_expense', col: 'currency' },
    { table: 'product_variant_price', col: 'unitCostCurrency' },
    { table: 'product_variant_price', col: 'retailPriceCurrency' },
    { table: 'plugin_subscription_plans', col: 'currency' },
    { table: 'plugin_billings', col: 'currency' }
  ];

  for (const { table, col } of updates) {
    try {
      const res = await client.query(`UPDATE "${table}" SET "${col}" = 'AED' WHERE "${col}" IS NOT NULL`);
      console.log(`[REBRAND DB] Updated ${table}.${col} to AED: ${res.rowCount} rows`);
    } catch (err) {
      console.warn(`[REBRAND DB] Could not update ${table}.${col}: ${err.message}`);
    }
  }

  // 4. Update any settings/integrations referencing Gauzy / Ever
  try {
    await client.query(`
      UPDATE integration 
      SET name = REPLACE(REPLACE(name, 'Ever Gauzy', 'OBMS ERP'), 'Gauzy', 'OBMS ERP')
    `);
  } catch (e) {}

  console.log('[REBRAND DB] Verification query:');
  const orgs = await client.query('SELECT name, currency FROM organization LIMIT 5');
  console.log('Sample Organizations:', orgs.rows);
  const inc = await client.query('SELECT DISTINCT currency, count(*) FROM income GROUP BY currency');
  console.log('Income Currencies:', inc.rows);
  const exp = await client.query('SELECT DISTINCT currency, count(*) FROM expense GROUP BY currency');
  console.log('Expense Currencies:', exp.rows);

  await client.end();
  console.log('[REBRAND DB] Completed successfully!');
}

run().catch((err) => {
  console.error('[REBRAND DB ERROR]', err);
  process.exit(1);
});
