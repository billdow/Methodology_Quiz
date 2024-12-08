from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import tempfile
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:8081",  # Local development
            "https://yourusername.github.io",  # GitHub Pages URL
            "http://yourusername.github.io"   # Non-HTTPS version
        ],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})

def get_methodology_details(methodology):
    details = {
        'waterfall': {
            'description': "Traditional, sequential approach best suited for projects with well-defined requirements and minimal expected changes.",
            'leadership_justification': """Based on your project's characteristics, implementing a Waterfall methodology presents a compelling strategic advantage for your organization. This approach provides a structured framework that maximizes resource efficiency through clearly defined phases and comprehensive documentation. The sequential nature of Waterfall methodology ensures precise budget forecasting and timeline management, which is particularly valuable for stakeholder communications and regulatory compliance. By maintaining clear lines of authority and established quality control measures, this methodology minimizes risks associated with scope creep and ensures consistent delivery standards. The front-loaded planning process, while initially time-intensive, significantly reduces costly mid-project changes and supports thorough risk assessment at each phase gate. This methodology is especially effective for projects requiring strict governance and audit trails, making it an ideal choice for initiatives where stability and predictability are paramount to success."""
        },
        'agile': {
            'description': "Iterative approach ideal for projects that require flexibility and frequent stakeholder feedback.",
            'leadership_justification': """The assessment results strongly indicate that an Agile methodology would optimize your project's success potential. This approach directly addresses the modern market's demand for rapid adaptation and continuous value delivery. By implementing Agile practices, your organization can accelerate time-to-market while maintaining the flexibility to respond to changing business conditions and customer needs. The iterative development cycle enables early risk identification and mitigation, while promoting higher team engagement and productivity through self-organization. Regular sprint reviews and continuous stakeholder feedback create a transparent environment that supports informed decision-making and ensures strategic alignment throughout the project lifecycle. This methodology particularly excels in environments where market conditions are dynamic and early return on investment is a key success factor."""
        },
        'DevOps': {
            'description': "Continuous delivery approach focusing on automation and integration between development and operations.",
            'leadership_justification': """The analysis reveals that a DevOps methodology would provide optimal results for your project requirements. This modern approach significantly enhances operational efficiency through comprehensive automation and seamless integration between development and operations teams. By implementing DevOps practices, your organization can achieve faster time-to-market while maintaining high quality standards through automated testing and continuous integration. The methodology's emphasis on automated deployment and standardized processes substantially reduces operational costs and human error risks. Real-time monitoring and rapid incident response capabilities ensure system reliability and stability, critical factors in maintaining business continuity. This approach is particularly effective for organizations seeking to establish a culture of continuous improvement and innovation while maintaining robust security and compliance standards."""
        },
        'hybrid': {
            'description': "Mixed approach combining elements of different methodologies to best suit varying project needs.",
            'leadership_justification': """Your project assessment indicates that a Hybrid methodology would provide the most effective framework for success. This sophisticated approach combines the most beneficial elements of multiple methodologies, allowing for optimized project delivery while maintaining organizational stability. By selectively implementing different methodological components, your team can adapt their approach based on specific project phases and requirements, ensuring maximum efficiency and risk management. This flexible framework supports progressive capability building while minimizing organizational disruption, making it particularly suitable for complex projects with diverse stakeholder needs. The balanced approach to change management and methodological flexibility creates an environment where innovation can flourish within a structured framework, supporting both short-term project success and long-term organizational growth."""
        }
    }
    return details.get(methodology, {})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    answers = request.json
    
    scores = {
        'waterfall': 0,
        'agile': 0,
        'DevOps': 0,
        'hybrid': 0
    }
    
    for question, answer in answers.items():
        if answer == 'structured':
            scores['waterfall'] += 2
        elif answer == 'flexible':
            scores['agile'] += 2
            scores['DevOps'] += 1
        elif answer == 'continuous':
            scores['DevOps'] += 2
        elif answer == 'mixed':
            scores['hybrid'] += 2
            
    recommended = max(scores.items(), key=lambda x: x[1])[0]
    
    result = {
        'scores': scores,
        'recommended': recommended,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'details': get_methodology_details(recommended)
    }
    
    return jsonify(result)

@app.route('/generate_report', methods=['POST'])
def generate_report():
    try:
        # Get data from form or JSON
        if request.is_json:
            data = request.json
        else:
            quiz_data = request.form.get('quiz_data')
            if not quiz_data:
                return jsonify({'error': 'No quiz data provided'}), 400
            try:
                data = json.loads(quiz_data)
            except json.JSONDecodeError as e:
                return jsonify({'error': f'Invalid JSON data: {str(e)}'}), 400

        # Validate required fields
        required_fields = ['recommended', 'scores', 'details']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            pdf_path = f.name
    
        # Create the PDF document
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        story.append(Paragraph('Project Methodology Assessment Report', title_style))
        
        # Timestamp
        story.append(Paragraph(f'Generated on: {data["timestamp"]}', styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Recommended Methodology
        story.append(Paragraph(f'Recommended Methodology: {data["recommended"].upper()}', styles['Heading2']))
        story.append(Spacer(1, 10))
        
        # Leadership Justification
        story.append(Paragraph('Leadership Justification', styles['Heading3']))
        justification_style = ParagraphStyle(
            'Justification',
            parent=styles['Normal'],
            spaceBefore=10,
            spaceAfter=20,
            leading=14
        )
        story.append(Paragraph(data['details']['leadership_justification'], justification_style))
        story.append(Spacer(1, 20))
        
        # Description
        story.append(Paragraph('Methodology Description', styles['Heading3']))
        story.append(Paragraph(data['details']['description'], styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Methodology Scores
        story.append(Paragraph('Methodology Scores', styles['Heading3']))
        # Filter out zero scores
        non_zero_scores = {k: v for k, v in data['scores'].items() if v > 0}
        if non_zero_scores:
            scores_data = [[k.capitalize(), f'{v}0%'] for k, v in non_zero_scores.items()]
            scores_table = Table(scores_data, colWidths=[2*inch, 1*inch])
            scores_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(scores_table)
        story.append(Spacer(1, 20))
        
        # Next Steps
        story.append(Paragraph('Next Steps', styles['Heading3']))
        next_steps = [
            "1. Review this assessment with key stakeholders",
            "2. Develop a transition plan if switching methodologies",
            "3. Identify training needs for the team",
            "4. Set up initial framework and tools for the chosen methodology",
            "5. Establish metrics to measure methodology effectiveness"
        ]
        for step in next_steps:
            story.append(Paragraph(step, styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Build the PDF
        doc.build(story)
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'methodology_assessment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/embed')
def embed():
    return render_template('embed.html')

@app.route('/embed_code')
def embed_code():
    host = request.host_url.rstrip('/')
    iframe_code = f'''<div class="methodology-quiz-wrapper" style="width: 100%; max-width: 800px; margin: 0 auto;">
    <iframe 
        src="{host}/embed"
        style="display: block; width: 100%; min-height: 1000px; border: none; overflow: hidden;"
        scrolling="yes"
    ></iframe>
</div>'''
    return render_template('embed_code.html', iframe_code=iframe_code)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
