export interface Project {
    id: string;
    name: string;
    organization_name: string;
    organization_eori: string;
    commodity_code: string;
    destination_market: string;
    status: 'CREATED' | 'UPLOADED' | 'PROCESSING' | 'COMPLIANT' | 'NON_COMPLIANT' | 'ERROR';
    has_geometry: boolean;
    created_at: string;
    updated_at?: string;
}

export interface ProjectListResponse {
    projects: Project[];
    total: number;
}

export interface DeforestationResult {
    is_deforestation_free: boolean;
    alerts_count: number;
    total_loss_ha_post_cutoff: number;
    analysis_period_start: string;
    analysis_period_end: string;
}

export interface WaterResult {
    risk_level: string;
    risk_score: number;
    in_veda_zone: boolean;
    aquifer_name?: string;
}

export interface ClimateResult {
    avg_annual_precipitation_mm: number;
    avg_temperature_celsius: number;
    precipitation_suitable: boolean;
}

export interface CarbonResult {
    estimated_co2e_tonnes: number;
    calculation_applicable: boolean;
    reason: string;
}

export interface AnalysisResultResponse {
    project_id: string;
    status: 'COMPLIANT' | 'NON_COMPLIANT' | 'ERROR';
    compliance_summary: string;
    area_hectares: number;
    geometry_valid: boolean;
    deforestation: DeforestationResult;
    water: WaterResult;
    climate: ClimateResult;
    carbon: CarbonResult;
    analyzed_at: string;
}

export interface ProjectCreateRequest {
    name: string;
    organization_name: string;
    organization_eori: string;
    commodity_code?: string;
    destination_market?: string;
}

export interface EUDRReportResponse {
    submission_type: string;
    version: string;
    header: {
        reference_number: string;
        operator: {
            name: string;
            eori: string;
            address: string;
        };
        destination_market: string;
    };
    commodity: {
        hs_code: string;
        scientific_name: string;
        trade_name: string;
        quantity: {
            amount: number;
            unit: string;
        };
    };
    geolocation: Record<string, unknown>;
    compliance: {
        deforestation_free_post_2020: boolean;
        relevant_legislation_check: boolean;
        audit_metadata: {
            engine: string;
            verification_timestamp: string;
            water_risk_assessment: string;
            water_risk_score: number;
            area_hectares: number;
            deforestation_alerts: number;
            carbon_footprint_tonnes: number;
        };
    };
    greenpass_reference: string;
    generated_at: string;
}
