import re, math, string, json, collections
import streamlit as st

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False

try:
    from transformers import pipeline as hf_pipeline
    TRANSFORMERS_OK = True
except ImportError:
    TRANSFORMERS_OK = False

try:
    import PyPDF2
    PDF_OK = True
except ImportError:
    PDF_OK = False

try:
    from docx import Document as DocxDoc
    DOCX_OK = True
except ImportError:
    DOCX_OK = False

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize, sent_tokenize
    for pkg in ["punkt", "stopwords", "punkt_tab"]:
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass
    NLTK_OK = True
except ImportError:
    NLTK_OK = False

st.set_page_config(
    page_title="PolicyAI · KDU LB3114",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@300;400;500&display=swap');
:root {
  --bg:#f5f0e8;--surface:#fdfaf4;--panel:#ffffff;--border:#e2d9c8;--border2:#cfc4b0;
  --teal:#2a7c6f;--teal-lt:#d6eeeb;--teal-mid:#a8d8d2;--coral:#d4614a;--coral-lt:#fde8e4;
  --amber:#c47d1e;--amber-lt:#fdf0d8;--lavender:#6b5ea8;--lav-lt:#ede9f8;
  --text:#2c2416;--text2:#5a4e3a;--muted:#9a8e7e;--r:12px;--r2:8px;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;background:var(--bg)!important;color:var(--text)!important;}
.stApp{background:var(--bg)!important;}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding:1.2rem 2rem 2rem!important;max-width:100%!important;}
.app-header{background:linear-gradient(135deg,#2a7c6f 0%,#1e5c52 40%,#3a9688 100%);border-radius:16px;padding:28px 36px;margin-bottom:24px;position:relative;overflow:hidden;box-shadow:0 4px 24px rgba(42,124,111,0.18);}
.app-header h1{font-family:'DM Serif Display',serif;font-size:2.1rem;font-weight:400;color:#fff;margin:0;}
.app-header p{font-family:'DM Mono',monospace;font-size:0.68rem;color:rgba(255,255,255,0.72);letter-spacing:1.5px;text-transform:uppercase;margin:8px 0 0;}
.panel-title{font-family:'DM Serif Display',serif;font-size:1.6rem;font-weight:400;color:var(--text);margin-bottom:2px;}
.panel-sub{font-family:'DM Mono',monospace;font-size:0.64rem;color:var(--muted);letter-spacing:1px;text-transform:uppercase;margin-bottom:18px;}
hr.line{border:none;border-top:1.5px solid var(--border);margin:20px 0;}
.stTextInput input,.stTextArea textarea{background:var(--panel)!important;border:1.5px solid var(--border)!important;color:var(--text)!important;border-radius:var(--r2)!important;font-family:'DM Sans',sans-serif!important;font-size:0.87rem!important;}
.stTextInput input:focus,.stTextArea textarea:focus{border-color:var(--teal)!important;box-shadow:0 0 0 3px rgba(42,124,111,0.12)!important;}
.stFileUploader>div{background:var(--surface)!important;border:2px dashed var(--border2)!important;border-radius:var(--r)!important;}
.stFileUploader>div:hover{border-color:var(--teal)!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--surface)!important;border-radius:var(--r)!important;border:1.5px solid var(--border)!important;padding:4px!important;gap:2px;display:flex!important;width:100%!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;border-radius:var(--r2)!important;font-size:0.78rem!important;font-family:'DM Sans',sans-serif!important;font-weight:500!important;flex:1 1 0!important;text-align:center!important;padding:6px 4px!important;}
.stTabs [aria-selected="true"]{background:var(--teal)!important;color:#fff!important;}
.stRadio>div{gap:8px;}
.stRadio label{background:var(--surface);border:1.5px solid var(--border);border-radius:var(--r2);padding:7px 18px!important;font-size:0.83rem!important;color:var(--text2)!important;font-family:'DM Sans',sans-serif!important;transition:all 0.15s;}
.stRadio label:has(input:checked){border-color:var(--teal)!important;color:var(--teal)!important;background:var(--teal-lt)!important;font-weight:600!important;}
.stButton>button{background:linear-gradient(135deg,#2a7c6f,#1e5c52)!important;color:#fff!important;border:none!important;border-radius:var(--r)!important;font-family:'DM Sans',sans-serif!important;font-weight:600!important;font-size:0.88rem!important;padding:10px 24px!important;width:100%;transition:all 0.2s!important;box-shadow:0 2px 8px rgba(42,124,111,0.2)!important;}
.stButton>button:hover{background:linear-gradient(135deg,#338a7c,#226b60)!important;box-shadow:0 4px 16px rgba(42,124,111,0.3)!important;transform:translateY(-1px)!important;}
.result-card{border-radius:var(--r);padding:22px 24px;margin-top:16px;font-size:0.88rem;line-height:1.85;}
.result-card.teal{background:var(--surface);border:1.5px solid var(--teal-mid);border-left:4px solid var(--teal);box-shadow:0 2px 12px rgba(42,124,111,0.08);}
.result-card.coral{background:var(--surface);border:1.5px solid #f0b8ae;border-left:4px solid var(--coral);box-shadow:0 2px 12px rgba(212,97,74,0.08);}
.result-label{font-family:'DM Mono',monospace;font-size:0.63rem;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;display:block;font-weight:500;}
.lbl-teal{color:var(--teal);}.lbl-coral{color:var(--coral);}
.summary-section{margin-bottom:14px;}
.summary-section-title{font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:1.2px;text-transform:uppercase;font-weight:600;margin-bottom:4px;display:flex;align-items:center;gap:6px;}
.summary-section-title.goals{color:#2a7c6f;}.summary-section-title.measures{color:#c47d1e;}.summary-section-title.direction{color:#6b5ea8;}
.summary-section-body{color:#2c2416;font-size:0.88rem;line-height:1.75;padding-left:4px;border-left:2px solid var(--border);}
.summary-section-body.goals{border-color:var(--teal-mid);}.summary-section-body.measures{border-color:#eac87a;}.summary-section-body.direction{border-color:#c4bce8;}
.summary-divider{border:none;border-top:1px solid var(--border);margin:12px 0;}
.stat-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px;}
.stat-chip{font-family:'DM Mono',monospace;font-size:0.65rem;padding:3px 11px;border-radius:20px;font-weight:400;}
.chip-teal{background:var(--teal-lt);color:var(--teal);border:1px solid var(--teal-mid);}
.chip-coral{background:var(--coral-lt);color:var(--coral);border:1px solid #f0b8ae;}
.chip-amber{background:var(--amber-lt);color:var(--amber);border:1px solid #eac87a;}
.chip-lav{background:var(--lav-lt);color:var(--lavender);border:1px solid #c4bce8;}
div[data-testid="column"] .stButton>button{background:var(--surface)!important;color:var(--teal)!important;border:1.5px solid var(--teal-mid)!important;font-size:0.78rem!important;padding:7px 10px!important;box-shadow:none!important;font-weight:500!important;}
div[data-testid="column"] .stButton>button:hover{background:var(--teal-lt)!important;border-color:var(--teal)!important;transform:none!important;}
.streamlit-expanderHeader{background:var(--surface)!important;border:1.5px solid var(--border)!important;border-radius:var(--r)!important;color:var(--text2)!important;font-size:0.82rem!important;font-family:'DM Sans',sans-serif!important;}
::-webkit-scrollbar{width:5px;}::-webkit-scrollbar-track{background:var(--bg);}::-webkit-scrollbar-thumb{background:var(--border2);border-radius:4px;}
.stAlert{border-radius:var(--r)!important;}
</style>
""", unsafe_allow_html=True)

# ── Session State ──
for k, v in {
    "policy_text":"","summary":"","draft":"","scenario_input":"","last_scenario":"",
    "summary_method":"","loaded_name":"","active_tab":"","dynamic_scenarios":[],
    "scenarios_generated_for":"","goals":"","measures":"","direction":"",
    "orig_wc":0,"summ_wc":0,"compression":0,"nlp_stats":{},"draft_mode":"summary",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Sample Policies ──
SAMPLE_POLICIES = {
    "Conditions of Carriage": """SriLankan Airlines Conditions of Carriage – Full Policy (Articles 1–19)

Article 1 – Definitions
SriLankan Airlines Limited (referred to as We or Our) operates under these Conditions of Carriage. You or Your refers to any passenger travelling on a valid ticket, excluding crew members. Key definitions: Checked Baggage means baggage in airline custody with a Baggage Check issued. Unchecked Baggage means cabin baggage remaining with the passenger. Electronic Ticket means a digital ticket including coupons and boarding information. Force Majeure means unexpected events beyond the airline's control that prevent travel. Special Drawing Rights (SDR) is the international monetary unit defined by the IMF. Agreed Stopping Places are scheduled stops between departure and destination. Authorised Agent is a sales agent appointed to sell tickets on behalf of the airline. Tariff refers to published fares, charges, and related conditions.

Article 2 – Applicability
These Conditions apply on all flights where SriLankan Airlines has legal liability to the passenger. For charter flights, these Conditions apply only if explicitly included in the charter agreement or referenced in the ticket. Some flights may be operated by another carrier under a code share agreement; passengers are informed at reservation. US code share flights follow the operating carrier's contingency plan for lengthy tarmac delays. Where these Conditions conflict with applicable law or tariffs, the law or tariffs prevail. If any clause is found invalid, the remaining provisions continue to apply. Where there is inconsistency between these Conditions and other airline regulations, these Conditions generally take precedence unless otherwise stated.

Article 3 – Tickets
Tickets are issued only to the passenger named on them and are non-transferable except as required by law. A ticket is generally valid for one year from the date of issue or from the date of first travel. Passengers unable to travel due to illness or bereavement may apply for ticket validity extensions with appropriate documentation. Coupons must be used in the sequence shown on the ticket; unauthorised changes result in fare recalculation. In cases of Force Majeure, the airline may issue a travel credit after deducting a reasonable administrative fee. Electronic tickets require valid government-issued identification at check-in. Lost or damaged tickets can be replaced upon proof of purchase; an administrative fee may apply and conditions exist to prevent fraud.

Article 4 – Fares, Taxes and Charges
Fares apply only for travel between the airports of origin and destination as shown on the ticket; they do not include ground transport between airports or town terminals. All applicable government taxes, airport charges, and carrier surcharges are the passenger's responsibility and are shown separately at the time of ticket purchase. Taxes and fees may change after ticket issuance; passengers must pay any increases and may claim refunds for reductions or abolishments. The airline may impose surcharges for increased costs arising from exceptional events. Fares are payable in the currency of the country where the ticket is issued; the airline may at its discretion accept payment in another currency.

Article 5 – Reservations
Reservations are recorded and confirmed in writing by the airline or its authorised agent upon request. Certain fare types may limit or exclude the ability to change or cancel a reservation. Advance seating requests will be honoured where possible but no particular seat is guaranteed; seats may be reassigned for operational, safety, or security reasons. The airline respects passenger privacy and processes personal data in accordance with its published privacy policy. Onward or return reservations may require reconfirmation within specified time limits; failure to reconfirm may result in cancellation. If a passenger fails to show up for a flight without prior notice, the airline may cancel all onward and return reservations on the same booking. If the passenger notifies the airline in advance, reservations will be maintained where technically possible.

Article 6 – Check-in and Boarding
Check-in counters generally open 3 hours before departure and close 1 hour prior to departure. Passengers must present themselves at the boarding gate no later than 30 minutes before scheduled departure. Failure to comply with check-in or boarding deadlines may result in cancellation of the reservation without refund entitlement. The airline is not liable for any loss or expense arising from the passenger's failure to meet check-in or boarding requirements. Passenger personal data collected at check-in is handled in accordance with the airline's privacy policy.

Article 7 – Refusal and Limitation of Carriage
The airline may refuse to carry passengers or their baggage on grounds including safety risk, health concerns, non-payment of fares, possession of invalid or fraudulent travel documents, prior violations of airline policy, or failure to comply with security checks. The airline may also refuse carriage to comply with government regulations or flight restrictions. Special assistance must be arranged in advance for unaccompanied minors, pregnant women, and passengers with disabilities or medical conditions; accepted passengers may not be refused carriage unless circumstances change significantly. Passengers with medical conditions must provide written clearance from a doctor, a MEDIF form, or a FREMEC card within specified timeframes if required. Wheelchair assistance at Colombo airport may be provided for an additional charge of LKR 1500, payable at the traffic cashier counter. Travel to or from the USA may have additional carriage rules available on request.

Article 8 – Baggage
Free baggage allowance depends on the ticket type and fare class. Economy class passengers are entitled to one carry-on bag not exceeding 7 kg. Business class passengers are entitled to two carry-on bags, each not exceeding 7 kg. Additional personal items such as a laptop bag, handbag, or infant items may be carried subject to conditions. Excess baggage beyond the free allowance is subject to additional charges. Prohibited items include dangerous goods, items restricted by law, firearms and ammunition (except for sporting use with specific packing requirements), and items unsafe due to weight, size, or fragility. Valuables including money, jewellery, electronics, and important documents must not be placed in checked baggage; the airline accepts no liability for such items. Animals must be carried in approved crates with valid health certificates, vaccination records, and entry permits. Guide dogs for passengers with disabilities are carried free of charge in addition to the standard baggage allowance. Codeshare flights operated by partner airlines including Malaysian Airlines, Etihad, Oman Air, Air India, Royal Jordanian, and Air Canada may have different baggage allowances. Checked baggage must be collected promptly; storage fees may apply and unclaimed baggage after three months may be disposed of. Only the bearer of the baggage check tag may claim checked baggage.

Article 9 – Schedules, Delays and Cancellations
Flight times published in timetables are not guaranteed and do not form part of the contract of carriage. If significant schedule changes occur after ticket purchase, passengers may be entitled to a refund or alternative arrangements. The airline will take all reasonable measures to avoid delays and may use alternative carriers or aircraft in exceptional circumstances. If a flight is cancelled or significantly disrupted, passengers may choose to travel on another flight without extra charge, be rerouted with any fare difference refunded, receive a full refund, or receive applicable compensation. These options represent the sole remedies available; no further liability applies for delays caused by exceptional circumstances beyond the airline's control. Passengers denied boarding involuntarily will receive compensation in accordance with applicable law and the airline's denied boarding policy, available on request.

Article 10 – Refunds
Refunds are made to the person named on the ticket or who paid for it, upon presentation of proof of payment and surrender of unused flight coupons. If the original payer is not the passenger and restrictions apply, refunds are returned to the payer. Involuntary refunds arising from airline cancellations, failure to operate, class downgrade, or caused missed connections entitle passengers to a full refund if the ticket is unused, or a partial refund for the unused portion. Voluntary refunds for cancellations initiated by the passenger are subject to applicable cancellation fees and fare restrictions. Refunds for lost tickets may be made upon submission of proof of loss and payment of an administrative charge, subject to conditions to prevent fraudulent claims. Refund applications must be submitted within one year of ticket issuance; late applications may be refused. All refunds are issued in the same currency and by the same method as the original payment. Voluntary refunds can only be processed by the carrier that issued the ticket or its authorised agent.

Article 11 – Conduct Aboard Aircraft
Passengers must not act in any way that endangers the aircraft, its crew, or any other person on board. Non-compliant or disruptive behaviour may result in physical restraint, disembarkation at any point, handover to authorities, or legal action. Passengers whose conduct causes an unscheduled aircraft diversion must bear all costs associated with that diversion. General regulations also cover restrictions on use of electronic devices, prohibition on on-board consumption of passenger-supplied alcoholic beverages, and airport restrictions on liquids, aerosols, and gels.

Article 12 – Arrangements for Additional Services
When the airline arranges services with third-party providers such as hotels, car rentals, or tours, it acts only as an agent and the terms and conditions of the third-party provider apply. If the airline provides surface transportation, separate conditions may apply and are available on request.

Article 13 – Administrative Formalities
Passengers are solely responsible for obtaining all required travel documents, visas, health certificates, and other entry or transit permits for all countries on their itinerary. The airline is not liable for any consequences arising from a passenger's failure to obtain the necessary documentation or comply with destination country laws. Passengers may be required to present exit permits, entry visas, health documents, or other required papers; carriage may be refused if documents are missing or incorrect. If a passenger is denied entry into any country, the passenger bears all fines and transport costs incurred; the original fare paid to the point of refusal is non-refundable. Passengers must reimburse the airline for any fines, penalties, or detention costs incurred due to their non-compliance with laws or regulations. Customs inspections must be complied with; the airline is not liable for loss or damage arising from inspections. Passengers must submit to all security checks required by governments, airport authorities, or the airline.

Article 14 – Successive Carriers
Carriage performed by multiple carriers under one ticket or conjunction tickets is considered a single operation for the purposes of the applicable Convention.

Article 15 – Liability for Damage
Liability for passenger death, wounding, or bodily injury is not subject to financial limits; the airline cannot exclude or limit liability for damages up to 128,821 SDRs per passenger even where all necessary measures were taken. Where damage is caused or contributed to by the negligence of the passenger, the airline's liability may be reduced or eliminated accordingly. In the event of passenger death, an advance payment of at least 15,000 SDRs per passenger must be made within 15 days to meet immediate economic needs; this advance is not an admission of liability and may be offset against subsequent compensation. The airline is not responsible for illness or aggravation of a medical condition arising from the passenger's pre-existing physical state. For checked baggage, liability is limited in accordance with the Montreal Convention unless damage is caused intentionally or recklessly. The airline is not liable for damage to unchecked baggage unless caused by its own negligence. The airline bears no liability for prohibited items, valuables, electronics, or documents placed in checked baggage. Claims for damage to checked baggage must be notified in writing within 7 days of receipt; claims for delayed baggage must be submitted within 21 days. All legal actions for damages must be brought within 2 years of the date of arrival at the destination or the scheduled arrival date.

Article 16 – Time Limitation on Claims and Actions
Acceptance of checked baggage by the bearer of the baggage check without complaint at delivery is evidence that the baggage was delivered in good condition unless the passenger proves otherwise. Written claims for baggage damage must be submitted as soon as the damage is discovered and no later than 7 days after receipt. Written claims for delayed checked baggage must be filed within 21 days from the date the baggage should have been available. The right to claim damages is extinguished if legal action is not brought within 2 years of the passenger's arrival, scheduled arrival, or the date carriage stopped.

Article 17 – Other Conditions
Additional regulations govern the carriage of unaccompanied minors, pregnant women, and sick passengers. Restrictions apply to the use of electronic devices on board. Passengers may not consume their own alcoholic beverages on board. A Denied Boarding Compensation Policy is available upon request. Airport restrictions on liquids, aerosols, and gels apply at all check-in and security points.

Article 18 – Interpretation
Article titles are for convenience only and are not used for interpretation of the text. SriLankan Airlines' designated IATA code is UL.

Article 19 – Air Passenger Protection Regulations (APPR) for Canadian Passengers
APPR applies to all SriLankan Airlines flights to, from, or within Canada, including connecting flights. APPR obligations were implemented in two stages: July 15 2019 covering communication of key information, denied boarding, tarmac delays, baggage, and musical instruments; and December 15 2019 covering all remaining obligations. Passengers involuntarily denied boarding are entitled to compensation of CAD 900 for delays under 6 hours, CAD 1800 for delays of 6 to 9 hours, and CAD 2400 for delays of 9 hours or more. Volunteers are requested before involuntary denied boarding is applied; last priority is given to unaccompanied minors, passengers with disabilities, families travelling together, and previously denied passengers. For flight delays and cancellations within the airline's control, passengers are entitled to care including food and drink, communication access such as Wi-Fi, and hotel accommodation with transport if an overnight stay is required, plus compensation of CAD 400 for delays of 3 to 6 hours, CAD 700 for 6 to 9 hours, and CAD 1000 for 9 hours or more. For disruptions outside the airline's control including weather, natural disasters, air traffic control instructions, medical emergencies, security threats, wildlife collisions, war, or manufacturing defects, the airline is required to rebook passengers but compensation does not apply. Children under 14 must be seated adjacent to a parent or guardian free of charge; children aged 0 to 4 in an adjacent seat, children aged 5 to 14 within the same row separated by no more than one seat. Cabin-sized musical instruments are carried free as part of the standard baggage allowance; larger instruments may require purchase of an additional seat or checking as baggage with applicable fees. Delayed baggage must be reported immediately at the airport or in writing within 48 hours; lost baggage claims must be filed within 21 days. Interim relief is available to cover immediate necessities for delayed baggage. Additional baggage fees are reimbursed if baggage is delayed, lost, or damaged. During tarmac delays after doors are closed or after landing, passengers are entitled to access to lavatories, proper ventilation, means of external communication where feasible, and food and drink. Passengers have the right to disembark after 3 hours on the tarmac unless safety, security, or air traffic control prevents it; priority is given to passengers with disabilities. Montreal Convention liability limits apply: cargo 22 SDR per kg, baggage 1288 SDR per passenger, delay of persons 5346 SDR per passenger, and death or bodily injury 128821 SDR per passenger, based on ratification effective January 18 2019 for Sri Lanka.""",

    "Online Booking Terms": """SriLankan Airlines – Online Booking Terms of Use (www.srilankan.com)

Formation of Contract
The online booking facility is owned and operated by SriLankan Airlines Limited (SLA). By using the booking facility, users agree to these Terms and the Conditions of Carriage. SLA does not guarantee completeness or accuracy of information on the site; content is subject to change without notice.

Limitations of Use
The website may not be used for prohibited, fraudulent, or unlawful purposes. Users may not interfere with site availability, resell services, or make unauthorised reservations. SLA reserves the right to cancel bookings if users breach these terms.

Booking Rules
Reservations are allowed for up to 9 passengers in Economy or Business class. Infants under 2 years and children under 12 must travel with an accompanying adult under the same reservation. Electronic tickets are issued for all bookings; a valid email address is required. Payment is required at time of reservation except for Book Now and Pay Later, available in Colombo and UAE only. Accepted payment methods include MasterCard, Visa, American Express, JCB, CUP, and Maestro. Virtual or e-cards are not accepted. Card and passport verification may be required at check-in.

Date Changes
Date changes are subject to fare conditions, local fees, fare differences, and processing charges. Online date changes apply only to bookings made online. Passengers must cancel and rebook at least 5 hours before departure. Name changes are not permitted once tickets are issued.

No Show Policy
Passengers who fail to cancel or rebook at least 5 hours before departure are classified as No Show. All subsequent sectors of the booking will be automatically cancelled. The higher of the cancellation fee or no-show fee plus any applicable fare differences will be charged.

Refunds and Cancellations
Restricted and promotional fares are generally non-refundable. Refund requests submitted within 5 hours of departure are subject to the higher of the No Show or Refund Penalty. Partial refunds for used segments are charged at the segment fare plus taxes and penalty. An Online Refund Request Form is available for tickets purchased on srilankan.com.

Travel Requirements
Obtaining valid visas and travel documents is the passenger's sole responsibility. A valid passport is required for the full duration of travel. SLA is not responsible if passengers are denied boarding due to missing documentation.

Taxes, Fees and Charges
Ticket prices may include government or airport taxes and carrier surcharges. Certain airport charges are payable locally and may not be included in the quoted fare.

Limitations of Liability
SLA is not liable for injury, loss, or damage arising from use of the website, technical failures, unauthorised access, or incomplete bookings. Maximum liability is limited to any service charge or subscription fee for accessing the website.

Information Security and Privacy
SLA takes reasonable measures to keep passenger information confidential. Users must provide accurate personal information; SLA is not responsible if reservations cannot be fulfilled due to incorrect data. Refer to the privacy policy on srilankan.com for details on data collection and processing.

Codeshare Flights
Codeshare flights appear on the same ticket but are operated by a partner airline under an SLA flight number. Different baggage allowances may apply; passengers are subject to the operating carrier's terms and conditions."""
}

SAMPLE_POLICY = list(SAMPLE_POLICIES.values())[0]

# ── Helpers ──
STOPWORDS_FALLBACK = set("""
a about above after again against all also am an and any are as at be because
been before being below between both but by can cannot could did do does doing
down during each few for from further get got had has have having he her here
hers herself him himself his how i if in into is it its itself let me more most
my myself no nor not of off on once only or other ought our ours ourselves out
over own same she should so some such than that the their theirs them themselves
then there these they this those through to too under until up very was we were
what when where which while who whom why will with would you your yours yourself
""".split())

def get_stopwords():
    if NLTK_OK:
        try:
            return set(stopwords.words("english"))
        except Exception:
            pass
    return STOPWORDS_FALLBACK

def extract_text(file_obj):
    name = file_obj.name.lower()
    raw = file_obj.read()
    if name.endswith(".pdf"):
        if PDF_OK:
            import PyPDF2, io
            reader = PyPDF2.PdfReader(io.BytesIO(raw))
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        return "[PyPDF2 not installed]"
    if name.endswith(".docx"):
        if DOCX_OK:
            from docx import Document
            import io
            doc = Document(io.BytesIO(raw))
            return "\n".join(p.text for p in doc.paragraphs)
        return "[python-docx not installed]"
    if name.endswith(".json"):
        try:
            return json.dumps(json.loads(raw), indent=2)
        except Exception:
            pass
    return raw.decode("utf-8", errors="replace")

def tfidf_summarise(text, n_sentences=8):
    if NLTK_OK:
        try:
            sentences = sent_tokenize(text)
        except Exception:
            sentences = re.split(r'(?<=[.!?])\s+', text)
    else:
        sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.split()) > 5]
    if not sentences:
        return text[:600]
    sw = get_stopwords()
    def tok(s):
        return [w.lower().strip(string.punctuation) for w in s.split()
                if w.lower().strip(string.punctuation) not in sw and len(w) > 2]
    sent_words = [tok(s) for s in sentences]
    N = len(sentences)
    all_vocab = set(w for ws in sent_words for w in ws)
    idf = {word: math.log((N+1)/(sum(1 for ws in sent_words if word in ws)+1))+1
           for word in all_vocab}
    sent_scores = []
    for i, words in enumerate(sent_words):
        freq = collections.Counter(words)
        total = len(words) or 1
        score = sum((freq[w]/total)*idf.get(w,1) for w in freq)
        sent_scores.append((score, i, sentences[i]))
    raw_tokens = text.split()
    filtered_tokens = [w for ws in sent_words for w in ws]
    top_terms = [w for w, _ in collections.Counter(filtered_tokens).most_common(8)]
    st.session_state["nlp_stats"] = {
        "sentences_found": N, "sentences_selected": n_sentences,
        "raw_tokens": len(raw_tokens), "filtered_tokens": len(filtered_tokens),
        "stopwords_removed": len(raw_tokens)-len(filtered_tokens),
        "vocab_size": len(all_vocab), "top_terms": top_terms, "method": "TF-IDF Extractive",
    }
    top = sorted(sent_scores, key=lambda x: -x[0])[:n_sentences]
    return " ".join(s for _, _, s in sorted(top, key=lambda x: x[1]))

def chunk_text(text, size=800):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]

@st.cache_resource(show_spinner=False)
def load_bart():
    if not TRANSFORMERS_OK:
        return None
    try:
        return hf_pipeline("summarization", model="facebook/bart-large-cnn", device=-1)
    except Exception:
        return None

def bart_summarise(text, max_l, min_l):
    pipe = load_bart()
    if pipe is None:
        return None
    try:
        chunks = chunk_text(text, 800)
        parts = [pipe(c, max_length=max_l, min_length=min_l, do_sample=False, truncation=True)[0]["summary_text"]
                 for c in chunks[:4]]
        return " ".join(parts)
    except Exception:
        return None

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"

def ollama_generate(prompt, timeout=120):
    if not REQUESTS_OK:
        return None, "requests_missing"
    try:
        r = requests.post(OLLAMA_URL, json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}, timeout=timeout)
        if r.status_code == 200:
            return r.json().get("response", "").strip(), None
        return None, f"http_{r.status_code}"
    except requests.exceptions.Timeout:
        return None, "timeout"
    except requests.exceptions.ConnectionError:
        return None, "connection_error"
    except Exception as e:
        return None, str(e)

def ollama_draft(source, scenario, source_type="summary"):
    source_label = "POLICY DOCUMENT (RAW TEXT)" if source_type == "direct" else "ORIGINAL POLICY SUMMARY"
    task_note = ("You have been given the full policy text directly. Extract the key provisions yourself, then adapt them."
                 if source_type == "direct" else "You have been given a structured summary of the policy.")
    prompt = (
        f"You are a senior policy drafting expert.\n\n{source_label}:\n{source}\n\n"
        f"TASK: {task_note} Write a formal adapted policy document for the following scenario:\n{scenario}\n\n"
        "Requirements:\n- Use professional policy language (shall, must, is required to)\n"
        "- Structure with clear sections: Title, Scope, Key Provisions, Rights and Obligations, Enforcement\n"
        "- Adapt the tone and priorities specifically to the given scenario\n"
        "- Length: approximately 400 words\n- Begin directly with the policy title, no preamble\n\nADAPTED POLICY:"
    )
    result, err = ollama_generate(prompt, timeout=180)
    if err == "timeout":
        return "⏳ Request timed out — Ollama may be busy. Please try again."
    if err == "connection_error":
        return "❌ Cannot connect to Ollama. Make sure Ollama is running on localhost:11434."
    if err:
        return f"❌ Error: {err}"
    return result or "❌ No response received from Ollama."

def summarise(text, mode):
    n_sent = {"Brief": 5, "Standard": 9, "Detailed": 14}.get(mode, 9)
    max_l = {"Brief": 130, "Standard": 220, "Detailed": 340}.get(mode, 220)
    min_l = {"Brief": 50, "Standard": 100, "Detailed": 150}.get(mode, 100)
    if TRANSFORMERS_OK:
        result = bart_summarise(text, max_l, min_l)
        if result:
            return result, "BART Transformer · Local NLP"
    return tfidf_summarise(text, n_sentences=n_sent), "TF-IDF Extractive NLP"

def safe_html(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r'\s+', ' ', text).strip()

def extract_structured_sections(text, mode):
    if NLTK_OK:
        try:
            sentences = sent_tokenize(text)
        except Exception:
            sentences = re.split(r'(?<=[.!?])\s+', text)
    else:
        sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.split()) > 4]
    goal_kw = {"aim","goal","objective","purpose","mission","intend","protect","ensure","guarantee","safeguard","promote","rights","welfare","safety","benefit","priority","commitment","designed","intended","seek","focus","target"}
    measure_kw = {"allowance","compensation","fee","charge","rate","amount","refund","penalty","payment","rebooking","cancellation","baggage","delay","denied","boarding","kg","cad","sdr","must","shall","required","restricted","permitted","entitled","submit","apply","document","valid","tax","cost","price","ticket","carry","checked","economy","business","class"}
    direction_kw = {"framework","convention","regulation","treaty","agreement","international","montreal","appr","governed","applicable","overall","balance","align","authority","jurisdiction","obligation","responsibility","enforce","scope","covers","operates","structure","approach","strategy","direction","policy"}
    def score(sentence, keywords):
        words = set(re.sub(r'[^a-z ]', '', sentence.lower()).split())
        return len(words & keywords)
    scored = [(s, score(s, goal_kw), score(s, measure_kw), score(s, direction_kw)) for s in sentences]
    if mode == "Brief":
        g_n, m_n, d_n = 1, 2, 1
    elif mode == "Standard":
        g_n, m_n, d_n = 2, 3, 2
    else:
        g_n, m_n, d_n = 3, 4, 3
    used_globally = set()
    def pick(field_idx, n):
        ranked = sorted(scored, key=lambda x: (-x[field_idx], x[(field_idx%3)+1], x[((field_idx+1)%3)+1]))
        selected = []
        for row in ranked:
            s = row[0]
            if s not in used_globally and len(selected) < n:
                selected.append(s)
                used_globally.add(s)
        return " ".join(selected)
    goals = pick(1, g_n) or (sentences[0] if sentences else "N/A")
    measures = pick(2, m_n) or (sentences[1] if len(sentences) > 1 else "N/A")
    direction = pick(3, d_n) or (sentences[-1] if sentences else "N/A")
    return {"goals": goals, "measures": measures, "direction": direction}

STUDENT_SCENARIOS = [
    {
        "label": "Passengers with Disabilities",
        "prompt": (
            "Adapt this policy specifically for passengers with physical disabilities and "
            "mobility impairments. Prioritise accessibility rights, mandatory special assistance "
            "procedures, priority boarding, wheelchair provisions, guide dog allowances, "
            "seating accommodations, and the airline's obligations to ensure dignified and "
            "barrier-free travel throughout the entire journey."
        ),
        "rationale": "Audience-based — shifts priorities to accessibility obligations and passenger rights.",
    },
    {
        "label": "Canadian Regulatory Compliance",
        "prompt": (
            "Rewrite this policy to fully comply with Canada's Air Passenger Protection "
            "Regulations (APPR). Emphasise mandatory compensation amounts for delays and "
            "denied boarding, tarmac delay passenger rights, seating of children adjacent "
            "to guardians, communication obligations, baggage liability, and recourse "
            "through the Canadian Transportation Agency (CTA)."
        ),
        "rationale": "Regulatory-based — shifts priorities to enforceable rights under Canadian law.",
    },
]

def check_ollama():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        if r.status_code == 200:
            models = [m["name"] for m in r.json().get("models", [])]
            has_llama = any("llama3.2" in m for m in models)
            return True, has_llama, models
        return False, False, []
    except Exception:
        return False, False, []

ollama_ok, llama_ok, ollama_models = check_ollama()

if ollama_ok and llama_ok:
    _pill = ("🟢", "llama3.2 · ready")
elif ollama_ok:
    _pill = ("🟡", "llama3.2 · missing")
else:
    _pill = ("🔴", "Ollama · offline")

st.markdown(f"""
<div class="app-header">
  <div style="display:flex;align-items:center;gap:20px;flex-wrap:wrap;">
    <span style="font-size:2.6rem;">⚖️</span>
    <div>
      <h1>PolicyAI System</h1>
      <p>NLP Policy Summarisation &amp; Generative Policy Drafting &nbsp;
        <span style="display:inline-flex;align-items:center;gap:4px;
                     background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.25);
                     border-radius:20px;padding:2px 9px;font-size:0.6rem;letter-spacing:0.6px;vertical-align:middle;opacity:0.9;">
          {_pill[0]} {_pill[1]}
        </span>
      </p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1, 1], gap="large")

# LEFT — SUMMARISATION

with left:
    st.markdown('<div class="panel-title">Policy Summarisation</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">Upload or paste any policy document</div>', unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["Upload File", "Paste Text", "Sample Policy"])

    with t1:
        uploaded = st.file_uploader("Upload", type=["pdf","docx","txt","json","md"], label_visibility="collapsed")
        if uploaded:
            file_id = f"{uploaded.name}_{uploaded.size}"
            if st.session_state.get("_last_upload_id") != file_id:
                st.session_state["_last_upload_id"] = file_id
                st.session_state.active_tab = "upload"
                st.session_state.policy_text = extract_text(uploaded)
                st.session_state.loaded_name = uploaded.name
                st.session_state.summary = st.session_state.goals = st.session_state.measures = st.session_state.direction = st.session_state.draft = ""
                st.session_state.dynamic_scenarios = []
                st.session_state.scenarios_generated_for = ""
                st.session_state.scenario_slots = [{"label":"","prompt":"","draft":""},{"label":"","prompt":"","draft":""}]
        if st.session_state.get("active_tab") == "upload" and st.session_state.policy_text:
            st.success(f"✅ {st.session_state.get('loaded_name','Document')} — {len(st.session_state.policy_text.split()):,} words")

    with t2:
        if "paste_area_val" not in st.session_state:
            st.session_state.paste_area_val = ""
        paste_val = st.text_area("Paste", height=160, placeholder="Paste the full text of your policy document here...",
                                  label_visibility="collapsed", value=st.session_state.paste_area_val, key="paste_area")
        st.session_state.paste_area_val = paste_val
        pb1, pb2 = st.columns([3, 1])
        with pb1:
            if st.button("Use This Text", key="btn_paste"):
                if paste_val.strip():
                    st.session_state.policy_text = paste_val
                    st.session_state.loaded_name = "Pasted Text"
                    st.session_state.active_tab = "paste"
                    st.session_state["_last_upload_id"] = None
                    st.session_state.summary = st.session_state.goals = st.session_state.measures = st.session_state.direction = st.session_state.draft = ""
                    st.session_state.dynamic_scenarios = []
                    st.session_state.scenarios_generated_for = ""
                    st.session_state.scenario_slots = [{"label":"","prompt":"","draft":""},{"label":"","prompt":"","draft":""}]
                else:
                    st.warning("Text area is empty.")
        with pb2:
            if st.button("Clear", key="btn_clear_paste"):
                st.session_state.policy_text = st.session_state.loaded_name = st.session_state.active_tab = st.session_state.paste_area_val = ""
                st.session_state.summary = st.session_state.goals = st.session_state.measures = st.session_state.direction = st.session_state.draft = ""
                st.session_state.dynamic_scenarios = []
                st.session_state.scenarios_generated_for = ""
                st.session_state.scenario_slots = [{"label":"","prompt":"","draft":""},{"label":"","prompt":"","draft":""}]
                st.session_state["_last_upload_id"] = None
                st.rerun()
        if st.session_state.get("active_tab") == "paste" and st.session_state.policy_text:
            st.success(f"✅ {len(st.session_state.policy_text.split()):,} words loaded")

    with t3:
        s_col1, s_col2 = st.columns(2)
        for col, (pol_label, pol_text) in zip([s_col1, s_col2], list(SAMPLE_POLICIES.items())):
            with col:
                is_selected = (st.session_state.get("active_tab") == "sample" and st.session_state.get("loaded_name") == pol_label)
                btn_label = f"✅ {pol_label}" if is_selected else pol_label
                if st.button(btn_label, key=f"btn_sample_{pol_label[:8]}", use_container_width=True):
                    st.session_state.policy_text = pol_text
                    st.session_state.loaded_name = pol_label
                    st.session_state.active_tab = "sample"
                    st.session_state.draft = ""
                    st.session_state["_last_upload_id"] = None
                    st.session_state.scenario_slots = [{"label":"","prompt":"","draft":""},{"label":"","prompt":"","draft":""}]
                    st.session_state["sc_ta_0"] = st.session_state["sc_ta_1"] = ""
                    st.session_state.summary = st.session_state.goals = st.session_state.measures = st.session_state.direction = ""
                    st.rerun()
        if st.session_state.get("active_tab") == "sample" and st.session_state.policy_text:
            wc = len(st.session_state.policy_text.split())
            art_count = len(re.findall(r"Article\s+\d+", st.session_state.policy_text, re.IGNORECASE))
            meta = f"{wc:,} words" + (f" · {art_count} articles" if art_count else "")
            st.success(f"✅ {st.session_state.get('loaded_name','')} — {meta}")

    st.markdown('<hr class="line">', unsafe_allow_html=True)
    st.markdown("**Select summary depth:**")
    mode = st.radio("Depth", ["Brief", "Standard", "Detailed"], horizontal=True, label_visibility="collapsed")
    depth_hint = {
        "Brief": "Short 3–4 sentence overview · 1 line per section",
        "Standard": "Covers goals, key measures and overall direction · 2 lines per section",
        "Detailed": "Full breakdown of all key provisions and clauses · 3–4 lines per section",
    }
    st.caption(f"ℹ️  {depth_hint[mode]}")

    if st.button("Generate Summary", key="btn_summarise"):
        if not st.session_state.policy_text.strip():
            st.warning("Please load or paste a policy document first.")
        else:
            try:
                with st.spinner("Summarising policy..."):
                    summary, method = summarise(st.session_state.policy_text, mode)
                    st.session_state.summary = summary
                    st.session_state.summary_method = method
                    sections = extract_structured_sections(summary, mode)
                    st.session_state.goals = safe_html(sections["goals"])
                    st.session_state.measures = safe_html(sections["measures"])
                    st.session_state.direction = safe_html(sections["direction"])
                    orig_wc = len(st.session_state.policy_text.split())
                    summ_wc = len(summary.split())
                    st.session_state.orig_wc = orig_wc
                    st.session_state.summ_wc = summ_wc
                    st.session_state.compression = round((1 - summ_wc / orig_wc) * 100) if orig_wc else 0
                st.rerun()
            except Exception as _e:
                st.error(f"❌ Summary failed: {_e}")

    if st.session_state.summary:
        wc = len(st.session_state.summary.split())
        st.markdown(f"""
        <div class="result-card teal">
          <span class="result-label lbl-teal">{mode} Summary</span>
          <div class="summary-section">
            <div class="summary-section-title goals"> &nbsp;Main Goals</div>
            <div class="summary-section-body goals">{st.session_state.goals}</div>
          </div>
          <hr class="summary-divider">
          <div class="summary-section">
            <div class="summary-section-title measures"> &nbsp;Key Measures &amp; Strategies</div>
            <div class="summary-section-body measures">{st.session_state.measures}</div>
          </div>
          <hr class="summary-divider">
          <div class="summary-section">
            <div class="summary-section-title direction"> &nbsp;Overall Direction</div>
            <div class="summary-section-body direction">{st.session_state.direction}</div>
          </div>
          <div class="stat-row">
            <span class="stat-chip chip-teal">{wc} words in summary</span>
            <span class="stat-chip chip-teal">{st.session_state.orig_wc:,} words original</span>
            <span class="stat-chip chip-lav">{st.session_state.compression}% compressed</span>
            <span class="stat-chip chip-teal">{mode} mode</span>
            <span class="stat-chip chip-amber">{st.session_state.summary_method}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        full_structured = (
            f"POLICY SUMMARY\n{'='*50}\n\n"
            f"MAIN GOALS\n{st.session_state.goals}\n\n"
            f"KEY MEASURES & STRATEGIES\n{st.session_state.measures}\n\n"
            f"OVERALL DIRECTION\n{st.session_state.direction}"
        )
        st.download_button("⬇️  Download Summary (.txt)", data=full_structured,
                           file_name="policy_summary.txt", mime="text/plain", use_container_width=True)

        nlp = st.session_state.get("nlp_stats", {})
        if nlp:
            with st.expander(" NLP Preprocessing Details"):
                st.markdown("""
                **How TF-IDF Extractive Summarisation Works:**
                1. **Sentence Tokenisation** — splits document into individual sentences
                2. **Stopword Removal** — removes common words (the, is, and…) that carry no meaning
                3. **Token Filtering** — keeps only meaningful content words (length > 2)
                4. **TF-IDF Scoring** — scores each word by how frequent it is in a sentence vs. how rare it is across all sentences
                5. **Sentence Ranking** — ranks sentences by their combined word scores
                6. **Top-N Selection** — picks the highest-scoring sentences and returns them in original order
                """)
                st.markdown("**Pipeline output for this document:**")
                c1, c2, c3 = st.columns(3)
                c1.metric("Sentences found", nlp.get("sentences_found", "—"))
                c2.metric("Sentences selected", nlp.get("sentences_selected", "—"))
                c3.metric("Vocabulary size", nlp.get("vocab_size", "—"))
                c1.metric("Raw tokens", nlp.get("raw_tokens", "—"))
                c2.metric("After filtering", nlp.get("filtered_tokens", "—"))
                c3.metric("Stopwords removed", nlp.get("stopwords_removed", "—"))
                top = nlp.get("top_terms", [])
                if top:
                    st.markdown(f"**Top TF-IDF terms:** `{'` · `'.join(top)}`")


# RIGHT — GENERATIVE DRAFTING

with right:
    st.markdown('<div class="panel-title"> Scenario-Based Policy Drafting</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-sub">Select a mode below, then generate your policy</div>', unsafe_allow_html=True)

    active_tab = st.session_state.get("active_tab", "")
    _policy_text = st.session_state.get("policy_text", "")
    _is_known_sample = any(_policy_text == v for v in SAMPLE_POLICIES.values())
    is_sample_mode = (active_tab == "sample") or _is_known_sample
    is_custom_mode = (active_tab in ("upload", "paste")) and not _is_known_sample
    current_summary = st.session_state.get("summary", "")

    if "scenario_slots" not in st.session_state:
        st.session_state.scenario_slots = [{"label":"","prompt":"","draft":""},{"label":"","prompt":"","draft":""}]
    if "right_mode" not in st.session_state:
        st.session_state.right_mode = None

    rm = st.session_state.right_mode

    st.markdown("""
    <style>
    div.mode-card-free .stButton>button,div.mode-card-adapt .stButton>button{
        background:#ffffff!important;border:2px solid #e0e0e0!important;color:#2c2416!important;
        height:auto!important;padding:20px 12px!important;border-radius:12px!important;
        font-size:0.88rem!important;line-height:1.5!important;white-space:pre-line!important;
        box-shadow:0 1px 4px rgba(0,0,0,0.06)!important;font-family:'DM Sans',sans-serif!important;}
    div.mode-card-free .stButton>button:hover,div.mode-card-adapt .stButton>button:hover{
        background:#f5f5f5!important;border-color:#2a7c6f!important;transform:translateY(-1px)!important;}
    div.mode-card-free-active .stButton>button,div.mode-card-adapt-active .stButton>button{
        background:linear-gradient(135deg,#2a7c6f,#1e5c52)!important;border:2px solid #2a7c6f!important;
        color:#fff!important;height:auto!important;padding:20px 12px!important;border-radius:12px!important;
        font-size:0.88rem!important;line-height:1.5!important;white-space:pre-line!important;
        box-shadow:0 4px 18px rgba(42,124,111,0.28)!important;font-family:'DM Sans',sans-serif!important;}
    </style>
    """, unsafe_allow_html=True)

    mc1, mc2 = st.columns(2)
    for col, mode_key, title, subtitle in [
       (mc1, "free",  "Free Draft", "Type anything · AI writes the policy"),
       (mc2, "adapt", "Adapt from Summary", " · Upload or load document"),
   ]:
        with col:
            is_active = rm == mode_key
            css_class = f"mode-card-{mode_key}-active" if is_active else f"mode-card-{mode_key}"
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            clicked = st.button(f"{title}\n{subtitle}", key=f"btn_mode_{mode_key}", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            if clicked and rm != mode_key:
                st.session_state.right_mode = mode_key
                st.rerun()

    # Only show content once a mode has been selected
    if st.session_state.right_mode is not None:
        st.markdown('<hr class="line">', unsafe_allow_html=True)

    # ── MODE A: FREE DRAFT ──
    if st.session_state.right_mode == "free":
        st.markdown('<div class="panel-sub">Describe any policy — AI writes it for you</div>', unsafe_allow_html=True)
        if not ollama_ok:
            st.markdown('<div style="background:var(--coral-lt);border:1px solid #f0b8ae;border-radius:var(--r);padding:10px 16px;margin-bottom:10px;font-family:\'DM Mono\',monospace;font-size:0.68rem;color:var(--coral);">🔴 Ollama not running — start it on localhost:11434</div>', unsafe_allow_html=True)
        elif not llama_ok:
            st.markdown('<div style="background:var(--amber-lt);border:1px solid #eac87a;border-radius:var(--r);padding:10px 16px;margin-bottom:10px;font-family:\'DM Mono\',monospace;font-size:0.68rem;color:var(--amber);">⚠️ llama3.2 not found — run: ollama pull llama3.2</div>', unsafe_allow_html=True)

        st.markdown("**What policy do you want to create?**")
        free_prompt = st.text_area("free_prompt", height=120,
            placeholder="e.g. Write a workplace social media policy for a tech company...\ne.g. Draft a refund policy for an e-commerce store...",
            label_visibility="collapsed", key="free_draft_input")

        if st.button("Generate Policy", key="btn_free_gen", use_container_width=True):
            if not free_prompt.strip():
                st.warning("Please describe the policy you want to create.")
            elif not ollama_ok:
                st.error("❌ Ollama is not running.")
            elif not llama_ok:
                st.error("❌ llama3.2 not found. Run: ollama pull llama3.2")
            else:
                prompt = (
                    "You are a senior policy drafting expert.\n\n"
                    f"TASK: Write a complete, formal policy document based on this request:\n{free_prompt.strip()}\n\n"
                    "Requirements:\n- Use professional policy language (shall, must, is required to)\n"
                    "- Structure with clear sections: Title, Purpose, Scope, Key Provisions, Rights and Obligations, Enforcement\n"
                    "- Be specific and practical — include real rules and guidelines\n"
                    "- Length: approximately 400-500 words\n- Begin directly with the policy title, no preamble\n\nPOLICY:"
                )
                with st.spinner("Writing policy with llama3.2..."):
                    result, err = ollama_generate(prompt, timeout=180)
                if err == "timeout":
                    st.error("⏳ Request timed out — Ollama may be busy. Please try again.")
                elif err == "connection_error":
                    st.error("❌ Cannot connect to Ollama.")
                elif err:
                    st.error(f"❌ Error: {err}")
                else:
                    st.session_state.free_draft_result = result or ""
                    st.rerun()

        if st.session_state.get("free_draft_result"):
            wc_f = len(st.session_state.free_draft_result.split())
            draft_html = (st.session_state.free_draft_result
                          .replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\n","<br>"))
            st.markdown(f"""
            <div class="result-card coral">
              <span class="result-label lbl-coral">Generated Policy</span>
              <div style="color:#2c2416;font-size:0.86rem;line-height:1.85;">{draft_html}</div>
              <div class="stat-row">
                <span class="stat-chip chip-coral">{wc_f} words</span>
                <span class="stat-chip chip-lav">llama3.2 · Ollama</span>
                <span class="stat-chip chip-amber">Free Draft</span>
              </div>
            </div>""", unsafe_allow_html=True)
            st.download_button("⬇️ Download Policy (.txt)", data=st.session_state.free_draft_result,
                               file_name="free_draft_policy.txt", mime="text/plain",
                               use_container_width=True, key="dl_free_draft")

    # ── MODE B: ADAPT FROM SUMMARY ──
    elif st.session_state.right_mode == "adapt":
        if not st.session_state.policy_text:
            st.markdown("""
            <div style="background:var(--amber-lt);border:1px solid #eac87a;border-left:4px solid var(--amber);
                        border-radius:var(--r);padding:12px 16px;">
              <div style="font-family:'DM Sans',sans-serif;font-size:0.83rem;font-weight:600;color:var(--amber);">
                Load a document on the left first
              </div>
              <div style="font-family:'DM Mono',monospace;font-size:0.64rem;color:var(--amber);opacity:0.8;margin-top:4px;">
                Upload a file, paste text, or pick a sample policy — then generate a summary to unlock drafting.
              </div>
            </div>""", unsafe_allow_html=True)
        else:
            if is_sample_mode:
                st.markdown('<div class="panel-sub">Use a pre-defined scenario or write your own</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="panel-sub">Describe a scenario and generate an adapted policy</div>', unsafe_allow_html=True)

            if is_sample_mode:
                st.markdown("**Quick-fill a scenario — or type your own below:**")
                pc1, pc2 = st.columns(2)
                for sc_idx, (col, sc) in enumerate(zip([pc1, pc2], STUDENT_SCENARIOS)):
                    with col:
                        slot_prompt = st.session_state.scenario_slots[sc_idx].get("prompt","") if sc_idx < len(st.session_state.scenario_slots) else ""
                        is_active = slot_prompt.strip() == sc["prompt"].strip()
                        bg = "var(--teal-lt)" if is_active else "var(--surface)"
                        bdr = "var(--teal)" if is_active else "var(--teal-mid)"
                        tick = "✅ " if is_active else ""
                        st.markdown(f"""
                        <div style="background:{bg};border:1.5px solid {bdr};border-radius:var(--r);padding:12px 14px;margin-bottom:6px;">
                          <div style="font-family:'DM Sans',sans-serif;font-size:0.83rem;font-weight:600;color:var(--teal);margin-bottom:4px;">{tick}{sc["label"]}</div>
                          <div style="font-family:'DM Mono',monospace;font-size:0.61rem;color:var(--muted);line-height:1.55;">{sc["rationale"]}</div>
                        </div>""", unsafe_allow_html=True)
                        if st.button(f"↙ Use in Slot {sc_idx+1}", key=f"fill_sc_{sc_idx}", use_container_width=True):
                            if sc_idx < len(st.session_state.scenario_slots):
                                st.session_state.scenario_slots[sc_idx]["label"] = sc["label"]
                                st.session_state.scenario_slots[sc_idx]["prompt"] = sc["prompt"]
                            else:
                                st.session_state.scenario_slots.append({"label": sc["label"], "prompt": sc["prompt"], "draft": ""})
                            st.session_state[f"sc_ta_{sc_idx}"] = sc["prompt"]
                            st.rerun()
                st.markdown('<hr class="line">', unsafe_allow_html=True)

            # ── SINGLE MERGED STATUS BANNER ──
            if not current_summary:
                st.markdown("""
                <div style="display:flex;align-items:center;gap:10px;
                            background:var(--amber-lt);border:1px solid #eac87a;
                            border-radius:var(--r);padding:12px 16px;margin-bottom:4px;">
                  <span style="font-size:1.3rem;"></span>
                  <div>
                    <div style="font-family:'DM Sans',sans-serif;font-size:0.83rem;font-weight:600;color:var(--amber);">One step to go</div>
                    <div style="font-family:'DM Mono',monospace;font-size:0.64rem;color:var(--amber);opacity:0.8;margin-top:2px;">
                      Click Generate Summary on the left to unlock drafting
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            if not ollama_ok:
                st.markdown('<div style="background:var(--coral-lt);border:1px solid #f0b8ae;border-radius:var(--r);padding:10px 16px;margin-top:6px;font-family:\'DM Mono\',monospace;font-size:0.68rem;color:var(--coral);">🔴 Ollama not running — start it on localhost:11434</div>', unsafe_allow_html=True)
            elif not llama_ok:
                st.markdown('<div style="background:var(--amber-lt);border:1px solid #eac87a;border-radius:var(--r);padding:10px 16px;margin-top:6px;font-family:\'DM Mono\',monospace;font-size:0.68rem;color:var(--amber);">⚠️ llama3.2 not found — run: ollama pull llama3.2</div>', unsafe_allow_html=True)

            st.markdown('<hr class="line">', unsafe_allow_html=True)

            SLOT_COLORS = ["coral", "teal", "lav", "amber"]
            for idx in range(len(st.session_state.scenario_slots)):
                slot = st.session_state.scenario_slots[idx]
                color = SLOT_COLORS[idx % len(SLOT_COLORS)]

                h1, h2 = st.columns([5, 1])
                with h1:
                    st.markdown(f"**Scenario {idx+1}**")
                with h2:
                    if st.button("🗑", key=f"del_slot_{idx}", disabled=not bool(slot.get("prompt","").strip()), help="Clear this scenario box"):
                        st.session_state.scenario_slots[idx] = {"label":"","prompt":"","draft":""}
                        st.session_state[f"sc_ta_{idx}"] = ""
                        if idx+1 >= len(st.session_state.scenario_slots):
                            st.session_state.scenario_slots.append({"label":"","prompt":"","draft":""})
                            st.session_state[f"sc_ta_{idx+1}"] = ""
                        st.rerun()

                ta_key = f"sc_ta_{idx}"
                if slot["prompt"] and st.session_state.get(ta_key, "") != slot["prompt"]:
                    st.session_state[ta_key] = slot["prompt"]

                new_prompt = st.text_area(f"sc_{idx}", height=85,
                    placeholder="Describe the target audience, constraints, or context for this scenario...",
                    label_visibility="collapsed", key=ta_key)
                st.session_state.scenario_slots[idx]["prompt"] = new_prompt

                ga, gb = st.columns([5, 1])
                with ga:
                    gen_btn = st.button(f"Generate Draft {idx+1}", key=f"btn_gen_{idx}", use_container_width=True)
                with gb:
                    redo_btn = st.button("🔄", key=f"btn_redo_{idx}", disabled=not slot["draft"], help="Regenerate")

                if gen_btn or redo_btn:
                    prompt_val = st.session_state.scenario_slots[idx]["prompt"].strip()
                    if not prompt_val:
                        st.warning(f"Please describe Scenario {idx+1} first.")
                    elif not current_summary:
                        st.warning("Generate a summary on the left first.")
                    elif not ollama_ok:
                        st.error("❌ Ollama is not running.")
                    elif not llama_ok:
                        st.error("❌ llama3.2 not found. Run: ollama pull llama3.2")
                    else:
                        with st.spinner(f"Generating Policy Draft {idx+1} with llama3.2..."):
                            st.session_state.scenario_slots[idx]["draft"] = ollama_draft(current_summary, prompt_val)

                if slot["draft"]:
                    wc_d = len(slot["draft"].split())
                    draft_html = slot["draft"].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace("\n","<br>")
                    sc_short = slot["prompt"][:65] + ("..." if len(slot["prompt"]) > 65 else "")
                    st.markdown(f"""
                    <div class="result-card {color}">
                      <span class="result-label lbl-{color}">Adapted Policy — Scenario {idx+1}</span>
                      <div style="font-size:0.72rem;color:#9a8e7e;margin-bottom:12px;font-family:'DM Mono',monospace;font-style:italic;">{sc_short}</div>
                      <div style="color:#2c2416;font-size:0.86rem;line-height:1.85;">{draft_html}</div>
                      <div class="stat-row">
                        <span class="stat-chip chip-{color}">{wc_d} words</span>
                        <span class="stat-chip chip-lav">llama3.2 · Ollama</span>
                        <span class="stat-chip chip-amber">Adapt from Summary</span>
                      </div>
                    </div>""", unsafe_allow_html=True)
                    st.download_button(f"⬇️ Download Draft {idx+1}", data=slot["draft"],
                                       file_name=f"policy_draft_scenario_{idx+1}.txt", mime="text/plain",
                                       use_container_width=True, key=f"dl_draft_{idx}")

                st.markdown('<hr class="line">', unsafe_allow_html=True)

            if st.button("➕ Add Scenario", use_container_width=True):
                st.session_state.scenario_slots.append({"label":"","prompt":"","draft":""})
                st.rerun()

            all_drafts = [s for s in st.session_state.scenario_slots if s["draft"]]
            if len(all_drafts) >= 2:
                sep = "=" * 50
                report_parts = [
                    f"POLICIAI MULTI-SCENARIO REPORT\n{sep}\n",
                    f"POLICY SUMMARY\n{sep}",
                    f"MAIN GOALS\n{st.session_state.goals}\n",
                    f"KEY MEASURES & STRATEGIES\n{st.session_state.measures}\n",
                    f"OVERALL DIRECTION\n{st.session_state.direction}\n",
                ]
                for i, s in enumerate(st.session_state.scenario_slots):
                    if s["draft"]:
                        report_parts.append(f"\n{sep}\nSCENARIO {i+1}\n{sep}\n{s['prompt']}\n")
                        report_parts.append(f"\nADAPTED POLICY DRAFT {i+1}\n{sep}\n{s['draft']}\n")
                st.download_button("⬇️ Download Full Multi-Scenario Report (.txt)",
                                   data="\n".join(report_parts), file_name="policy_ai_full_report.txt",
                                   mime="text/plain", use_container_width=True)

# ── Status Bar ──
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
st.markdown('<hr class="line">', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
for col, (label, ok) in zip([c1,c2,c3,c4], [
    ("Policy Loaded", bool(st.session_state.policy_text)),
    ("Summary Ready", bool(st.session_state.summary)),
    ("Drafts Generated", sum(1 for s in st.session_state.get("scenario_slots",[]) if s["draft"]) > 0),
    ("Ollama Active", ollama_ok and llama_ok),
]):
    bg = "#d6eeeb" if ok else "#f5f0e8"
    col_ = "#2a7c6f" if ok else "#9a8e7e"
    icon = "✅" if ok else "○"
    col.markdown(
        f"<div style='background:{bg};border-radius:8px;padding:8px;text-align:center;"
        f"font-family:DM Mono,monospace;font-size:0.68rem;color:{col_};'>{icon} {label}</div>",
        unsafe_allow_html=True)