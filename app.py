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
from streamlit_markmap import markmap

# Keep the existing Pydantic models for compatibility
class AuditSubNode(BaseModel):
    sub_title: str = Field(description="3-5 words describing this specific aspect")
    sub_content: str = Field(description="Brief specific point (max 40 words)")

class AuditInsightNode(BaseModel):
    node_title: str = Field(description="5-7 words describing the audit insight", max_length=50)
    sub_nodes: List[AuditSubNode] = Field(description="2-4 specific sub-aspects of this insight", min_items=2, max_items=4)

class ProcessedAuditDocument(BaseModel):
    document_id: str
    document_title: str
    document_type: str
    audit_insights: List[AuditInsightNode] = Field(description="3-6 most important audit insights from this document")

class UnifiedAuditMindMap(BaseModel):
    unified_title: str = Field(description="5-7 words summarizing the audit scope of all documents")
    audit_context: str = Field(description="Brief description of what this collection tells auditors")
    documents: List[ProcessedAuditDocument] = Field(description="All processed documents with audit insights")
    
    @model_validator(mode="after")
    def validate_audit_structure(self) -> Self:
        if not self.documents:
            raise ValueError("Must have at least one document")
        if len(self.unified_title.split()) > 7:
            raise ValueError("Unified title must be 5-7 words maximum")
        return self

class AuditMindMapWarning(Warning):
    """Warning for audit mind map generation failures"""

# MODIFIED FUNCTIONS TO USE STATIC MARKDOWN FILE

def load_static_mindmap() -> tuple:
    """Load the pre-saved mindmap markdown file"""
    mindmap_file = "mindmap_5038c8c4.md"
    
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

def show_fullscreen_mindmap(mindmap_content: str, audit_data: Dict):
    """Display fullscreen mind map modal similar to NotebookLM"""
    
    # Modal CSS styling
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
        width: 95vw;
        height: 95vh;
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
    }
    
    .mindmap-body {
        flex: 1;
        padding: 1rem;
        overflow: auto;
        background: #f8f9fa;
    }
    
    .close-btn {
        background: rgba(255,255,255,0.2);
        border: 1px solid rgba(255,255,255,0.3);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .close-btn:hover {
        background: rgba(255,255,255,0.3);
        border-color: rgba(255,255,255,0.5);
    }
    
    .mindmap-stats {
        display: flex;
        gap: 2rem;
        margin-bottom: 1rem;
        padding: 1rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
        height: calc(100% - 150px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)
    
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
        markmap(mindmap_content, height=600)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
        
        with col1:
            if st.button("💾 Download", use_container_width=True):
                st.download_button(
                    "📥 Download MD",
                    mindmap_content,
                    f"mindmap_{uuid.uuid4().hex[:8]}.md",
                    "text/markdown",
                    use_container_width=True
                )
        
        with col2:
            if st.button("📊 Export JSON", use_container_width=True):
                st.download_button(
                    "📥 Download JSON",
                    json.dumps(audit_data, indent=2),
                    f"mindmap_data_{uuid.uuid4().hex[:8]}.json",
                    "application/json",
                    use_container_width=True
                )
        
        with col3:
            if st.button("🔄 Regenerate", use_container_width=True):
                st.session_state.mindmap_generated = False
                st.session_state.show_fullscreen = False
                st.rerun()
        
        with col4:
            if st.button("✖️ Close Fullscreen View", type="primary", use_container_width=True):
                st.session_state.show_fullscreen = False
                st.rerun()

# Facts Overview Functions (keeping unchanged from original)
def load_facts_data():
    """Load the policy data"""
    sample_data = {
    "tls_version_for_data_transmission": [
        {
        "value": "TLS 1.2",
        "document_title": "Encryption Management.md",
        "fact_name": "Transport Layer Security version for data transmission",
        "source_sentence": "Transport Layer Security TLS 1.2",
        "context": "Standard for encrypting data channels between end-users and application backend",
        "reference": "Encryption standards - Data Transmission - Full Document (Section 1)"
        }
    ],
    "scp_encryption_strength": [
        {
        "value": "At least AES 128",
        "document_title": "Encryption Management.md",
        "fact_name": "Secure Copy Protocol encryption strength",
        "source_sentence": "Secure Copy Protocol At least AES 128",
        "context": "Standard for encrypting data channels using SCP",
        "reference": "Encryption standards - Data Transmission - Full Document (Section 1)"
        }
    ],
    "dsa_minimum_key_size": [
        {
        "value": "1024",
        "document_title": "Encryption Management.md",
        "fact_name": "Digital Signature Algorithm minimum key size",
        "source_sentence": "Digital Signatures DSA, with key size of at least 1024",
        "context": "Minimum key size for DSA digital signatures",
        "reference": "Encryption standards - Data Transmission - Full Document (Section 1)"
        }
    ],
    "rsa_minimum_key_size_for_digital_signatures": [
        {
        "value": "1024",
        "document_title": "Encryption Management.md",
        "fact_name": "RSA minimum key size for digital signatures",
        "source_sentence": "RSA, with key size of at least 1024",
        "context": "Minimum key size for RSA digital signatures",
        "reference": "Encryption standards - Data Transmission - Full Document (Section 1)"
        }
    ],
    "aes_encryption_strength_for_data_at_rest_current": [
        {
        "value": "AES256",
        "document_title": "Encryption Management.md",
        "fact_name": "AES encryption strength for data at rest (current standard)",
        "source_sentence": "[Cloud Hosting Service] on which [Company Name]'s customers' data resides, encrypts all customer content stored at rest using AES256, except a small number of Persistent Disks created before 2015 that use AES128.",
        "context": "Encryption strength for customer content stored at rest",
        "reference": "Data Storage - Full Document (Section 1)"
        }
    ],
    "aes_encryption_strength_for_data_at_rest_legacy": [
        {
        "value": "AES128",
        "document_title": "Encryption Management.md",
        "fact_name": "AES encryption strength for data at rest (legacy disks)",
        "source_sentence": "[Cloud Hosting Service] on which [Company Name]'s customers' data resides, encrypts all customer content stored at rest using AES256, except a small number of Persistent Disks created before 2015 that use AES128.",
        "context": "Encryption strength for persistent disks created before 2015",
        "reference": "Data Storage - Full Document (Section 1)"
        }
    ],
    "aes_additional_encryption_options": [
        {
        "value": "AES 128 and AES 256",
        "document_title": "Encryption Management.md",
        "fact_name": "Advanced Encryption Standard options for additional encryption",
        "source_sentence": "Advanced Encryption Standard AES 128 and AES 256",
        "context": "Standards for additional encryption of data at rest",
        "reference": "Data Storage - Encryption standards - Full Document (Section 1)"
        }
    ],
    "sha_additional_encryption_options": [
        {
        "value": "SHA 2 and SHA 3",
        "document_title": "Encryption Management.md",
        "fact_name": "Secure Hash Algorithm options for additional encryption",
        "source_sentence": "Secure Hash Algorithm SHA 2 and SHA 3",
        "context": "Hashing standards for additional encryption of data at rest",
        "reference": "Data Storage - Encryption standards - Full Document (Section 1)"
        }
    ],
    "secure_password_storing_method": [
        {
        "value": "bcrypt hashing function",
        "document_title": "Encryption Management.md",
        "fact_name": "Secure password storing method",
        "source_sentence": "Secure Password Storing bcrypt hashing function",
        "context": "Standard for secure password storage",
        "reference": "Data Storage - Encryption standards - Full Document (Section 1)"
        }
    ],
    "on_call_engineer_coverage": [
        {
        "value": "24/7/365",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "On-call engineer coverage",
        "source_sentence": "On-call engineer: 24/7/365 reacts to system outages; Informs service owners and other interested (impacted) parties about the system outage;",
        "context": "Continuous on-call engineer availability for system outages",
        "reference": "Roles and responsibilities - Introduction + Owner + Approver + Last Approved + Scope and applicability + Roles and responsibilities (Section 1)"
        }
    ],
    "recovery_time_objective": [
        {
        "value": "72 hours",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "Recovery time objective (RTO)",
        "source_sentence": "[Company Name] commits externally to an RTO of 72 hours.",
        "context": "Maximum allowed downtime for system resources before unacceptable business impact",
        "reference": "Requirements for the production availability - Definitions + General company\u02bcs DRP + Requirements for the production availability + Monitoring and notification (Section 2)"
        },
        {
        "value": "between an hour and a day",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "Recovery Time Objective (RTO)",
        "source_sentence": "an RTO of between an hour and a day, which allows for a warm failover in a disaster scenario, with some components of the application running all the time in a standby mode - such as databases - while others are scaled out in the event of an actual disaster, such as web servers.",
        "context": "Timeframe for restoring operations after a disaster",
        "reference": "Disaster Recovery Plan, first section - Disaster Recovery Plan + Create and deploy DRP + Activation and notification stage (Section 12)"
        }
    ],
    "recovery_point_objective_customer_facing_applications": [
        {
        "value": "1 hour",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "Recovery Point Objective (RPO) for customer-facing applications",
        "source_sentence": "[Company Name]'s customer-facing applications have an RPO of an hour, so they take advantage of asynchronous replication.",
        "context": "RPO defines the maximum targeted period in which data might be lost due to a major incident.",
        "reference": "Approach for data availability - Disaster Recovery + Approach for data availability + Monitoring of database backup creation and restoration (Section 5)"
        }
    ],
    "database_backup_frequency": [
        {
        "value": "every 30 minutes",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "Database backup frequency",
        "source_sentence": "[Company Name] backs up every 30 minutes of databases with customers' data, logging, and billing information to another [Cloud Hosting Service] region.",
        "context": "Frequency at which customer data, logging, and billing databases are backed up to another region.",
        "reference": "Approach for data availability - Disaster Recovery + Approach for data availability + Monitoring of database backup creation and restoration (Section 5)"
        }
    ],
    "postgres_snapshot_frequency": [
        {
        "value": "hourly",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "Postgres snapshot frequency",
        "source_sentence": "Postgres machines have hourly snapshots of their data drives, so restoring from those snapshots and replaying the queues should result in very little to no data loss.",
        "context": "Frequency of data drive snapshots for Postgres machines",
        "reference": "Data loss - Disaster Recovery Plan + Data loss + Recovery + Impact + [Company Name] Status + Data loss + SQL outage + Recovery (Section 7)"
        }
    ],
    "application_disaster_recovery_plan_percentage": [
        {
        "value": "12",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "Percentage of applications with Disaster Recovery Plan",
        "source_sentence": "Application | % of Apps | Examples apps | RTO & RPO values\nDisaster Recovery Plan | 12 |  | ",
        "context": "Percentage of applications covered by a Disaster Recovery Plan",
        "reference": "Defining Availability Requirements - Table - Determine recovery requirements + Disaster Recovery Plan + Defining Availability Requirements + Recovery Point Objective (RPO) + Recovery Time Objective (RTO) (Section 10)"
        }
    ],
    "tier_1_system_percentage": [
        {
        "value": "5%",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "Tier 1 system percentage",
        "source_sentence": "1 (most important) | 5% | Global or external customer-facing applications such as real-time payments and eCommerce storefronts. | 4 hours | 72 hours",
        "context": "Percentage of systems classified as Tier 1 (most important)",
        "reference": "System Tiering Table - Disaster Recovery Plan + System Tiering + Choose Disaster Recovery Strategy (Section 11)"
        }
    ],
    "tier_1_system_recovery_point_objective": [
        {
        "value": "4 hours",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "Tier 1 system RPO",
        "source_sentence": "1 (most important) | 5% | Global or external customer-facing applications such as real-time payments and eCommerce storefronts. | 4 hours | 72 hours",
        "context": "Recovery Point Objective for Tier 1 systems",
        "reference": "System Tiering Table - Disaster Recovery Plan + System Tiering + Choose Disaster Recovery Strategy (Section 11)"
        }
    ],
    "tier_1_system_recovery_time_objective": [
        {
        "value": "72 hours",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "Tier 1 system RTO",
        "source_sentence": "1 (most important) | 5% | Global or external customer-facing applications such as real-time payments and eCommerce storefronts. | 4 hours | 72 hours",
        "context": "Recovery Time Objective for Tier 1 systems",
        "reference": "System Tiering Table - Disaster Recovery Plan + System Tiering + Choose Disaster Recovery Strategy (Section 11)"
        }
    ],
    "tier_2_system_percentage": [
        {
        "value": "35%",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "Tier 2 system percentage",
        "source_sentence": "Tier 2 | 35% | Regional or important internal applications such as CRM or ERP. | Up to 1 day |",
        "context": "Percentage of systems classified as Tier 2",
        "reference": "System Tiering Table - Disaster Recovery Plan + System Tiering + Choose Disaster Recovery Strategy (Section 11)"
        }
    ],
    "tier_2_system_recovery_point_objective": [
        {
        "value": "Up to 1 day",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "Tier 2 system RPO",
        "source_sentence": "Tier 2 | 35% | Regional or important internal applications such as CRM or ERP. | Up to 1 day |",
        "context": "Recovery Point Objective for Tier 2 systems",
        "reference": "System Tiering Table - Disaster Recovery Plan + System Tiering + Choose Disaster Recovery Strategy (Section 11)"
        }
    ],
    "tier_3_system_percentage": [
        {
        "value": "60%",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "Tier 3 system percentage",
        "source_sentence": "Tier 3 (least important) | 60% | Team or departmental applications, such as back-office, leave booking, internal travel, accounting, and HR. | More than 1 day |",
        "context": "Percentage of systems classified as Tier 3 (least important)",
        "reference": "System Tiering Table - Disaster Recovery Plan + System Tiering + Choose Disaster Recovery Strategy (Section 11)"
        }
    ],
    "tier_3_system_recovery_point_objective": [
        {
        "value": "More than 1 day",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "Tier 3 system RPO",
        "source_sentence": "Tier 3 (least important) | 60% | Team or departmental applications, such as back-office, leave booking, internal travel, accounting, and HR. | More than 1 day |",
        "context": "Recovery Point Objective for Tier 3 systems",
        "reference": "System Tiering Table - Disaster Recovery Plan + System Tiering + Choose Disaster Recovery Strategy (Section 11)"
        }
    ],
    "high_impact_system_disaster_recovery_plan_test_frequency": [
        {
        "value": "Annually or after significant changes",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "High-impact system DRP test frequency",
        "source_sentence": "A full-scale functional exercise should be conducted annually or after significant changes to the system.",
        "context": "Frequency of full-scale functional disaster recovery exercise for high-impact systems",
        "reference": "System criticality table - Periodically test DRP + Disaster Recovery Plan + Disaster Recovery Plan (Section 17)"
        }
    ],
    "disaster_recovery_plan_review_frequency": [
        {
        "value": "annually or whenever significant changes occur",
        "document_title": "Disaster Recovery Plan.md",
        "fact_name": "Disaster Recovery Plan review frequency",
        "source_sentence": "It is essential that the DRP be reviewed and updated annually or whenever significant changes occur to any plan element to ensure that new information is documented and contingency measures are revised if required.",
        "context": "Specifies the required frequency for reviewing and updating the DRP",
        "reference": "Disaster Recovery Plan section - Documentation of Results + Additional Testing Recommendations + Disaster Recovery Plan (Section 19)"
        }
    ],
    "password_minimum_length": [
        {
        "value": "12 characters",
        "document_title": "Antivirus Management Procedure.md",
        "fact_name": "Password minimum length",
        "source_sentence": "Minimum Password length 12 characters",
        "context": "",
        "reference": "Section 4.2 Regular scans and monitoring - Investigating received reports of potential malware. + 4. Antivirus management procedure + 4.1 Antivirus software Installation and maintenance + 4.2 Regular scans and monitoring (Section 2)"
        },
        {
        "value": "15 characters",
        "document_title": "Access Management Policy.md",
        "fact_name": "Password minimum length",
        "source_sentence": "Password minimum characters length required 15.",
        "context": "Specifies the minimum number of characters required for user passwords",
        "reference": "User Access Management - Full Document (Section 1)"
        }
    ],
    "security_training_frequency": [
        {
        "value": "quarterly",
        "document_title": "Antivirus Management Procedure.md",
        "fact_name": "Security training frequency",
        "source_sentence": "During quaterly security training, employees are regularly introduced to various cyber security threats and the importance of anti-virus protection as an integral component of our security measures.",
        "context": "Frequency of employee security training sessions",
        "reference": "6. User awareness - 6. User awareness + 7. Violation of the policy + Antivirus Management + Procedure + History of the document (Section 7)"
        },
        {
        "value": "Annual",
        "document_title": "Data Management Policy.md",
        "fact_name": "Data awareness and privacy training frequency",
        "source_sentence": "[Company Name] shall hold annual data awareness and data privacy trainings to ensure data protection standards and best practice are communicated across the organization.",
        "context": "Frequency of mandatory data awareness and privacy training for employees",
        "reference": "Data Protection - Data Protection + Review + Legal + Data Anonymization + Data Management + Policy (Section 9)"
        },
        {
        "value": "monthly",
        "document_title": "Information Security Policy.md",
        "fact_name": "Security training frequency",
        "source_sentence": "In addition, they also pass the security training during onboarding and repeat it monthly.",
        "context": "Frequency of recurring security training for personnel",
        "reference": "Security awareness - Full Document (Section 1)"
        }
    ],
    "data_retention_requirements_review_frequency": [
        {
        "value": "Annual",
        "document_title": "Data Management Policy.md",
        "fact_name": "Data retention requirements review frequency",
        "source_sentence": "Management shall review data retention requirements during the annual review of this policy.",
        "context": "Frequency of management review of data retention requirements",
        "reference": "Review - Data Protection + Review + Legal + Data Anonymization + Data Management + Policy (Section 9)"
        }
    ],
    "event_data_deletion_period": [
        {
        "value": "90 days",
        "document_title": "Data Management Policy.md",
        "fact_name": "Event data deletion period",
        "source_sentence": "Event Data ... 90 days unless the customer account is deleted.",
        "context": "Time after which event data is deleted if not associated with a deleted customer account",
        "reference": "Data Management Policy / APPENDIX B \u2013 Data Retention Additional Guidance - Customer Accounts: + Data Management + Policy + APPENDIX B \u2013 Data Retention Additional Guidance (Section 11)"
        }
    ],
    "event_data_deletion_after_account_deletion": [
        {
        "value": "within 24 hours of organization deletion",
        "document_title": "Data Management Policy.md",
        "fact_name": "Event data deletion after account deletion",
        "source_sentence": "If customer organization account is deleted, within 24 hours of organization deletion.",
        "context": "Timeframe for deleting event data after customer organization account is deleted",
        "reference": "Data Management Policy / APPENDIX B \u2013 Data Retention Additional Guidance - Customer Accounts: + Data Management + Policy + APPENDIX B \u2013 Data Retention Additional Guidance (Section 11)"
        }
    ],
    "employee_data_retention_period_after_employment": [
        {
        "value": "minimum 6 years after employment",
        "document_title": "Data Management Policy.md",
        "fact_name": "Employee data retention period after employment",
        "source_sentence": "Retain for the duration of employment + minimum 6 years after employment.",
        "context": "Retention period for employee data after employment ends",
        "reference": "Data Management Policy / APPENDIX B \u2013 Data Retention Additional Guidance - Customer Accounts: + Data Management + Policy + APPENDIX B \u2013 Data Retention Additional Guidance (Section 11)"
        }
    ],
    "financial_data_retention_period": [
        {
        "value": "minimum 7 years",
        "document_title": "Data Management Policy.md",
        "fact_name": "Financial data retention period",
        "source_sentence": "Minimum 7 years",
        "context": "Retention period for internal financial data",
        "reference": "Data Management Policy / APPENDIX B \u2013 Data Retention Additional Guidance - Customer Accounts: + Data Management + Policy + APPENDIX B \u2013 Data Retention Additional Guidance (Section 11)"
        }
    ],
    "access_rights_review_frequency": [
        {
        "value": "at least semi-annual",
        "document_title": "Access Management Policy.md",
        "fact_name": "Access rights review frequency",
        "source_sentence": "Administrators shall perform access rights reviews of production systems on at least a semi-annual basis to verify that user access is limited to systems that are required for their job function.",
        "context": "Frequency with which administrators must review access rights of production systems",
        "reference": "Access Rights Reviews - Full Document (Section 1)"
        }
    ],
    "maximum_access_termination_period": [
        {
        "value": "24 business hours",
        "document_title": "Access Management Policy.md",
        "fact_name": "Maximum access termination period",
        "source_sentence": "The maximum allowable time period for access termination is 24 business hours.",
        "context": "Maximum allowable time to remove access after employment or contract termination or change in job function",
        "reference": "Removal & Adjustment of Access Rights - Full Document (Section 1)"
        }
    ],
    "security_objectives_and_principles_review_frequency": [
        {
        "value": "at least annually",
        "document_title": "Information Security Policy.md",
        "fact_name": "Security objectives and principles review frequency",
        "source_sentence": "[Company Name] reviews security objectives and principles at least annually to reflect internal and external factors and requirements of the interested parties.",
        "context": "Frequency of reviewing security objectives and principles",
        "reference": "Policy - Full Document (Section 1)"
        }
    ],
    "information_security_risk_assessment_frequency": [
        {
        "value": "annually or upon significant change",
        "document_title": "Information Security Policy.md",
        "fact_name": "Information security risk assessment frequency",
        "source_sentence": "Information security risk assessments are conducted by the GRC team annually or upon significant change to the business, IT systems or [Company Name]\u02bcs products.",
        "context": "Frequency of information security risk assessments by GRC team",
        "reference": "Management planning - Full Document (Section 1)"
        },
        {
        "value": "quarterly",
        "document_title": "Risk Management Assessment and Treatment Policy.md",
        "fact_name": "Enterprise risk assessment frequency",
        "source_sentence": "An quaterly risk assessment covering the enterprise, including information assets as part of the initial implementation of the Information Security Management System (ISMS).",
        "context": "Frequency of enterprise-wide risk assessments as part of ISMS implementation",
        "reference": "Criteria for performing information security risk assessments - Criteria for performing information security risk assessments + Risk Assessment Methodology + Establish scope and context (Section 2)"
        },
        {
        "value": "Annually",
        "document_title": "Risk Management Assessment and Treatment Policy.md",
        "fact_name": "Annual risk assessment frequency",
        "source_sentence": "The annual risk assessment results shall be communicated to top management.",
        "context": "Specifies that risk assessment results are communicated annually",
        "reference": "Risk monitoring and reporting - Management approval + Risk monitoring and reporting + Regular review + Maintenance of the Risk Register/Treatment Plan (Section 11)"
        }
    ],
    "information_security_and_company_objectives_risk_review_frequency": [
        {
        "value": "quarterly",
        "document_title": "Information Security Policy.md",
        "fact_name": "Information security and company objectives risk review frequency",
        "source_sentence": "Risks to achieving information security and general company\u02bcs objectives are assessed and reviewed at the quarterly Board meetings and during the annual and quarterly OKRs planning process.",
        "context": "Frequency of risk reviews at Board meetings",
        "reference": "Management planning - Full Document (Section 1)"
        }
    ],
    "vendor_review_frequency": [
        {
        "value": "Annually",
        "document_title": "Vendor Management Policy.md",
        "fact_name": "Vendor review frequency",
        "source_sentence": "The vendor risk level will determine the level of diligence in the initial review and annually thereafter.",
        "context": "Frequency of ongoing vendor reviews after initial onboarding",
        "reference": "Monitoring, Evaluation & Review of Vendors and Integrations - Full Document (Section 1)"
        }
    ],
    "policy_review_frequency": [
        {
        "value": "Annually",
        "document_title": "Vendor Management Policy.md",
        "fact_name": "Policy review frequency",
        "source_sentence": "This policy will be reviewed annually.",
        "context": "Frequency of policy review",
        "reference": "Vendor Management Policy - Policy - Full Document (Section 1)"
        }
    ],
    "high_risk_vendor_compliance_review_frequency": [
        {
        "value": "Annual",
        "document_title": "Vendor Management Policy.md",
        "fact_name": "High risk vendor compliance review frequency",
        "source_sentence": "Annual compliance review of security documents (i.e CAIQ, SiG, white-papers) and certificates (ex: SOC 2, ISO 27001).",
        "context": "Frequency of compliance review for high risk vendors",
        "reference": "Renewal Vendor Review Criteria - Full Document (Section 1)"
        }
    ],
    "document_review_frequency": [
        {
        "value": "annually",
        "document_title": "Risk Management Assessment and Treatment Policy.md",
        "fact_name": "Document review frequency",
        "source_sentence": "This document shall be reviewed annually for approval.",
        "context": "Frequency with which the risk management policy document is reviewed for approval",
        "reference": "The Risk assessment and treatment process - Introduction + Owner + Approver + Last Reviewed + Roles and Responsibilities + The Risk assessment and treatment process (Section 1)"
        }
    ],
    "risk_likelihood_grading_scale": [
        {
        "value": "1 (low) to 5 (high)",
        "document_title": "Risk Management Assessment and Treatment Policy.md",
        "fact_name": "Risk likelihood grading scale",
        "source_sentence": "Graded on a numerical scale of 1 (low) to 5 (high).",
        "context": "Numerical scale used to grade risk likelihood",
        "reference": "Risk Management, Assessment, and Treatment Policy - Likelihood Determination - Perform Risk Analysis + Likelihood Determination + Risk Management, Assessment, and Treatment Policy (Section 4)"
        }
    ],
    "risk_impact_grading_scale": [
        {
        "value": "1 (low) to 5 (high)",
        "document_title": "Risk Management Assessment and Treatment Policy.md",
        "fact_name": "Risk impact grading scale",
        "source_sentence": "The impact of each risk will be graded on a numerical scale of 1 (low) to 5 (high).",
        "context": "Numerical scale used to grade risk impact",
        "reference": "Impact Determination, Table 2 - Impact Determination (Section 5)"
        }
    ],
    "risk_score_threshold_high_classification": [
        {
        "value": "12 or more",
        "document_title": "Risk Management Assessment and Treatment Policy.md",
        "fact_name": "Risk score threshold for High classification",
        "source_sentence": "Each risk will be allocated a classification based on its score as follows:\n\n- High: 12 or more",
        "context": "Defines the minimum risk score for a risk to be classified as High",
        "reference": "Risk Management, Assessment, and Treatment - Risk Management, Assessment, and Treatment + Policy + Risk Management, Assessment, and Treatment (Section 7)"
        }
    ],
    "risk_score_range_medium_classification": [
        {
        "value": "5 to 10 inclusive",
        "document_title": "Risk Management Assessment and Treatment Policy.md",
        "fact_name": "Risk score range for Medium classification",
        "source_sentence": "Each risk will be allocated a classification based on its score as follows:\n\n- Medium: 5 to 10 inclusive",
        "context": "Defines the risk score range for a risk to be classified as Medium",
        "reference": "Risk Management, Assessment, and Treatment - Risk Management, Assessment, and Treatment + Policy + Risk Management, Assessment, and Treatment (Section 7)"
        }
    ],
    "risk_score_range_low_classification": [
        {
        "value": "1 to 4 inclusive",
        "document_title": "Risk Management Assessment and Treatment Policy.md",
        "fact_name": "Risk score range for Low classification",
        "source_sentence": "Each risk will be allocated a classification based on its score as follows:\n\n- Low: 1 to 4 inclusive",
        "context": "Defines the risk score range for a risk to be classified as Low",
        "reference": "Risk Management, Assessment, and Treatment - Risk Management, Assessment, and Treatment + Policy + Risk Management, Assessment, and Treatment (Section 7)"
        }
    ]}
    return sample_data

def categorize_facts(data):
    """Categorize facts into consistent and inconsistent"""
    inconsistent_keys = ['security_training_frequency', 'information_security_risk_assessment_frequency', 
                        'recovery_time_objective', 'password_minimum_length']
    
    inconsistent_facts = {k: v for k, v in data.items() if k in inconsistent_keys and len(v) > 1}
    consistent_facts = {k: v for k, v in data.items() if k not in inconsistent_keys or len(v) == 1}
    
    return inconsistent_facts, consistent_facts

def show_facts_overview_popup():
    """Display Facts Overview popup with the complete policy analyzer"""
    
    # Facts Overview CSS
    st.markdown("""
    <style>
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
        .fact-metric {
            background-color: #f5f5f5;
            border: 2px solid #9e9e9e;
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
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("🔍 Policy Document Inconsistency Analyzer")
    st.markdown("---")
    
    # Load data
    data = load_facts_data()
    inconsistent_facts, consistent_facts = categorize_facts(data)
    
    # Sidebar
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
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 All Facts", "🚨 Inconsistencies", "✅ Consistent Facts", "📊 Analytics"])
    
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
            
            # Display all facts organized by policy field
            for idx, (field_name, facts) in enumerate(data.items(), 1):
                # Determine if this field is consistent or inconsistent
                status = "Inconsistent" if len(facts) > 1 and field_name in ['security_training_frequency', 'information_security_risk_assessment_frequency', 'recovery_time_objective', 'password_minimum_length'] else "Consistent"
                status_emoji = "⚠️" if status == "Inconsistent" else "✅"
                
                fact_name = facts[0]["fact_name"]
                if not fact_name:
                    fact_name = field_name.replace('_', ' ').title()
                
                with st.expander(f"{status_emoji} {field_name.replace('_', ' ').title()} ({len(facts)} fact{'s' if len(facts) > 1 else ''})", expanded=False):
                    st.markdown(f"**Policy Field:** `{fact_name}`")
                    st.markdown(f"**Status:** {status}")
                    
                    # Create facts table with updated columns
                    facts_data = []
                    for fact in facts:
                        facts_data.append({
                            "Value": fact["value"],
                            "Document": fact["document_title"],
                            "Fact Name": fact["fact_name"],
                            "Source Sentence": fact.get("source_sentence", "N/A"),
                            "Reference": fact["reference"]
                        })
                    
                    df = pd.DataFrame(facts_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Show status-specific information
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
            
            for idx, (field_name, facts) in enumerate(inconsistent_facts.items(), 1):
                with st.expander(f"🔴 {field_name.replace('_', ' ').title()} ({len(facts)} conflicts)", expanded=True):
                    # Use the most common fact_name or a generic one for the field
                    display_fact_name = facts[0]['fact_name'] if len(set(fact['fact_name'] for fact in facts)) == 1 else field_name.replace('_', ' ').title()
                    st.markdown(f"**Policy Field:** {display_fact_name}")
                    
                    # Create comparison table with updated columns
                    comparison_data = []
                    for fact in facts:
                        comparison_data.append({
                            "Value": fact["value"],
                            "Document": fact["document_title"],
                            "Source Sentence": fact.get("source_sentence", "N/A"),
                            "Reference": fact["reference"]
                        })
                    
                    df = pd.DataFrame(comparison_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Recommendation box
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
            
            # Create a clean display of consistent facts
            for field_name, facts in consistent_facts.items():
                fact = facts[0]  # Since consistent facts have only one entry
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="consistent-metric">
                        <h4>{field_name.replace('_', ' ').title()}</h4>
                        <p><strong>Value:</strong> {fact['value']}</p>
                        <p><strong>Source:</strong> "{fact.get('source_sentence', 'N/A')[:100]}{'...' if len(fact.get('source_sentence', '')) > 100 else ''}"</p>
                        <span class="doc-badge">{fact['document_title']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("✅ **Consistent**")
    
    with tab4:
        st.header("📊 Policy Consistency Analytics")
        
        # Consistency overview chart
        consistency_data = {
            'Status': ['Consistent', 'Inconsistent'],
            'Count': [len(consistent_facts), len(inconsistent_facts)],
            'Color': ['#4CAF50', '#F44336']
        }
        
        fig_pie = px.pie(
            values=consistency_data['Count'], 
            names=consistency_data['Status'],
            title="Overall Policy Consistency Distribution",
            color_discrete_map={'Consistent': '#4CAF50', 'Inconsistent': '#F44336'}
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Document-wise analysis
        if inconsistent_facts:
            st.subheader("📄 Documents Contributing to Inconsistencies")
            
            doc_inconsistencies = {}
            for field_name, facts in inconsistent_facts.items():
                for fact in facts:
                    doc_name = fact['document_title']
                    if doc_name not in doc_inconsistencies:
                        doc_inconsistencies[doc_name] = 0
                    doc_inconsistencies[doc_name] += 1
            
            doc_df = pd.DataFrame([
                {'Document': doc, 'Inconsistent Fields': count}
                for doc, count in doc_inconsistencies.items()
            ])
            
            fig_bar = px.bar(
                doc_df, 
                x='Document', 
                y='Inconsistent Fields',
                title="Inconsistent Fields by Document",
                color='Inconsistent Fields',
                color_continuous_scale='Reds'
            )
            fig_bar.update_xaxes(tickangle=45)
            st.plotly_chart(fig_bar, use_container_width=True)

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

# Sample documents (keeping empty as in original)
SAMPLE_DOCUMENTS = [
    {
        "id": "security_policy",
        "title": "Information Security Policy",
        "type": "Policy Document",
        "content": """
        This Information Security Policy establishes comprehensive security controls across the organization. 
        
        The policy mandates role-based access controls (RBAC) with quarterly access reviews conducted by system owners. Multi-factor authentication is required for all privileged accounts and remote access scenarios.
        
        Security incident response procedures require initial response within 2 hours for critical incidents, with mandatory escalation to the CISO for any incidents involving personal data or system compromise. All incidents must be documented in the central incident management system.
        
        Annual risk assessments are required for all critical systems, with results reported to the executive team and board of directors. Vulnerability scanning occurs monthly with critical vulnerabilities requiring remediation within 72 hours.
        
        Security awareness training is mandatory for all employees annually, with specialized training for privileged users every 6 months. Training completion is tracked and reported to management quarterly.
        
        Data classification requires all information to be labeled as Public, Internal, Confidential, or Restricted. Encryption is mandatory for all Confidential and Restricted data both in transit and at rest using AES-256 standards.
        
        Third-party security assessments are required before any vendor is granted access to organizational systems or data. Annual security questionnaires and on-site assessments are conducted for critical vendors.
        
        The policy is reviewed annually by the security committee and updated as needed. All policy violations are investigated and may result in disciplinary action up to and including termination.
        """
    },
    {
        "id": "data_governance",
        "title": "Data Governance Framework",
        "type": "Framework Document", 
        "content": """
        The Data Governance Framework establishes accountability for data quality, privacy, and lifecycle management across all business units.
        
        Data stewardship roles are defined with business data owners responsible for data quality and access decisions. Technical data custodians implement and maintain data security controls as directed by data owners.
        
        Personal data processing requires documented lawful basis under GDPR with privacy impact assessments mandatory for high-risk processing activities. Data subject rights requests must be fulfilled within 30 days with documented evidence of completion.
        
        Data retention schedules are established for all data categories with automated deletion processes where technically feasible. Legal hold procedures override standard retention when litigation or regulatory investigation is pending.
        
        Data quality monitoring includes automated data profiling with quality scorecards published monthly to data owners. Data quality issues affecting critical business processes trigger immediate investigation and remediation.
        
        Master data management processes ensure single source of truth for customer, product, and financial data. Change control procedures require approval from data owners before implementing any changes to master data definitions.
        
        Cross-border data transfers are governed by appropriate safeguards including Standard Contractual Clauses or adequacy decisions. Transfer logs are maintained and reviewed quarterly by the privacy office.
        
        Data breach response procedures integrate with overall incident response with specific timelines for privacy impact assessment and regulatory notification within 72 hours where required.
        """
    },
    {
        "id": "vendor_management",
        "title": "Third-Party Risk Management Policy",
        "type": "Risk Management Policy",
        "content": """
        Third-Party Risk Management Policy governs the assessment and ongoing monitoring of vendors with access to organizational data or systems.
        
        Vendor risk assessment is required before contract execution using standardized questionnaires and risk scoring methodology. Critical vendors undergo annual on-site security assessments conducted by qualified security professionals.
        
        Contract terms must include security requirements, right to audit clauses, and incident notification obligations. Data processing agreements are required for any vendor processing personal data on behalf of the organization.
        
        Ongoing monitoring includes quarterly business reviews for critical vendors and annual security questionnaire updates. Performance metrics are tracked including SLA compliance, security incidents, and control effectiveness.
        
        Vendor access management requires unique identities for all vendor personnel with access regularly reviewed and certified by business owners. VPN access is limited to specific systems and monitored through centralized logging.
        
        Incident response procedures require vendors to notify the organization within 4 hours of any security incident affecting organizational data or systems. Post-incident reviews assess vendor response effectiveness and may trigger contract modifications.
        
        Vendor termination procedures ensure secure return or destruction of organizational data with certificates of destruction required for sensitive data. Access is immediately revoked upon contract termination or expiration.
        
        Business continuity planning includes assessment of critical vendor dependencies with documented contingency plans for vendor failure scenarios. Alternative vendor options are maintained for critical services.
        """
    },
    {
        "id": "internal_audit",
        "title": "Internal Audit Charter",
        "type": "Charter Document",
        "content": """
        The Internal Audit Charter establishes the purpose, authority, and responsibility of the internal audit function within the organization's governance structure.
        
        Internal audit reports functionally to the Audit Committee of the Board and administratively to the Chief Executive Officer, ensuring independence and objectivity in audit activities.
        
        Audit scope includes evaluation of risk management, control, and governance processes across all organizational activities, systems, and functions. No restrictions are placed on audit access to records, personnel, or physical properties.
        
        Risk-based audit planning methodology prioritizes audit activities based on risk assessment, regulatory requirements, and management requests. The annual audit plan is approved by the Audit Committee and updated quarterly.
        
        Audit standards compliance follows Institute of Internal Auditors International Standards with external quality assessments conducted every five years. Audit staff maintain professional certifications and complete continuing education requirements.
        
        Audit findings are communicated to management through formal reports with management responses documenting corrective action plans and target completion dates. Follow-up procedures verify implementation of agreed-upon actions.
        
        Quality assurance program includes supervisory review of all audit work, client feedback surveys, and performance metrics tracking. Audit effectiveness is measured through key performance indicators reported to the Audit Committee quarterly.
        
        Coordination with external auditors and regulators ensures efficient audit coverage and minimizes duplication of effort. Audit results relevant to regulatory compliance are shared with appropriate oversight bodies as required.
        """
    }
]

def main():
    """Three-Panel Document Mind Map Interface"""
    st.set_page_config(
        page_title="Corporate Security and Risk Management Frameworks", 
        layout="wide",
        page_icon="🔒"
    )

    # Custom CSS for three-panel layout
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .panel-header {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-left: 4px solid #2a5298;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    
    .document-item {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .document-item:hover {
        border-color: #2a5298;
        box-shadow: 0 2px 8px rgba(42, 82, 152, 0.1);
    }
    
    .document-item.selected {
        border-color: #2a5298;
        background: #f8f9ff;
        box-shadow: 0 2px 8px rgba(42, 82, 152, 0.2);
    }
    
    .content-panel {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        height: 600px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
    }
    
    .tab-container {
        background: white;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        height: 600px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    
    .mindmap-container {
        height: 500px;
        overflow: auto;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'selected_doc_id' not in st.session_state:
        st.session_state.selected_doc_id = None
    
    if 'mindmap_generated' not in st.session_state:
        st.session_state.mindmap_generated = False
        st.session_state.mindmap_content = None
        st.session_state.mindmap_data = None
    
    if 'show_fullscreen' not in st.session_state:
        st.session_state.show_fullscreen = False
    
    # Initialize Facts Overview popup state
    if 'show_facts_popup' not in st.session_state:
        st.session_state.show_facts_popup = False

    # Check if fullscreen mode should be shown
    if st.session_state.show_fullscreen and st.session_state.mindmap_content:
        show_fullscreen_mindmap(st.session_state.mindmap_content, st.session_state.mindmap_data)
        return
    
    # Check if Facts Overview popup should be shown
    if st.session_state.show_facts_popup:
        show_facts_overview_popup()
        return

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>Organization Policy Analyzer</h1>
        <p>Comprehensive document analysis and mind mapping interface</p>
    </div>
    """, unsafe_allow_html=True)

    left_col, middle_col, right_col = st.columns([1, 2, 1.5])

    # RIGHT PANEL - Tabs (Mind Map, Facts Overview, etc.)
    with right_col:
        st.markdown('<div class="panel-header">🎛️ Studio</div>', unsafe_allow_html=True)
        
        with st.container():
            # Updated tabs to include Facts Overview after Mind Map
            tab1, tab2 = st.tabs(["🗺️ Mind Map", "📊 Facts Overview"])
            
            with tab1:
                st.markdown("### 🧠 Document Mind Map")
                
                # Generate mind map button - now uses static content
                if st.button("🚀 Load Mind Map", type="primary", use_container_width=True):
                    with st.spinner("📂 Loading static mind map..."):
                        markdown_content, audit_data = generate_audit_mindmap()
                        
                        if markdown_content:
                            st.session_state.mindmap_generated = True
                            st.session_state.mindmap_content = markdown_content
                            st.session_state.mindmap_data = audit_data
                            st.session_state.show_fullscreen = True
                            st.success("✅ Mind map loaded!")
                            st.rerun()
                        else:
                            st.error("❌ Mind map loading failed")
                
                # Display mind map preview if generated
                if st.session_state.mindmap_generated and st.session_state.mindmap_content:
                    st.markdown("---")
                    
                    # Show summary
                    if st.session_state.mindmap_data:
                        audit_data = st.session_state.mindmap_data
                        st.markdown(f"**🎯 {audit_data.get('unified_title', 'Audit Analysis')}**")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Documents", len(audit_data.get("documents", [])))
                        with col2:
                            total_insights = sum(len(doc.get("audit_insights", [])) for doc in audit_data.get("documents", []))
                            st.metric("Insights", total_insights)
                    
                    # Open fullscreen button
                    if st.button("🔍 Open Fullscreen View", use_container_width=True):
                        st.session_state.show_fullscreen = True
                        st.rerun()
                    
                    # Interactive mind map preview in container
                    st.markdown('<div class="mindmap-container">', unsafe_allow_html=True)
                    markmap(st.session_state.mindmap_content, height=400)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Download options
                    st.download_button(
                        "💾 Download Mind Map",
                        st.session_state.mindmap_content,
                        f"mindmap_{uuid.uuid4().hex[:8]}.md",
                        "text/markdown",
                        use_container_width=True
                    )
                
                else:
                    st.info("👆 Click 'Load Mind Map' to display the pre-built interactive mind map")
            
            with tab2:
                st.markdown("### 📊 Policy Facts Analysis")
                st.info("📋 Analyze policy inconsistencies and facts across documents")
                
                # Button to open Facts Overview popup
                if st.button("🔍 Open Facts Overview", type="primary", use_container_width=True):
                    st.session_state.show_facts_popup = True
                    st.rerun()
                
                # Preview of facts analysis
                st.markdown("**Preview:**")
                facts_data = load_facts_data()
                inconsistent_facts, consistent_facts = categorize_facts(facts_data)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Facts", len(facts_data))
                    st.metric("Consistent", len(consistent_facts))
                with col2:
                    st.metric("Inconsistencies", len(inconsistent_facts))
                    consistency_rate = (len(consistent_facts) / len(facts_data)) * 100 if facts_data else 0
                    st.metric("Consistency Rate", f"{consistency_rate:.1f}%")

if __name__ == "__main__":
    main()
