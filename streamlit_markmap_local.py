import streamlit.components.v1 as components

def markmap(data, height=600):
    data = str(data)
    markdown_style = '''
        <style>
            .markmap {{
                position: relative;
                width: 100%;
                height: {}px;
            }}
            .markmap > svg {{
                width: 100%;
                height: 100%;
            }}
        </style>'''.format(height)
    
    markdown_html = f'''
        {markdown_style}
        <script>
            window.markmap = {{
                autoLoader: {{ 
                    manual: true, 
                    toolbar: true 
                }},
            }};
        </script>
        <script src="https://cdn.jsdelivr.net/npm/markmap-autoloader@latest"></script>
        <script>
            // Render after a short delay to ensure proper initialization
            setTimeout(() => {{
                markmap.autoLoader.renderAll();
            }}, 100);
        </script>
        
        <div class='markmap'>
            <script type="text/template">
{data}
            </script>
        </div>
    '''
    markmap_component = components.html(markdown_html, height=height)
    return markmap_component