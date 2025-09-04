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
                        <p><strong>Source Sentence:</strong> "{fact.get('source_sentence', 'N/A')[:100]}{'...' if len(fact.get('source_sentence', '')) > 100 else ''}"</p>
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

    # Handle modal states first
    if st.session_state.show_fullscreen and st.session_state.mindmap_content:
        show_fullscreen_mindmap(st.session_state.mindmap_content, st.session_state.mindmap_data)
        return
    
    if st.session_state.show_facts_popup:
        show_facts_overview_popup()
        return

    # Main demo landing page
    create_demo_landing_page()

if __name__ == "__main__":
    main()
