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
