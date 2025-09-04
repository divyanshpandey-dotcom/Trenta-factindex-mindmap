import uuid
import os
import warnings
import json
import re
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self
from typing import List, Union, Dict, Optional
from streamlit_markmap_local import markmap

class AuditMindMapWarning(Warning):
    """Warning for audit mind map generation failures"""

# MODIFIED FUNCTIONS TO USE STATIC MARKDOWN FILE

def load_static_mindmap() -> tuple:
    """Load the pre-saved mindmap markdown file"""
    mindmap_file = "mindmap_c67fffff.md"
    
    try:
        # Read the markdown content
        with open(mindmap_file, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        
        # Create mock audit data structure based on the markdown content
        audit_data = parse_markdown_to_audit_data(markdown_content)
        
        return markdown_content, audit_data
        
    except FileNotFoundError:
        # Fallback with the provided content if file not found
        markdown_content = """"""
        
        audit_data = parse_markdown_to_audit_data(markdown_content)
        return markdown_content, audit_data

def parse_markdown_to_audit_data(markdown_content: str) -> Dict:
    """Parse markdown content into audit data structure"""
    lines = markdown_content.split('\n')
    
    # Extract title
    unified_title = "Integrated Controls Framework Overview"
    for line in lines:
        if line.startswith('# 🔍'):
            unified_title = line.replace('# 🔍', '').strip()
            break
    
    # Parse documents and insights
    documents = []
    current_doc = None
    current_insight = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('## 📋'):
            # New document
            if current_doc:
                documents.append(current_doc)
            current_doc = {
                "document_id": str(uuid.uuid4())[:8],
                "document_title": line.replace('## 📋', '').strip(),
                "document_type": "Policy Document",
                "audit_insights": []
            }
            
        elif line.startswith('### 🎯'):
            # New insight
            if current_insight and current_doc:
                current_doc["audit_insights"].append(current_insight)
            current_insight = {
                "node_title": line.replace('### 🎯', '').strip(),
                "sub_nodes": []
            }
            
        elif line.startswith('#### 🔸'):
            # Sub node title
            if current_insight:
                sub_title = line.replace('#### 🔸', '').strip()
                current_insight["sub_nodes"].append({
                    "sub_title": sub_title,
                    "sub_content": ""
                })
                
        elif line.startswith('##### ') and current_insight and current_insight["sub_nodes"]:
            # Sub node content
            content = line.replace('#####', '').strip()
            current_insight["sub_nodes"][-1]["sub_content"] = content
    
    # Add last insight and document
    if current_insight and current_doc:
        current_doc["audit_insights"].append(current_insight)
    if current_doc:
        documents.append(current_doc)
    
    return {
        "unified_title": unified_title,
        "audit_context": "Comprehensive framework covering security, data governance, risk management and audit controls",
        "documents": documents
    }

def generate_audit_mindmap(documents: List[Dict] = None) -> Union[tuple, tuple]:
    """Generate audit-focused mind map using static markdown file"""
    try:
        # Ignore the documents parameter and use static content
        markdown_content, audit_data = load_static_mindmap()
        return markdown_content, audit_data
        
    except Exception as e:
        warnings.warn(
            message=f"Static mind map loading failed: {e}",
            category=AuditMindMapWarning,
        )
        return None, None

def load_source_documents():
    """Load the source documents mapping from JSON file"""
    source_docs_file = "source_documents.json"
    
    try:
        with open(source_docs_file, 'r', encoding='utf-8') as file:
            source_docs = json.load(file)
        return source_docs
    except FileNotFoundError:
        # Fallback sample data for demo
        return {
                "security_policy.pdf": {
                    "title": "Information Security Policy",
                    "content": """
        # Information Security Policy
**Document Version:** 2.1  
**Last Updated:** March 15, 2024  
**Document Type:** Policy Document  
**Approval Authority:** Chief Information Security Officer  
**Review Cycle:** Annual  

## 1. Executive Summary

This Information Security Policy establishes comprehensive security controls across the organization to protect information assets, maintain business continuity, and ensure regulatory compliance. The policy framework encompasses access management, incident response, risk assessment, training, and data protection measures designed to safeguard organizational data and systems against evolving security threats.

## 2. Policy Scope and Objectives

### 2.1 Scope
This policy applies to all employees, contractors, vendors, and third parties who access organizational information systems, data, or facilities. The policy covers all information assets regardless of format, location, or storage medium.

### 2.2 Objectives
- Establish robust access controls and authentication mechanisms
- Implement effective incident response and recovery procedures
- Maintain continuous risk assessment and vulnerability management
- Ensure comprehensive security awareness and training programs
- Protect sensitive data through classification and encryption standards

## 3. Role-Based Access and Authentication Controls

### 3.1 Role-Based Access Control (RBAC) Implementation
All system access must be governed by role-based access control principles, ensuring users receive minimum necessary permissions based on job functions and business requirements.

**Key Requirements:**
- Access provisioning based on documented job roles and responsibilities
- Segregation of duties for sensitive functions and processes
- Regular review and validation of role definitions and permissions
- Automated access provisioning where technically feasible

### 3.2 Quarterly Access Reviews
System owners must conduct comprehensive access reviews every quarter to validate user permissions and identify unauthorized or excessive access.

**Review Process:**
- Generate access reports for all systems under management
- Validate each user's access against current job responsibilities
- Document review findings and remediation actions
- Submit completed reviews to Information Security within 10 business days

### 3.3 Multi-Factor Authentication Requirements
Multi-factor authentication (MFA) is mandatory for all privileged accounts and remote access scenarios to provide enhanced security for sensitive system access.

**Implementation Standards:**
- Deploy MFA for all administrative and privileged user accounts
- Require MFA for all remote access connections including VPN
- Utilize approved authentication factors: something you know, have, or are
- Maintain backup authentication methods for business continuity

## 4. Incident Response and Escalation Procedures

### 4.1 Incident Classification and Response Times
Security incidents are classified based on severity levels with corresponding response time requirements to ensure appropriate resource allocation and management attention.

**Response Time Requirements:**
- **Critical Incidents:** Initial response within 2 hours
- **High Severity:** Initial response within 4 hours
- **Medium Severity:** Initial response within 8 hours
- **Low Severity:** Initial response within 24 hours

### 4.2 Mandatory CISO Escalation
All incidents involving personal data breaches or system compromise must be immediately escalated to the Chief Information Security Officer regardless of initial severity assessment.

**Escalation Triggers:**
- Unauthorized access to personal or confidential data
- System compromise or malware infection
- Denial of service attacks affecting business operations
- Suspected insider threats or policy violations

### 4.3 Centralized Incident Documentation
All security incidents must be documented in the central incident management system to ensure proper tracking, analysis, and reporting capabilities.

**Documentation Requirements:**
- Incident discovery and initial assessment details
- Response actions taken and personnel involved
- Business impact assessment and affected systems
- Root cause analysis and corrective action plans

## 5. Risk Assessment and Vulnerability Management

### 5.1 Annual Risk Assessments
All critical systems must undergo comprehensive annual risk assessments to identify vulnerabilities, threats, and potential business impacts.

**Assessment Components:**
- Asset inventory and criticality classification
- Threat landscape analysis and vulnerability identification
- Risk calculation based on likelihood and impact
- Control effectiveness evaluation and gap analysis
- Executive reporting with risk treatment recommendations

### 5.2 Monthly Vulnerability Scanning
Automated vulnerability scanning must be performed monthly on all network-connected systems to identify security weaknesses and configuration issues.

**Scanning Requirements:**
- Authenticated scans for internal systems where possible
- External perimeter scanning from internet perspective
- Database and application-specific vulnerability assessments
- Wireless network security assessments quarterly

### 5.3 Critical Vulnerability Remediation
Critical vulnerabilities must be remediated within 72 hours of identification to minimize exposure to potential attacks.

**Remediation Process:**
- Immediate notification to system owners and security team
- Risk assessment and business impact analysis
- Coordinated patching or compensating control implementation
- Validation testing and vulnerability re-scan confirmation

## 6. Security Awareness and Training Controls

### 6.1 Annual Employee Training
All employees must complete mandatory security awareness training annually to maintain current knowledge of security threats, policies, and procedures.

**Training Components:**
- Current threat landscape and attack methodologies
- Organizational security policies and procedures
- Incident reporting requirements and contact information
- Data handling and protection best practices

### 6.2 Specialized Privileged User Training
Users with elevated system privileges must complete additional specialized training every six months due to increased security responsibilities and risk exposure.

**Advanced Training Topics:**
- Advanced persistent threat recognition and response
- Secure system administration practices
- Privileged access management and monitoring
- Incident response procedures and forensic preservation

### 6.3 Training Compliance Monitoring
Training completion rates and compliance metrics are tracked and reported to management quarterly to ensure program effectiveness and identify areas for improvement.

## 7. Data Classification and Encryption Standards

### 7.1 Mandatory Data Classification
All organizational information must be classified according to sensitivity levels to ensure appropriate protection measures are applied consistently.

**Classification Levels:**
- **Public:** Information approved for public disclosure
- **Internal:** Information for internal organizational use
- **Confidential:** Sensitive information requiring protection
- **Restricted:** Highly sensitive information with strict access controls

### 7.2 AES-256 Encryption Requirements
All Confidential and Restricted data must be encrypted using AES-256 encryption standards both in transit and at rest to prevent unauthorized access.

**Implementation Standards:**
- Transport Layer Security (TLS) 1.3 for data in transit
- Full disk encryption for endpoint devices and servers
- Database-level encryption for sensitive data fields
- Secure key management and rotation procedures
        """,
                    "type": "Policy Document",
                    "last_updated": "2024-03-15",
                    "version": "2.1"
                },
                "data_governance.pdf": {
                    "title": "Data Governance Framework",
                    "content": """
        # Data Governance Framework
**Document Version:** 3.0  
**Last Updated:** February 28, 2024  
**Document Type:** Framework Document  
**Approval Authority:** Chief Data Officer  
**Review Cycle:** Annual  

## 1. Executive Summary

The Data Governance Framework establishes comprehensive accountability structures for data quality, privacy, and lifecycle management across all business units. This framework ensures data assets are properly managed, protected, and leveraged to support business objectives while maintaining compliance with privacy regulations and organizational policies.

## 2. Framework Scope and Principles

### 2.1 Scope
This framework applies to all data assets across the organization, including structured and unstructured data, regardless of storage location, format, or business application.

### 2.2 Governance Principles
- Data is a strategic organizational asset requiring active management
- Clear accountability and stewardship roles for all data domains
- Privacy by design in all data processing activities
- Data quality drives business value and decision-making effectiveness
- Lifecycle management from creation to secure destruction

## 3. Data Stewardship Roles and Accountability

### 3.1 Business Data Owner Responsibilities
Business data owners are accountable for data quality, access decisions, and business value realization within their respective domains.

**Primary Responsibilities:**
- Define data quality standards and acceptance criteria
- Make access authorization decisions based on business need
- Approve data sharing agreements and usage policies
- Participate in data governance committee activities
- Ensure compliance with privacy and regulatory requirements

### 3.2 Technical Data Custodian Duties
Technical data custodians implement and maintain security controls, backup procedures, and technical infrastructure as directed by data owners.

**Core Functions:**
- Implement technical security controls and access mechanisms
- Maintain data backup and recovery capabilities
- Monitor data usage and access patterns
- Execute data lifecycle management procedures
- Provide technical expertise for data governance initiatives

### 3.3 Data Governance Committee Structure
Cross-functional data governance committees provide oversight and decision-making authority for enterprise data management initiatives.

**Committee Composition:**
- Executive sponsor from senior leadership
- Business data owners from each major domain
- Technical representatives from IT and security
- Privacy officer and legal counsel
- Data quality and analytics representatives

## 4. GDPR Compliance and Privacy Controls

### 4.1 Lawful Basis Documentation
All personal data processing activities must have documented lawful basis under GDPR with regular review and validation procedures.

**Documentation Requirements:**
- Clear identification of applicable lawful basis
- Purpose limitation and data minimization assessment
- Data subject notification and consent mechanisms where required
- Regular review of processing necessity and proportionality

### 4.2 Privacy Impact Assessments
High-risk personal data processing activities require comprehensive privacy impact assessments before implementation.

**Assessment Triggers:**
- Large-scale systematic monitoring of public areas
- Processing of special category personal data
- Automated decision-making with legal or significant effects
- Data processing involving vulnerable individuals

### 4.3 Data Subject Rights Management
Data subject rights requests must be fulfilled within 30 days with documented evidence of completion and appropriate record-keeping.

**Rights Management Process:**
- Centralized request intake and tracking system
- Identity verification procedures for requesters
- Cross-system data location and extraction capabilities
- Response documentation and audit trail maintenance

## 5. Data Retention and Legal Hold Procedures

### 5.1 Comprehensive Retention Schedules
Retention schedules are established for all data categories based on business requirements, regulatory obligations, and risk considerations.

**Schedule Components:**
- Business justification for retention periods
- Regulatory and legal requirement analysis
- Storage cost and risk assessment
- Disposal method and certification requirements

### 5.2 Automated Deletion Implementation
Automated deletion processes are implemented where technically feasible to ensure consistent application of retention policies.

**Automation Capabilities:**
- Database triggers for record-level deletion
- File system monitoring and automated purging
- Application-integrated retention management
- Exception handling and manual review processes

### 5.3 Legal Hold Override Procedures
Legal hold procedures override standard retention schedules during litigation, regulatory investigation, or audit scenarios.

**Hold Management:**
- Legal hold notification and acknowledgment process
- System-wide hold implementation and monitoring
- Regular hold review and release procedures
- Documentation of hold decisions and scope

## 6. Data Quality Monitoring and Master Data Management

### 6.1 Automated Data Profiling
Continuous data quality monitoring through automated profiling identifies quality issues and trends across all data domains.

**Profiling Metrics:**
- Completeness, accuracy, and consistency measurements
- Data freshness and timeliness indicators
- Referential integrity and constraint violations
- Statistical anomaly detection and trending

### 6.2 Monthly Quality Scorecards
Quality scorecards are published monthly to data owners providing visibility into data quality performance and improvement opportunities.

**Scorecard Elements:**
- Overall quality scores by data domain and system
- Trend analysis and performance indicators
- Issue identification and remediation status
- Benchmark comparisons and improvement targets

### 6.3 Master Data Management
Master data management processes ensure single source of truth for critical data entities across all business applications.

**MDM Capabilities:**
- Golden record creation and maintenance
- Data matching and deduplication processes
- Change control and approval workflows
- Distribution and synchronization mechanisms
        """,
                    "type": "Framework Document",
                    "last_updated": "2024-02-28",
                    "version": "3.0"
                },
                "vendor_management.pdf": {
                    "title": "Third-Party Risk Management Policy",
                    "content": """
        # Third-Party Risk Management Policy
**Document Version:** 1.8  
**Last Updated:** January 20, 2024  
**Document Type:** Risk Management Policy  
**Approval Authority:** Chief Risk Officer  
**Review Cycle:** Annual  

## 1. Executive Summary

The Third-Party Risk Management Policy establishes comprehensive procedures for assessing, monitoring, and managing risks associated with vendors and service providers. This policy ensures organizational data and systems remain protected when accessed or processed by external parties while maintaining business continuity and regulatory compliance.

## 2. Policy Scope and Risk Categories

### 2.1 Policy Scope
This policy applies to all third-party relationships involving access to organizational data, systems, facilities, or services that could impact business operations or security posture.

### 2.2 Risk Categories
- **Cyber Security:** Data breaches, system compromise, and security control deficiencies
- **Operational:** Service disruptions, performance failures, and business continuity risks
- **Compliance:** Regulatory violations, policy non-compliance, and audit findings
- **Financial:** Credit risk, pricing changes, and financial stability concerns
- **Reputational:** Public relations impacts and brand damage from vendor incidents

## 3. Vendor Risk Assessment and Onboarding

### 3.1 Pre-Contract Risk Assessment
All vendors must undergo comprehensive risk assessment before contract execution using standardized questionnaires and risk scoring methodology.

**Assessment Components:**
- Security control maturity and effectiveness evaluation
- Financial stability and business continuity capabilities
- Regulatory compliance and certification status
- References and past performance validation
- Geographic and jurisdictional risk considerations

### 3.2 Risk Scoring and Classification
Vendors are classified based on risk scores and criticality to business operations to determine appropriate oversight and monitoring requirements.

**Classification Levels:**
- **Critical:** Essential services with high risk exposure
- **Important:** Significant business impact with moderate risk
- **Standard:** Limited impact with standard risk profile
- **Low:** Minimal impact with basic risk considerations

### 3.3 Annual On-Site Security Assessments
Critical vendors undergo annual on-site security assessments conducted by qualified security professionals to validate control implementation and effectiveness.

**Assessment Scope:**
- Physical security controls and environmental protections
- Technical security architecture and monitoring capabilities
- Personnel security practices and access management
- Incident response procedures and business continuity plans

## 4. Contractual Security and Data Protection

### 4.1 Mandatory Security Requirements
All vendor contracts must include comprehensive security requirements, right to audit clauses, and incident notification obligations.

**Contract Provisions:**
- Minimum security control standards and implementation requirements
- Regular security assessment and audit rights
- Incident notification timelines and escalation procedures
- Data protection and privacy requirement compliance

### 4.2 Data Processing Agreements
Vendors processing personal data on behalf of the organization must execute data processing agreements compliant with applicable privacy regulations.

**Agreement Components:**
- Processing purpose limitations and data minimization requirements
- Data subject rights support and assistance obligations
- International data transfer safeguards and restrictions
- Sub-processor approval and oversight requirements

### 4.3 Service Level Agreements
Performance expectations and measurement criteria are documented in service level agreements with penalties for non-compliance.

**SLA Elements:**
- Availability and performance benchmarks
- Response time requirements for issues and requests
- Quality metrics and measurement methodologies
- Penalty structures and remediation procedures

## 5. Ongoing Vendor Monitoring and Performance Management

### 5.1 Quarterly Business Reviews
Critical vendors participate in quarterly business reviews to assess performance, address issues, and plan future requirements.

**Review Topics:**
- Performance against established service levels
- Security incident summary and lessons learned
- Business relationship satisfaction and improvement opportunities
- Technology roadmap alignment and future planning

### 5.2 Annual Security Questionnaire Updates
All vendors must complete updated security questionnaires annually to maintain current risk assessment information.

**Questionnaire Updates:**
- Changes to security controls and certifications
- New regulatory compliance requirements
- Incident history and response improvements
- Business continuity and disaster recovery capabilities

### 5.3 Continuous Monitoring Program
Automated monitoring tools and manual review processes provide ongoing visibility into vendor risk posture and performance.

**Monitoring Components:**
- Security rating services and threat intelligence feeds
- Financial stability monitoring and credit assessments
- Regulatory compliance and certification tracking
- News and media monitoring for reputation risks

## 6. Vendor Access Management and Termination

### 6.1 Access Control Requirements
All vendor personnel accessing organizational systems must have unique identities with access regularly reviewed and certified by business owners.

**Access Management:**
- Individual user accounts with strong authentication
- Role-based access aligned with job responsibilities
- Regular access reviews and recertification procedures
- Privileged access monitoring and session recording

### 6.2 Secure Termination Procedures
Vendor termination procedures ensure secure return or destruction of organizational data with appropriate certification and validation.

**Termination Activities:**
- Immediate access revocation across all systems
- Data return or certified destruction verification
- Final security assessment and clearance procedures
- Transition planning and knowledge transfer requirements

### 6.3 Business Continuity Planning
Critical vendor dependencies are assessed with documented contingency plans for vendor failure scenarios and alternative service providers.

**Continuity Planning:**
- Single points of failure identification and mitigation
- Alternative vendor identification and qualification
- Transition procedures and timeline development
- Regular testing and plan validation exercises
        """,
                    "type": "Risk Management Policy",
                    "last_updated": "2024-01-20",
                    "version": "1.8"
                },
                "internal_audit.pdf": {
                    "title": "Internal Audit Charter",
                    "content": """
        # Internal Audit Charter
**Document Version:** 2.3  
**Last Updated:** April 10, 2024  
**Document Type:** Charter Document  
**Approval Authority:** Board Audit Committee  
**Review Cycle:** Annual  

## 1. Executive Summary

The Internal Audit Charter establishes the purpose, authority, and responsibility of the internal audit function within the organization's governance structure. This charter ensures audit independence, defines comprehensive audit scope, and establishes quality standards that enable effective risk management, control evaluation, and governance process improvement.

## 2. Charter Purpose and Mission

### 2.1 Internal Audit Mission
To enhance and protect organizational value by providing risk-based and objective assurance, advice, and insight to management and the board of directors.

### 2.2 Charter Authority
This charter is established by the Board of Directors and defines the internal audit function's purpose, authority, and responsibility within the organization's governance framework.

### 2.3 Organizational Independence
Internal audit maintains organizational independence through dual reporting relationships and unrestricted access to information, personnel, and systems necessary to fulfill audit responsibilities.

## 3. Audit Independence and Reporting Structure

### 3.1 Functional Reporting to Audit Committee
Internal audit reports functionally to the Audit Committee of the Board of Directors to ensure independence and objectivity in audit activities.

**Functional Reporting Responsibilities:**
- Annual audit plan approval and significant changes
- Audit results communication and management responses
- Resource adequacy assessment and budget approval
- Chief Audit Executive performance evaluation and compensation

### 3.2 Administrative Reporting to CEO
Internal audit reports administratively to the Chief Executive Officer for day-to-day operations and resource management.

**Administrative Responsibilities:**
- Daily operational management and resource allocation
- Staff hiring, performance evaluation, and development
- Coordination with management and other assurance providers
- Administrative policy compliance and implementation

### 3.3 Independence Safeguards
Specific safeguards ensure audit independence and objectivity are maintained throughout all audit activities.

**Safeguard Mechanisms:**
- Direct board access without management present
- Prohibition from operational responsibilities and decision-making
- Rotation of audit staff on long-term engagements
- Annual independence confirmation and conflict disclosure

## 4. Comprehensive Audit Scope and Authority

### 4.1 Unlimited Audit Scope
Internal audit scope includes evaluation of risk management, control, and governance processes across all organizational activities, systems, and functions.

**Audit Coverage Areas:**
- Financial and operational process effectiveness
- Information technology systems and cybersecurity controls
- Regulatory compliance and ethics program effectiveness
- Risk management framework and control environment

### 4.2 Unrestricted Access Rights
No restrictions are placed on internal audit access to records, personnel, or physical properties relevant to audit objectives.

**Access Rights Include:**
- All organizational records, documents, and information systems
- Personnel interviews and facility inspections
- External party communications and contract documentation
- Board and senior management meeting observations

### 4.3 Authority Limitations
Internal audit does not have authority to direct operational activities, make management decisions, or implement corrective actions.

**Prohibited Activities:**
- Operational decision-making or process ownership
- Implementation of controls or corrective actions
- Approval of transactions or operational procedures
- Direct responsibility for control design or maintenance

## 5. Risk-Based Audit Planning and Methodology

### 5.1 Risk Assessment Methodology
Internal audit utilizes comprehensive risk assessment methodology to prioritize audit activities based on organizational risk exposure and strategic objectives.

**Risk Assessment Components:**
- Business process and system risk evaluation
- Management concerns and regulatory requirements
- Previous audit results and external examination findings
- Industry risks and emerging threat considerations

### 5.2 Annual Audit Plan Development
The annual audit plan is developed through systematic risk assessment and stakeholder input with approval by the Audit Committee.

**Planning Process:**
- Enterprise risk assessment and audit universe update
- Stakeholder input collection and priority setting
- Resource requirement analysis and capacity planning
- Quarterly plan updates and adjustment procedures

### 5.3 Audit Engagement Management
Individual audit engagements follow structured methodology ensuring consistent quality and comprehensive coverage.

**Engagement Phases:**
- Planning and risk assessment with scope definition
- Fieldwork execution and testing procedures
- Finding development and recommendation formulation
- Report preparation and management response coordination

## 6. Professional Standards and Quality Assurance

### 6.1 IIA Standards Compliance
All internal audit activities comply with Institute of Internal Auditors International Professional Practices Framework standards.

**Standards Implementation:**
- Attribute standards for audit function characteristics
- Performance standards for audit activity management
- Implementation guidance and practice advisory adoption
- Ethics code compliance and professional conduct requirements

### 6.2 External Quality Assessment Program
External quality assessments are conducted every five years by qualified independent reviewers to evaluate audit effectiveness and standards compliance.

**Assessment Scope:**
- Conformance with professional standards and best practices
- Audit methodology effectiveness and quality indicators
- Organizational independence and objectivity maintenance
- Value-added services and stakeholder satisfaction

### 6.3 Continuous Professional Development
Internal audit staff maintain professional competency through certification maintenance and continuing education requirements.

**Development Requirements:**
- Professional certification achievement and maintenance
- Annual continuing education hour completion
- Technical and industry training participation
- Internal knowledge sharing and best practice development

## 7. Audit Communication and Follow-Up

### 7.1 Audit Reporting Standards
Audit findings are communicated through formal written reports with clear findings, recommendations, and management responses.

**Report Components:**
- Executive summary with overall assessment and key findings
- Detailed findings with risk ratings and recommendations
- Management responses with action plans and target dates
- Implementation timeline and resource requirement documentation

### 7.2 Follow-Up Procedures
Systematic follow-up procedures verify timely implementation of agreed-upon management actions and assess remediation effectiveness.

**Follow-Up Process:**
- Quarterly status reporting on open audit recommendations
- Independent validation of completed corrective actions
- Risk assessment for overdue or incomplete responses
- Escalation procedures for persistent non-compliance

### 7.3 Communication with External Parties
Coordination with external auditors, regulators, and other oversight bodies ensures efficient audit coverage and minimizes duplication.

**External Coordination:**
- Audit plan sharing and coverage mapping
- Findings communication and remediation coordination
- Regulatory examination support and liaison activities
- Professional development and best practice sharing
        """,
                    "type": "Charter Document",
                    "last_updated": "2024-04-10",
                    "version": "2.3"
                }
            }

# Modified show_fullscreen_mindmap function
# Updated show_fullscreen_mindmap function with scrollable document panels

def show_fullscreen_mindmap(mindmap_content: str, audit_data: Dict):
    """Display fullscreen mind map modal with scrollable source documents"""
    
    # Enhanced Modal CSS styling with individual document scrollers
    st.markdown("""
    <style>
    .mindmap-modal {
        position: fixed;
        z-index: 999999;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.8);
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .mindmap-modal-content {
        background-color: #ffffff;
        width: 98vw;
        height: 98vh;
        border-radius: 12px;
        position: relative;
        display: flex;
        flex-direction: column;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .mindmap-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 12px 12px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 1.2rem;
        font-weight: bold;
        flex-shrink: 0;
    }
    
    .mindmap-body {
        flex: 1;
        display: flex;
        overflow: hidden;
        background: #f8f9fa;
    }
    
    .mindmap-main-content {
        flex: 2;
        display: flex;
        flex-direction: column;
        padding: 1rem;
        overflow: auto;
    }
    
    .source-docs-panel {
        flex: 1;
        background: white;
        border-left: 2px solid #e0e0e0;
        padding: 1rem;
        overflow-y: auto;
        max-width: 400px;
        height: 100%;
    }
    
    .source-docs-header {
        background: #f8f9fa;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 4px solid #2a5298;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .source-doc-item {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 1rem;
        overflow: hidden;
        transition: all 0.3s ease;
    }
    
    .source-doc-item:hover {
        border-color: #2a5298;
        box-shadow: 0 2px 8px rgba(42, 82, 152, 0.15);
    }
    
    .source-doc-header {
        background: #f8f9fa;
        padding: 0.75rem;
        border-bottom: 1px solid #e0e0e0;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: sticky;
        top: 0;
        z-index: 5;
    }
    
    .source-doc-title {
        font-weight: bold;
        color: #1e3c72;
        font-size: 0.9rem;
    }
    
    .source-doc-type {
        background: #e3f2fd;
        color: #1565c0;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.7rem;
    }
    
    /* NEW: Scrollable content container for each document */
    .source-doc-content-container {
        max-height: 300px;
        overflow-y: auto;
        border-top: 1px solid #f0f0f0;
    }
    
    .source-doc-content {
        padding: 0.75rem;
        font-size: 0.85rem;
        line-height: 1.4;
        color: #333;
        white-space: pre-wrap;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .source-doc-meta {
        padding: 0.5rem 0.75rem;
        background: #fafafa;
        font-size: 0.75rem;
        color: #666;
        border-top: 1px solid #f0f0f0;
        position: sticky;
        bottom: 0;
    }
    
    /* Custom scrollbar styling */
    .source-doc-content-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .source-doc-content-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
    }
    
    .source-doc-content-container::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
    }
    
    .source-doc-content-container::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
    
    .source-docs-panel::-webkit-scrollbar {
        width: 8px;
    }
    
    .source-docs-panel::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    .source-docs-panel::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 4px;
    }
    
    .source-docs-panel::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
    
    .mindmap-stats {
        display: flex;
        gap: 2rem;
        margin-bottom: 1rem;
        padding: 1rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        flex-shrink: 0;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #2a5298;
        display: block;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.25rem;
    }
    
    .mindmap-container-fullscreen {
        background: white;
        border-radius: 8px;
        flex: 1;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    
    .action-buttons {
        padding: 1rem 2rem;
        background: white;
        border-top: 1px solid #e0e0e0;
        flex-shrink: 0;
    }
    
    /* Expand/Collapse indicator */
    .expand-indicator {
        font-size: 0.8rem;
        color: #666;
        transition: transform 0.3s ease;
    }
    
    .expand-indicator.expanded {
        transform: rotate(90deg);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Load source documents
    source_docs = load_source_documents()
    
    # Create modal container
    modal_container = st.empty()
    
    with modal_container.container():
        # Header with title and close button
        st.markdown(f"""
        <div class="mindmap-header">
            <div>
                <span>🧠 {audit_data.get('unified_title', 'Audit Mind Map')}</span>
                <div style="font-size: 0.9rem; font-weight: normal; margin-top: 0.25rem; opacity: 0.9;">
                    {audit_data.get('audit_context', 'Interactive document analysis')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Main body with two-panel layout
        st.markdown('<div class="mindmap-body">', unsafe_allow_html=True)
        
        # Create two columns: main content and source documents
        main_col, source_col = st.columns([2, 1])
        
        with main_col:
            st.markdown('<div class="mindmap-main-content">', unsafe_allow_html=True)
            
            # Statistics section
            total_insights = sum(len(doc.get("audit_insights", [])) for doc in audit_data.get("documents", []))
            total_subnodes = sum(
                len(insight.get("sub_nodes", [])) 
                for doc in audit_data.get("documents", []) 
                for insight in doc.get("audit_insights", [])
            )
            
            st.markdown(f"""
            <div class="mindmap-stats">
                <div class="stat-item">
                    <span class="stat-number">{len(audit_data.get("documents", []))}</span>
                    <div class="stat-label">Documents</div>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{total_insights}</span>
                    <div class="stat-label">Insights</div>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{total_subnodes}</span>
                    <div class="stat-label">Controls</div>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(mindmap_content.split())}</span>
                    <div class="stat-label">Words</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Mind map container
            st.markdown('<div class="mindmap-container-fullscreen">', unsafe_allow_html=True)
            markmap(mindmap_content, height=500)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with source_col:
            st.markdown('<div class="source-docs-panel">', unsafe_allow_html=True)
            
            # Source documents header
            st.markdown(f"""
            <div class="source-docs-header">
                <h4 style="margin: 0; color: #1e3c72;">📄 Source Documents ({len(source_docs)})</h4>
                <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #666;">
                    Original policy documents referenced in the mind map analysis
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display source documents with individual scrollable content
            for idx, (filename, doc_info) in enumerate(source_docs.items()):
                # Create expandable document sections
                expanded_key = f"doc_expanded_{idx}"
                if expanded_key not in st.session_state:
                    st.session_state[expanded_key] = False
                
                # Document header (always visible)
                st.markdown(f"""
                <div class="source-doc-item">
                    <div class="source-doc-header" onclick="toggleDocument({idx})">
                        <div>
                            <div class="source-doc-title">📋 {doc_info['title']}</div>
                            <div class="source-doc-type">{doc_info['type']}</div>
                        </div>
                        <div class="expand-indicator" id="indicator_{idx}">▶</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Use expander for document content with custom styling
                with st.expander("", expanded=False):
                    # Document metadata
                    st.markdown(f"""
                    **Version:** {doc_info['version']} | **Last Updated:** {doc_info['last_updated']}  
                    **File:** `{filename}`
                    """)
                    
                    # Scrollable content container
                    st.markdown("**Document Content:**")
                    
                    # Create scrollable text area for content
                    content_preview = doc_info["content"][:3000] + "..." if len(doc_info["content"]) > 3000 else doc_info["content"]
                    
                    # Use a container with custom CSS for scrolling
                    st.markdown(f"""
                    <div class="source-doc-content-container">
                        <div class="source-doc-content">{content_preview}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Document actions
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"📖 Full Content", key=f"view_full_{idx}", help=f"View complete {doc_info['title']}"):
                            # Show full content in a text area
                            st.text_area(
                                "Complete Document", 
                                value=doc_info["content"], 
                                height=400,
                                key=f"full_content_{idx}"
                            )
                    
                    with col2:
                        if st.button(f"📋 Copy Text", key=f"copy_{idx}", help="Copy content to clipboard"):
                            st.code(doc_info["content"][:500] + "...", language="text")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action buttons at bottom
        st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
        
        with col1:
            if st.button("💾 Export MD", use_container_width=True):
                st.download_button(
                    "📥 Download",
                    mindmap_content,
                    f"mindmap_{uuid.uuid4().hex[:8]}.md",
                    "text/markdown",
                    use_container_width=True
                )
        
        with col2:
            if st.button("📊 Export JSON", use_container_width=True):
                st.download_button(
                    "📥 Download",
                    json.dumps(audit_data, indent=2),
                    f"mindmap_data_{uuid.uuid4().hex[:8]}.json",
                    "application/json",
                    use_container_width=True
                )
        
        with col3:
            if st.button("📄 Export Sources", use_container_width=True):
                st.download_button(
                    "📥 Download",
                    json.dumps(source_docs, indent=2),
                    f"source_documents_{uuid.uuid4().hex[:8]}.json",
                    "application/json",
                    use_container_width=True
                )
        
        with col4:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.mindmap_generated = False
                st.session_state.show_fullscreen = False
                st.rerun()
        
        with col5:
            if st.button("✖️ Close Fullscreen View", type="primary", use_container_width=True):
                st.session_state.show_fullscreen = False
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

        # JavaScript for document expansion (optional enhancement)
        st.markdown("""
        <script>
        function toggleDocument(idx) {
            const indicator = document.getElementById('indicator_' + idx);
            if (indicator) {
                indicator.classList.toggle('expanded');
            }
        }
        </script>
        """, unsafe_allow_html=True)


# Facts Overview Functions (keeping unchanged from original)
def load_facts_data():
    """Load the policy data"""
    factIndex_file = "factIndex.json"
    
    try:
        # Load JSON content
        with open(factIndex_file, 'r', encoding='utf-8') as file:
            factIndex_content = json.load(file)
        
        return factIndex_content
        
    except FileNotFoundError:
        # Fallback with the provided content if file not found
        factIndex_content = {}
        
        return factIndex_content

    # sample_data = json.load(open("factIndex.json"))
    # return sample_data

def categorize_facts(data):
    """Categorize facts into consistent and inconsistent"""
    inconsistent_keys = ['security_training_frequency', 'information_security_risk_assessment_frequency', 
                        'recovery_time_objective', 'password_minimum_length']
    
    inconsistent_facts = {k: v for k, v in data.items() if k in inconsistent_keys and len(v) > 1}
    consistent_facts = {k: v for k, v in data.items() if k not in inconsistent_keys or len(v) == 1}
    
    return inconsistent_facts, consistent_facts

def search_sentence_in_document(sentence, document_content, context_chars=200):
    """Search for a sentence in document content and return context"""
    if not sentence or not document_content:
        return None, None, None
    
    # Clean the sentence for better matching
    clean_sentence = sentence.strip().lower()
    clean_content = document_content.lower()
    
    # Try exact match first
    if clean_sentence in clean_content:
        start_idx = clean_content.find(clean_sentence)
        end_idx = start_idx + len(clean_sentence)
        
        # Get context around the sentence
        context_start = max(0, start_idx - context_chars)
        context_end = min(len(document_content), end_idx + context_chars)
        
        context = document_content[context_start:context_end]
        highlighted_context = context.replace(sentence, f'<span class="highlighted-sentence">{sentence}</span>')
        
        return True, highlighted_context, start_idx
    else:
        # Try fuzzy matching with partial sentences
        words = clean_sentence.split()
        if len(words) >= 3:  # Only try fuzzy matching for longer sentences
            for i in range(len(words) - 2):
                partial_sentence = ' '.join(words[i:i+3])
                if partial_sentence in clean_content:
                    start_idx = clean_content.find(partial_sentence)
                    end_idx = start_idx + len(partial_sentence)
                    
                    context_start = max(0, start_idx - context_chars)
                    context_end = min(len(document_content), end_idx + context_chars)
                    
                    context = document_content[context_start:context_end]
                    highlighted_context = context.replace(partial_sentence, f'<span class="highlighted-sentence">{partial_sentence}</span>')
                    
                    return True, highlighted_context, start_idx
    
    return False, None, None

def create_clickable_sentence(sentence, fact_id, document_title):
    """Create a clickable sentence element"""
    if not sentence or sentence == "N/A":
        return sentence
    
    # Create a unique key for this sentence
    sentence_key = f"sentence_{fact_id}_{hash(sentence) % 10000}"
    
    # Use st.button to make it clickable
    if st.button(
        f"🔍 {sentence[:100]}{'...' if len(sentence) > 100 else ''}", 
        key=sentence_key,
        help=f"Click to find this sentence in {document_title}",
        use_container_width=True
    ):
        return sentence
    
    return None

def load_mindmap_policy_source_documents():
    """Load the policy source documents from the provided data"""
    return {
        "access_management_policy.pdf": {
            "title": "Access Management Policy",
            "content": """This Access Management Policy establishes comprehensive access controls across the organization. The policy mandates role-based access controls (RBAC) with quarterly access reviews conducted by system owners. Multi-factor authentication is required for all privileged accounts and remote access scenarios.

Access to information computing resources is limited to personnel with a business requirement for such access. Access rights shall be granted or revoked in accordance with this Access Control Policy based on the principle of least privilege.

Password minimum characters length required 15. User IDs shall be promptly disabled or removed when users leave the organization or contract work ends. Access rights reviews are performed on at least a semi-annual basis to verify that user access is limited to systems that are required for their job function.""",
            "type": "Policy Document",
            "last_updated": "2024-03-15",
            "version": "2.1"
        },
        "antivirus_management_procedure.pdf": {
            "title": "Antivirus Management Procedure",
            "content": """The Antivirus Management Procedure is established to protect the company's electronic data, reduce the risk of data breaches, and safeguard the overall cybersecurity infrastructure by outlining requirements for effective antivirus management.

All company systems including corporate laptops must have company-approved antivirus software installed. Automated antivirus scans must be configured to run on all systems. Minimum Password length 12 characters is required.

Security training is conducted quarterly with employees regularly introduced to various cyber security threats and the importance of anti-virus protection as an integral component of security measures.""",
            "type": "Procedure Document",
            "last_updated": "2024-02-20",
            "version": "1.0"
        },
        "data_management_policy.pdf": {
            "title": "Data Management Policy",
            "content": """The Data Management Policy establishes data classification and handling requirements across all Company information systems. Data is classified into four levels: Highly Confidential, Confidential, Private, and Public.

Highly confidential data consists of the most sensitive business information including all customer data submitted to the service (Event Data). Access for non-pre approved roles requires documented approval from the data owner.

Data retention requirements specify that Event Data has 90 days retention unless customer account is deleted. Employee Data is retained for duration of employment plus minimum 6 years after employment. Financial Data is retained for minimum 7 years.""",
            "type": "Policy Document",
            "last_updated": "2024-01-10",
            "version": "1.2"
        },
        "disaster_recovery_plan.pdf": {
            "title": "Disaster Recovery Plan",
            "content": """The Disaster Recovery Plan applies to production IT infrastructure providing customer services. Company commits externally to an RTO of 72 hours with RPO parameter not officially communicated to customers.

The plan establishes systematic approaches including monitoring via Datadog tool, with on-call Engineers receiving alerts about critical failures. Customer-facing applications have an RPO of an hour utilizing asynchronous replication.

Database backups occur every 30 minutes with data backed up to another Cloud region. Monitoring is performed via Datadog with jobs tracking snapshot creation and verification of appropriate backup amounts.""",
            "type": "Operational Plan",
            "last_updated": "2024-04-05",
            "version": "3.0"
        },
        "encryption_management.pdf": {
            "title": "Encryption Management Procedure",
            "content": """The Encryption Management Procedure applies to all highly confidential and confidential information. Encryption protection must be applied at any storage means and while transmitting through any channels.

Company uses Cloud Hosting Service for production infrastructure with automatic encryption of all VM-to-VM traffic within VPC network. Transport Layer Security standard is TLS 1.2, with Secure Copy Protocol using at least AES 128.

For data storage, Cloud provider encrypts all customer content stored at rest using AES256. Additional encryption follows standards including AES 128 and AES 256, SHA 2 and SHA 3 for Secure Hash Algorithm, and bcrypt hashing function for secure password storing.""",
            "type": "Procedure Document",
            "last_updated": "2024-03-01",
            "version": "4.0"
        },
        "information_security_policy.pdf": {
            "title": "Information Security Policy",
            "content": """This Information Security Policy applies to all Company information assets regardless of format or processing. The primary goal is preserving confidentiality, integrity, and availability of all forms of information assets.

Security objectives include providing secure and reliable products and services to clients, establishing secure relationships with third parties, complying with applicable legislation, implementing ISMS according to leading security standards, and protecting intellectual property.

Personnel accept the Acceptable Use Policy and Code of Conduct during onboarding and pass security training during onboarding with monthly repetition. Risk assessments are conducted annually or upon significant change to business, IT systems or products.""",
            "type": "Policy Document",
            "last_updated": "2024-02-15",
            "version": "1.0"
        },
        "risk_management_policy.pdf": {
            "title": "Risk Management Assessment and Treatment Policy",
            "content": """The Risk Management Policy is aligned with ISO/IEC 27001 Information Security Management Systems standards. Risk assessment is performed quarterly covering the enterprise including information assets as part of ISMS implementation.

Risk analysis assigns numerical values to likelihood and impact using a 1-5 scale. Total risk is calculated as Likelihood × Impact and classified as High (12 or more), Medium (5 to 10 inclusive), or Low (1 to 4 inclusive).

Risk treatment options include Accept, Mitigate, Avoid, or Share the risk with another party. Controls selection uses ISO/IEC 27001 Annex A as starting point supplemented by ISO/IEC 27002 and ISO/IEC 27018 guidance.""",
            "type": "Risk Management Policy",
            "last_updated": "2024-01-25",
            "version": "2.0"
        },
        "vendor_management_policy.pdf": {
            "title": "Vendor Management Policy",
            "content": """The Vendor Management Policy applies to all data and information systems that are business critical and/or process, store, or transmit Company data including all software vendors utilized to deliver services.

Proper due diligence is performed prior to provisioning access or engaging in processing activities. Initial vendor review assigns risk levels: High risk requires SOC 2 OR ISO 27001 review and security questionnaire; Medium risk requires similar review with risk evaluation; Low risk requires publicly available security information review.

Annual compliance reviews are performed for high-risk vendors with security document and certificate reviews. Medium and low risk vendors receive compliance reviews if major changes occur or during renewal with certificate collection.""",
            "type": "Risk Management Policy",
            "last_updated": "2024-03-20",
            "version": "1.8"
        }
    }

# Modified function to load policy documents from individual files
# Modified function to load policy documents from individual files
def load_policy_source_documents_from_files():
    """Load policy documents from individual markdown files in the policies/ directory"""
    import os
    
    # Define the policy files mapping
    policy_files = {
        "access_management_policy.md": {
            "title": "Access Management Policy",
            "type": "Policy Document",
            "last_updated": "2024-03-15",
            "version": "2.1"
        },
        "antivirus_management_procedure.md": {
            "title": "Antivirus Management Procedure", 
            "type": "Procedure Document",
            "last_updated": "2024-02-20",
            "version": "1.0"
        },
        "data_management_policy.md": {
            "title": "Data Management Policy",
            "type": "Policy Document", 
            "last_updated": "2024-01-10",
            "version": "1.2"
        },
        "disaster_recovery_plan.md": {
            "title": "Disaster Recovery Plan",
            "type": "Operational Plan",
            "last_updated": "2024-04-05", 
            "version": "3.0"
        },
        "encryption_management.md": {
            "title": "Encryption Management Procedure",
            "type": "Procedure Document",
            "last_updated": "2024-03-01",
            "version": "4.0"
        },
        "information_security_policy.md": {
            "title": "Information Security Policy",
            "type": "Policy Document",
            "last_updated": "2024-02-15",
            "version": "1.0"
        },
        "risk_management_assessment_and_treatment_policy.md": {
            "title": "Risk Management Assessment and Treatment Policy",
            "type": "Risk Management Policy",
            "last_updated": "2024-01-25",
            "version": "2.0"
        },
        "vendor_management_policy.md": {
            "title": "Vendor Management Policy",
            "type": "Risk Management Policy",
            "last_updated": "2024-03-20",
            "version": "1.8"
        }
    }
    
    policies_directory = ""
    loaded_policies = {}
    
    # # Create policies directory if it doesn't exist
    # if not os.path.exists(policies_directory):
    #     st.warning(f"Policies directory '{policies_directory}' not found. Using fallback data.")
    #     return load_mindmap_policy_source_documents()  # Fallback to embedded data
    
    # Load each policy file
    for filename, metadata in policy_files.items():
        file_path = os.path.join(policies_directory, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            loaded_policies[filename] = {
                "title": metadata["title"],
                "content": content,
                "type": metadata["type"],
                "last_updated": metadata["last_updated"],
                "version": metadata["version"]
            }
            
        except FileNotFoundError:
            st.warning(f"Policy file '{filename}' not found in '{policies_directory}' directory.")
            # Use fallback content for missing files
            loaded_policies[filename] = {
                "title": metadata["title"],
                "content": f"Content for {metadata['title']} not found. Please ensure the file {filename} exists in the {policies_directory} directory.",
                "type": metadata["type"],
                "last_updated": metadata["last_updated"],
                "version": metadata["version"]
            }
            
        except Exception as e:
            st.error(f"Error loading policy file '{filename}': {str(e)}")
            loaded_policies[filename] = {
                "title": metadata["title"],
                "content": f"Error loading content: {str(e)}",
                "type": metadata["type"],
                "last_updated": metadata["last_updated"],
                "version": metadata["version"]
            }
    
    return loaded_policies

# Updated show_facts_overview_popup function to use file-based loading
def show_facts_overview_popup_with_files():
    """Display Facts Overview popup with source documents loaded from files"""
    
    # Enhanced Facts Overview CSS with two-panel layout
    st.markdown("""
    <style>
        
        .facts-main-content {
            flex: 2;
            overflow-y: auto;
            padding-right: 1rem;
        }
        
        .facts-source-panel {
            flex: 1;
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 1rem;
            overflow-y: auto;
            max-width: 400px;
            height: fit-content;
            max-height: 100%;
        }
        
        .facts-source-header {
            background: #f8f9fa;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 4px solid #2a5298;
        }
        
        .policy-content-preview {
            background: #f8f9fa;
            padding: 0.75rem;
            border-radius: 6px;
            font-size: 0.85rem;
            line-height: 1.4;
            border-left: 3px solid #2a5298;
            max-height: 200px;
            overflow-y: auto;
            white-space: pre-wrap;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        .facts-source-doc-item {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-bottom: 1rem;
            overflow: hidden;
            transition: all 0.3s ease;
        }
        
        .facts-source-doc-item:hover {
            border-color: #2a5298;
            box-shadow: 0 2px 8px rgba(42, 82, 152, 0.15);
        }
        
        .inconsistent-metric {
            background-color: #ffebee;
            border: 2px solid #f44336;
            border-radius: 10px;
            padding: 10px;
            margin: 5px 0;
        }
        .consistent-metric {
            background-color: #e8f5e8;
            border: 2px solid #4caf50;
            border-radius: 10px;
            padding: 10px;
            margin: 5px 0;
        }
        .warning-box {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }
        .info-box {
            background-color: #e3f2fd;
            border: 1px solid #90caf9;
            border-radius: 5px;
            padding: 15px;
            margin: 10px 0;
        }
        .doc-badge {
            display: inline-block;
            padding: 3px 8px;
            margin: 2px;
            background-color: #e1f5fe;
            border-radius: 15px;
            font-size: 12px;
            border: 1px solid #0277bd;
        }
        
        /* NEW: Clickable source sentence styling */
        .clickable-sentence {
            background: linear-gradient(120deg, #a8e6cf 0%, #dcedc1 100%);
            border: 1px solid #4caf50;
            border-radius: 6px;
            padding: 8px 12px;
            margin: 4px 0;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            display: inline-block;
            max-width: 100%;
            word-wrap: break-word;
        }
        
        .clickable-sentence:hover {
            background: linear-gradient(120deg, #4caf50 0%, #8bc34a 100%);
            color: white;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
        }
        
        .clickable-sentence::after {
            content: "🔍";
            position: absolute;
            right: 8px;
            top: 50%;
            transform: translateY(-50%);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .clickable-sentence:hover::after {
            opacity: 1;
        }
        
        .sentence-search-result {
            background: #fff3cd;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            position: relative;
        }
        
        .sentence-search-result::before {
            content: "📍";
            position: absolute;
            top: -10px;
            left: 20px;
            background: white;
            padding: 0 8px;
            font-size: 1.2rem;
        }
        
        .highlighted-sentence {
            background: #ffeb3b;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: bold;
        }
        
        .search-context {
            background: #f8f9fa;
            padding: 0.5rem;
            border-radius: 4px;
            margin-top: 0.5rem;
            font-size: 0.9rem;
            color: #666;
        }
    </style>
    """, unsafe_allow_html=True)

    # Add this CSS to your existing styles
    st.markdown("""
        <style>
            .document-link-button {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.5rem 1rem;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white !important;
                text-decoration: none !important;
                border-radius: 6px;
                font-size: 0.85rem;
                font-weight: 500;
                border: none;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .document-link-button:hover {
                background: linear-gradient(135deg, #2a5298 0%, #3d5998 100%);
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(42, 82, 152, 0.4);
            }
        </style>
        """, unsafe_allow_html=True)
    
    # Header
    st.title("🔍 Policy Document Inconsistency Analyzer")
    st.markdown("---")
    
    # Load data
    data = load_facts_data()
    inconsistent_facts, consistent_facts = categorize_facts(data)
    source_docs = load_policy_source_documents_from_files()
    
    # Create main layout
    st.markdown('<div class="facts-modal-body">', unsafe_allow_html=True)
    
    # Main content area
    main_col, source_col = st.columns([2, 1])
    
    with main_col:
        st.markdown('<div class="facts-main-content">', unsafe_allow_html=True)
        
        # Sidebar controls
        st.sidebar.header("📊 Dashboard Controls")
        
        # File upload option
        uploaded_file = st.sidebar.file_uploader("Upload JSON Data", type=['json'])
        if uploaded_file is not None:
            data = json.load(uploaded_file)
            inconsistent_facts, consistent_facts = categorize_facts(data)
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📋 Total Objective Facts", 
                value=len(data),
                help="Total number of objective facts analyzed"
            )
        
        with col2:
            st.metric(
                label="⚠️ Inconsistent Facts", 
                value=len(inconsistent_facts),
                delta=f"-{len(inconsistent_facts)} conflicts",
                delta_color="inverse",
                help="Fields with conflicting values across documents"
            )
        
        with col3:
            st.metric(
                label="✅ Consistent Facts", 
                value=len(consistent_facts),
                delta=f"+{len(consistent_facts)} aligned",
                delta_color="normal",
                help="Fields with consistent values across documents"
            )
        
        with col4:
            consistency_rate = (len(consistent_facts) / len(data)) * 100 if data else 0
            st.metric(
                label="📈 Consistency Rate", 
                value=f"{consistency_rate:.1f}%",
                help="Percentage of consistent policy fields"
            )
        
        # Main content tabs (same as before)
        tab1, tab2, tab3 = st.tabs(["📋 All Facts", "🚨 Inconsistencies", "✅ Consistent Facts"])
        
        with tab1:
            st.header("📋 All Objective Facts Overview")
            
            if not data:
                st.warning("No data available to display.")
            else:
                st.markdown("""
                <div class="info-box">
                    <strong>📋 Complete Facts Inventory:</strong> This section displays all objective facts extracted from your policy documents, 
                    organized by policy field. Each fact includes its value, source document, source sentence, context, and reference information.
                </div>
                """, unsafe_allow_html=True)
                
                # Display all facts with clickable source sentences
                for idx, (field_name, facts) in enumerate(data.items(), 1):
                    status = "Inconsistent" if len(facts) > 1 and field_name in ['security_training_frequency', 'information_security_risk_assessment_frequency', 'recovery_time_objective', 'password_minimum_length'] else "Consistent"
                    status_emoji = "⚠️" if status == "Inconsistent" else "✅"
                    
                    fact_name = facts[0]["fact_name"]
                    if not fact_name:
                        fact_name = field_name.replace('_', ' ').title()
                    
                    with st.expander(f"{status_emoji} {field_name.replace('_', ' ').title()} ({len(facts)} fact{'s' if len(facts) > 1 else ''})", expanded=False):
                        st.markdown(f"**Policy Field:** `{fact_name}`")
                        st.markdown(f"**Status:** {status}")
                        
                        # Display facts with clickable source sentences
                        for fact_idx, fact in enumerate(facts):
                            col1, col2, col3, col4 = st.columns([1, 2, 3, 1])
                            
                            with col1:
                                st.markdown(f"**Value:** {fact['value']}")
                            
                            with col2:
                                st.markdown(f"**Document:** {fact['document_title']}")
                            
                            with col3:
                                source_sentence = fact.get("source_sentence", "N/A")
                                print(source_sentence)
                                if source_sentence != "N/A":
                                    # Create clickable sentence
                                    sentence_key = f"all_facts_search_{field_name}_{fact_idx}_{hash(source_sentence) % 10000}"
                                    if st.button(
                                        f"🔍 {source_sentence[:80]}{'...' if len(source_sentence) > 80 else ''}", 
                                        key=sentence_key,
                                        help=f"Click to find this sentence in {fact['document_title']}",
                                        use_container_width=True
                                    ):
                                        # Search for the sentence in the source document
                                        source_docs = load_policy_source_documents_from_files()
                                        doc_title = fact['document_title']
                                        
                                        # Find the matching document
                                        matching_doc = None
                                        for filename, doc_info in source_docs.items():
                                            if filename == doc_title:
                                                matching_doc = doc_info
                                                break
                                        # print(matching_doc)
                                        if matching_doc:
                                            found, context, position = search_sentence_in_document(
                                                source_sentence, 
                                                matching_doc['content']
                                            )
                                            if found:
                                                st.session_state.search_result = {
                                                    'sentence': source_sentence,
                                                    'document': doc_title,
                                                    'context': context,
                                                    'position': position
                                                }
                                            else:
                                                st.session_state.search_result = {
                                                    'sentence': source_sentence,
                                                    'document': doc_title,
                                                    'context': "Sentence not found in document",
                                                    'position': None
                                                }
                                        else:
                                            st.session_state.search_result = {
                                                'sentence': source_sentence,
                                                'document': doc_title,
                                                'context': "Source document not found",
                                                'position': None
                                            }
                                
                                else:
                                    st.markdown("*No source sentence available*")
                            
                            with col4:
                                st.markdown(f"**Ref:** {fact['reference']}")
                            
                            st.markdown("---")
                        
                        # Display search result if available
                        if st.session_state.search_result:
                            result = st.session_state.search_result
                            st.markdown(f"""
                            <div class="sentence-search-result">
                                <h4>📍 Search Result</h4>
                                <p><strong>Document:</strong> {result['document']}</p>
                                <p><strong>Searching for:</strong> "{result['sentence']}"</p>
                                <div class="search-context">
                                    {result['context']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Clear search result button
                            if st.button("❌ Clear Search Result", key=f"clear_all_facts_search_{field_name}"):
                                st.session_state.search_result = None
                                st.rerun()
                        
                        if status == "Inconsistent":
                            st.markdown("""
                            <div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; margin-top: 10px;">
                                <strong>⚠️ Action Required:</strong> This field has conflicting values across documents. Review and standardize to ensure consistency.
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style="background-color: #d4edda; padding: 10px; border-radius: 5px; margin-top: 10px;">
                                <strong>✅ Well Aligned:</strong> This field maintains consistent values across all documents.
                            </div>
                            """, unsafe_allow_html=True)
        
        with tab2:
            st.header("⚠️ Policy Inconsistencies Requiring Attention")
            
            if not inconsistent_facts:
                st.success("🎉 No inconsistencies found! All policies are aligned.")
            else:
                st.markdown("""
                <div class="warning-box">
                    <strong>⚠️ Critical Issues Found:</strong> The following policy fields have conflicting values across different documents. 
                    This may lead to confusion, compliance issues, or operational problems.
                </div>
                """, unsafe_allow_html=True)
                
                # Session state for sentence search is initialized in main()
                
                for idx, (field_name, facts) in enumerate(inconsistent_facts.items(), 1):
                    with st.expander(f"🔴 {field_name.replace('_', ' ').title()} ({len(facts)} conflicts)", expanded=True):
                        display_fact_name = facts[0]['fact_name'] if len(set(fact['fact_name'] for fact in facts)) == 1 else field_name.replace('_', ' ').title()
                        st.markdown(f"**Policy Field:** {display_fact_name}")
                        
                        # Display facts with clickable source sentences
                        for fact_idx, fact in enumerate(facts):
                            col1, col2, col3, col4 = st.columns([1, 2, 3, 1])
                            
                            with col1:
                                st.markdown(f"**Value:** {fact['value']}")
                            
                            with col2:
                                st.markdown(f"**Document:** {fact['document_title']}")
                            
                            with col3:
                                source_sentence = fact.get("source_sentence", "N/A")
                                if source_sentence != "N/A":
                                    # Create clickable sentence
                                    sentence_key = f"search_{field_name}_{fact_idx}_{hash(source_sentence) % 10000}"
                                    if st.button(
                                        f"🔍 {source_sentence[:80]}{'...' if len(source_sentence) > 80 else ''}", 
                                        key=sentence_key,
                                        help=f"Click to find this sentence in {fact['document_title']}",
                                        use_container_width=True
                                    ):
                                        # Search for the sentence in the source document
                                        source_docs = load_policy_source_documents_from_files()
                                        doc_title = fact['document_title']
                                        
                                        # Find the matching document
                                        matching_doc = None
                                        for filename, doc_info in source_docs.items():
                                            if filename == doc_title:
                                                matching_doc = doc_info
                                                break
                                        
                                        if matching_doc:
                                            found, context, position = search_sentence_in_document(
                                                source_sentence, 
                                                matching_doc['content']
                                            )
                                            if found:
                                                st.session_state.search_result = {
                                                    'sentence': source_sentence,
                                                    'document': doc_title,
                                                    'context': context,
                                                    'position': position
                                                }
                                            else:
                                                st.session_state.search_result = {
                                                    'sentence': source_sentence,
                                                    'document': doc_title,
                                                    'context': "Sentence not found in document",
                                                    'position': None
                                                }
                                        else:
                                            st.session_state.search_result = {
                                                'sentence': source_sentence,
                                                'document': doc_title,
                                                'context': "Source document not found",
                                                'position': None
                                            }
                                
                                else:
                                    st.markdown("*No source sentence available*")
                            
                            with col4:
                                st.markdown(f"**Ref:** {fact['reference']}")
                            
                            st.markdown("---")
                        
                        # Display search result if available
                        if st.session_state.search_result:
                            result = st.session_state.search_result
                            st.markdown(f"""
                            <div class="sentence-search-result">
                                <h4>📍 Search Result</h4>
                                <p><strong>Document:</strong> {result['document']}</p>
                                <p><strong>Searching for:</strong> "{result['sentence']}"</p>
                                <div class="search-context">
                                    {result['context']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Clear search result button
                            if st.button("❌ Clear Search Result", key=f"clear_search_{field_name}"):
                                st.session_state.search_result = None
                                st.rerun()
                        
                        st.markdown("""
                        <div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; margin-top: 10px;">
                            <strong>💡 Recommendation:</strong> Review and standardize this policy across all documents to ensure consistency.
                        </div>
                        """, unsafe_allow_html=True)
        
        with tab3:
            st.header("✅ Consistent Policy Facts")
            
            if not consistent_facts:
                st.warning("No consistent facts found in the current dataset.")
            else:
                st.markdown("""
                <div class="info-box">
                    <strong>✅ Well-Aligned Policies:</strong> These policy fields have consistent values across documents, 
                    indicating good policy governance and documentation practices.
                </div>
                """, unsafe_allow_html=True)
                
                for field_name, facts in consistent_facts.items():
                    fact = facts[0]
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div class="consistent-metric">
                            <h4>{field_name.replace('_', ' ').title()}</h4>
                            <p><strong>Value:</strong> {fact['value']}</p>
                            <p><strong>Source Sentence:</strong> "{fact.get('source_sentence', 'N/A')[:100]}{'...' if len(fact.get('source_sentence', '')) > 100 else ''}"</p>
                            <span class="doc-badge">{fact['document_title']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("✅ **Consistent**")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with source_col:
        st.markdown('<div class="facts-source-panel">', unsafe_allow_html=True)
        
        # Source documents header
        st.markdown(f"""
        <div class="facts-source-header">
            <h4 style="margin: 0; color: #1e3c72;">📄 Source Policy Documents ({len(source_docs)})</h4>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.85rem; color: #666;">
                Original policy documents referenced in the inconsistency analysis
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display source documents with full content
        for filename, doc_info in source_docs.items():
            with st.expander(f"📋 {doc_info['title']}", expanded=False):
                
                # Document metadata
                st.markdown(f"""
                **Type:** {doc_info['type']}  
                **Version:** {doc_info['version']}  
                **Last Updated:** {doc_info['last_updated']}  
                **File:** `{filename}`
                """)
                
                st.markdown("**Full Document Content:**")
                # Display the full content in a scrollable container
                content_preview = doc_info["content"][:2000] + "..." if len(doc_info["content"]) > 2000 else doc_info["content"]
                st.markdown(f'<div class="policy-content-preview">{content_preview}</div>', unsafe_allow_html=True)
                
                # Add view full document button
                if st.button(f"📖 Show Complete Document", key=f"facts_view_{filename}", help=f"View complete {doc_info['title']}"):
                    # Create a modal-like display for full content
                    st.text_area(
                        f"Complete Content: {doc_info['title']}", 
                        value=doc_info["content"], 
                        height=400, 
                        help="Full document content"
                    )
        
        # Export options
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 Export Policies", use_container_width=True):
                st.download_button(
                    "📥 Download JSON",
                    json.dumps(source_docs, indent=2),
                    f"policy_sources_{uuid.uuid4().hex[:8]}.json",
                    "application/json",
                    use_container_width=True
                )
        
        with col2:
            if st.button("📊 Export Facts", use_container_width=True):
                st.download_button(
                    "📥 Download JSON",
                    json.dumps(data, indent=2),
                    f"facts_data_{uuid.uuid4().hex[:8]}.json",
                    "application/json",
                    use_container_width=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Close button for popup
    if st.button("✖️ Close Facts Overview", type="primary", use_container_width=True):
        st.session_state.show_facts_popup = False
        st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 14px;">
        Policy Document Inconsistency Analyzer | Built with ❤️ using Streamlit
    </div>
    """, unsafe_allow_html=True)

# Update your main function to use the new function
# Replace the call to show_facts_overview_popup() with show_facts_overview_popup_with_files()

def create_demo_landing_page():
    """Enhanced landing page specifically designed for auditor demonstrations"""
    
    # Demo-focused header with value proposition
    st.markdown("# 🔒 Organization Policy Analyzer")
    st.markdown("### AI-Powered Audit Intelligence for Policy Document Analysis")
    
    # Stats in columns
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    with stat_col1:
        st.metric("Policy Documents", "4")
    with stat_col2:
        st.metric("Key Insights", "23")
    with stat_col3:
        st.metric("Policy Consistency", "85%")
    
    st.divider()
    
    # Demo scenario context
    st.info("""
    **📋 Demo Scenario**
    
    **Organization:** TechCorp Inc. | **Audit Scope:** Security & Risk Management Framework
    
    Sample documents include: Data Classification Policy, Business Continuity Plan, Information Security Policy, and IT Risk Management Framework
    """)
    
    # Main feature columns
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        # Interactive Mind Map Section
        with st.container(border=True):
            # Header with badge
            header_col1, header_col2 = st.columns([3, 1])
            with header_col1:
                st.markdown("### 🗺️ Interactive Mind Map")
            with header_col2:
                st.markdown("🏷️ **Core Feature**")
            
            st.markdown("**What it does for auditors:**")
            st.markdown("""
            - Visualizes policy relationships across documents
            - Identifies coverage gaps in control frameworks
            - Maps compliance requirements to actual controls
            - Provides hierarchical view of risk management structure
            """)
            
            # Demo preview box
            st.success("""
            **📊 Sample Insights in Demo:**
            • 4 interconnected policy documents  
            • 23 key audit findings mapped  
            • 3 levels of detail (expandable view)  
            • Cross-reference analysis included
            """)
            
            # Mind Map button
            if st.button(
                "🚀 Start Mind Map Demo", 
                type="primary", 
                use_container_width=True,
                help="Launch interactive visualization of TechCorp's policy framework"
            ):
                with st.spinner("Loading TechCorp policy analysis..."):
                    try:
                        markdown_content, audit_data = generate_audit_mindmap()
                        if markdown_content:
                            st.session_state.mindmap_generated = True
                            st.session_state.mindmap_content = markdown_content
                            st.session_state.mindmap_data = audit_data
                            st.session_state.show_fullscreen = True
                            st.success("✅ Mind map ready! Opening full analysis...")
                            st.rerun()
                        else:
                            st.error("❌ Demo data loading failed")
                    except Exception as e:
                        st.error(f"❌ Error loading demo: {str(e)}")
            
            # Quick metrics
            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("Documents", "4", delta=None)
            with metric_col2:
                st.metric("Insights", "23", delta=None)
    
    with col2:
        # Policy Inconsistency Analyzer Section
        with st.container(border=True):
            # Header with badge
            header_col1, header_col2 = st.columns([3, 1])
            with header_col1:
                st.markdown("### 📊 Policy Inconsistency Analyzer")
            with header_col2:
                st.markdown("🏷️ **Critical Tool**")
            
            st.markdown("**What it does for auditors:**")
            st.markdown("""
            - Automatically detects policy conflicts across documents
            - Highlights compliance risk areas requiring attention
            - Provides evidence trails with source references
            - Generates audit findings with recommendations
            """)
            
            # Alert-style demo preview
            st.warning("""
            **⚠️ Sample Findings in Demo:**
            • Password length requirements: 8 vs 12 characters  
            • Security training: Annual vs Quarterly frequency  
            • RTO requirements: 24hrs vs 48hrs conflict  
            • Risk assessment cycles: Inconsistent timing
            """)
            
            # Policy Analysis button
            if st.button(
                "🔍 Launch Policy Analysis Demo", 
                type="primary", 
                use_container_width=True,
                help="Analyze TechCorp's policy inconsistencies and compliance gaps"
            ):
                st.session_state.show_facts_popup = True
                st.rerun()
            
            # Load and display metrics
            try:
                facts_data = load_facts_data()
                inconsistent_facts, consistent_facts = categorize_facts(facts_data)
                
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric("Issues Found", len(inconsistent_facts), delta=None, delta_color="inverse")
                with metric_col2:
                    st.metric("Aligned Policies", len(consistent_facts), delta=None, delta_color="normal")
            except Exception as e:
                # Fallback metrics
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric("Issues Found", "8", delta=None, delta_color="inverse")
                with metric_col2:
                    st.metric("Aligned Policies", "15", delta=None, delta_color="normal")

    st.divider()

    # Demo guidance section
    st.markdown("### 🎯 Demo Flow Recommendation")
    
    # Create three columns for the steps
    step_col1, step_col2, step_col3 = st.columns(3)
    
    with step_col1:
        with st.container(border=True):
            st.markdown("#### 1️⃣ Start with Mind Map")
            st.markdown("Show the big picture view of policy framework relationships and audit scope")
    
    with step_col2:
        with st.container(border=True):
            st.markdown("#### 2️⃣ Deep Dive into Inconsistencies")
            st.markdown("Demonstrate specific policy conflicts that require auditor attention")
    
    with step_col3:
        with st.container(border=True):
            st.markdown("#### 3️⃣ Show Export Capabilities")
            st.markdown("Export findings for audit documentation and client reporting")



def add_demo_css():
    """Enhanced CSS styling for demo presentation"""
    st.markdown("""
    <style>
    .demo-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #3d5998 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(42, 82, 152, 0.3);
    }
    
    .demo-subtitle {
        font-size: 1.2rem;
        margin: 1rem 0;
        opacity: 0.9;
    }
    
    .demo-stats {
        display: flex;
        justify-content: center;
        gap: 3rem;
        margin-top: 1.5rem;
    }
    
    .demo-stat {
        text-align: center;
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    
    .demo-stat .stat-number {
        display: block;
        font-size: 2rem;
        font-weight: bold;
        color: #fff;
    }
    
    .demo-stat .stat-label {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    .demo-scenario {
        background: #e3f2fd;
        border: 1px solid #2196f3;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .demo-scenario h3 {
        color: #1565c0;
        margin-top: 0;
    }
    
    .demo-feature-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        height: 100%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .demo-feature-card:hover {
        border-color: #2a5298;
        box-shadow: 0 6px 20px rgba(42, 82, 152, 0.15);
        transform: translateY(-2px);
    }
    
    .feature-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .feature-header h2 {
        margin: 0;
        color: #1e3c72;
        font-size: 1.4rem;
    }
    
    .feature-badge {
        background: #ff4757;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .feature-description ul {
        margin: 1rem 0;
        padding-left: 1.2rem;
    }
    
    .feature-description li {
        margin: 0.5rem 0;
        color: #333;
    }
    
    .demo-preview {
        background: #f8f9fa;
        border-left: 4px solid #2a5298;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .demo-preview.alert-style {
        background: #fff3cd;
        border-left-color: #ffc107;
    }
    
    .quick-metrics {
        display: flex;
        justify-content: space-around;
        margin-top: 1rem;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    .quick-metrics.alert-border {
        border: 1px solid #ffc107;
    }
    
    .metric-item {
        text-align: center;
    }
    
    .metric-item.inconsistent .metric-value {
        color: #dc3545;
    }
    
    .metric-item.consistent .metric-value {
        color: #28a745;
    }
    
    .metric-value {
        display: block;
        font-size: 1.8rem;
        font-weight: bold;
        color: #2a5298;
    }
    
    .metric-name {
        font-size: 0.9rem;
        color: #666;
    }
    
    .demo-guidance {
        background: #fff;
        border: 2px solid #28a745;
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    
    .demo-guidance h3 {
        color: #155724;
        margin-top: 0;
    }
    
    .demo-steps {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }
    
    .step-item {
        flex: 1;
        min-width: 200px;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
    }
    
    .step-number {
        background: #28a745;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        flex-shrink: 0;
    }
    
    .step-content strong {
        color: #155724;
    }
    
    .step-content p {
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)

# Update the main function to use the demo landing page
def main():
    """Demo-focused three-panel interface for auditor presentations"""
    st.set_page_config(
        page_title="Policy Analyzer Demo - Audit Intelligence Platform", 
        layout="wide",
        page_icon="🔒"
    )

    # Add demo-specific CSS
    add_demo_css()

    # Initialize session state
    if 'selected_doc_id' not in st.session_state:
        st.session_state.selected_doc_id = None
    
    if 'mindmap_generated' not in st.session_state:
        st.session_state.mindmap_generated = False
        st.session_state.mindmap_content = None
        st.session_state.mindmap_data = None
    
    if 'show_fullscreen' not in st.session_state:
        st.session_state.show_fullscreen = False
    
    if 'show_facts_popup' not in st.session_state:
        st.session_state.show_facts_popup = False
    
    if 'search_result' not in st.session_state:
        st.session_state.search_result = None


    # Handle modal states first
    if st.session_state.show_fullscreen and st.session_state.mindmap_content:
        show_fullscreen_mindmap(st.session_state.mindmap_content, st.session_state.mindmap_data)
        return
    
    if st.session_state.show_facts_popup:
        show_facts_overview_popup_with_files()
        return

    # Main demo landing page
    create_demo_landing_page()

if __name__ == "__main__":
    main()