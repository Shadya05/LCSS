import io
import base64
import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from ocr import extract_text_from_image, extract_fields
from database import init_db, insert_record, update_impact, get_all_records, get_record_by_survey_number
from cnn_model import classify_document
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

GOVERNMENT_LAND_RATES = {
    'default': 100000
}

init_db()

def get_fair_compensation(land_area, district_or_village):
    try:
        area_val = float(''.join(filter(lambda c: c.isdigit() or c=='.', land_area)))
    except:
        area_val = 0
    rate = GOVERNMENT_LAND_RATES.get(district_or_village.lower(), GOVERNMENT_LAND_RATES['default'])
    return area_val * rate

def assess_compensation_fairness(comp_received, fair_comp):
    try:
        comp_val = float(''.join(filter(lambda c: c.isdigit() or c=='.', comp_received)))
    except:
        comp_val = 0
    return comp_val >= fair_comp

def generate_grievance_report(record):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Land Compensation Grievance Report", styles['Title']),
        Spacer(1,12)
    ]
    for field, value in record.items():
        story.append(Paragraph(f"<b>{field.replace('_',' ').title()}:</b> {value}", styles['Normal']))
        story.append(Spacer(1,6))
    story.append(Paragraph("This report highlights potential under-compensation and legal support to seek justice.", styles['Italic']))
    doc.build(story)
    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files or request.files['file'].filename == '':
        return jsonify(error="No file uploaded"), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    raw_text = extract_text_from_image(filepath)
    extracted_data = extract_fields(raw_text)
    classification = classify_document(filepath)

    district_or_village = extracted_data.get('district','').lower() or extracted_data.get('village','').lower()
    fair_comp = get_fair_compensation(extracted_data.get('land_area',''), district_or_village)
    comp_received = extracted_data.get('compensation_amount','')
    is_fair = assess_compensation_fairness(comp_received, fair_comp)

    record = {
        **extracted_data,
        'fair_compensation': fair_comp,
        'fairness_passed': is_fair,
        'raw_text': raw_text,
        'classification_result': classification
    }
    insert_record(record)

    return jsonify({
        'extracted_data': extracted_data,
        'classification': classification,
        'fair_compensation': fair_comp,
        'compensation_received': comp_received,
        'is_fair_compensation': is_fair,
        'message': "Compensation seems fair." if is_fair else "Below fair rate. Consider grievance filing."
    })

@app.route('/download_grievance/<survey_number>')
def download_grievance(survey_number):
    record = get_record_by_survey_number(survey_number)
    if not record:
        return jsonify(error="Record not found"), 404
    buffer = generate_grievance_report(record)
    return (
        buffer.getvalue(),
        200,
        {
            'Content-Type': 'application/pdf',
            'Content-Disposition': f'attachment; filename=Grievance_Report_{survey_number}.pdf'
        }
    )

@app.route('/records')
def records():
    return jsonify(get_all_records())

@app.route('/update_impact', methods=['POST'])
def update_impact_route():
    data = request.json
    survey_number = data.get('survey_number')
    if not survey_number:
        return jsonify(error="Survey number required"), 400
    success, message = update_impact(data)
    if success:
        return jsonify(success=True, message=message)
    else:
        return jsonify(success=False, message=message), 400

@app.route('/dashboard')
def dashboard():
    records = get_all_records()
    df = pd.DataFrame(records)
    img1 = create_land_usage_chart(df)
    img2 = create_families_affected_chart(df)
    img3 = create_compensation_fairness_chart(df)
    return render_template('dashboard.html', img1=img1, img2=img2, img3=img3)

def create_land_usage_chart(df):
    plt.figure(figsize=(6,6))
    usage_counts = df['public_usage'].value_counts()
    sns.set_palette("pastel")
    usage_counts.plot.pie(autopct='%1.1f%%')
    plt.title('Land Usage Distribution')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return f'data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}'

def create_families_affected_chart(df):
    plt.figure(figsize=(6,4))
    families_data = df.groupby('survey_number')['families_affected'].sum()
    families_data.plot.bar()
    plt.title('Families Affected per Survey')
    plt.ylabel('Number of Families')
    plt.xticks(rotation=45)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return f'data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}'

def create_compensation_fairness_chart(df):
    plt.figure(figsize=(6,4))
    fairness_counts = df['classification_result'].value_counts()
    sns.set_palette("muted")
    fairness_counts.plot.bar()
    plt.title('Document Classification Counts')
    plt.ylabel('Count')
    plt.xticks(rotation=0)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return f'data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}'

@app.route('/get_market_value', methods=['POST'])
def get_market_value():
    data = request.json
    today_rate_per_acre = 200000  # update with real value or API if available
    area = float(str(data['landArea']).replace(",", "") or 0)
    market_value = area * today_rate_per_acre
    comp_received = float(str(data['received']).replace(",", "") or 0)
    compensation_gap = market_value - comp_received
    amount_still_owed = max(compensation_gap, 0)
    suggestion = ""
    if amount_still_owed > 0:
        suggestion = (
            f"You are owed approx. INR {amount_still_owed:,.2f} "
            f"as per today's value. Prepare grievance documents using the grievance PDF. "
            f"Contact your local land acquisition office, attach the report, "
            f"and request enhanced compensation referencing present land market rates. "
            f"You may also seek legal help or approach Lok Adalat for dispute resolution."
        )
    else:
        suggestion = "Your compensation matches or exceeds today's market rate. No further grievance is suggested."
    
    # Bar chart generation
    plt.figure(figsize=(5, 3))
    plt.bar(['Received', "Today's Value"], [comp_received, market_value], 
            color=['#22d3ee', '#f87171'])
    plt.ylabel('INR')
    plt.title('Compensation Comparison')
    
    for i, v in enumerate([comp_received, market_value]):
        plt.text(i, v, f'₹{int(v):,}', ha='center', va='bottom', fontweight='bold')
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    img_chart = base64.b64encode(buf.getvalue()).decode()
    
    return jsonify({
        "market_value": "{:,.2f}".format(market_value),
        "compensation_gap": "{:,.2f}".format(compensation_gap),
        "amount_still_owed": "{:,.2f}".format(amount_still_owed),
        "suggestion": suggestion,
        "chart": img_chart
    })


if __name__ == '__main__':
    app.run(debug=True)
