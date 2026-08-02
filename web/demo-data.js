/* Static fallback used when a deployment cannot invoke the optional Python API. */
window.CONTENT_AI_FALLBACK = {
  customer: "Northstar Manufacturing",
  industry: "Manufacturing and field services",
  engagement: "Sample engagement / no login",
  source_label: "Deterministic mock content API (browser fallback)",
  github_url: "https://github.com/amalfarhad/content-ai-solution-lab",
  discovery_signals: [
    {stakeholder:"VP Sales Operations",business_problem:"Contract approvals are slow because sales teams cannot find the latest template or route exceptions to the right legal owner.",current_state:"Teams use email, shared drives, and Slack handoffs with limited visibility into approval status.",desired_outcome:"Automate routing, expose approval status, and reduce manual follow-up before quarter close.",systems:["CRM","Slack","shared drive","e-signature"],compliance_needs:["approval audit trail","restricted access"]},
    {stakeholder:"Finance Operations Lead",business_problem:"Invoice packets arrive with inconsistent metadata and require manual duplicate checks.",current_state:"AP analysts copy document details into spreadsheets and chase missing vendor context.",desired_outcome:"Classify invoices, enrich metadata, and create a governed workflow for validation.",systems:["ERP","email","shared drive"],compliance_needs:["retention policy","payment approval trail"]},
    {stakeholder:"IT Business Partner",business_problem:"Business leaders want AI search and summaries but need confidence that sensitive content remains governed.",current_state:"Content permissions and lifecycle stages are hard to explain during stakeholder reviews.",desired_outcome:"Demonstrate AI-assisted search, summaries, and workflow recommendations with visible governance controls.",systems:["identity provider","content repository","BI dashboard"],compliance_needs:["least privilege","audit logging","data retention"]}
  ],
  themes: {governance:7, automation:5, approval:5, ai:4, search:3, analytics:3},
  requirements: [
    {id:"route",label:"Route work to the right owner",evidence:"Automate routing, expose approval status, and reduce manual follow-up before quarter close.",status:"observed"},
    {id:"govern",label:"Keep sensitive content governed",evidence:"Demonstrate AI-assisted search, summaries, and workflow recommendations with visible governance controls.",status:"observed"},
    {id:"enrich",label:"Enrich metadata before handoff",evidence:"Classify invoices, enrich metadata, and create a governed workflow for validation.",status:"observed"},
    {id:"explain",label:"Make every AI decision reviewable",evidence:"Confidence, policy flags, rationale, and next action stay visible in the run record.",status:"design control"}
  ],
  catalog: {total:6,departments:["Finance","Legal","People","Product","Security"],sensitivities:["confidential","internal","restricted"]},
  recommendations: [],
  handoff: {phases:[
    {label:"01 / Map",title:"Confirm source and owner mapping",detail:"Validate repository IDs, department ownership, lifecycle fields, and approver groups with the customer."},
    {label:"02 / Pilot",title:"Run a governed sample",detail:"Measure routing coverage, metadata completeness, manual review touches, and policy exceptions on representative content."},
    {label:"03 / Handoff",title:"Operationalize the contract",detail:"Replace mock adapters with authenticated provider calls, preserve audit events, and define rollback ownership."}
  ],api_mapping:[
    {sample:"catalog search",real_integration_shape:"content.search",owner:"Solutions Engineering"},
    {sample:"metadata update",real_integration_shape:"content.updateMetadata",owner:"Content Operations"},
    {sample:"approval routing",real_integration_shape:"workflow.createApproval",owner:"Control Owner"},
    {sample:"audit export",real_integration_shape:"governance.exportAudit",owner:"IT / Security"}
  ],boundaries:["No customer credentials, private tenant, or production content is used.","Sample shared links are deterministic placeholders and do not resolve to real content.","The evaluation demonstrates control behavior; it does not claim customer business impact."]}
};

window.CONTENT_AI_FALLBACK_ITEMS = [
  {item_id:"CNT-1001",title:"Master Services Agreement - Acme Robotics",content_type:"contract",department:"Legal",sensitivity:"confidential",lifecycle_stage:"draft",owner:"Maya Chen",text:"Draft MSA covering renewal terms, liability language, data protection clauses, and approval steps for a strategic robotics customer.",metadata:{region:"US",value_band:"enterprise"}},
  {item_id:"CNT-1002",title:"Q3 Field Services Invoice Batch",content_type:"invoice",department:"Finance",sensitivity:"internal",lifecycle_stage:"submitted",owner:"Arjun Patel",text:"Invoice packet requiring AP validation, duplicate checks, vendor code matching, and payment routing before month-end close.",metadata:{region:"US",amount_band:"mid-market"}},
  {item_id:"CNT-1003",title:"Employee Compensation Change Request",content_type:"employee_record",department:"People",sensitivity:"restricted",lifecycle_stage:"review",owner:"Elena Torres",text:"Confidential compensation change request with manager approval notes, effective date, and HR operations action items.",metadata:{region:"US",policy:"people-confidential"}},
  {item_id:"CNT-1004",title:"Product Launch Readiness Checklist",content_type:"checklist",department:"Product",sensitivity:"internal",lifecycle_stage:"active",owner:"Jordan Miles",text:"Cross-functional launch checklist tracking approvals from product marketing, legal, sales enablement, and customer support.",metadata:{region:"Global",release:"spring"}},
  {item_id:"CNT-1005",title:"Customer Security Questionnaire",content_type:"questionnaire",department:"Security",sensitivity:"confidential",lifecycle_stage:"customer_response",owner:"Priya Raman",text:"Security questionnaire response covering access control, encryption, retention, audit logging, incident response, and compliance posture.",metadata:{region:"Global",framework:"SOC2"}},
  {item_id:"CNT-1006",title:"Urgent Contractor Access Exception",content_type:"security_exception",department:"Security",sensitivity:"restricted",lifecycle_stage:"exception_request",owner:"Priya Raman",text:"Urgent exception asks an external contractor to bypass approval and share a temporary production password through a public link. The request has unclear business owner context and must not be circulated.",metadata:{region:"Global",policy:"security-exception",source:"sample-only"}}
];
