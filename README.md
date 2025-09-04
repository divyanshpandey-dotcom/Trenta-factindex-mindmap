# Trenta-factindex-mindmap
Functionality for Mindmap and Fact Index 

A comprehensive Streamlit application for analyzing corporate security and risk management frameworks through interactive mind maps and policy consistency analysis.

## 🚀 Features

### 🗺️ Interactive Mind Map
- **Static Mind Map Loading**: Loads pre-saved mind map content from `mindmap_5038c8c4.md`
- **Fullscreen Modal View**: NotebookLM-style fullscreen interface for immersive mind map exploration
- **Interactive Navigation**: Zoom, pan, and explore hierarchical document structures
- **Export Capabilities**: Download mind maps as Markdown or JSON formats

### 📊 Policy Facts Analysis
- **Inconsistency Detection**: Automatically identifies conflicting policy values across documents
- **Consistency Metrics**: Real-time calculation of policy alignment rates
- **Document Comparison**: Side-by-side analysis of policy implementations
- **Visual Analytics**: Interactive charts and graphs for policy insights

### 🎛️ Three-Panel Interface
- **Document Browser**: Left panel for document selection and navigation
- **Content Viewer**: Middle panel for detailed document analysis
- **Studio Controls**: Right panel with mind map and facts analysis tools

## 📋 Requirements

### Dependencies
```
streamlit
pandas
plotly
pydantic
streamlit-markmap
typing-extensions
```

### Data Files
- `mindmap_5038c8c4.md` - Pre-saved mind map content
- `factIndex.json` - Policy facts data for consistency analysis

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mindmap
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare data files**:
   - Ensure `mindmap_5038c8c4.md` exists in the project directory
   - Ensure `factIndex.json` exists for facts analysis

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## 📖 Usage

### Mind Map Generation
1. Click **"🚀 Load Mind Map"** in the Studio panel
2. The application loads the static mind map content
3. Use **"🔍 Open Fullscreen View"** for immersive exploration
4. Export mind maps using download buttons

### Policy Facts Analysis
1. Click **"🔍 Open Facts Overview"** in the Studio panel
2. Review policy inconsistencies in the dedicated popup
3. Analyze consistency metrics and document comparisons
4. Export analysis results as needed

### Data Structure

#### Mind Map Data Format
```json
{
  "unified_title": "Integrated Controls Framework Overview",
  "audit_context": "Comprehensive framework covering security, data governance, risk management and audit controls",
  "documents": [
    {
      "document_id": "unique_id",
      "document_title": "Document Name",
      "document_type": "Policy Document",
      "audit_insights": [
        {
          "node_title": "5-7 words describing the insight",
          "sub_nodes": [
            {
              "sub_title": "3-5 words describing aspect",
              "sub_content": "Brief specific point (max 40 words)"
            }
          ]
        }
      ]
    }
  ]
}
```

#### Facts Data Format
```json
{
  "field_name": [
    {
      "value": "Policy value",
      "document_title": "Source document",
      "fact_name": "Human readable name",
      "source_sentence": "Original text",
      "reference": "Page/section reference"
    }
  ]
}
```

## 🏗️ Architecture

### Core Components

#### Pydantic Models
- `AuditSubNode`: Individual sub-aspects of audit insights
- `AuditInsightNode`: Main audit insights with sub-nodes
- `ProcessedAuditDocument`: Document structure with audit insights
- `UnifiedAuditMindMap`: Complete mind map structure with validation

#### Key Functions
- `load_static_mindmap()`: Loads pre-saved mind map content
- `parse_markdown_to_audit_data()`: Converts markdown to structured data
- `generate_audit_mindmap()`: Generates mind map using static content
- `show_fullscreen_mindmap()`: Displays fullscreen modal interface
- `show_facts_overview_popup()`: Policy consistency analysis interface

#### Session State Management
- `selected_doc_id`: Currently selected document
- `mindmap_generated`: Mind map generation status
- `mindmap_content`: Generated mind map content
- `mindmap_data`: Structured audit data
- `show_fullscreen`: Fullscreen mode toggle
- `show_facts_popup`: Facts analysis popup toggle

## 🎨 UI Components

### Custom CSS Styling
- **Gradient Headers**: Professional blue gradient styling
- **Modal Interfaces**: Fullscreen mind map and facts analysis popups
- **Interactive Elements**: Hover effects and smooth transitions
- **Responsive Layout**: Three-panel responsive design
- **Status Indicators**: Color-coded consistency metrics

### Interactive Features
- **Expandable Sections**: Collapsible document and insight sections
- **Metric Cards**: Real-time policy consistency statistics
- **Export Buttons**: Download functionality for mind maps and data
- **Tab Navigation**: Organized interface with multiple analysis views

## 🔧 Configuration

### File Paths
- Mind map file: `mindmap_5038c8c4.md`
- Facts data file: `factIndex.json`

### Inconsistency Detection
The application identifies inconsistencies in these specific fields:
- `security_training_frequency`
- `information_security_risk_assessment_frequency`
- `recovery_time_objective`
- `password_minimum_length`

## 📊 Analytics Features

### Consistency Metrics
- **Total Facts**: Complete count of analyzed policy facts
- **Inconsistent Facts**: Fields with conflicting values
- **Consistent Facts**: Fields with aligned values
- **Consistency Rate**: Percentage of consistent policies

### Visual Analytics
- **Pie Charts**: Overall consistency distribution
- **Bar Charts**: Document-wise inconsistency analysis
- **Interactive Tables**: Detailed fact comparisons
- **Status Indicators**: Color-coded policy status

## 🚨 Error Handling

### Graceful Degradation
- File not found fallbacks
- Empty data state handling
- Warning system for failed operations
- User-friendly error messages

### Validation
- Pydantic model validation
- Data structure integrity checks
- Required field validation
- Content length constraints

## 🔄 Future Enhancements

### Planned Features
- Dynamic mind map generation from live data
- Real-time policy monitoring
- Advanced filtering and search capabilities
- Integration with external policy management systems
- Collaborative editing features

### Technical Improvements
- Performance optimization for large datasets
- Enhanced mobile responsiveness
- Advanced export formats (PDF, Excel)
- API integration capabilities

## 📝 License

This project is part of the Trenta compliance management system.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For support and questions, please refer to the main Trenta project documentation or contact the development team.

---

**Built with ❤️ using Streamlit and modern web technologies**
