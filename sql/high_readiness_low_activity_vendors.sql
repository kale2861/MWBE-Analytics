SELECT
    vendor_formal_name,
    naics_sector,
    borough_clean,
    operational_readiness_score,
    procurement_activity_score,
    vendor_capacity_score
FROM mwbe_vendor_intelligence_enriched
WHERE operational_readiness_score >= 0.70
AND procurement_activity_score <= 0.30
ORDER BY operational_readiness_score DESC;