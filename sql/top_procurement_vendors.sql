SELECT
    vendor_formal_name,
    naics_sector,
    procurement_contract_count,
    total_procurement_value,
    procurement_activity_score
FROM mwbe_vendor_intelligence_enriched
WHERE has_procurement_award = 1
ORDER BY total_procurement_value DESC
LIMIT 25;